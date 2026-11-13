"""Build and validate saves, HD presentation and packs with a private USA ROM.

All captures stay in build/. The playable entry point is rebuilt on exit.
"""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import shutil


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--build', type=Path, default=Path('build'))
    parser.add_argument('--preview-save', type=Path,
                        help='Also verify a read-only copy of the compatible preview save')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    build = args.build.resolve()
    rom = args.rom.resolve(strict=True)
    out = build / 'runtime-validation'
    out.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    for key in list(env):
        if key.startswith(('POWER_RANGERS_HD_', 'SNESRECOMP_')):
            env.pop(key)

    def run(command, name, cwd=out):
        print(name, flush=True)
        with (out / f'{name}.log').open('w', encoding='utf-8') as log:
            subprocess.run([str(x) for x in command], cwd=cwd, env=env,
                           stdout=log, stderr=subprocess.STDOUT, check=True)

    def build_entry(entry):
        label = entry or 'playable'
        run(['cmake', '-S', root, '-B', build,
             '-DSNESRECOMP_SETUP_HOST=OFF', f'-DPOWER_RANGERS_TEST_ENTRY={entry}'],
            f'configure-{label}')
        run(['cmake', '--build', build, '--config', 'Release', '--parallel', '4'],
            f'build-{label}')

    exe_name = 'MightyMorphinPowerRangersTheMovieSNESRecomp'
    executable = build / 'Release' / f'{exe_name}.exe' if os.name == 'nt' else build / exe_name
    try:
        build_entry('save')
        run([executable, 'keys'], 'save-bindings')
        for players in (1, 2):
            directory = out / f'players-{players}'
            directory.mkdir(exist_ok=True)
            for mode in ('write', 'read'):
                run([executable, rom, mode, directory / 'checkpoint.state',
                     directory / 'expected.txt', players], f'save-{players}-{mode}')
            expected = directory / 'checkpoint.state.baseline-after.ppm'
            restored = directory / 'checkpoint.state.restored-after.ppm'
            if expected.read_bytes() != restored.read_bytes():
                raise RuntimeError(f'Restored image differs, players={players}')
        if args.preview_save:
            preview = out / 'preview-compatibility.state'
            shutil.copyfile(args.preview_save.resolve(strict=True), preview)
            hashes = out / 'preview-future.txt'
            for mode in ('record', 'read'):
                run([executable, rom, mode, preview, hashes, 1], f'preview-{mode}')
            if (Path(str(preview) + '.baseline-after.ppm').read_bytes() !=
                    Path(str(preview) + '.restored-after.ppm').read_bytes()):
                raise RuntimeError('Preview save restored a different image')
        build_entry('gpu')
        run([executable], 'graphics-gpu')
        sample = out / 'sample-pack'
        invalid = out / 'invalid-pack'
        invalid.mkdir(exist_ok=True)
        run([sys.executable, root / 'tools/hd_pack_tool.py', '--example', sample],
            'generate-synthetic-pack')
        build_entry('packs')
        run([executable, sample, invalid], 'hd-pack')
        test_build = build / 'runtime-tests'
        run(['cmake', '-S', root / 'tests', '-B', test_build], 'configure-components')
        run(['cmake', '--build', test_build, '--config', 'Release', '--parallel', '4'],
            'build-components')
        run(['ctest', '--test-dir', test_build, '-C', 'Release', '--output-on-failure'],
            'component-tests')
    finally:
        build_entry('')
    print(f'PASS. Private evidence: {out}')


if __name__ == '__main__':
    main()
