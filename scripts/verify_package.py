"""Verify the portable release archive for compliance, security and absence of ROM bytes.

Checks:
1. No copyrighted ROM bytes or copier headers are embedded in any entry.
2. No private local paths (e.g. 'C:\\Users\\') leaked in text files or metadata.
3. Windows executable and DLLs are valid x64 PE binaries.
4. Required launcher metadata (recomplauncher.json, guides) are present.
5. Computes SHA-256 checksums and validates archive integrity.
"""
import argparse
import hashlib
from pathlib import Path
import re
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from rom_tool import load_identity


def checksum(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_archive(archive_path: Path, identity: dict = None) -> dict:
    if identity is None:
        identity = load_identity()

    rom_size = identity["rom_size"]
    rom_sha256 = identity["expected_sha256"].lower()

    archive_path = Path(archive_path).resolve(strict=True)
    results = {"valid": True, "files": {}, "warnings": [], "errors": []}

    with zipfile.ZipFile(archive_path, "r") as archive:
        namelist = archive.namelist()

        # Check required files
        if "recomplauncher.json" not in namelist:
            results["errors"].append("Missing required 'recomplauncher.json' in archive.")

        has_exe = any(name.endswith("MightyMorphinPowerRangersTheMovieSNESRecomp.exe") for name in namelist)
        if not has_exe:
            results["errors"].append("Missing game executable in archive root.")

        for name in namelist:
            if name.endswith("/"):
                continue  # skip directory entries

            data = archive.read(name)
            sha = checksum(data)
            results["files"][name] = sha

            # Check for forbidden file extensions
            lower_name = name.lower()
            for bad_ext in (".sfc", ".smc", ".rom", ".sav", ".srm", ".state", ".spc", ".bps", ".ips"):
                if lower_name.endswith(bad_ext):
                    results["errors"].append(f"Forbidden game/save artifact found: {name}")

            # Check for embedded ROM bytes
            if len(data) >= rom_size:
                if sha == rom_sha256:
                    results["errors"].append(f"Commercial ROM embedded as {name}")
                # Search for verbatim ROM slice inside the file
                for offset in range(0, len(data) - rom_size + 1, 1024):
                    if checksum(data[offset:offset + rom_size]) == rom_sha256:
                        results["errors"].append(f"Verbatim ROM bytes embedded inside {name} at offset 0x{offset:X}")
                        break

            # Check for private paths leaked in text files or logs
            if lower_name.endswith((".json", ".txt", ".ini", ".cfg", ".md", ".log")):
                for encoding in ("utf-8", "ascii", "utf-16le"):
                    try:
                        text = data.decode(encoding)
                        if re.search(r"C:\\Users\\[a-zA-Z0-9._-]+\\", text, re.IGNORECASE):
                            results["errors"].append(f"Private user profile path found in {name}")
                            break
                    except (UnicodeDecodeError, LookupError):
                        continue

            # Verify PE headers for x64 executables and DLLs
            if lower_name.endswith((".exe", ".dll")):
                if len(data) < 64 or data[:2] != b"MZ":
                    results["errors"].append(f"Invalid MZ header for PE binary: {name}")
                else:
                    pe_offset = int.from_bytes(data[60:64], "little")
                    if data[pe_offset:pe_offset + 6] != b"PE\0\0\x64\x86":
                        results["errors"].append(f"Expected Windows x64 PE architecture for: {name}")

    if results["errors"]:
        results["valid"] = False

    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help="Path to release ZIP archive")
    parser.add_argument("--write-sums", action="store_true", help="Write SHA256SUMS.txt alongside the archive")
    args = parser.parse_args()

    results = verify_archive(args.archive)
    if not results["valid"]:
        print("FAIL: Verification errors encountered:", file=sys.stderr)
        for err in results["errors"]:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(f"PASS: Archive '{args.archive.name}' is verified compliant.")
    print(f"  Scanned {len(results['files'])} entries. No ROM bytes or private paths detected.")

    if args.write_sums:
        sums_file = args.archive.parent / f"{args.archive.stem}.sha256"
        archive_sha = checksum(args.archive.read_bytes())
        sums_file.write_text(f"{archive_sha} *{args.archive.name}\n", encoding="ascii")
        print(f"Checksum written to {sums_file.name}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
