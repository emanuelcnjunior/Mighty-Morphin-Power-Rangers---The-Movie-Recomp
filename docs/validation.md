# Validation log

## 2026-11-13 - Version 0.2.0 closure

- User approved closing the version, requested fullscreen startup and a Select
  shortcut for HD, and authorized commit/push.
- Fullscreen is the startup policy, including an existing windowed config;
  Alt+Enter and F10 can still switch to a window during the session.
- P1 Select (DS4 Share) toggles Original/HD once on release. Select combinations
  and modal input do not toggle. Start keeps its original game action, and the
  physical/virtual DS4Windows pair cannot double-toggle the global setting.
- A fresh Release build completed in `build-final`, with 24 GPU combinations,
  59 HD/configuration checks and all four component tests passing. The fourth
  test covers Select taps, holds, chords, release and modal cancellation.
- Both framework patches applied to fresh pinned sources and passed a second
  idempotent application. Save fingerprints normalize source line endings.
- A private copy of the user's actual preview Quick Save was loaded by the
  final runtime in two fresh processes. All 180 future state/image hashes and
  120 repeated boundary restores passed. The original file was not modified.
  Its exact preview schema is accepted only on the matching Windows/MSVC ABI;
  other incompatible schemas remain rejected.
- Startup smoke reached the first simulated frame and audio callback with
  version 0.2.0, OpenGL and `fullscreen=1`.

No ROM, user save, generated game code or captured game image is included in
the commit. Physical confirmation of the final Select shortcut is still pending.

## 2026-11-13 - Save/load and HD presentation

- Adapted the title save extension and graphics profile from TMNT IV
  `d17d051ca5ccb8051aa91e812e0ef183c14ff30c`, using the already matching
  framework/UI pins and retaining the Power Rangers display-memory fix.
- Five manual slots plus an isolated quick slot; F1/F2, L2/R2, F11 browser,
  atomic files under LocalAppData, and ROM/schema/integrity preflight.
- Release build completed with no warnings in the final build. Original/HD,
  Scale2x/Sharp/Nearest, F10 settings, Alt+Enter fullscreen, persisted video
  preferences and external texture-pack loading are enabled.
- Save validation: two input-port scenarios, each written in one process and
  restored in another. All 180 subsequent complete-machine/visible-frame hashes
  matched; each process also passed 120 boundary save/restore/replay checks.
  This validates both serialized input ports, not a complete two-player campaign.
- Invalid CRC, truncated files, wrong ROM, wrong schema and wrong identity were
  rejected without modifying the running state. Save-browser and graphics-panel
  open/navigation/cancel operations preserved guest state and visible pixels.
- GPU: NVIDIA GTX 1650, OpenGL 3.3, 24 mode/filter/output combinations at
  512x448, 1280x720, 1920x1080 and 3840x2160; zero failures. Synthetic atlas,
  alpha fallback, brightness and masking also passed.
- HD pack/configuration probe: 59 checks passed, including content IDs,
  transactional reload, unsupported-effect fallback, viewport bounds,
  fullscreen selection/persistence and keybindings.
- Three ROM-free component tests passed: display-memory isolation, raster
  journal and atomic state writing (partial write, flush/close/rename failures,
  locked destination, interrupted child process and recovery).
- Reproduction: `tools/validate_runtime.py`. Private evidence is ignored under
  `build/runtime-validation/`; the script restored the playable entry point.

Physical DS4 save/load, fullscreen interaction and audio after restoration still
need user confirmation. No redrawn Power Rangers texture pack is bundled;
the immediate visual enhancement is GPU filtering with optional pack support.

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
