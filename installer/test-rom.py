"""Exercise the actual retail ROM gate with private, isolated fixtures."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exe', type=Path, required=True)
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=Path('build-installer/rom-validation'))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    identity = {}
    for raw in (root / 'rom_identity.txt').read_text(encoding='utf-8').splitlines():
        if '=' in raw and not raw.lstrip().startswith('#'):
            key, value = raw.split('=', 1)
            identity[key.strip()] = value.split('#', 1)[0].strip().strip('"')
    exe, rom, out = args.exe.resolve(strict=True), args.rom.resolve(strict=True), args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    original = rom.read_bytes()
    assert hashlib.sha256(original).hexdigest() == identity['expected_sha256']
    env = dict(os.environ, POWER_RANGERS_USER_DATA=str(out / 'user-data'))
    results = []

    def probe(name, option, path, expected, custom_env=None):
        result = subprocess.run([str(exe), option, str(path)], env=custom_env or env,
                                capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        if result.returncode != expected:
            raise RuntimeError(f'{name}: exit={result.returncode}, expected={expected}')
        results.append(dict(test=name, result='PASS', exit=result.returncode))

    probe('Original USA ROM', '--validate-rom', rom, 0)
    renamed = out / 'ROM com outro nome 日本.smc'
    renamed.write_bytes(original)
    probe('Renamed valid ROM and Unicode path', '--validate-rom', renamed, 0)
    corrupt = out / 'corrupt.sfc'
    changed = bytearray(original)
    changed[12345] ^= 1
    corrupt.write_bytes(changed)
    probe('Corrupt USA ROM', '--validate-rom', corrupt, 2)
    changed[0x7fd9] = 2
    region = out / 'wrong-region.sfc'
    region.write_bytes(changed)
    probe('Synthetic different-region content', '--validate-rom', region, 2)
    invalid = out / 'invalid.sfc'
    invalid.write_bytes(b'not a ROM')
    probe('Invalid file / wrong size', '--validate-rom', invalid, 2)
    headered = out / 'headered.sfc'
    headered.write_bytes(bytes(512) + original)
    probe('Copier header rejected', '--validate-rom', headered, 2)
    truncated = out / 'truncated.sfc'
    truncated.write_bytes(original[:-1])
    probe('Truncated ROM', '--validate-rom', truncated, 2)
    probe('Missing file', '--validate-rom', out / 'missing.sfc', 2)
    probe('Import renamed USA ROM', '--import-rom', renamed, 0)
    canonical = out / 'user-data' / identity['rom_file']
    assert canonical.read_bytes() == original
    unicode_env = dict(env, POWER_RANGERS_USER_DATA=str(out / 'Perfil João 日本'))
    probe('Unicode user-data directory', '--import-rom', rom, 0, unicode_env)
    assert (out / 'Perfil João 日本' / identity['rom_file']).read_bytes() == original
    probe('Invalid import preserves last good ROM', '--import-rom', corrupt, 2)
    assert canonical.read_bytes() == original
    blocked_root = out / 'blocked-data'
    blocked_root.mkdir(exist_ok=True)
    (blocked_root / identity['rom_file']).mkdir(exist_ok=True)
    blocked_env = dict(env, POWER_RANGERS_USER_DATA=str(blocked_root))
    probe('Import write failure', '--import-rom', rom, 3, blocked_env)
    (out / 'results.json').write_text(json.dumps(results, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(results, indent=2))
    print(f'PASS: {len(results)} retail ROM checks; original user data untouched')


if __name__ == '__main__':
    main()
