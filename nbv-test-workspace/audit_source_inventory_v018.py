# -*- coding: utf-8 -*-
"""Read-only inventory/freshness audit of the installed vanilla source tables."""
from pathlib import Path
import hashlib
import json
import sys
import zipfile

BASE = Path(__file__).resolve().parent.parent
MOD = BASE / 'hoi4-national-buff'
GAME = Path(r'E:/Steam/steamapps/common/Hearts of Iron IV')
sys.path.insert(0, str(MOD / 'tools'))
from build_mod import SOURCE_TABLES


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    tables = {}
    actual_hashes = {}
    for filename in SOURCE_TABLES:
        path = MOD / 'tools/data' / filename
        data = json.loads(path.read_text(encoding='utf-8'))
        mismatches = []
        for relative, metadata in data.get('source_files', {}).items():
            expected = metadata.get('sha256') if isinstance(metadata, dict) else metadata
            source_path = GAME / relative
            if not source_path.is_file():
                mismatches.append({'file': relative, 'reason': 'missing'})
                continue
            if relative not in actual_hashes:
                actual_hashes[relative] = digest(source_path)
            if expected != actual_hashes[relative]:
                mismatches.append({'file': relative, 'reason': 'hash_changed'})
        tables[filename] = {
            'table_sha256': digest(path),
            'file_count': len(data.get('source_files', {})),
            'mismatches': mismatches,
            'statistics': data.get('statistics', {}),
        }
    ideas = json.loads((MOD / 'tools/data/source-bindings.json').read_text(encoding='utf-8'))
    dynamic = json.loads((MOD / 'tools/data/dynamic-source-bindings.json').read_text(encoding='utf-8'))
    inventory = {}
    for folder, data in [('ideas', ideas), ('dynamic_modifiers', dynamic)]:
        actual = {p.relative_to(GAME).as_posix() for p in (GAME / 'common' / folder).rglob('*.txt')}
        recorded = {s for s in data['source_files'] if s.startswith('common/' + folder + '/')}
        inventory[folder] = {'actual_files': len(actual), 'recorded_files': len(recorded),
                             'unscanned_files': sorted(actual-recorded),
                             'obsolete_files': sorted(recorded-actual)}
    dlc_scripts = []
    loose_dlc_scripts = []
    archives = []
    for path in (GAME / 'dlc').rglob('*'):
        if not path.is_file():
            continue
        relative = path.relative_to(GAME).as_posix()
        if path.suffix.lower() == '.txt' and any(s in relative.lower() for s in ['/common/ideas/', '/common/dynamic_modifiers/']):
            loose_dlc_scripts.append(relative)
        if path.suffix.lower() != '.zip':
            continue
        archives.append(relative)
        with zipfile.ZipFile(path) as archive:
            for member in archive.namelist():
                normalized = '/' + member.replace('\\', '/').lower()
                if any(s in normalized for s in ['/common/ideas/', '/common/dynamic_modifiers/']):
                    dlc_scripts.append({'archive': relative, 'member': member})
    display = json.loads((MOD / 'tools/data/source-display-manifest.json').read_text(encoding='utf-8'))
    generated_hash_mismatches = []
    for relative, expected in display['input_hashes'].items():
        path = MOD / 'tools/data' / relative
        if not path.is_file() or digest(path) != expected:
            generated_hash_mismatches.append(relative)
    report = {
        'date': '2026-10-25', 'mod_version': '0.1.8', 'game_version': '1.19.3.0',
        'scope': 'Installed vanilla files and current generated source tables; not an all-source semantic completeness proof.',
        'tables': tables, 'inventory': inventory,
        'unique_source_files_hash_checked': len(actual_hashes),
        'dlc_archives_checked': archives,
        'dlc_archived_idea_dynamic_files': dlc_scripts,
        'dlc_loose_idea_dynamic_files': loose_dlc_scripts,
        'generated_input_hash_mismatches': generated_hash_mismatches,
    }
    out = BASE / 'nbv-test-workspace/source-inventory-audit-v018.json'
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k != 'tables'}, ensure_ascii=True, indent=2))
    print('table file hash mismatches:', sum(len(t['mismatches']) for t in tables.values()))


if __name__ == '__main__':
    main()
