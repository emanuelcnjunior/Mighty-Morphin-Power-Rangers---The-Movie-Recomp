# Based on the TMNT IV source/ABI guard. Absolute checkout paths are excluded.
file(GLOB_RECURSE _save_sources CONFIGURE_DEPENDS
    "${SNESRECOMP_ROOT}/runner/src/*.c" "${SNESRECOMP_ROOT}/runner/src/*.h"
    "${CMAKE_SOURCE_DIR}/src/*.c" "${CMAKE_SOURCE_DIR}/src/*.h"
    "${CMAKE_SOURCE_DIR}/recomp/*.cfg")
list(SORT _save_sources)
set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS ${_save_sources})
set(_save_contract "power-rangers-movie-save-v1;${CMAKE_C_COMPILER_ID};${CMAKE_C_COMPILER_VERSION};${CMAKE_SIZEOF_VOID_P}")
string(APPEND _save_contract ";${CMAKE_BUILD_TYPE};${CMAKE_C_FLAGS};${CMAKE_C_FLAGS_RELEASE};slots=5;hd=1")
get_cmake_property(_save_options CACHE_VARIABLES)
list(SORT _save_options)
foreach(_save_option IN LISTS _save_options)
    if(_save_option MATCHES "^SNESRECOMP_" AND NOT _save_option MATCHES "ROOT|DIR|PATH")
        string(APPEND _save_contract ";${_save_option}=${${_save_option}}")
    endif()
endforeach()
foreach(_save_source IN LISTS _save_sources)
    # Git may check out the same source with LF or CRLF. Line endings do not
    # change the execution ABI and must not invalidate otherwise equal saves.
    file(READ "${_save_source}" _save_text)
    string(REPLACE "\r\n" "\n" _save_text "${_save_text}")
    string(SHA256 _save_hash "${_save_text}")
    string(APPEND _save_contract "${_save_hash}")
endforeach()
string(SHA256 POWER_RANGERS_SAVE_SCHEMA "${_save_contract}")
file(CONFIGURE OUTPUT "${CMAKE_CURRENT_BINARY_DIR}/save_schema.h"
    CONTENT "#define POWER_RANGERS_SAVE_SCHEMA \"@POWER_RANGERS_SAVE_SCHEMA@\"\n" @ONLY)
