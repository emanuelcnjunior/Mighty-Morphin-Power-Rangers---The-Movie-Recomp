# Validation log

## 2026-11-13 - First run on the second Windows PC

- Verified the USA ROM against the pinned CRC32 and SHA-256.
- Built Windows x64 Release with MSVC 19.44.35229 and SDL3 3.4.10.
- User confirmed working image, audio and DS4 input, then reported sprite
  flicker and apparently mirrored animation during movement.
- Reproduced malformed running sprites with scripted input and both live
  gamepad slots disabled. The issue therefore also occurs without DS4 input.
- Fixed mixed-frame graphics memory: the bottom blanking interval prepares
  next-frame OAM/VRAM before the deferred renderer draws the completed field.
  See `patches/README.md` for the opt-in display-memory latch and framework patch.
- Replayed the same 1,597-frame boot/selection/rightward-movement sequence.
  All 61 captured WRAM images in frames 1536-1596 were identical before/after;
  inspected consecutive images no longer contained detached sprite pieces.
- Both renderers produced pixel-identical images for all 61 corrected frames.
- Both ROM-free runtime tests passed: display-memory isolation/restoration and
  the existing raster-journal contract. Fresh patch application and repeat
  configuration were also verified.

- User confirmed the corrected animation looks right during gameplay with
  the DS4 after rebuilding and relaunching.

Broader gameplay coverage is still pending. Earlier frame-extension save states
are incompatible with the updated extension size.

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
