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
