"""Unit tests for SNES ROM verification and header inspection using synthetic fixtures only."""
import hashlib
from pathlib import Path
import struct
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT / "tools"))
from rom_tool import load_identity, validate, inspect


class TestRomTool(unittest.TestCase):
    def test_load_identity_defaults(self):
        identity = load_identity()
        self.assertEqual(identity["rom_size"], 1572864)
        self.assertEqual(identity["region"], "USA")
        self.assertEqual(identity["mapping"], "lorom")
        self.assertEqual(
            identity["expected_sha256"],
            "c706b70097c679f6f0ced6f77a30620807d0b2555fc3c683c0ec2fc791176039"
        )

    def test_validate_synthetic_rom(self):
        # Create a synthetic 1,572,864 byte fixture
        synthetic_size = 1572864
        synthetic_data = b"\xEA" * synthetic_size
        synthetic_sha = hashlib.sha256(synthetic_data).hexdigest()
        identity = {
            "rom_size": synthetic_size,
            "expected_sha256": synthetic_sha,
            "expected_crc32": "",
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            rom_path = Path(tmpdir) / "test_rom.sfc"
            rom_path.write_bytes(synthetic_data)

            # Valid read
            result = validate(rom_path, identity)
            self.assertEqual(len(result), synthetic_size)
            self.assertEqual(result, synthetic_data)

            # Reject undersized
            rom_path.write_bytes(b"\xEA" * (synthetic_size - 1))
            with self.assertRaisesRegex(ValueError, "Wrong size"):
                validate(rom_path, identity)

            # Reject oversized / copier header
            rom_path.write_bytes(b"\xEA" * (synthetic_size + 512))
            with self.assertRaisesRegex(ValueError, "Wrong size"):
                validate(rom_path, identity)

            # Reject modified content / SHA-256 mismatch
            bad_data = b"\x00" + (b"\xEA" * (synthetic_size - 1))
            rom_path.write_bytes(bad_data)
            with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                validate(rom_path, identity)

            # Reject missing file
            with self.assertRaises(FileNotFoundError):
                validate(Path(tmpdir) / "nonexistent.sfc", identity)

    def test_inspect_synthetic_lorom_header(self):
        data = bytearray(0x8000)
        header_offset = 0x7FC0
        title = b"POWER RANGERS TEST   "
        data[header_offset:header_offset + 21] = title
        data[header_offset + 0x15] = 0x20  # LoROM
        data[header_offset + 0x16] = 0x00  # ROM only
        data[header_offset + 0x17] = 0x0B  # 16 Mbit code
        data[header_offset + 0x18] = 0x00  # No SRAM
        data[header_offset + 0x19] = 0x01  # North America / USA
        data[header_offset + 0x1A] = 0x33  # Extended developer code
        data[header_offset + 0x1B] = 0x00  # Version 1.0

        # Checksum and complement
        checksum = 0x1234
        complement = 0xEDCB  # 0x1234 ^ 0xEDCB == 0xFFFF
        struct.pack_into("<HH", data, header_offset + 0x1C, complement, checksum)

        # Vectors
        struct.pack_into("<H", data, header_offset + 0x2A, 0x8100)  # NMI
        struct.pack_into("<H", data, header_offset + 0x2E, 0x8200)  # IRQ
        struct.pack_into("<H", data, header_offset + 0x3C, 0x8000)  # Reset

        info = inspect(bytes(data))
        self.assertEqual(info["title"], "POWER RANGERS TEST")
        self.assertEqual(info["map_mode"], "0x20")
        self.assertEqual(info["destination_code"], "0x01")
        self.assertEqual(info["checksum"], "0x1234")
        self.assertEqual(info["checksum_complement"], "0xEDCB")
        self.assertTrue(info["checksum_pair_valid"])
        self.assertEqual(info["reset_vector"], "0x8000")
        self.assertEqual(info["nmi_vector"], "0x8100")
        self.assertEqual(info["irq_vector"], "0x8200")


if __name__ == "__main__":
    unittest.main()
