# Validation log

## 2026-11-13 — Windows boot-to-title

Build configuration:

- Windows x64 Release
- MSVC 19.44.35230
- CMake 4.4.4
- SDL3 3.4.10
- SNESRecomp `8c5219b42de7b26f15890d16b84fabb442bdbe5d`
- recomp-ui `5aece1f2ab7447593465d21905ae7408eb656c59`

Validated manually with the supported USA ROM:

- Executable starts successfully.
- Game reaches visible output/title flow.
- Audio is present.
- Keyboard input responds.

Not yet validated:

- Starting and completing the first stage.
- Sprite priority, scrolling, raster effects, and transitions under gameplay.
- Two-player input.
- Pause/continue/game-over paths.
- Save states, rewind, launcher settings, and clean shutdown.
- Full-game progression and ending.

The next milestone is a first-stage playthrough while watching the runtime log
for unresolved dispatch targets, interpreter fallbacks, or post-mortem output.
