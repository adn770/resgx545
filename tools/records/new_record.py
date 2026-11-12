#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Draft an evidence record from a published closing session's own files.

    python3 tools/records/new_record.py --session DIR --id E<nnn> --stage S [S ...]
        [--unit U] [--out FILE]

DIR is a session of resgx545-data (`render/closing-r6-misc`). The draft's front matter and
method paragraph are written from what the session holds: the attempts that ran the stages
(out/<stamp>/ with the stage's directory, log or score), the start time and the driver log of
each, every freeze (FROZEN*.sha256, PREDICTIONS*.sha256, their sha256 and file counts, the
first line of each FREEZE*.txt, in the session and in a directory of it such as freeze1/), the
FROZEN.commits pins (data: and resgx545: lines too, `untracked` build products), the tools and
their built sources (TOOL*.sha256), the module and tool hashes the runner's env files expect, the
resgx545 and resgx545-data main commits the session names, the stop lines and lead decisions of
the logs, the scores kept, and a POSTRUN-FIX.md. The frozen scorer's SUMMARY lines go verbatim
into the verdict section. The claim, what ran, the results, what it shows and what it does not
are left as TODO-FILL markers: the record passes `evidence.py` once they are written (and the
unit and terms are set). Nothing is written to the session.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import pathlib
import re
import sys

TODO = "TODO-FILL"
STAMP = re.compile(r"\d{8}-\d{6}")
ENV_KEY = re.compile(r"(SHA|SRCV|SRCVERSION|COMMIT|TIP|FW)", re.I)
MAIN = re.compile(r"\b(resgx545(?:-data)?) main \**([0-9a-f]{7,40})\b")
DECISION = re.compile(r"\b(lead|decision|decided)\b", re.I)
STOP = re.compile(r"^## STOP(?! SIGNATURE)|\bstop(?:s|ped)? (?:with )?rc \d+")


def _sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _lines(p: pathlib.Path) -> list[str]:
    try:
        return p.read_text(errors="replace").splitlines()
    except OSError:
        return []


def _home(text: str) -> str:
    """An absolute home path as ~/ (the author's user name stays out of the record)."""
    return re.sub(r"(?<![\w/])/(?:home|Users)/[^/\s]+/", "~/", text)


def attempts(session: pathlib.Path, stage: str) -> list[pathlib.Path]:
    """The attempt directories under out/ that hold the stage's directory, log or score; out/
    itself when it holds the stage directly (the older layout)."""
    out = session / "out"
    if not out.is_dir():
        return []
    marks = (stage, f"{stage}.log", f"score-{stage}.txt")
    if any((out / m).exists() for m in marks):
        return [out]
    return sorted(d for d in out.iterdir()
                  if d.is_dir() and any((d / m).exists() for m in marks))


def log_blocks(session: pathlib.Path) -> list[dict]:
    """The stage blocks of the session's driver logs: {log, attempt, freeze, stage, time,
    summary, stops, decisions}. An attempt line (`attempt <stamp>...; FROZEN*.sha256 <hash>`)
    names the attempt and its freeze for the blocks after it; `#### <stage> <time>` opens one."""
    blocks = []
    for log in sorted(session.glob("*.log")):
        attempt, freeze, cur = None, None, None
        for line in _lines(log):
            m = re.match(r"attempt (\S+?)[:\s]", line)
            if m:
                attempt = m.group(1)
                f = re.search(r"\b((?:FROZEN|PREDICTIONS)[-\w.]*\.sha256) ([0-9a-f]{64})", line)
                freeze = f"{f.group(1)} {f.group(2)}" if f else None
                cur = None
                continue
            m = re.match(r"#### (\S+) (\d\d:\d\d:\d\d)", line)
            if m:
                cur = {"log": log.name, "attempt": attempt, "freeze": freeze,
                       "stage": m.group(1), "time": m.group(2), "summary": [], "stops": [],
                       "decisions": []}
                blocks.append(cur)
                continue
            if cur is None or line.startswith("[") or "gma500" in line:
                continue
            if line.startswith("SUMMARY"):
                cur["summary"].append(line.strip())
            elif STOP.search(line):
                cur["stops"].append(line.lstrip("# ").strip()[:240])
            elif DECISION.search(line):
                cur["decisions"].append(line.strip()[:240])
    return blocks


def freezes(session: pathlib.Path) -> list[tuple[str, str, int]]:
    """(path, sha256, file count) of each freeze in the session and its directories."""
    out = []
    for pat in ("FROZEN*.sha256", "PREDICTIONS*.sha256"):
        for p in sorted(session.glob(pat)) + sorted(session.glob(f"*/{pat}")):
            n = sum(1 for x in _lines(p) if x.strip() and not x.startswith("#"))
            out.append((str(p.relative_to(session)), _sha(p), n))
    return out


def freeze_notes(session: pathlib.Path) -> list[str]:
    notes = []
    for p in sorted(session.glob("FREEZE*.txt")) + sorted(session.glob("*/FREEZE*.txt")):
        first = next((x for x in _lines(p) if x.strip()), "")
        notes.append(f"{p.relative_to(session)} '{_home(first.strip())}'")
    return notes


def pins(session: pathlib.Path) -> list[str]:
    out = []
    for p in sorted(session.glob("FROZEN.commits")) + sorted(session.glob("*/FROZEN.commits")):
        for line in _lines(p):
            f = line.split()
            if line.startswith("#") or len(f) < 3:
                continue
            where = "untracked" if f[1] == "untracked" else f"at {f[1][:8]}"
            out.append(f"{f[2]} {where}" if p.parent == session
                       else f"{p.parent.name}/: {f[2]} {where}")
    return out


def tools(session: pathlib.Path) -> list[str]:
    out = []
    for p in sorted(session.glob("TOOL*.sha256")):
        for line in _lines(p):
            if line.strip() and not line.startswith("#"):
                out.append(f"{p.name}: {_home(' '.join(line.split()))}")
    for p in sorted(session.rglob("manifest")):
        if "out" in p.relative_to(session).parts:
            continue
        body = "; ".join(x.strip() for x in _lines(p) if x.strip())
        out.append(f"{p.relative_to(session)}: {_home(body)}")
    return out


def env_hashes(session: pathlib.Path) -> list[str]:
    out = []
    envs = sorted(session.glob("*.env")) + sorted(session.glob("*/*.env"))
    for p in envs:
        for line in _lines(p):
            m = re.match(r"(?:export\s+)?([A-Z_][A-Z0-9_]*)=(\S+)", line)
            if m and ENV_KEY.search(m.group(1)):
                out.append(f"{p.relative_to(session)} {m.group(1)}={m.group(2)}")
    return out


def main_commits(session: pathlib.Path) -> list[str]:
    seen: dict[str, None] = {}
    docs = (sorted(session.glob("*.md")) + sorted(session.glob("*.txt"))
            + sorted(session.glob("postrun/*")))
    for p in docs:
        if p.is_file():
            for repo, commit in MAIN.findall(p.read_text(errors="replace")):
                seen.setdefault(f"{repo} main {commit}", None)
    return list(seen)


def dataset_id(session: pathlib.Path) -> str:
    return f"{session.parent.name}-{session.name}"


def draft(session: pathlib.Path, rid: str, stages: list[str], unit: str | None = None) -> str:
    """The record's text: front matter, then the prose sections."""
    session = pathlib.Path(session)
    ds = dataset_id(session)
    blocks = [b for b in log_blocks(session) if b["stage"] in stages]
    att = {s: attempts(session, s) for s in stages}
    unknown = [s for s in stages if not att[s] and not any(b["stage"] == s for b in blocks)]
    if unknown:
        raise ValueError(f"no attempt or log block of stage(s) {', '.join(unknown)} "
                         f"in {session}")
    dirs = sorted({a for s in stages for a in att[s]})

    parts = [f"{session.name.removeprefix('closing-')} ({session.parent.name}/{session.name}), "
             f"stage{'s' if len(stages) > 1 else ''} {', '.join(stages)} of the question-closing "
             f"pass ({TODO}: round, decisions, plan), dataset {ds}"]
    for a in dirs:
        rel = a.relative_to(session)
        mine = [b for b in blocks
                if b["attempt"] == a.name or (b["attempt"] is None and len(dirs) == 1)]
        bits = [f"{b['stage']} {b['time']}" for b in mine]
        logs = sorted({b["log"] for b in mine})
        fr = sorted({b["freeze"] for b in mine if b["freeze"]})
        scores = sorted(p.name for s in stages for p in a.glob(f"score-{s}*.txt"))
        desc = f"attempt {rel}"
        extra = []
        if bits:
            extra.append(", ".join(bits) + " Mac time")
        if logs:
            extra.append("driver log " + ", ".join(logs))
        if fr:
            extra.append("its freeze " + ", ".join(fr))
        if scores:
            extra.append("scores " + ", ".join(scores))
        parts.append(desc + (f" ({'; '.join(extra)})" if extra else ""))
    parts.append(f"on the laptop ({TODO}: host, kernel, module srcversion, firmware, tool, "
                 f"the job commands and rows)")
    fz = freezes(session)
    if fz:
        parts.append("freezes: " + ", ".join(f"{p} {h} ({n} files)" for p, h, n in fz))
    notes = freeze_notes(session)
    if notes:
        parts.append("freeze notes: " + "; ".join(notes))
    pn = pins(session)
    if pn:
        parts.append("FROZEN.commits pins: " + ", ".join(pn))
    tl = tools(session)
    if tl:
        parts.append("tools: " + "; ".join(tl))
    ev = env_hashes(session)
    if ev:
        parts.append("the runner expects: " + ", ".join(ev))
    mc = main_commits(session)
    if mc:
        parts.append("pinned commits named by the session: " + ", ".join(mc))
    stops = [f"{b['stage']}: '{s}'" for b in blocks for s in b["stops"]]
    parts.append("stops in the logs: " + ("; ".join(stops) if stops else "none"))
    dec = [f"{b['stage']}: '{d}'" for b in blocks for d in b["decisions"]]
    parts.append("lead decisions in the logs: " + ("; ".join(dec) if dec else "none"))
    if (session / "POSTRUN-FIX.md").exists():
        parts.append("a post-run scorer fix (POSTRUN-FIX.md)")
    method = "; ".join(parts)

    data = []
    for a in dirs:
        rel = a.relative_to(session)
        subs = [s for s in stages if (a / s).is_dir()]
        data += [f"{ds}:{rel}/{s}/" for s in subs] or [f"{ds}:{rel}/"]
    for d in sorted({pathlib.Path(p).parent for p, _, _ in fz} - {pathlib.Path(".")}):
        data.append(f"{ds}:{d}/")
    for d in ("postrun", "fold"):
        if (session / d).is_dir():
            data.append(f"{ds}:{d}/")
    stamp = next((STAMP.search(a.name) for a in dirs if STAMP.search(a.name)), None)
    date = (f"{stamp.group(0)[:4]}-{stamp.group(0)[4:6]}-{stamp.group(0)[6:8]}" if stamp
            else datetime.date.today().isoformat())

    q = json.dumps
    head = "\n".join([
        "+++",
        f"id = {q(rid)}",
        f"claim = {q(f'{TODO}: the claim, with the frozen verdict quoted')}",
        f"unit = {q(unit or TODO)}",
        f"method = {q(method, ensure_ascii=False)}",
        'tiers = ["HW"]',
        f"date = {q(date)}",
        "data = [" + ", ".join(q(d) for d in data) + "]",
        "terms = []",
        "+++",
    ])
    verdict = []
    for b in sorted(blocks, key=lambda b: (b["attempt"] or "", b["time"])):
        where = f"attempt {b['attempt']}, " if b["attempt"] else ""
        for s in b["summary"]:
            verdict.append(f"{where}stage {b['stage']} ({b['log']}): `{s}`")
    body = [
        f"**What ran.** {TODO}",
        "**Frozen verdict (as printed).** "
        + ("; ".join(verdict) + "." if verdict else f"{TODO}: no SUMMARY line in the logs"),
        f"**Results [HW].** {TODO}",
        f"**What it shows.** {TODO}",
        f"**What it does not show.** {TODO}",
    ]
    return head + "\n" + "\n\n".join(body) + "\n"


def todos(text: str) -> int:
    """How many TODO-FILL markers a draft still has."""
    return text.count(TODO)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--session", required=True, type=pathlib.Path)
    ap.add_argument("--id", required=True)
    ap.add_argument("--stage", required=True, nargs="+", action="extend")
    ap.add_argument("--unit")
    ap.add_argument("--out", type=pathlib.Path)
    a = ap.parse_args(argv)
    if not a.session.is_dir():
        print(f"new_record: no session {a.session}", file=sys.stderr)
        return 2
    try:
        text = draft(a.session, a.id, a.stage, a.unit)
    except ValueError as e:
        print(f"new_record: {e}", file=sys.stderr)
        return 2
    if a.out:
        a.out.write_text(text)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
