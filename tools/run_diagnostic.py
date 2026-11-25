"""Run the game with diagnostic tracing and export a sanitized, ROM-free ZIP report."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from rom_tool import validate


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", required=True, type=Path, help="Path to verified USA SNES ROM")
    parser.add_argument("--exe", type=Path, help="Path to MightyMorphinPowerRangersTheMovieSNESRecomp.exe")
    parser.add_argument("--output", type=Path, help="Path for generated diagnostic ZIP file")
    parser.add_argument("game_args", nargs="*", help="Optional extra arguments passed to the executable")
    args = parser.parse_args()

    # 1. Verify ROM compliance
    try:
        validate(args.rom)
    except Exception as err:
        print(f"Error: ROM verification failed: {err}", file=sys.stderr)
        return 1

    # 2. Locate executable
    if args.exe:
        exe = args.exe.resolve(strict=True)
    else:
        # Look in standard build / release locations
        candidates = [
            ROOT / "build/Release/MightyMorphinPowerRangersTheMovieSNESRecomp.exe",
            ROOT / "build/MightyMorphinPowerRangersTheMovieSNESRecomp.exe",
            ROOT / "MightyMorphinPowerRangersTheMovieSNESRecomp.exe",
        ]
        exe = None
        for cand in candidates:
            if cand.is_file():
                exe = cand.resolve()
                break
        if not exe:
            print("Error: Executable not found. Pass --exe <path> explicitly.", file=sys.stderr)
            return 1

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    diagnostic_dir = ROOT / "local" / f"diagnostic-{stamp}"
    diagnostic_dir.mkdir(parents=True, exist_ok=False)

    env = os.environ.copy()
    env["SNESRECOMP_DIAGNOSTIC"] = "1"

    command = [str(exe), str(args.rom.resolve()), "--no-launcher", *args.game_args]
    print(f"Starting diagnostic session for: {exe.name}")
    print("Reproduce the issue or gameplay scenario, then close the game.")

    stdout_log = diagnostic_dir / "stdout.log"
    stderr_log = diagnostic_dir / "stderr.log"

    with stdout_log.open("w", encoding="utf-8") as stdout, \
         stderr_log.open("w", encoding="utf-8") as stderr:
        result = subprocess.run(command, cwd=diagnostic_dir, env=env, stdout=stdout, stderr=stderr)

    metadata = {
        "created_utc": stamp,
        "exit_code": result.returncode,
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "executable_sha256": sha256_file(exe),
        "rom_sha256": sha256_file(args.rom),
        "game_args": args.game_args,
        "privacy": "Archive contains diagnostic logs and metadata only; no ROM or save files.",
    }

    metadata_path = diagnostic_dir / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    archive = (args.output or (ROOT / f"diagnostic-{stamp}.zip")).resolve()
    archive.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
        for name in ("metadata.json", "stdout.log", "stderr.log"):
            file_path = diagnostic_dir / name
            if file_path.is_file():
                bundle.write(file_path, name)

    print("\nDiagnostic report generated successfully:")
    print(f"  Archive: {archive}")
    print("  Privacy: No ROM data, save states, or personal identifiable files were packaged.")
    print("You can attach this ZIP to your GitHub issue.")
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
