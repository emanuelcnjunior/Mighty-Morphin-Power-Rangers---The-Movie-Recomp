"""Replace the retail profile in a legacy setup pack with a picker-only profile."""
import json
from pathlib import Path
import sys
import zipfile

archive = Path(sys.argv[1])
profile = json.loads(Path('recomplauncher.json').read_text(encoding='utf-8'))
profile = {key: profile[key] for key in ('$schema', 'format', 'name', 'repo')}
profile['start'] = {'program': [
    'MightyMorphinPowerRangersTheMovieSNESRecomp.exe',
    'MightyMorphinPowerRangersTheMovieSNESRecomp'], 'args': ['--launcher']}
temporary = archive.with_suffix('.tmp.zip')
with zipfile.ZipFile(archive) as source, zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED) as target:
    prefix = source.namelist()[0].split('/')[0]
    manifest = prefix + '/recomplauncher.json'
    for entry in source.infolist():
        if entry.filename != manifest:
            target.writestr(entry, source.read(entry))
    target.writestr(manifest, json.dumps(profile, indent=2) + '\n')
temporary.replace(archive)
