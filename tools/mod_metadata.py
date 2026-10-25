"""Stable distribution directory; preserve launcher-owned mod metadata."""
from pathlib import Path
import re

MOD_DIRECTORY_NAME = 'nbv-national-buff'
DEFAULT_DISPLAY_NAME = '国家BUFF统计 UI'


def descriptor_text(path, version):
    """Update only the build version, retaining names, Workshop IDs and images."""
    path = Path(path)
    if not re.fullmatch(r'[0-9]+(?:\.[0-9]+)*', version):
        raise ValueError('Invalid build version.')
    if not path.exists():
        return (f'name="{DEFAULT_DISPLAY_NAME}"\nversion="{version}"\n'
                'supported_version="1.19.*"\ntags={ "Utilities" "Gameplay" }\n')
    text = path.read_text(encoding='utf-8-sig')
    if len(re.findall(r'(?m)^[ \t]*name[ \t]*=', text)) != 1:
        raise ValueError('Existing descriptor must contain one display name.')
    version_lines = re.findall(r'(?m)^[ \t]*version[ \t]*=', text)
    if not version_lines:
        return text.rstrip('\n') + f'\nversion="{version}"\n'
    pattern = r'(?m)^([ \t]*version[ \t]*=[ \t]*)"[^"\r\n]*"([ \t]*(?:#[^\r\n]*)?)$'
    if len(version_lines) != 1 or len(re.findall(pattern, text)) != 1:
        raise ValueError('Existing descriptor has an ambiguous version; leave it intact.')
    return re.sub(pattern, lambda match: match[1] + '"' + version + '"' + match[2], text)
