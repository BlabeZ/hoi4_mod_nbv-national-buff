from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import time

HERE = Path(__file__).resolve().parent
PRODUCTION = Path(r'D:\projects\hoi4_mod\1\nbv-national-buff\install-local.ps1')
RUN = HERE / ('fixture-run-' + time.strftime('%H%M%S'))
RUN.mkdir()
RESULTS = []


def descriptor(name='Source default', version='0.1.11', extra=''):
    return f'name="{name}"\nversion="{version}"\nsupported_version="1.19.*"\ntags={{ "Utilities" "Gameplay" }}\n' + extra


def field(text, name):
    matches = re.findall(r'^\s*' + re.escape(name) + r'\s*=\s*"([^"\r\n]*)"\s*$', text, re.M)
    assert len(matches) <= 1, (name, matches)
    return matches[0] if matches else None


def replace_field(text, name, value):
    text = re.sub(r'^\s*' + re.escape(name) + r'\s*=.*\n?', '', text, flags=re.M)
    return text.rstrip() + f'\n{name}="{value}"\n'


def make_fixture(name):
    root = RUN / name
    source = root / 'project' / 'nbv-national-buff'
    source.mkdir(parents=True)
    shutil.copyfile(PRODUCTION, source / 'install-local.ps1')
    for section in ['common', 'gfx', 'interface', 'localisation']:
        (source / section).mkdir()
        (source / section / 'sample.txt').write_text(section + ' original', encoding='utf-8')
    (source / 'descriptor.mod').write_text(descriptor(), encoding='utf-8')
    profile = root / 'profile'
    (profile / 'mod').mkdir(parents=True)
    return root, source, profile


def install(source, profile, expected=True, *extra):
    result = subprocess.run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(source / 'install-local.ps1'), '-UserDirectory', str(profile), *extra], capture_output=True)
    text = result.stdout.decode('utf-8', errors='replace') + result.stderr.decode('utf-8', errors='replace')
    with (RUN / 'process-output.txt').open('a', encoding='utf-8') as f:
        f.write(f'\nSOURCE={source}\nEXPECTED={expected}\nEXIT={result.returncode}\n{text}\n')
    assert (result.returncode == 0) == expected, (result.returncode, text)
    return text


def files_hash(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}


def test(name, fn):
    try:
        fn()
        RESULTS.append({'name': name, 'passed': True})
    except Exception as error:
        RESULTS.append({'name': name, 'passed': False, 'error': repr(error)})


def migration_update_rename():
    root, source, profile = make_fixture('migration-update-rename')
    external = profile / 'mod' / 'nbv_national_buff.mod'
    (source / 'cover.png').write_bytes(b'fixture-cover')
    external.write_text(descriptor('原有显示名称', extra='remote_file_id="123456789"\npicture="cover.png"\n') + f'path="{source.as_posix()}"\n', encoding='utf-8')
    install(source, profile)
    target = profile / 'mod' / 'nbv-national-buff'
    assert target.is_dir()
    assert field(external.read_text(encoding='utf-8'), 'path') == target.as_posix()
    assert field((target / 'descriptor.mod').read_text(encoding='utf-8'), 'name') == '原有显示名称'
    assert field((target / 'descriptor.mod').read_text(encoding='utf-8'), 'remote_file_id') == '123456789'
    assert (target / 'cover.png').read_bytes() == b'fixture-cover'
    assert field((source / 'descriptor.mod').read_text(encoding='utf-8'), 'name') == 'Source default'

    # A managed update removes a former shipped file, keeps untracked user files,
    # and refreshes content without changing the registration identity.
    (source / 'common' / 'sample.txt').unlink()
    (source / 'common' / 'new.txt').write_text('new content', encoding='utf-8')
    (source / 'descriptor.mod').write_text(descriptor(version='0.1.12'), encoding='utf-8')
    (target / 'user-note.txt').write_text('keep', encoding='utf-8')
    install(source, profile)
    assert not (target / 'common' / 'sample.txt').exists()
    assert (target / 'common' / 'new.txt').read_text() == 'new content'
    assert (target / 'user-note.txt').read_text() == 'keep'
    assert field(external.read_text(encoding='utf-8'), 'version') == '0.1.12'
    assert field(external.read_text(encoding='utf-8'), 'remote_file_id') == '123456789'

    # Exact filesystem order observed in installed launcher's renameV0Mod:
    # rename directory, rename sibling registration, update descriptor and DB.
    renamed = target.parent / '国家修正统计 新名称'
    renamed_external = target.parent / '国家修正统计 新名称.mod'
    target.rename(renamed)
    external.rename(renamed_external)
    renamed_descriptor = renamed / 'descriptor.mod'
    text = replace_field(renamed_descriptor.read_text(encoding='utf-8'), 'name', renamed.name)
    renamed_descriptor.write_text(text, encoding='utf-8')
    renamed_external.write_text(replace_field(text, 'path', renamed.as_posix()), encoding='utf-8')
    (source / 'descriptor.mod').write_text(descriptor(version='0.1.13'), encoding='utf-8')
    (source / 'cover.png').unlink()  # Covers uploaded only in deployed directory survive.
    install(source, profile)
    assert not target.exists()
    assert not external.exists()
    assert len(list((profile / 'mod').glob('*.mod'))) == 1
    assert field(renamed_external.read_text(encoding='utf-8'), 'name') == renamed.name
    assert field(renamed_external.read_text(encoding='utf-8'), 'path') == renamed.as_posix()
    assert field(renamed_external.read_text(encoding='utf-8'), 'version') == '0.1.13'
    assert field(renamed_external.read_text(encoding='utf-8'), 'remote_file_id') == '123456789'
    assert (renamed / 'cover.png').read_bytes() == b'fixture-cover'
    manifest = json.loads((renamed / '.nbv-install.json').read_text(encoding='utf-8'))
    assert manifest['registration'] == renamed_external.name
    assert source.is_dir()


def id_conflict():
    root, source, profile = make_fixture('id-conflict')
    source_descriptor = source / 'descriptor.mod'
    source_descriptor.write_text(descriptor(extra='remote_file_id="111"\n'), encoding='utf-8')
    install(source, profile)
    source_descriptor.write_text(descriptor(extra='remote_file_id="222"\n'), encoding='utf-8')
    before = files_hash(profile)
    output = install(source, profile, False)
    assert 'Conflicting Workshop IDs' in output
    assert before == files_hash(profile)


def other_descriptor():
    root, source, profile = make_fixture('other-descriptor')
    other = root / 'other-mod'
    other.mkdir()
    external = profile / 'mod' / 'nbv_national_buff.mod'
    external.write_text(descriptor('Other mod') + f'path="{other.as_posix()}"\n', encoding='utf-8')
    before = files_hash(profile)
    output = install(source, profile, False)
    assert 'A different descriptor' in output
    assert before == files_hash(profile)


def other_directory():
    root, source, profile = make_fixture('other-directory')
    target = profile / 'mod' / 'nbv-national-buff'
    target.mkdir()
    (target / 'user.txt').write_text('unrelated content', encoding='utf-8')
    before = files_hash(profile)
    output = install(source, profile, False)
    assert 'not managed by this installer' in output
    assert before == files_hash(profile)


def malicious_manifest():
    root, source, profile = make_fixture('outside-manifest-path')
    install(source, profile)
    target = profile / 'mod' / 'nbv-national-buff'
    marker = target / '.nbv-install.json'
    data = json.loads(marker.read_text(encoding='utf-8'))
    data['files'].append('../../outside.txt')
    marker.write_text(json.dumps(data), encoding='utf-8')
    outside = profile / 'outside.txt'
    outside.write_text('keep', encoding='utf-8')
    before = files_hash(profile)
    output = install(source, profile, False)
    assert 'Unsafe path in installation manifest' in output
    assert before == files_hash(profile)


def duplicate_installations():
    root, source, profile = make_fixture('duplicate-installations')
    install(source, profile)
    target = profile / 'mod' / 'nbv-national-buff'
    duplicate = profile / 'mod' / 'duplicate'
    shutil.copytree(target, duplicate)
    external = profile / 'mod' / 'duplicate.mod'
    text = (profile / 'mod' / 'nbv_national_buff.mod').read_text(encoding='utf-8')
    external.write_text(replace_field(text, 'path', duplicate.as_posix()), encoding='utf-8')
    before = files_hash(profile)
    output = install(source, profile, False)
    assert 'Multiple NBV installations' in output
    assert before == files_hash(profile)


def junction_escape():
    root, source, profile = make_fixture('nested-junction')
    install(source, profile)
    target = profile / 'mod' / 'nbv-national-buff'
    outside = root / 'unrelated-data'
    outside.mkdir()
    sentinel = outside / 'sample.txt'
    sentinel.write_text('unrelated original', encoding='utf-8')
    (target / 'common').rename(target / 'common-original')
    ps_quote = lambda x: "'" + str(x).replace("'", "''") + "'"
    command = 'New-Item -ItemType Junction -Path ' + ps_quote(target / 'common') + ' -Target ' + ps_quote(outside) + ' | Out-Null'
    result = subprocess.run(['powershell', '-NoProfile', '-Command', command], capture_output=True)
    assert result.returncode == 0, result.stderr.decode('utf-8', errors='replace')
    before = files_hash(outside)
    install(source, profile, False)
    assert before == files_hash(outside), 'Nested junction allowed writes outside target'


for name, fn in [('migration_normal_update_and_launcher_rename', migration_update_rename), ('workshop_id_conflict_refuses_without_changes', id_conflict), ('other_mod_descriptor_not_overwritten', other_descriptor), ('other_mod_directory_not_overwritten', other_directory), ('manifest_escape_refused_without_changes', malicious_manifest), ('duplicate_installations_refused', duplicate_installations), ('nested_junction_escape_refused', junction_escape)]:
    test(name, fn)

report = {'script_sha256': hashlib.sha256(PRODUCTION.read_bytes()).hexdigest(), 'run_directory': str(RUN), 'passed': all(x['passed'] for x in RESULTS), 'results': RESULTS}
(RUN / 'results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
raise SystemExit(0 if report['passed'] else 1)
