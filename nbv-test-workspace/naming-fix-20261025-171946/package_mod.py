"""Package this mod and its source tools, excluding external test profiles/addons."""
from pathlib import Path
import hashlib
import json
import zipfile
from build_mod import write, VERSION

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT.parent / 'dist'


def main():
    static = json.loads((ROOT / 'tools/data/static-validation.json').read_text(encoding='utf-8'))
    engine = json.loads((ROOT / 'tools/data/engine-validation.json').read_text(encoding='utf-8'))
    assert static['通过'], 'Static validation must pass before packaging.'
    assert engine.get('mod_version') == VERSION and engine.get('all_checks_passed'), \
        'A completed passing engine run for this version is required before packaging.'
    OUT.mkdir(exist_ok=True)
    target = OUT / ('national-buff-ui-' + VERSION + '.zip')
    files = sorted(p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc')
    assert not any('nbv_smoke' in p.name for p in files), 'A test addon must not be distributed as production data.'
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            archive.write(path, 'hoi4-national-buff/' + path.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None
        assert len(archive.namelist()) == len(files)
    result = dict(path=target.as_posix(), bytes=target.stat().st_size,
                  sha256=hashlib.sha256(target.read_bytes()).hexdigest(), file_count=len(files),
                  files=[p.relative_to(ROOT).as_posix() for p in files])
    write(OUT / 'package-manifest.json', json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'files'}))


if __name__ == '__main__':
    main()
