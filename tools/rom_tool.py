"""SNES ROM identity verification and header inspection tool.

Operates purely on memory and metadata; never outputs commercial ROM bytes.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys
import zlib

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IDENTITY_PATH = ROOT / "rom_identity.txt"


def load_identity(path=DEFAULT_IDENTITY_PATH):
    identity = {}
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Identity file not found: {path}")
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, value = line.split("=", 1)
            identity[key.strip()] = value.strip().strip('"').strip("'")
    if "rom_size" in identity:
        identity["rom_size"] = int(identity["rom_size"])
    return identity


def validate(path, identity=None):
    if identity is None:
        identity = load_identity()
    expected_size = identity["rom_size"]
    expected_sha256 = identity["expected_sha256"].lower()

    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"ROM file not found: {path}")

    with path.open("rb") as stream:
        data = stream.read(expected_size + 1)

    if len(data) != expected_size:
        raise ValueError(
            f"Wrong size: expected {expected_size} bytes; got {len(data)} "
            "(copier headers, truncated or expanded dumps are rejected)."
        )

    digest = hashlib.sha256(data).hexdigest().lower()
    if digest != expected_sha256:
        raise ValueError(
            f"SHA-256 mismatch: got {digest}, expected {expected_sha256}. "
            "Modified, patched, non-USA, or headered ROM rejected."
        )

    if "expected_crc32" in identity and identity["expected_crc32"]:
        crc = f"{zlib.crc32(data) & 0xFFFFFFFF:08x}".lower()
        expected_crc = identity["expected_crc32"].lower()
        if crc != expected_crc:
            raise ValueError(f"CRC-32 mismatch: got {crc}, expected {expected_crc}.")

    return data


def inspect(data):
    if len(data) < 0x8000:
        raise ValueError("Data too small to contain an SNES LoROM header.")

    header_offset = 0x7FC0
    title_raw = data[header_offset:header_offset + 21]
    title = title_raw.decode("ascii", errors="replace").strip()

    def u16(offset):
        return struct.unpack_from("<H", data, offset)[0]

    complement = u16(header_offset + 0x1C)
    checksum = u16(header_offset + 0x1E)
    nmi_vector = u16(header_offset + 0x2A)  # native NMI
    irq_vector = u16(header_offset + 0x2E)  # native IRQ
    reset_vector = u16(header_offset + 0x3C)  # emulation reset vector

    map_mode = data[header_offset + 0x15]
    rom_type = data[header_offset + 0x16]
    rom_size_code = data[header_offset + 0x17]
    sram_size_code = data[header_offset + 0x18]
    destination_code = data[header_offset + 0x19]
    developer_id = data[header_offset + 0x1A]
    rom_version = data[header_offset + 0x1B]

    crc32_hex = f"{zlib.crc32(data) & 0xFFFFFFFF:08x}"
    sha256_hex = hashlib.sha256(data).hexdigest()

    return {
        "title": title,
        "map_mode": f"0x{map_mode:02X}",
        "rom_type": f"0x{rom_type:02X}",
        "rom_size_code": f"0x{rom_size_code:02X}",
        "sram_size_code": f"0x{sram_size_code:02X}",
        "destination_code": f"0x{destination_code:02X}",
        "developer_id": f"0x{developer_id:02X}",
        "version": rom_version,
        "checksum": f"0x{checksum:04X}",
        "checksum_complement": f"0x{complement:04X}",
        "checksum_pair_valid": (checksum ^ complement) == 0xFFFF,
        "reset_vector": f"0x{reset_vector:04X}",
        "nmi_vector": f"0x{nmi_vector:04X}",
        "irq_vector": f"0x{irq_vector:04X}",
        "size_bytes": len(data),
        "crc32": crc32_hex,
        "sha256": sha256_hex,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["validate", "inspect"])
    parser.add_argument("rom", type=Path, help="Path to SNES ROM file")
    parser.add_argument("--identity", type=Path, default=DEFAULT_IDENTITY_PATH,
                        help="Path to rom_identity.txt")
    args = parser.parse_args()

    try:
        identity = load_identity(args.identity)
        data = validate(args.rom, identity)
    except (OSError, ValueError) as error:
        print(f"ROM check failed: {error}", file=sys.stderr)
        return 1

    if args.command == "validate":
        print(f"PASS: ROM verified against {identity.get('display_name', 'SNES ROM')} identity.")
        print(f"  Size:   {len(data)} bytes")
        print(f"  SHA256: {hashlib.sha256(data).hexdigest()}")
    elif args.command == "inspect":
        info = inspect(data)
        print(json.dumps(info, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
