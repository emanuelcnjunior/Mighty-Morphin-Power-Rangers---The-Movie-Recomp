# v0.2.1 — Windows x64 portable ZIP

This candidate hardens and simplifies the Windows distribution after review of
the v0.2.0 installer.

- Removes the local toolchain downloader/rebuild module from precompiled retail
  builds.
- Replaces the public Inno installer with
  `Power-Rangers-The-Movie-PC-v0.2.1-Windows-x64.zip` as the exclusive
  RecompLauncher Easy Setup and portable Windows distribution. The explicit
  platform/architecture suffix supports automatic build recognition.
- Publishes the ZIP checksum as a sidecar and in `SHA256SUMS.txt`.
- Keeps ROM SHA-256 validation/import, saves, graphics, input, launcher and
  runtime features unchanged.

The release contains no ROM. Players must supply the original unheadered USA
SNES ROM (1,572,864 bytes; SHA-256
`c706b70097c679f6f0ced6f77a30620807d0b2555fc3c683c0ec2fc791176039`).

No installer is included in this release. The legacy Inno scripts remain in
the source tree only for maintenance and are not part of the normal build.

Automated build, schema/ZIP, ROM import and install/reinstall smoke tests passed
in the earlier audit. The rebuilt package is revalidated for this release;
in-app RecompLauncher validation by the team, controller/manual hotkey and
gameplay save-state regression checks remain pending. See
`docs/security-audit.md` for exact evidence and limitations.

ZIP SHA-256:
`56d1963b0713188b60cd1586715547f75f4251df4dd5890a1787ebdfae9466d8`
