#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The state digest: the project's state on one page, rendered as doc/state_digest.md from the
tracked tree only, so that a check can tell whether it is current.

It lists the open questions (the hardware queue by value, then the parked ones) with each one's
unit, value and last three records; the records of the last N days up to the newest record's
date, with their claims; the published closing sessions (the dataset manifests of
`<area>/closing-*`) with their dates, modules, fork tips and laptop tools; the tool and fork
versions (the fork pin of tools/forkpin.py, the module srcversions the sessions name, the
sha256 of the helpers a session copies); the known tool weaknesses (HACKING.md's section, when
there is one); and the size of the simulator's unmodelled baseline
(crates/SIM_UNMODELLED.toml, when it exists).

    python3 tools/records/digest.py [--check] [--days N]
        write (--check: compare) doc/state_digest.md
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import pathlib
import re
import sys
import textwrap
import tomllib

ROOT = pathlib.Path(__file__).resolve().parents[2]
DOC = "doc/state_digest.md"
WIDTH = 100
DAYS = 2
VALUE_ORDER = {"high": 0, "medium": 1, "low": 2, None: 3}
HELPERS = ("tools/closing/scorekit.py", "tools/closing/sessioncheck.py")


def _front(path: pathlib.Path) -> dict:
    text = path.read_text()
    head, sep, _ = text[4:].partition("\n+++\n")
    if not text.startswith("+++\n") or not sep:
        raise ValueError(f"{path}: no front matter")
    return tomllib.loads(head)


def _wrap(text: str, indent: str = "  ") -> list[str]:
    return textwrap.wrap(text, WIDTH, subsequent_indent=indent, break_on_hyphens=False,
                         break_long_words=False)


def _short(text: str, n: int) -> str:
    text = " ".join(text.split())
    return text if len(text) <= n else text[:n].rsplit(" ", 1)[0] + " ..."


def _num(rid: str) -> int:
    m = re.search(r"\d+", rid)
    return int(m.group(0)) if m else -1


def questions(root: pathlib.Path) -> list[str]:
    qs = [_front(p) for p in sorted((root / "questions").glob("*/Q*.md"))]
    hw = sorted((q for q in qs if q["kind"] == "hw"),
                key=lambda q: (VALUE_ORDER.get(q.get("value"), 3), q["unit"], _num(q["id"])))
    parked = sorted((q for q in qs if q["kind"] != "hw"), key=lambda q: (q["kind"], _num(q["id"])))
    out = ["## Open questions", ""]
    out += _wrap(f"{len(qs)} open: {len(hw)} hw, {len(parked)} parked. Each with its unit, value "
                 "and the last three records of its evidence list.", "")
    out.append("")
    for q in hw + parked:
        last = sorted(q.get("evidence", []), key=_num)[-3:]
        recs = ", ".join(last) if last else "none"
        tag = (q.get("value") or "no value") if q["kind"] == "hw" else f"{q['kind']} (parked)"
        out += _wrap(f"- `{q['id']}` {q['unit']}, {tag}: {_short(q['question'], 140)} ({recs})")
    return out + [""]


def recent(root: pathlib.Path, days: int) -> list[str]:
    recs = [_front(p) for p in (root / "evidence").glob("*/E*.md")]
    out = ["## Recent records", ""]
    if not recs:
        return out + ["No records.", ""]
    newest = max(datetime.date.fromisoformat(r["date"]) for r in recs)
    first = newest - datetime.timedelta(days=days - 1)
    keep = sorted((r for r in recs if datetime.date.fromisoformat(r["date"]) >= first),
                  key=lambda r: (r["date"], _num(r["id"])), reverse=True)
    out += _wrap(f"{len(keep)} records of {first} to {newest} (the last {days} days to the "
                 "newest record's date), newest first; the claims are cut at 200 characters.", "")
    out.append("")
    for r in keep:
        out += _wrap(f"- `{r['id']}` {r['unit']}, {r['date']}: {_short(r['claim'], 200)}")
    return out + [""]


def _session_facts(method: str) -> tuple[list[str], list[str], list[str]]:
    srcv = sorted(set(re.findall(r"srcversion ([0-9A-F]{20,})", method)))
    forks = sorted(set(re.findall(r"branch ([\w-]+ at [0-9a-f]{8})", method)))
    tools = sorted(set(re.findall(r"~/[\w./-]*sgxfive-test[\w-]*", method)))
    return srcv, forks, tools


def sessions(root: pathlib.Path) -> tuple[list[str], list[dict]]:
    found = []
    for p in sorted((root / "datasets").glob("*.toml")):
        m = tomllib.loads(p.read_text())
        paths = [x for x in m.get("paths", []) if re.fullmatch(r"[a-z]+/closing-[^/]+/?", x)]
        if not paths:
            continue
        text = f"{m.get('title', '')} {m.get('method', '')}"
        srcv, forks, tools = _session_facts(text)
        found.append({"path": paths[0].rstrip("/"), "date": m.get("date", "?"), "srcv": srcv,
                      "forks": forks, "tools": tools, "id": p.stem})
    found.sort(key=lambda s: (s["date"], s["path"]), reverse=True)
    out = ["## Closing sessions", ""]
    out += _wrap(f"{len(found)} published sessions (dataset manifests of `<area>/closing-*`), "
                 "newest first: date, module srcversion, fork tip, laptop tools.", "")
    out.append("")
    for s in found:
        bits = [s["date"]]
        bits.append("module " + ", ".join(s["srcv"]) if s["srcv"] else "module not named")
        if s["forks"]:
            bits.append("fork " + ", ".join(s["forks"]))
        bits.append("tools " + ", ".join(s["tools"]) if s["tools"] else "tools not named")
        out += _wrap(f"- `{s['path']}`: " + "; ".join(bits))
    return out + [""], found


def versions(root: pathlib.Path, found: list[dict]) -> list[str]:
    out = ["## Tool and fork versions", ""]
    fp = root / "tools/forkpin.py"
    m = re.search(r'^PIN = "([0-9a-f]+)"', fp.read_text(), re.M) if fp.is_file() else None
    out += _wrap(f"- fork pin (`tools/forkpin.py`): {m.group(1) if m else 'not found'}")
    seen: dict[str, dict] = {}
    for s in found:
        for v in s["srcv"]:
            e = seen.setdefault(v, {"date": s["date"], "n": 0, "forks": set()})
            e["date"] = max(e["date"], s["date"])
            e["n"] += 1
            e["forks"] |= set(s["forks"]) if len(s["srcv"]) == 1 else set()
    for v, e in sorted(seen.items(), key=lambda kv: kv[1]["date"], reverse=True):
        fk = f", fork {', '.join(sorted(e['forks']))}" if e["forks"] else ""
        out += _wrap(f"- module srcversion {v}: last named {e['date']}, {e['n']} sessions{fk}")
    for h in HELPERS:
        p = root / h
        if p.is_file():
            out += _wrap(f"- `{h}` sha256 {hashlib.sha256(p.read_bytes()).hexdigest()[:16]}")
    return out + [""]


def weaknesses(root: pathlib.Path) -> list[str]:
    out = ["## Known tool weaknesses", ""]
    h = root / "HACKING.md"
    lines = h.read_text().splitlines() if h.is_file() else []
    start = next((i for i, x in enumerate(lines)
                  if re.match(r"#+ .*weakness", x, re.I)), None)
    if start is None:
        return out + ["None listed: no known-weaknesses section in HACKING.md.", ""]
    level = len(lines[start]) - len(lines[start].lstrip("#"))
    body = []
    for x in lines[start + 1:]:
        m = re.match(r"(#+) ", x)
        if m and len(m.group(1)) <= level:
            break
        body.append(x.rstrip())
    out += _wrap(f"From HACKING.md, \"{lines[start].lstrip('# ')}\":", "")
    return out + [""] + [x for x in "\n".join(body).strip().splitlines()] + [""]


def sim(root: pathlib.Path) -> list[str]:
    out = ["## Simulator coverage baseline", ""]
    p = root / "crates/SIM_UNMODELLED.toml"
    if not p.is_file():
        return out + ["no `crates/SIM_UNMODELLED.toml` yet.", ""]
    data = tomllib.loads(p.read_text())
    n = sum(len(v) if isinstance(v, list) else 1 for v in data.values())
    return out + [f"{n} entries in `crates/SIM_UNMODELLED.toml` (what the simulator does not "
                  "model).", ""]


def render(root: pathlib.Path = ROOT, days: int = DAYS) -> str:
    root = pathlib.Path(root)
    out = ["<!-- SPDX-" "License-Identifier: MIT -->",
           "<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->",
           "# State digest", "",
           "*Generated from the tracked tree by `tools/records/digest.py`; do not edit.*", ""]
    out += _wrap("Where the project stands, on one page: the open questions, the newest "
                 "records, the published closing sessions, the tool and fork versions, the "
                 "known tool weaknesses and the simulator's unmodelled baseline. The records, "
                 "questions and manifests themselves hold the detail.", "")
    out.append("")
    out += questions(root)
    out += recent(root, days)
    sec, found = sessions(root)
    out += sec
    out += versions(root, found)
    out += weaknesses(root)
    out += sim(root)
    return "\n".join(out).rstrip() + "\n"


def main(argv: list[str] | None = None, root: pathlib.Path = ROOT) -> int:
    ap = argparse.ArgumentParser(description="render doc/state_digest.md")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--days", type=int, default=DAYS)
    a = ap.parse_args(sys.argv[1:] if argv is None else argv)
    text = render(root, a.days)
    doc = pathlib.Path(root) / DOC
    if a.check:
        ok = doc.is_file() and doc.read_text() == text
        if not ok:
            print(f"digest: {DOC} is not current (run tools/records/digest.py)", file=sys.stderr)
        return 0 if ok else 1
    doc.parent.mkdir(parents=True, exist_ok=True)
    doc.write_text(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
