# Dependency map

## Confirmed

### TMNT IV reference port

- Repository: `https://github.com/emanuelcnjunior/TMNT-IV-Turtles-in-Time-PC-Recomp.git`
- Reference commit: `d17d051ca5ccb8051aa91e812e0ef183c14ff30c`
- SNESRecomp pin: `8c5219b42de7b26f15890d16b84fabb442bdbe5d`
- recomp-ui pin: `5aece1f2ab7447593465d21905ae7408eb656c59`

The Power Rangers project now uses the same two pinned submodules. The TMNT
project confirms that generated code belongs in ignored `src/gen/`, analysis
configuration belongs in `recomp/`, and the per-game integration boundary is
`src/game_rtl.c`.

### recomp-ui

- Repository: `https://github.com/emanuelcnjunior/recomp-ui.git`
- Default branch inspected at: `3f1d6f122a58823614abce14f5b86f4d165a629c`
- Port-specific branch: `tmnt4-save-hotkeys`
- Integration: CMake `recomp_target_launcher_ui(<target> CONSOLE snes)`
- Host requirements: C/C++17, CMake, SDL2 or SDL3, OpenGL, Threads

The TMNT branch extends the SNES launcher profile with `QuickSave` and
`QuickLoad`, defaulting to F1 and F2. This is UI/host wiring; the target runtime
still has to implement the underlying save-state operations.

## Still required

1. A working Python 3.11+ installation available as `python` on PATH.
2. Rust 1.85+ through rustup with the default MSVC toolchain.
3. Visual Studio 2022 with Desktop development with C++, Windows SDK, and CMake
   tools for Windows.
4. Confirmation of the first target: faithful boot-to-title milestone or a
   complete playable port with launcher/save-state features from the start.

Git for Windows and Git Bash are already available. The current Python launcher
points at a missing Microsoft Store Python 3.10 installation; `cargo`, `rustc`,
`cmake`, and the Visual C++ compiler are not currently discoverable.
