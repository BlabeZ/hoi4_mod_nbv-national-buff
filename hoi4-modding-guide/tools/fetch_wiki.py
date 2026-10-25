"""Fetch attributed, text-only HOI4 Wiki references. Requires Python 3 + requests.

Snapshots are CC BY-SA 3.0 unless a page states otherwise. This script does not
execute source content. Existing snapshots are replaced only when run explicitly.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
import hashlib
import json
import re
import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "references" / "wiki"
PAGES = [
    "Modding", "Localisation", "Scopes", "Conditions",
    "Triggers", "Effect", "Effects", "Modifiers", "Variables", "Data_structures",
    "Scripted_effect", "Scripted_trigger", "On_actions", "Event_modding",
    "Decision_modding", "National_focus_modding", "Idea_modding",
    "Country_creation", "Character_modding", "Technology_modding",
    "Equipment_modding", "Unit_modding", "Map_modding", "State_modding",
    "Interface_modding", "Scripted_GUI_modding", "Graphical_asset_modding",
    "AI_modding", "Defines", "Console_commands", "Troubleshooting",
    "Music_modding", "Sound_modding", "Military_industrial_organization_modding",
]


class WikiText(HTMLParser):
    """Keep article text and preformatted code; omit navigation and scripts."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.active = False
        self.div_depth = 0
        self.skip = 0
        self.parts = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if not self.active and tag == "div" and "mw-parser-output" in a.get("class", "").split():
            self.active = True
            self.div_depth = 1
            return
        if not self.active:
            return
        if tag == "div":
            self.div_depth += 1
        if tag in ("script", "style"):
            self.skip += 1
        if self.skip:
            return
        if tag in ("h1", "h2", "h3", "h4", "p", "pre", "ul", "ol", "tr", "table", "br"):
            self.parts.append("\n")
        if tag == "li":
            self.parts.append("\n- ")
        if tag in ("td", "th"):
            self.parts.append("\t")
        if tag == "a" and a.get("href", "").startswith("http"):
            self.links.append(a["href"])

    def handle_endtag(self, tag):
        if not self.active:
            return
        if tag in ("script", "style"):
            self.skip = max(0, self.skip - 1)
        if tag == "div":
            self.div_depth -= 1
            if self.div_depth == 0:
                self.active = False
        if not self.skip and tag in ("h1", "h2", "h3", "h4", "p", "pre", "li", "tr", "table"):
            self.parts.append("\n")

    def handle_data(self, data):
        if self.active and not self.skip:
            self.parts.append(data)


def fetch(page):
    url = "https://hoi4.paradoxwikis.com/" + page
    record = {"id": page, "url": url, "retrieved_at_utc": datetime.now(timezone.utc).isoformat()}
    try:
        response = requests.get(url, timeout=40)
        record["http_status"] = response.status_code
        response.raise_for_status()
        html = response.content.decode("utf-8")
        revision = re.search(r'"wgRevisionId":(\d+)', html)
        title = re.search(r"<title>(.*?)</title>", html, re.S)
        modified = re.search(r'id="footer-info-lastmod">(.*?)</li>', html, re.S)
        if "<title>Client Challenge</title>" in html:
            raise ValueError("Client Challenge returned instead of article; page contents and existence not verified")
        if not revision or "Attribution-ShareAlike 3.0" not in html:
            raise ValueError("Missing wiki revision or expected CC BY-SA notice; inspect manually")
        parser = WikiText()
        parser.feed(html)
        body = re.sub(r"\n[ \t]*\n(?:[ \t]*\n)+", "\n\n", "".join(parser.parts)).strip()
        if len(body) < 100:
            raise ValueError("Article body too short")
        oldid = revision.group(1)
        record.update({
            "title": unescape(title.group(1)) if title else page,
            "revision_id": int(oldid),
            "revision_url": f"https://hoi4.paradoxwikis.com/index.php?title={page}&oldid={oldid}",
            "history_url": f"https://hoi4.paradoxwikis.com/index.php?title={page}&action=history",
            "last_modified_text": unescape(modified.group(1)).strip() if modified else None,
            "license": "CC BY-SA 3.0; exceptions may apply as noted in source",
            "external_links": sorted(set(parser.links)),
            "local_path": f"references/wiki/{page}.txt",
            "status": "full_article_text_retrieved",
        })
        header = (f"{record['title']}\nSource: {url}\nRevision: {record['revision_url']}\n"
                  f"Authors/contributors: {record['history_url']}\n"
                  f"Retrieved: {record['retrieved_at_utc']}\nLast edit: {record['last_modified_text']}\n"
                  "License: CC BY-SA 3.0, https://creativecommons.org/licenses/by-sa/3.0/\n"
                  "Transformation: HTML article converted to plain text; navigation, images and scripts omitted.\n"
                  "Tables are tab-separated. Consult the source for layout, footnotes and exceptions.\n\n")
        content = header + body + "\n"
        (OUT / (page + ".txt")).write_text(content, encoding="utf-8")
        record["sha256"] = hashlib.sha256((OUT / (page + ".txt")).read_bytes()).hexdigest()
        record["characters"] = len(content)
    except Exception as error:
        record.update({"status": "not_retrieved", "error": str(error)})
    return record


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=4) as pool:
        records = list(pool.map(fetch, PAGES))
    (ROOT / "sources-wiki.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for record in records:
        print(record["id"], record["status"], record.get("characters", record.get("error", "")))
