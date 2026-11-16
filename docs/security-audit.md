# Security audit for v0.2.1

Audit date: 2026-11-16. Scope: published v0.2.0 Windows installer, its
installed payload, the Windows x64 retail build, and the v0.2.1 candidate
artifacts. This report separates observations from hypotheses and pending
external checks. A lower antivirus detection count is not proof of safety.

## Published v0.2.0 evidence

The installer was downloaded from the project's GitHub v0.2.0 release. Its
SHA-256 is `dffa345b2898bc55452c1ac3e61c9b845bc3a98f8f1a3fa7a9082f76cef0d44f`,
matching the file reported by RecompLauncher. It is a 5,600,410-byte,
unsigned Inno Setup 6.7.4 executable. The supplied VirusTotal result reported
4/75 detections; the VirusTotal UI/API was not available to this environment,
so no engine-level rescan or behavioural trace is claimed here.

An isolated per-user install showed this payload:

- one unsigned x64 game executable, SHA-256
  `d6493ad044b03a6856170fca2df456926671b31ee6a141df4d3c0c97ae8c86fe`;
- ten Microsoft Visual C++ 14.44.35211 runtime DLLs, all with valid Microsoft
  Authenticode signatures;
- launcher fonts/images, licenses, `recomplauncher.json`, a manifest, and an
  empty mod-package placeholder;
- the unsigned Inno uninstaller generated at install time.

No ROM, save, personal configuration, PDB, object file, source file, Python
script, Rust program, credential, or test log was present in the installed
program payload. The install was per-user (`PrivilegesRequired=lowest`), used
HKCU for its uninstall registration, created only requested shortcuts, and
made no persistence entry beyond the standard Inno uninstall record.

PE inspection with MSVC `dumpbin` found six ordinary sections in the game
executable (`.text`, `.rdata`, `.data`, `.pdata`, `.rsrc`, `.reloc`) and no UPX
section or UPX marker. No project packaging step invokes UPX, encryption, or
an obfuscator. The Inno executable has the normal setup overlay containing its
compressed payload. `lzma2`/solid compression in v0.2.0 was documented Inno
behaviour, not evidence by itself of malicious code.

## Identified causes and corrections

Two unnecessary behaviours were present in the v0.2.0 retail path:

1. `snesrecomp_codegen_host.c` was linked into the already-compiled retail
   game. That setup-host module contains toolchain download, hidden
   `CreateProcess`, local rebuild, and relaunch code. Those capabilities are
   appropriate for the separate source/setup pack, but are unnecessary in a
   retail executable that already contains generated code. v0.2.1 conditionally
   excludes the module whenever `POWER_RANGERS_RETAIL_WINDOWS=ON`.
2. Inno validated the ROM and then launched the game hidden during
   `ssPostInstall` to import it. v0.2.1 performs no custom-code execution during
   installation. Standalone users choose/import their ROM visibly on first
   launch; RecompLauncher continues to call the documented `--import-rom`
   preparation command.

The installer remains per-user, makes no downloads, runs no PowerShell or
command script, and contains no custom registry instructions. Solid compression
was disabled to make individual-file extraction and review less coupled; LZMA2
remains for ordinary distribution size. This is a transparency/maintainability
choice, not an antivirus-evasion measure.

The game still imports `CreateProcessA/W`, `ShellExecuteW`, and `WS2_32.dll`
through the shared desktop runtime, SDL, file/open-folder UI, and UDP launcher
components. Their continued presence is disclosed and must not be represented
as eliminated. Static source review found no retail updater or automatic
download path after removing the setup host. Network-capable code supports
launcher/netplay infrastructure and is not initiated by the installer.

## v0.2.1 candidate artifacts

| Artifact | Bytes | SHA-256 | Authenticode |
| --- | ---: | --- | --- |
| `MightyMorphinPowerRangersTheMovieSNESRecomp.exe` | 11,610,624 | `b7f89cf372dd38addf1809a8f82ab29a4dad9d149f6c4f98474264071318b4a5` | Not signed |
| `Power-Rangers-The-Movie-PC-v0.2.1-Windows-x64.zip` | 4,585,854 | `56d1963b0713188b60cd1586715547f75f4251df4dd5890a1787ebdfae9466d8` | Not applicable |

`dist/SHA256SUMS.txt` and the ZIP `.sha256` sidecar are the checksum sources.
The release publishes no installer. Only the three imported
CRT DLLs are bundled (`msvcp140.dll`, `vcruntime140.dll`, and
`vcruntime140_1.dll`); all are Microsoft-signed version 14.44.35211. SDL 3.4.10 is built statically from the
pinned archive whose configured SHA-256 is
`12b34280415ec8418c864408b93d008a20a6530687ee613d60bfbd20411f2785`.
Framework submodules remain at the commits in `framework_pins.txt`; no submodule
reference was changed for this release.

## Tests performed

- MSVC 19.44 Windows x64 Release build: passed.
- Runtime dependency resolution with CMake: passed, no unresolved DLLs.
- Official RecompLauncher schema and ZIP layout validation: passed.
- Twelve valid/invalid/Unicode/import/preservation ROM cases: passed.
- Clean install, invalid-ROM rejection, valid import, video/audio/fullscreen
  scripted start, uninstall, user-data preservation, reinstall and second
  start: passed.
- Payload deny-list and known-ROM hash check: passed.
- Microsoft Defender 4.18.26100.4-0, signatures 1.463.326.0: no threats found
  in the executable, ZIP, or installer. This is one local engine result only.

Hardware controller input, perceptual graphics-filter quality, five-slot
save/load during real gameplay, F1/F2/F6/F10/F11 interaction, Alt+Enter, and an
external HD texture pack were not manually exercised in this audit. The build
uses the unchanged runtime implementations, but these items remain pending
manual regression testing. The candidate was not tested inside the actual
RecompLauncher application and was not submitted to VirusTotal.

## Publication and false-positive review

The Windows x64 ZIP is the exclusive public release artifact. Upload the ZIP,
its checksum sidecar and `SHA256SUMS.txt`, then verify the uploaded hash. The
schema validation reported here is not final RecompLauncher approval; the
team's in-app analysis remains pending. If binaries are submitted separately
to VirusTotal, preserve the report URLs and compare the game EXE and each DLL.
If a vendor flags a file, use that vendor's false-positive
portal with the SHA-256, public source/release URL, this audit, the exact build
commit, dependency provenance, and the explanation above. Do not request
reclassification before checking that the uploaded hash equals the candidate.

Suggested English response after publication and external validation:

> We investigated the v0.2.0 report rather than assuming a false positive. The
> retail build unnecessarily contained our source/setup-host module (toolchain
> download, process creation and rebuild/relaunch code), and the old installer
> ran the game hidden to import the ROM. v0.2.1 removes the setup-host module
> from retail builds and removes installers from public distribution; ROM import now happens
> visibly on first launch or through RecompLauncher's documented prepare step.
> The release also provides a root-layout portable Windows x64 ZIP, a complete
> file manifest and SHA256SUMS. No ROM is distributed. Please review the new
> hashes and the attached scan links/audit; we understand that approval depends
> on your independent analysis.
