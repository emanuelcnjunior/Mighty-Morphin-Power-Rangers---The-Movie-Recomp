"""Validate the launcher profile and optional retail ZIP against the official guide.

Requires jsonschema. Download recomplauncher-agent.md from the official SDK,
then pass its path with --guide. No game files are needed.
"""
import argparse
import codecs
import hashlib
import json
from pathlib import Path
import re
import zipfile

import jsonschema


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--guide', type=Path, required=True)
    parser.add_argument('--zip', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    guide = args.guide.read_text(encoding='utf-8')
    schema = json.loads(guide.split('# The JSON schema', 1)[1]
                        .split('```json', 1)[1].split('```', 1)[0])
    jsonschema.Draft7Validator.check_schema(schema)
    raw = (root / 'recomplauncher.json').read_bytes()
    profile = json.loads(raw)
    jsonschema.validate(profile, schema)
    source = (root / 'src/game_paths.c').read_text(encoding='utf-8')
    source = source.split('const char kGameDefaultConfig[] =', 1)[1].split(';', 1)[0]
    ini = ''.join(codecs.decode(s, 'unicode_escape')
                  for s in re.findall(r'"([^"]*)"', source))
    defaults = {}
    for line in ini.splitlines():
        if line.startswith('['):
            section = line[1:-1]
        elif '=' in line:
            key, value = line.split('=', 1)
            defaults[section + '/' + key.strip()] = value.strip()
    assert profile['config'][0]['new'] == defaults, 'First-run defaults differ from the game'
    assert not profile['config'][0].get('always'), 'Do not force existing preferences'
    print('PASS: official schema and first-run defaults; no forced preferences')
    if args.zip:
        identity = dict(re.findall(r'^\s*(\w+)\s*=\s*([^\n#]+)',
                                   (root / 'rom_identity.txt').read_text(encoding='utf-8'), re.M))
        with zipfile.ZipFile(args.zip) as archive:
            assert archive.read('recomplauncher.json') == raw
            for program in profile['start']['program'] + profile['prepare']['program']:
                assert program in archive.namelist(), program
            for entry in archive.infolist():
                if entry.is_dir():
                    continue
                path = Path(entry.filename)
                assert path.suffix.lower() not in ('.sfc', '.smc', '.rom', '.bin', '.srm', '.sav', '.state', '.spc', '.bps', '.ips'), path
                assert path.name not in ('config.ini', 'keybinds.ini', 'rom.cfg', 'state.toml'), path
                assert hashlib.sha256(archive.read(entry)).hexdigest() != identity['expected_sha256'].strip(), path
        print('PASS: retail ZIP profile, executable, no known ROM or user data')


if __name__ == '__main__':
    main()
