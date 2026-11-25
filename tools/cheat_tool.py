"""Parse, decode and validate SNES Game Genie and Pro Action Replay cheat codes.

Supports standalone Game Genie (XXXX-XXXX), Pro Action Replay (XXXXXX:YY or XXXXXXYY),
multi-part combinations (CODE1+CODE2), and RetroArch-style .cht files.
"""
import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import sys

GENIE_ALPHABET = "DF4709156BC8A23E"
REAL_HEX = "0123456789ABCDEF"
ASSIGNMENT = re.compile(r'^([a-zA-Z0-9_]+)\s*=\s*(?:"([^"]*)"|(\S+))\s*$')


@dataclass(frozen=True)
class Patch:
    kind: str       # 'rom' or 'ram'
    address: int    # 24-bit SNES bus address
    value: int      # 8-bit replacement value
    width: int = 1


@dataclass(frozen=True)
class Cheat:
    index: int
    description: str
    code: str
    enabled: bool
    patches: tuple[Patch, ...]


def decode_game_genie(code: str) -> Patch:
    cleaned = code.strip().upper()
    if len(cleaned) != 9 or cleaned[4] != "-":
        raise ValueError(f"Invalid SNES Game Genie format: '{code}'. Expected 'XXXX-XXXX'.")

    stripped = cleaned[:4] + cleaned[5:]
    trans = ""
    for ch in stripped:
        idx = GENIE_ALPHABET.find(ch)
        if idx == -1:
            raise ValueError(f"Invalid character '{ch}' in Game Genie code: '{code}'")
        trans += REAL_HEX[idx]

    data = int(trans, 16)
    byte_val = (data >> 24) & 0xFF
    addr = data & 0xFFFFFF

    address = (
        ((addr & 0x003C00) << 10) +
        ((addr & 0x00003C) << 14) +
        ((addr & 0xF00000) >> 8) +
        ((addr & 0x000003) << 10) +
        ((addr & 0x00C000) >> 6) +
        ((addr & 0x0F0000) >> 12) +
        ((addr & 0x0003C0) >> 6)
    )
    # Addresses in SNES bus >= 0x7E0000 and <= 0x7FFFFF are WRAM
    kind = "ram" if (0x7E0000 <= address <= 0x7FFFFF) else "rom"
    return Patch(kind=kind, address=address, value=byte_val)


def decode_pro_action_replay(code: str) -> Patch:
    cleaned = code.strip().upper().replace(":", "")
    if len(cleaned) != 8 or not re.fullmatch(r"[0-9A-F]{8}", cleaned):
        raise ValueError(f"Invalid SNES Pro Action Replay code: '{code}'. Expected 8 hex digits.")

    address = int(cleaned[:6], 16)
    value = int(cleaned[6:], 16)
    kind = "ram" if (0x7E0000 <= address <= 0x7FFFFF) else "rom"
    return Patch(kind=kind, address=address, value=value)


def decode_part(code: str) -> Patch:
    cleaned = code.strip()
    if "-" in cleaned:
        return decode_game_genie(cleaned)
    return decode_pro_action_replay(cleaned)


def parse(path: Path) -> list[Cheat]:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Cheat file not found: {path}")

    values = {}
    for line_num, raw_line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        match = ASSIGNMENT.fullmatch(line)
        if not match:
            raise ValueError(f"Invalid assignment on line {line_num}: {raw_line}")
        values[match.group(1)] = match.group(2) if match.group(2) is not None else match.group(3)

    if "cheats" not in values:
        raise ValueError("Missing 'cheats' count definition in cheat file.")

    try:
        count = int(values["cheats"])
    except ValueError as err:
        raise ValueError(f"Invalid 'cheats' value: {values['cheats']}") from err

    cheats = []
    for idx in range(count):
        prefix = f"cheat{idx}_"
        desc = values.get(f"{prefix}desc", f"Cheat {idx}")
        code = values.get(f"{prefix}code")
        if not code:
            raise ValueError(f"Cheat {idx} missing 'code' entry.")
        enabled = values.get(f"{prefix}enable", "false").lower() == "true"

        parts = [p.strip() for p in code.split("+")]
        patches = tuple(decode_part(p) for p in parts)
        cheats.append(Cheat(index=idx, description=desc, code=code, enabled=enabled, patches=patches))

    return cheats


def select(cheats: list[Cheat], expression: str) -> list[Cheat]:
    if not expression or not expression.strip():
        return []

    indices = []
    for item in expression.replace(";", ",").split(","):
        item = item.strip()
        if not item:
            continue
        try:
            indices.append(int(item))
        except ValueError as err:
            raise ValueError(f"Invalid cheat index: '{item}'") from err

    cheat_map = {c.index: c for c in cheats}
    selected = []
    seen_writes = {}  # address -> (value, cheat_index)

    for idx in indices:
        if idx not in cheat_map:
            raise ValueError(f"Cheat index {idx} out of range (max: {len(cheats) - 1})")
        cheat = cheat_map[idx]
        for patch in cheat.patches:
            if patch.address in seen_writes:
                prev_val, prev_idx = seen_writes[patch.address]
                if prev_val != patch.value:
                    raise ValueError(
                        f"Conflict: Cheat {idx} ('{cheat.description}') writes 0x{patch.value:02X} "
                        f"to 0x{patch.address:06X}, but Cheat {prev_idx} already writes 0x{prev_val:02X}."
                    )
            seen_writes[patch.address] = (patch.value, idx)
        selected.append(cheat)

    return selected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    decode_cmd = sub.add_parser("decode", help="Decode a Game Genie or PAR code")
    decode_cmd.add_argument("code", help="Code string (e.g. DB6E-0D6D or 7E0628:05)")

    list_cmd = sub.add_parser("list", help="List cheats in a .cht file")
    list_cmd.add_argument("path", type=Path, help="Path to .cht file")

    validate_cmd = sub.add_parser("validate", help="Validate a .cht file and check selection")
    validate_cmd.add_argument("path", type=Path, help="Path to .cht file")
    validate_cmd.add_argument("--select", type=str, default="", help="Comma-separated indices to select")

    args = parser.parse_args()

    if args.command == "decode":
        for part in args.code.split("+"):
            patch = decode_part(part)
            print(f"Code: {part} -> {patch.kind.upper()} address: 0x{patch.address:06X}, value: 0x{patch.value:02X}")
    elif args.command == "list":
        cheats = parse(args.path)
        print(f"Loaded {len(cheats)} cheats from {args.path.name}:")
        for c in cheats:
            print(f"  [{c.index:02d}] {c.description} ({c.code})")
    elif args.command == "validate":
        cheats = parse(args.path)
        print(f"Valid syntax: {len(cheats)} cheats loaded.")
        if args.select:
            chosen = select(cheats, args.select)
            print(f"Selection valid: {len(chosen)} active cheats without conflicts.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
