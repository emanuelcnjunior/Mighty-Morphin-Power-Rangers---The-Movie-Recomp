# Mighty Morphin Power Rangers: The Movie — recompilation

Clean-room reimplementation work for the US SNES release. The original ROM is
used only as a local analysis input and must never be committed or distributed.

## Current status

- ROM identity and internal SNES header validated.
- LoROM address conversion and reset-vector inspection are automated.
- Official SNESRecomp scaffold integrated with the same framework pins used by
  the TMNT IV reference port.
- Initial native analysis generated 24 exact AOT variants from four roots in
  bank `$00` (70 control-flow edges, no LLE-only variants in this first slice).
- Windows x64 Release build succeeds with MSVC 19.44, CMake 4.4.4, SDL3 3.4.10,
  and the shared `recomp-ui` launcher.
- Interactive boot-to-title validation passed on Windows: video, audio, and
  keyboard input all work. Full gameplay correctness is not yet established.

Validated source image:

| Property | Value |
| --- | --- |
| File | `Mighty Morphin Power Rangers - The Movie (USA).sfc` |
| Size | 1,572,864 bytes (12 Mbit) |
| SHA-256 | `c706b70097c679f6f0ced6f77a30620807d0b2555fc3c683c0ec2fc791176039` |
| Mapping | LoROM (`$20`) |
| Reset vector | `$00:8000` |
| SRAM | none declared |

## Validate the local ROM

Place the ROM anywhere under `rom/`, then run:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\analyze-rom.ps1
```

The script refuses unexpected hashes by default. Pass `-AllowUnknownHash` only
when deliberately investigating another dump.

## Generate and build

```powershell
& 'C:\Program Files\Git\bin\bash.exe' tools/regen.sh --rom `
  'C:/path/to/Mighty Morphin Power Rangers - The Movie (USA).sfc'

cmake -S . -B build -G 'Visual Studio 17 2022' -A x64
cmake --build build --config Release --parallel 4
```

Generated ROM-derived C under `src/gen/` is intentionally ignored.

## Save/load and HD presentation

For a ready-to-play Windows installer which asks for the user's own USA ROM,
see [installer instructions](installer/README.md). No ROM is bundled. The
installer and shortcuts use the generated Red Ranger icon.

The desktop build integrates five manual save-state slots plus a separate Quick
Save, guarded full-machine restoration, an Original/HD GPU presenter, Scale2x,
Sharp and Nearest filters, fullscreen controls and optional external texture
packs. The sprite display-memory fix is retained.

- F1 / L2: Quick Save. F2 / R2: Quick Load.
- F11 / Share+R1: save-state browser.
- F6: Original/HD. F10: graphics settings. Alt+Enter: fullscreen.
- Ctrl+L / Share+L3: in-game launcher.

On Windows saves live in `%LOCALAPPDATA%\PowerRangersMovieRecomp\saves\`.
Version 0.2.0 starts fullscreen. A Select tap shortcut was implemented, but the
user reported that it did not toggle HD on their DS4; use F6/F10 while that
shortcut remains under investigation.
HD filtering works without a texture pack; redrawn game artwork is not bundled.
See [save/load and graphics guide](docs/save-and-graphics.md) for controls,
compatibility, texture-pack authoring and reproducible validation.

## Roadmap

1. Decode the reset path and hardware initialization.
2. Identify interrupt handlers, bank boundaries, and data/code regions.
3. Build a symbol map and translate one subsystem at a time.
4. Add deterministic tests against captured original-game behavior.
5. Add a portable runtime and replace extracted assets with runtime-loaded,
   user-supplied ROM data where required.

## External components

The launcher reference is Emanuel's `recomp-ui` fork. The TMNT-specific branch
adds SNES quick-save and quick-load bindings and is the preferred integration
baseline:

```text
https://github.com/emanuelcnjunior/recomp-ui.git
branch: tmnt4-save-hotkeys
```

`recomp-ui` supplies the launcher, settings UI, ROM selection/verification,
controller configuration, and runtime-menu frontend. It does **not** translate
65C816 code or provide the SNES execution/runtime core. Those must come from
the corresponding SNES recompilation toolchain and game-port repository.

This repository intentionally contains no copyrighted ROM bytes or extracted
assets.
