#!/usr/bin/env python3
"""Copy shared markup, CSS and scripts from partials/ into the sections that mark where they go.

Markup and scripts: {%- comment -%}partial:NAME{%- endcomment -%} ... {%- comment -%}/partial:NAME{%- endcomment -%}
CSS:                /* partial:NAME */ ... /* /partial:NAME */
Edit partials/, then run this before `theme.py build`. `--check` exits non-zero when a section is out of date.
"""
import re
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
partials = root / "partials"
html_re = re.compile(r"(\{%- comment -%\}partial:([a-z0-9-]+)\{%- endcomment -%\})(.*?)(\{%- comment -%\}/partial:\2\{%- endcomment -%\})", re.S)
css_re = re.compile(r"(/\* partial:([a-z0-9-]+) \*/)(.*?)(/\* /partial:\2 \*/)", re.S)


def fill(regex, ext, text):
    def sub(match):
        body = (partials / f"{match.group(2)}.{ext}").read_text(encoding="utf-8").rstrip("\n")
        return f"{match.group(1)}\n{body}\n{match.group(4)}"

    return regex.sub(sub, text)


stale = []
for section in sorted((root / "src" / "sections").iterdir()):
    for name, regex, ext in (("body.html", html_re, "html"), ("style.css", css_re, "css")):
        path = section / name
        if not path.exists():
            continue
        old = path.read_text(encoding="utf-8")
        new = fill(regex, ext, old)
        if new != old:
            stale.append(f"{section.name}/{name}")
            if "--check" not in sys.argv:
                path.write_text(new, encoding="utf-8")
if stale:
    print(("out of date: " if "--check" in sys.argv else "synced: ") + ", ".join(stale))
    sys.exit(1 if "--check" in sys.argv else 0)
