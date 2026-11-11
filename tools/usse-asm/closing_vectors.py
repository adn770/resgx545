#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Vectors from a closing session's kept jobs (round 4, sim item 4 of R3-P11): the loop proofs of
the pixel loops (4b) and the timings of every job's regtimeline (4d).

The input is a stage directory of a published session (render/closing-r3-pixel/out/<attempt>/
<stage>: cases.tsv and, per job, <name>.txt.gz with the probe's lines and the `tl` rows of the
regtimeline) and the session's bins/ (the programs the jobs ran, as sent).

Loop proofs: one vector a job whose program is a loop of the session (`loop-*`), in the layout of
doc/specs/vectors.md with init.task = "loop-proof" and readback.o0 null (the generic replay leaves
it out): readback.proof is the value the job's pixels read and how many of how many (the program
proves itself: MARK = 0xC0DE0000 | N where the counter reached zero, 0 for E431's `ba` loop), which
the replay (crates/sgx-sim/tests/closing_vectors.rs) must reproduce from the program alone. A job of
another program (the green control) is listed in the skipped, not converted.

Timings: one file a stage (format sgx545-timings), a row a job: the burst, the TA clocks' run, the
STATUS2 bits and when they showed, as the regtimeline read them. They are measurements, not a
simulator prediction; the definitions are those of the scorers of the session (closing4/pixel/
px_rule.py and ta_rule.py): the burst is the longest run of non-idle samples that holds a value
other than the idle and tick ones, tile_time_us = (burst - 60.2) / 4 is meaningful for a 64 x 32
fill only, ta_run_us is the longest run of 0x0008 = 0x000ccff8.

    closing_vectors.py --session DIR --out OUT [STAGE...]

DIR is render/closing-r3-pixel of the data repository; OUT is its vectors/closing/r3-pixel (loop
vectors in loops/<stage>.vec.json, timings in timings/<stage>.timing.json).
"""
from __future__ import annotations

import argparse
import dataclasses
import gzip
import hashlib
import json
import pathlib
import re
import struct
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pbdump  # noqa: E402

FORMAT = "sgx545-vectors"
TIMINGS = "sgx545-timings"
VERSION = 1
IDLE, TICK, TA_CLOCKS = 0x20, 0xccfa0, 0xccff8
G3D_CLOCKS = (0xfffa7, 0xfffa4)
TRI_CODE_INDEX = 0x20       # a --tri pixel program sits at index 0x20 of the pixel page (r3loops.py)
STAGES = ["q-f0", "q-f1a", "q-f1b", "q-t"]
TIMING_STAGES = STAGES + ["q-v"]
_PROBE = re.compile(r"^probe (\S+): (.*)$")
_PROOF = re.compile(r"^(0x[0-9a-f]+) \((\d+) of (\d+)\)$")
_MIXED = re.compile(r"(0x[0-9a-f]+) x(\d+)")
_TRI = re.compile(r"^tri (\d+)x(\d+)")
_STATUS2 = re.compile(r"status2 (\d+) -> (\d+)")
_TEMPS = re.compile(r"--temps (\d+)")
_VLOOP = re.compile(r"^vloop-(b2v|b4v|b8v|b12v|b16v)-i(\d+)$")
DEPTH_BASE = 0x3f200000     # the stored depth word of z = 0.25 + 4 N ulp is this + N (templates/vtx_loop.s)
_LOOP = re.compile(r"^loop-(rel|abs)-(b2|b4|b8|b8n|b12|b16|ld8)-i(\d+)$")


@dataclasses.dataclass
class Job:
    label: str = ""
    proof: tuple | None = None          # (value, pixels with it, pixels of the job)
    tri: tuple | None = None
    regs: list = dataclasses.field(default_factory=list)
    rows: list = dataclasses.field(default_factory=list)    # (t ns, [register values])


def parse_job(text: str) -> Job:
    """The probe's lines and the regtimeline of one kept job."""
    j = Job()
    for line in text.splitlines():
        if line.startswith("tl "):
            p = line.split()
            try:
                j.rows.append((int(p[1]), [int(x, 16) for x in p[2:]]))
            except ValueError:
                pass        # a torn row
            continue
        if line.startswith("timeline: regs"):
            j.regs = line.split("samples")[0].split()[2:]
            continue
        m = _PROBE.match(line)
        if not m:
            continue
        j.label = j.label or m.group(1)
        rest = m.group(2)
        t = _TRI.match(rest)
        if t:
            j.tri = (int(t.group(1)), int(t.group(2)))
        if rest.startswith("o0 mixed"):
            vals = [(v, int(c)) for v, c in _MIXED.findall(rest)]
            mark = [x for x in vals if x[0].startswith("0xc0de")] or vals[-1:]
            j.proof = (int(mark[0][0], 16), mark[0][1], sum(c for _, c in vals))
        elif rest.startswith("o0 "):
            p = _PROOF.match(rest[3:])
            if p:
                j.proof = (int(p.group(1), 16), int(p.group(2)), int(p.group(3)))
    return j


def _h32(v: int) -> str:
    return f"0x{v & 0xffffffff:08x}"


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def read_job(path: pathlib.Path) -> Job:
    return parse_job(gzip.open(path, "rt", errors="replace").read())


def cases(stage_dir: pathlib.Path) -> list[dict]:
    """The job table of a stage: name, args and STATUS2 before and after (None where not printed)."""
    out = []
    for line in (stage_dir / "cases.tsv").read_text().splitlines()[1:]:
        f = line.split("\t")
        s = _STATUS2.search(line)
        out.append({"name": f[0], "set": f[2], "args": f[6],
                    "before": int(s.group(1)) if s else None, "after": int(s.group(2)) if s else None})
    return out


def _words(blob: bytes) -> list[str]:
    return [f"0x{w:016x}" for w in struct.unpack(f"<{len(blob) // 8}Q", blob)]


def loop_vector(case: dict, job: Job, bins: pathlib.Path, rel: str) -> dict:
    m = _LOOP.match(job.label)
    if not m or job.proof is None:
        raise KeyError("not a loop program")
    form, _, n = m.group(1), m.group(2), int(m.group(3))
    value = job.proof[0]
    want = 0 if form == "abs" else 0xC0DE0000 | n
    if value != want:
        raise ValueError(f"{case['name']}: proof 0x{value:08x} is not the counter's 0x{want:08x} ({job.label})")
    temps = _TEMPS.search(case["args"])
    host = "fill" if job.tri is None else "tri"
    return {"id": case["name"],
            "program": {"isa": "usse", "entry": 0, "source": "recorded",
                        "words": _words((bins / f"{job.label}.bin").read_bytes())},
            "init": {"task": "loop-proof", "host": host, "instances": job.proof[2],
                     "temps": int(temps.group(1)) if temps else None,
                     "code_index": TRI_CODE_INDEX if host == "tri" else 0},
            "readback": {"failed": None, "o0": None, "mixed": [], "scratch": {}, "pixels": None,
                         "proof": {"o0": _h32(value), "count": job.proof[1], "of": job.proof[2]}},
            "provenance": {"probe": job.label, "case": 0, "table": rel, "template": "", "inputs": {},
                           "params": {}, "options": case["args"].split()[1:] if host == "tri" else [],
                           "question": "Q082"}}


def loop_vectors(stage_dir: pathlib.Path, bins: pathlib.Path, rel: str = "") -> tuple[list, dict]:
    """(vectors, {job: why not}) of a stage: every job whose program is a session loop."""
    vs, skipped = [], {}
    for c in cases(stage_dir):
        job = read_job(stage_dir / f"{c['name']}.txt.gz")
        try:
            vs.append(loop_vector(c, job, bins, rel or str(stage_dir)))
        except KeyError:
            skipped[c["name"]] = "not a loop program"
    return vs, skipped


def validate_loops(vs: list) -> None:
    for v in vs:
        p = v["readback"]["proof"]
        if not re.fullmatch(r"0x[0-9a-f]{8}", p["o0"]) or not 0 < p["count"] <= p["of"]:
            raise ValueError(f"{v['id']}: bad proof {p}")
        for w in v["program"]["words"]:
            if not re.fullmatch(r"0x[0-9a-f]{16}", w):
                raise ValueError(f"{v['id']}: bad word {w}")


def depth_words(param: bytes, tadata: bytes) -> list[int] | None:
    """The stored depth word of every vertex of the first object of a render dump, None when the
    dump does not decode (the reader of the session's score/r3lib.py)."""
    try:
        ws = pbdump.obj(param) if param else []
        o = pbdump.first_object(param, tadata) if param and tadata else None
    except Exception:
        return None
    if not ws or o is None:
        return None
    big = 0
    for i, w in enumerate(o["packed"]):
        big |= w << (32 * i)
    return [(big >> (80 * v + 48)) & 0xffffffff for v in range(len(o["vertices"]))]


def vertex_vector(case: dict, label: str, words: list[int], bins: pathlib.Path, rel: str) -> dict:
    """A vertex-loop job: the vertex program as run and the stored depth word of each vertex, which
    is DEPTH_BASE + N where the loop ran N times (E807's loop proof); instances are the vertices the
    dump decodes (the scorer's nv: 15 of a 48-vertex draw), init.draw_vertices the draw's. The replay computes z (o2) in
    the simulator and the stored word as the float32 0.5 + 0.5 z."""
    m = _VLOOP.match(label)
    if not m:
        raise KeyError("not a vertex loop program")
    n = int(m.group(2))
    if not words or any(w != DEPTH_BASE + n for w in words):
        raise ValueError(f"{case['name']}: depth words {[hex(w) for w in words]} are not "
                         f"0x{DEPTH_BASE:08x} + {n} on every vertex")
    temps, drawn = _TEMPS.search(case["args"]), re.search(r"--vertices (\d+)", case["args"])
    return {"id": case["name"],
            "program": {"isa": "usse", "entry": 0, "source": "recorded",
                        "words": _words((bins / f"{label}.bin").read_bytes())},
            "init": {"task": "vertex", "instances": len(words), "per": len(words),
                     "temps": int(temps.group(1)) if temps else None, "outputs": ["o2"], "skip": [],
                     "draw_vertices": int(drawn.group(1)) if drawn else 3},
            "readback": {"failed": None, "o0": None, "mixed": [], "scratch": {}, "pixels": None,
                         "vertices": None, "depth_words": [_h32(w) for w in words]},
            "provenance": {"probe": label, "case": 0, "table": rel, "template": "templates/vtx_loop.s",
                           "inputs": {"N": n}, "params": {"body": m.group(1)},
                           "options": case["args"].split()[1:], "question": "Q082"}}


def vertex_vectors(stage_dir: pathlib.Path, bins: pathlib.Path, rel: str) -> tuple[list, dict]:
    """(vectors, {job: why not}) of the vertex-loop jobs of a stage that ran."""
    vs, skipped = [], {}
    for c in cases(stage_dir):
        txt = stage_dir / f"{c['name']}.txt.gz"
        if not txt.is_file():
            continue            # not run: the timings file lists it
        label = read_job(txt).label
        dumps = [stage_dir / f"{c['name']}.{label}.{k}.bin.gz" for k in ("param", "tadata")]
        if not _VLOOP.match(label):
            skipped[c["name"]] = "not a vertex loop program"
        elif not all(d.is_file() for d in dumps):
            skipped[c["name"]] = "no render dump"
        else:
            ws = depth_words(*(gzip.open(d).read() for d in dumps))
            try:
                if ws is None:
                    raise ValueError(f"{c['name']}: the dump does not decode")
                vs.append(vertex_vector(c, label, ws, bins, rel))
            except ValueError as e:
                skipped[c["name"]] = str(e)
    return vs, skipped


BG = 0xff203040             # the target's background (the target is cleared to it)
_DIRECT = re.compile(r"^c-(rd|rdf|rdf128)-(g23|g24|g25)$")
_ROW = re.compile(r"row (\d+): (.*)$")


def grid(text: str, w: int, h: int) -> list[list[int]] | None:
    """The pixel rows a job printed (`--pixels`), None unless h rows of w."""
    rows = {}
    for line in text.splitlines():
        m = _ROW.search(line)
        if m:
            rows[int(m.group(1))] = [int(v, 16) for v in m.group(2).split()]
    g = [rows[i] for i in sorted(rows)]
    return g if len(g) == h and all(len(r) == w for r in g) else None


def _f32_hi(v: int) -> float:
    return struct.unpack("<f", struct.pack("<I", v & 0xffff0000))[0]


def source_of(vx: int, vy: int, w: int, h: int):
    """The pixel a premise control's word pair names: the float in the high half of each word is the
    pixel's centre in the target's [-1, 1] (the scorer's source_of, score_c3.py)."""
    sx = round(_f32_hi(vx) * w / 2 + w / 2 - .5)
    sy = round(_f32_hi(vy) * h / 2 + h / 2 - .5)
    return (sx, sy) if 0 <= sx < w and 0 <= sy < h else None


def decoded(gx, gy, w: int, h: int) -> list[bool]:
    """Per pixel (raster order): the premise control confirms it, both its words written (not the
    background, tag 15) and naming the pixel itself. The direct reads are compared only there."""
    out = []
    for y in range(h):
        for x in range(w):
            vx, vy = gx[y][x], gy[y][x]
            out.append(BG not in (vx, vy) and vx & 15 == 15 == vy & 15 and source_of(vx, vy, w, h) == (x, y))
    return out


def direct_vectors(stage_dir: pathlib.Path, bins: pathlib.Path, rel: str) -> tuple[list, dict]:
    """The direct reads of p-c3 (E808: g23, g24 or g25 written to o0 at the default triangle, the
    full 64 x 64 and the full 128 x 128 triangle): the program, the image the job printed, and the
    premise control's mask (c-<shape>-pa-x and -y): readback.undecoded lists the pixels (raster index)
    whose position it does not confirm, which a replay leaves out."""
    vs, skipped = [], {}
    for c in cases(stage_dir):
        m = _DIRECT.match(c["name"])
        if not m or not (stage_dir / f"{c['name']}.txt.gz").is_file():
            continue
        shape, reg = m.groups()
        w = int(re.search(r"--width (\d+)", c["args"]).group(1))
        h = int(re.search(r"--height (\d+)", c["args"]).group(1))
        job = read_job(stage_dir / f"{c['name']}.txt.gz")
        text = gzip.open(stage_dir / f"{c['name']}.txt.gz", "rt", errors="replace").read()
        img = grid(text, w, h)
        prem = [stage_dir / f"c-{shape}-pa-{a}.txt.gz" for a in "xy"]
        if img is None:
            skipped[c["name"]] = "no pixel rows"
        elif not all(p.is_file() for p in prem):
            skipped[c["name"]] = "no premise control"
        else:
            gx, gy = (grid(gzip.open(p, "rt", errors="replace").read(), w, h) for p in prem)
            if gx is None or gy is None:
                skipped[c["name"]] = "no premise pixel rows"
                continue
            vs.append({"id": c["name"],
                       "program": {"isa": "usse", "entry": 0, "source": "recorded",
                                   "words": _words((bins / f"{job.label}.bin").read_bytes())},
                       "init": {"task": "direct-read", "host": "tri", "width": w, "height": h,
                                "temps": int(_TEMPS.search(c["args"]).group(1)), "code_index": TRI_CODE_INDEX,
                                "reads": reg, "background": _h32(BG)},
                       "readback": {"failed": None, "o0": None, "mixed": [], "scratch": {}, "pixels": None,
                                    "image": [_h32(v) for r in img for v in r],
                                    "undecoded": [i for i, d in enumerate(decoded(gx, gy, w, h)) if not d]},
                       "provenance": {"probe": job.label, "case": 0, "table": rel, "template": "",
                                      "inputs": {}, "params": {"premise": [f"c-{shape}-pa-x", f"c-{shape}-pa-y"]},
                                      "options": c["args"].split()[1:], "question": "Q276"}})
    return vs, skipped


def _burst(rows, i8):
    """(t0, t1) of the job's burst: the longest run of non-idle samples (closed by the idle one)
    that holds a value other than the idle and tick ones."""
    runs, cur = [], []
    for t, v in rows:
        if v[i8] == IDLE:
            if cur:
                cur.append((t, v))
                runs.append(cur)
                cur = []
        else:
            cur.append((t, v))
    if cur:
        runs.append(cur)
    job = [r for r in runs if any(v[i8] not in (IDLE, TICK) for _, v in r)]
    if not job:
        return None
    b = max(job, key=lambda r: r[-1][0] - r[0][0])
    return b


def _ta_run(rows, i8):
    best, cur = None, None
    for t, v in rows:
        if v[i8] == TA_CLOCKS:
            cur = t if cur is None else cur
        elif cur is not None:
            if best is None or t - cur > best[1] - best[0]:
                best = (cur, t)
            cur = None
    return best


def _us(ns):
    return None if ns is None else round(ns / 1000.0, 1)


def timing(job: Job, after: int | None) -> dict:
    """The row of a job: times in microseconds, t6 and t7 from the burst's first sample, a_us the
    first sample with the 3D's clocks on (0xfffa7 or 0xfffa4), d6 from it, d7 from the TA run's
    start. bit6 and bit7 are the job's own STATUS2 read after the run (the last timeline sample
    where the table printed none)."""
    i8, i118 = job.regs.index("0x0008"), job.regs.index("0x0118")
    last = job.rows[-1][1][i118] if job.rows else None
    s2 = after if after is not None else last
    b = _burst(job.rows, i8)
    run = _ta_run(job.rows, i8)
    t0 = b[0][0] if b else None
    t7 = next((t for t, v in job.rows if v[i118] & 0x80), None)
    t6 = next((t for t, v in job.rows if t0 is not None and t >= t0 and v[i118] & 0x40), None)
    a = next((t for t, v in b if v[i8] in G3D_CLOCKS), None) if b else None
    rel = lambda t: None if t is None or t0 is None else _us(t - t0)  # noqa: E731
    burst = None if b is None else _us(b[-1][0] - t0)
    return {"burst_us": burst,
            "tile_time_us": None if burst is None else round((burst - 60.2) / 4, 1),
            "a_us": rel(a), "ta_run_us": 0.0 if run is None else _us(run[1] - run[0]),
            "ta_run_start_us": None if run is None else rel(run[0]),
            "t6_us": rel(t6), "t7_us": rel(t7),
            "d6_us": None if t6 is None or a is None else _us(t6 - a),
            "d7_us": None if t7 is None or run is None else _us(t7 - run[0]),
            "bit6": bool(s2 is not None and s2 & 0x40), "bit7": bool(s2 is not None and s2 & 0x80),
            "status2_after": None if s2 is None else _h32(s2), "samples": len(job.rows)}


def timings(stage_dir: pathlib.Path, session: str) -> dict:
    rows, not_run = [], []
    for c in cases(stage_dir):
        if not (stage_dir / f"{c['name']}.txt.gz").is_file():
            not_run.append(c["name"])       # a job of the table the session stopped before
            continue
        job = read_job(stage_dir / f"{c['name']}.txt.gz")
        if "0x0008" not in job.regs or "0x0118" not in job.regs:
            continue
        rows.append({"id": c["name"], "set": c["set"], "program": job.label, **timing(job, c["after"])})
    return {"format": TIMINGS, "version": VERSION,
            "run": {"session": session, "stage": stage_dir.name, "tool": f"closing_vectors.py {VERSION}"},
            "note": "per job, from the regtimeline the job ran under: measurements of the hardware, "
                    "not a simulator prediction (sgx-sim and sgx-pipe have no clock); times in us; "
                    "tile_time_us = (burst_us - 60.2) / 4 means a tile's time for a 64 x 32 fill only",
            "not_run": not_run, "jobs": rows}


def vector_doc(stage_dir: pathlib.Path, vs: list, skipped: dict, session: str) -> dict:
    names = [v["id"] for v in vs]
    raws = [f"{session}/out/{stage_dir.parent.name}/{stage_dir.name}/{n}.txt.gz" for n in names]
    return {"format": FORMAT, "version": VERSION,
            "run": {"raw": raws, "raw_sha256": [_sha((stage_dir / f"{n}.txt.gz").read_bytes()) for n in names],
                    "tool": f"closing_vectors.py {VERSION}"},
            "vectors": vs, "orphans": [], "skipped": skipped}


def convert(stage_dir: pathlib.Path, bins: pathlib.Path, out: pathlib.Path, session: str) -> tuple[int, int]:
    stage = stage_dir.name
    n = 0
    if stage in STAGES:
        vs, skipped = loop_vectors(stage_dir, bins, f"{session}/out/{stage_dir.parent.name}/{stage}")
        validate_loops(vs)
        (out / "loops").mkdir(parents=True, exist_ok=True)
        (out / "loops" / f"{stage}.vec.json").write_text(
            json.dumps(vector_doc(stage_dir, vs, skipped, session), indent=1) + "\n")
        n = len(vs)
    if stage == "p-c3":
        vs, skipped = direct_vectors(stage_dir, bins, f"{session}/out/{stage_dir.parent.name}/{stage}")
        (out / "direct-reads").mkdir(parents=True, exist_ok=True)
        (out / "direct-reads" / "p-c3.vec.json").write_text(
            json.dumps(vector_doc(stage_dir, vs, skipped, session), separators=(",", ":")) + "\n")
        return len(vs), 0
    if stage == "q-v":
        vs, skipped = vertex_vectors(stage_dir, bins, f"{session}/out/{stage_dir.parent.name}/{stage}")
        (out / "loops").mkdir(parents=True, exist_ok=True)
        (out / "loops" / "q-v.vec.json").write_text(
            json.dumps(vector_doc(stage_dir, vs, skipped, session), indent=1) + "\n")
        n = len(vs)
    doc = timings(stage_dir, session)
    (out / "timings").mkdir(parents=True, exist_ok=True)
    (out / "timings" / f"{stage}.timing.json").write_text(json.dumps(doc, indent=1) + "\n")
    return n, len(doc["jobs"])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--session", required=True, type=pathlib.Path)
    ap.add_argument("--out", required=True, type=pathlib.Path)
    ap.add_argument("stages", nargs="*", default=TIMING_STAGES)
    a = ap.parse_args(argv)
    att = sorted((a.session / "out").glob("2026*"))[-1]
    rel = "/".join(a.session.parts[-2:])
    for s in a.stages:
        n, t = convert(att / s, a.session / "bins", a.out, rel)
        print(f"{s}: {n} loop vectors, {t} timing rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
