cmake_minimum_required(VERSION 3.20)
project(MightyMorphinPowerRangersTheMovieSNESRecomp C CXX)

set(CMAKE_C_STANDARD 11)
option(POWER_RANGERS_RETAIL_WINDOWS "Build the end-user ROM import flow" OFF)
set(POWER_RANGERS_TEST_ENTRY "" CACHE STRING "Private runtime probe: save, gpu, or packs")
set_property(CACHE POWER_RANGERS_TEST_ENTRY PROPERTY STRINGS "" save gpu packs)

# Release pin for lobby matching. Release builds stamp the VERSION file so two
# peers can prove they are the same build; everything else stamps "dev".
file(READ "${CMAKE_CURRENT_SOURCE_DIR}/VERSION" _GAME_VER_RAW)
string(STRIP "${_GAME_VER_RAW}" GAME_RELEASE_VERSION)
set(SNESRECOMP_BUILD_VERSION "" CACHE STRING
    "Lobby release pin (empty = Release uses VERSION, else dev)")
if(SNESRECOMP_BUILD_VERSION STREQUAL "")
    get_property(_is_multi GLOBAL PROPERTY GENERATOR_IS_MULTI_CONFIG)
    if(_is_multi)
        set(SNESRECOMP_BUILD_VERSION "$<IF:$<CONFIG:Release>,${GAME_RELEASE_VERSION},dev>")
    elseif(CMAKE_BUILD_TYPE STREQUAL "Release")
        set(SNESRECOMP_BUILD_VERSION "${GAME_RELEASE_VERSION}")
    else()
        set(SNESRECOMP_BUILD_VERSION "dev")
    endif()
endif()

set(SNESRECOMP_ROOT "${CMAKE_SOURCE_DIR}/snesrecomp" CACHE PATH
    "Path to the snesrecomp checkout used by this game")
if(NOT EXISTS "${SNESRECOMP_ROOT}/runner/runner.cmake")
    message(FATAL_ERROR
        "snesrecomp submodule missing at ${SNESRECOMP_ROOT}.\n"
        "Run: git submodule update --init --recursive")
endif()
include("${CMAKE_SOURCE_DIR}/cmake/framework_patches.cmake")
power_rangers_patch_framework("${SNESRECOMP_ROOT}")

# Mod packages are part of every project, not an option. The launcher's Mods
# page, the .snesmod loader, the trusted-plugin registry and netplay's mod-set
# gate all hang off this one switch; a build without it cannot exchange mods
# with a peer that has them, and the framework says so at every lobby init.
# Must precede the include: runner.cmake reads it to add the loader sources.
set(SNESRECOMP_ENABLE_MODS ON CACHE BOOL
    "Mod package loader + trusted plugins (required for every title)" FORCE)
include(${SNESRECOMP_ROOT}/runner/runner.cmake)

set(_game_entry src/main.c)
if(POWER_RANGERS_TEST_ENTRY STREQUAL "save")
    set(_game_entry tests/save_runtime_probe.c)
elseif(POWER_RANGERS_TEST_ENTRY STREQUAL "gpu")
    set(_game_entry tests/graphics_gpu_probe.c)
elseif(POWER_RANGERS_TEST_ENTRY STREQUAL "packs")
    set(_game_entry tests/hd_pack_probe.c)
elseif(NOT POWER_RANGERS_TEST_ENTRY STREQUAL "")
    message(FATAL_ERROR "POWER_RANGERS_TEST_ENTRY must be save, gpu, packs, or empty")
endif()
add_executable(MightyMorphinPowerRangersTheMovieSNESRecomp
    ${SNESRECOMP_RUNNER_SOURCES}
    ${_game_entry}
    src/host_contract.c
    src/game_rtl.c
    src/game_save.c
    src/game_paths.c
    src/gen_stubs.c
)

# Save files contain native execution residue. Only the same source/ABI
# contract may restore it; validate before changing the live machine.
include("${CMAKE_SOURCE_DIR}/cmake/save_schema.cmake")
target_include_directories(MightyMorphinPowerRangersTheMovieSNESRecomp PRIVATE
    "${CMAKE_CURRENT_BINARY_DIR}")
target_compile_definitions(MightyMorphinPowerRangersTheMovieSNESRecomp PRIVATE
    SNES_SAVESTATE_SLOTS=5 SNESRECOMP_PERSISTENT_SAVE_PROFILE=1
    SNESRECOMP_HD_ASSETS=1)

# ROM identity. rom_identity.txt is the one place the digests live: the build
# turns it into snesrecomp_rom_identity.h (SNESRECOMP_ROM_EXPECTED_SHA256 and
# friends) for src/main.c, and tools/regen.sh, scripts/package_release.sh and
# the release workflow read the same file. A revision bump is one edit there.
snesrecomp_rom_identity(MightyMorphinPowerRangersTheMovieSNESRecomp ${CMAKE_SOURCE_DIR}/rom_identity.txt)

# Generated recompiler output. Not committed: it is derived from a copyrighted
# ROM, so every developer regenerates it locally from their own copy -- and a
# release does not ship it either. With -DSNESRECOMP_SETUP_HOST=ON and an empty
# src/gen/, this builds the SETUP HOST instead: the same executable minus the
# recompiled code, whose only path is the launcher's Generate & rebuild wizard.
# That is what release zips contain; the player's machine produces the
# playable binary from their own ROM. Without the option an empty src/gen/ is
# still a hard error (the framework owns the message).
snesrecomp_target_generated_code(MightyMorphinPowerRangersTheMovieSNESRecomp ${CMAKE_SOURCE_DIR}/src/gen)

# The mod catalog. This names WHERE the packages are; the framework owns the
# layout they are staged into beside the executable, and stages them on every
# build OF THE EXECUTABLE -- including the launcher's own Generate & rebuild on
# a player's machine, which builds only this target and would skip a sibling
# ALL target. mods/preloaded/packages/ holds reviewed, default-disabled
# packages; players install .snesmod archives through the launcher.
# snesrecomp/docs/MOD_PACKAGES.md.
#
# It used to be `snesrecomp_target_stage_dir(... ${CMAKE_SOURCE_DIR}/mods mods)`
# -- the destination spelled per title, which is how three ports in the same
# workspace ended up shipping an empty Mods page and nothing said so. Declaring
# it is now also enforced: a project with packages that never calls this fails
# to configure.
snesrecomp_target_mod_catalog(MightyMorphinPowerRangersTheMovieSNESRecomp ${CMAKE_SOURCE_DIR}/mods/preloaded)
# Any other directory the game reads exe-relative (a translations/ table, ...)
# is staged with snesrecomp_target_stage_dir, never with a separate ALL target.

target_include_directories(MightyMorphinPowerRangersTheMovieSNESRecomp PRIVATE
    ${SNESRECOMP_RUNNER_INCLUDE_DIRS}
    # common_rtl.c includes "config.h": the desktop key-map / Config contract
    # the framework host supplies (snesrecomp_target_desktop_host below).
    ${SNESRECOMP_ROOT}/runner/src/desktop
    ${CMAKE_SOURCE_DIR}/src
    ${CMAKE_SOURCE_DIR}/recomp
)
target_link_libraries(MightyMorphinPowerRangersTheMovieSNESRecomp PRIVATE ${SNESRECOMP_RUNNER_LIBRARIES})
target_compile_definitions(MightyMorphinPowerRangersTheMovieSNESRecomp PRIVATE
    SNES_GAME_VERSION="${SNESRECOMP_BUILD_VERSION}"
    SNES_GAME_TITLE="Mighty Morphin Power Rangers The Movie"
)
snesrecomp_target_sdl(MightyMorphinPowerRangersTheMovieSNESRecomp)

# The desktop host: launcher flow, ROM resolution, config.ini + [KeyMap],
# window + SDL/OpenGL presenters, audio, gamepads, the save-state browser and
# rewind filmstrip, the pacing clock, crash handlers and the post-mortem
# report. src/main.c is the shim that names this title and supplies its
# hooks; the host is the framework's and improves on a submodule pull.
# Add TIER2 once this port reads the interpreter-gap manifest after each run.
snesrecomp_target_desktop_host(MightyMorphinPowerRangersTheMovieSNESRecomp)
# rom.cfg (the ROM the wizard set this project up from; git-ignored) is
# staged beside the executable when none is there yet, so the first launch
# opens on that dump rather than asking for one.
if(NOT POWER_RANGERS_RETAIL_WINDOWS)
    snesrecomp_target_rom_cache(MightyMorphinPowerRangersTheMovieSNESRecomp)
endif()

# Shared Dear ImGui pre-boot launcher (ROM picker, verification, display /
# audio / input settings). Self-contained: it brings its own ImGui, GL link and
# staged assets, and defines RECOMP_LAUNCHER so src/main.c compiles its GUI path.
set(RECOMP_UI_ROOT "${CMAKE_SOURCE_DIR}/recomp-ui" CACHE PATH
    "Root directory of the recomp-ui launcher repo" FORCE)
if(NOT EXISTS "${RECOMP_UI_ROOT}/recomp_ui.cmake")
    message(FATAL_ERROR
        "recomp-ui missing at ${RECOMP_UI_ROOT}.\n"
        "Run: git submodule update --init --recursive recomp-ui")
endif()
include(${RECOMP_UI_ROOT}/recomp_ui.cmake)
# Stage the film-inspired cover and the project's Red Ranger emblem.
recomp_target_launcher_ui(MightyMorphinPowerRangersTheMovieSNESRecomp CONSOLE snes
    BOXART "${CMAKE_SOURCE_DIR}/launcher_assets/img/boxart.tga"
    BRAND "${CMAKE_SOURCE_DIR}/launcher_assets/img/brand_mark.tga")

# Generate & rebuild belongs only to source/setup-host builds. The retail
# executable already contains recompiled code and imports a verified ROM; it
# must not carry the toolchain downloader, hidden process creation or rebuild
# and relaunch implementation.
if(NOT POWER_RANGERS_RETAIL_WINDOWS)
    target_sources(MightyMorphinPowerRangersTheMovieSNESRecomp PRIVATE
        ${SNESRECOMP_ROOT}/host/snesrecomp_codegen_host.c)
    target_include_directories(MightyMorphinPowerRangersTheMovieSNESRecomp PRIVATE
        ${SNESRECOMP_ROOT}/host
        ${RECOMP_UI_ROOT}/src)
endif()

# Netplay is not built into this target.
# No multitap: two seats, one controller per port.
if(WIN32)
    enable_language(RC)
    string(REPLACE "." "," POWER_RANGERS_RESOURCE_VERSION "${GAME_RELEASE_VERSION}")
    configure_file(installer/power-rangers.rc.in
        "${CMAKE_CURRENT_BINARY_DIR}/power-rangers.rc" @ONLY)
    target_sources(MightyMorphinPowerRangersTheMovieSNESRecomp PRIVATE
        "${CMAKE_CURRENT_BINARY_DIR}/power-rangers.rc")
endif()
if(WIN32 AND POWER_RANGERS_RETAIL_WINDOWS)
    file(STRINGS "${CMAKE_SOURCE_DIR}/rom_identity.txt" _rom_size_line REGEX "^rom_size[ \t]*=")
    string(REGEX MATCH "=[ \t]*([0-9]+)" _rom_size_match "${_rom_size_line}")
    set(_rom_size "${CMAKE_MATCH_1}")
    if(NOT _rom_size MATCHES "^[0-9]+$")
        message(FATAL_ERROR "rom_identity.txt must define rom_size")
    endif()
    target_sources(MightyMorphinPowerRangersTheMovieSNESRecomp PRIVATE src/windows_rom.c)
    target_compile_definitions(MightyMorphinPowerRangersTheMovieSNESRecomp PRIVATE
        POWER_RANGERS_RETAIL_WINDOWS=1 POWER_RANGERS_ROM_SIZE=${_rom_size})
    if(MSVC)
        set_source_files_properties(src/windows_rom.c PROPERTIES COMPILE_OPTIONS /utf-8)
        target_link_options(MightyMorphinPowerRangersTheMovieSNESRecomp PRIVATE
            /SUBSYSTEM:WINDOWS /ENTRY:mainCRTStartup)
    endif()
    target_link_libraries(MightyMorphinPowerRangersTheMovieSNESRecomp PRIVATE comdlg32 shell32)
endif()
