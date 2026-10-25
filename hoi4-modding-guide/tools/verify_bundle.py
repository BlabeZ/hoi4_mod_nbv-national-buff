"""Check this documentation bundle. Does not launch HOI4 or run CWTools."""
from pathlib import Path
from urllib.parse import unquote
from collections import Counter
import codecs
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]


def check_braces(text, path):
    depth = 0
    quoted = escaped = commented = False
    for char in text:
        if commented:
            if char == "\n":
                commented = False
            continue
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
            continue
        if char == "#":
            commented = True
        elif char == '"':
            quoted = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            assert depth >= 0, f"Unexpected closing brace: {path}"
    assert depth == 0 and not quoted, f"Unbalanced braces or quotes: {path}"


def main():
    files = [ROOT.parent / "README.md", *ROOT.glob("*.md"), ROOT / "examples/README.md"]
    links = 0
    for path in files:
        content = path.read_text(encoding="utf-8")
        content = re.sub(r"```.*?```", "", content, flags=re.S)
        for match in re.finditer(r"\]\(([^)]+)\)", content):
            target = match[1].strip("<>")
            if re.match(r"[a-zA-Z]+:", target) or target.startswith("#"):
                continue
            target = unquote(target.split("#", 1)[0])
            resolved = (path.parent / target).resolve()
            # This report is created only after all checks below pass.
            if resolved != (ROOT / "verification-results.json").resolve():
                assert resolved.exists(), f"Broken local link: {path.name} -> {target}"
            links += 1
    demo = ROOT / "examples/minimal_mod"
    scripts = list(demo.rglob("*.txt"))
    for path in scripts:
        raw = path.read_bytes()
        assert not raw.startswith(codecs.BOM_UTF8), f"Unexpected script BOM: {path}"
        check_braces(raw.decode("utf-8"), path)
    required = {"h4guide.1.t", "h4guide.1.d", "h4guide.1.a", "h4guide_training_spirit", "h4guide_training_spirit_desc"}
    localisations = list(demo.rglob("*.yml"))
    for path in localisations:
        raw = path.read_bytes()
        assert raw.startswith(codecs.BOM_UTF8), f"Missing localisation BOM: {path}"
        content = raw.decode("utf-8-sig")
        language = path.parent.name
        assert path.name.endswith(f"_l_{language}.yml")
        assert content.splitlines()[0] == f"l_{language}:"
        keys = re.findall(r'^[ \t]+([\w.]+):\d*[ \t]+"[^\r\n]*"[ \t]*\r?$', content, re.M)
        assert len(keys) == len(set(keys)), f"Duplicate localisation key: {path}"
        assert required.issubset(set(keys)), f"Missing localisation key: {path}"
    upstream = json.loads((ROOT / "references/cwtools-hoi4-config/Config/script_documentation.json").read_text(encoding="utf-8-sig"))
    inventory = json.loads((ROOT / "references/api/inventory.json").read_text(encoding="utf-8"))
    counts = Counter(entry["family"] for entry in inventory["entries"])
    assert counts == {"effects": 553, "triggers": 598, "modifiers": 764}
    for token in ("add_political_power", "add_ideas", "set_country_flag", "log", "if"):
        assert token in upstream["effects"], f"Unlisted effect: {token}"
    for token in ("has_country_flag", "always"):
        assert token in upstream["triggers"], f"Unlisted trigger: {token}"
    assert any(x.get("name") == "political_power_gain" for x in upstream["modifiers"])
    script_text = "\n".join(p.read_text(encoding="utf-8") for p in scripts)
    for symbol in ("h4guide_can_receive_reward", "h4guide_grant_reward", "h4guide_training_spirit"):
        assert re.search(r"\b" + symbol + r"\s*=\s*\{", script_text), f"Missing definition: {symbol}"
    wiki = json.loads((ROOT / "sources-wiki.json").read_text(encoding="utf-8"))
    successful = [x for x in wiki if x["status"] == "full_article_text_retrieved"]
    for record in successful:
        raw = (ROOT / record["local_path"]).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == record["sha256"], "Wiki snapshot hash mismatch"
    config_files = list((ROOT / "references/cwtools-hoi4-config").rglob("*"))
    config_files = [p for p in config_files if p.is_file()]
    assert len(config_files) == 116
    result = {"authored_markdown_local_links_checked": links,
              "example_scripts_checked": len(scripts), "localisation_files_checked": len(localisations),
              "wiki_snapshots_hash_verified": len(successful), "upstream_snapshot_files": len(config_files),
              "api_documentation_records": dict(counts), "game_test_performed": False,
              "cwtools_validator_run": False, "status": "PASS"}
    (ROOT / "verification-results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
