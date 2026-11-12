#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Data statements of the closing pass that no simulator replays (round 4, sim item 4 of R3-P11,
the part closing_vectors.py leaves): one table of rows a job, each row what the kept files of the
job say and nothing else.

    depth    E795-E798 (render/closing-r3-geo g-da, g-db, g-dc, g-dd): the stored depth word of each
             vertex of the first object of the render dump, the stored 1/w, the vertex count
    dword36  E803: per job of g-d36 and of the side tables of g-c4 .. g-c7, the count before the last
             abort (CR_DPM_GLOBAL_PAGE_STATUS low half, 0x072c) and the dword 36 of the control block
    pbpages  E824 (render/closing-r3k-pixel k-f4): the parameter buffer pages a job's dump writes
             (the non-zero 4 KiB pages and their runs), the TA data size, the tile count
    counts   the count tables of the DPM stages (r3-geo g-c4 .. g-c7 and g-d36, r3-geo-c g-qf and
             g-qh): partial renders (rising edges of 0x0658 bit 0), the status at the first abort
             (thr0), the peak of each TA run, the control block's dwords 36 to 38
    zls      r3-geo-c g-z (E730's reader) and r6-misc q287 (E885, odd heights): the stored (not 1.0f)
             dwords of the depth store's tile area and their extent

Format sgx545-tables: {format, version, run, kind, note, replay, rows, skipped}. replay says whether
a simulator replays the table: only the zls tables do (sgx-pipe's ZLS band, E831 and E885, held to every
row by crates/sgx-pipe/tests/zls_table.rs, which counts odd widths as refused rows), `replayed` with the test's
name; the others (the TA's depth words, the DPM, the parameter buffer pages) are not modelled, so they are
`refused` with the reason, never a pass. The rows are measurements
of the hardware, the keys the readers' own (closing3/r3-geo-c score/score_r3.py, closing-r3-geo
score/dpm3.py and score_r3.py, closing4/render4x/pb_pages.py).

    closing_tables.py KIND --session DIR --out OUT STAGE...

DIR is a session directory of the data repository (render/closing-r3-geo, closing-r3k-pixel,
closing-r6-misc, or the r3-geo-c session wherever it is published: it is an argument, not a fixed path).
A stage directory is DIR/out/STAGE or DIR/out/<latest attempt>/STAGE. OUT is the vectors/closing directory.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import pathlib
import re
import struct
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import closing_vectors as cv  # noqa: E402
import pbdump  # noqa: E402

TABLES = "sgx545-tables"
VERSION = 1
TOOL = f"closing_tables.py {VERSION}"
PAGE = 4096
BG = 0x3F800000             # the depth buffer's background 1.0f (r3_geo.BG)
FILL = 0xDEADBEEF           # the buffer's pre-fill (r3_geo.FILL)
TILE_W, TILE_H = 32, 16     # tiles of the depth store, 512 dwords a tile
RULE_REASON = {
    "depth": "the TA's stored depth word is not a modelled rule (E795, E796: every frozen formula refuted)",
    "dword36": "the DPM page counts and the TA/3D control block are not modelled by sgx-sim or sgx-pipe",
    "pbpages": "the TA's parameter buffer page writes are not modelled by sgx-sim",
    "counts": "the DPM abort and partial render sequence is not modelled by sgx-sim or sgx-pipe",
    "zls": "the ZLS store band is not modelled by sgx-sim (Q287 is open for odd widths): a table, not a replay",
}
# tables a test replays: kind -> the test (file::function) that holds every modelled row to the model
REPLAYED = {
    "zls": {"test": "crates/sgx-pipe/tests/zls_table.rs::the_band_replays_every_modelled_row_of_the_zls_tables",
            "model": "sgx-pipe zls::in_band, rule A at even sizes (E831) and odd heights (E885); odd widths are "
                     "refused rows (Q287)"},
}


def find_stage(session: pathlib.Path, stage: str) -> pathlib.Path:
    """DIR/out/STAGE, else the stage of the latest attempt directory under DIR/out."""
    plain = session / "out" / stage
    if plain.is_dir():
        return plain
    att = sorted(p for p in (session / "out").glob(f"2026*/{stage}") if p.is_dir())
    if not att:
        raise FileNotFoundError(f"{session}: no stage {stage}")
    return att[-1]


def read_cases(stage_dir: pathlib.Path) -> list[dict]:
    lines = (stage_dir / "cases.tsv").read_text().splitlines()
    hdr = lines[0].split("\t")
    return [dict(zip(hdr, ln.split("\t"))) for ln in lines[1:]]


def _gz(stage_dir: pathlib.Path, name: str) -> bytes | None:
    p = stage_dir / name
    return gzip.open(p).read() if p.is_file() else None


def _text(stage_dir: pathlib.Path, name: str) -> str | None:
    b = _gz(stage_dir, name)
    return None if b is None else b.decode(errors="replace")


def _sha(stage_dir: pathlib.Path, name: str) -> str | None:
    p = stage_dir / name
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None


def _opt(args: str, opt: str) -> int | None:
    m = re.search(rf"{re.escape(opt)} (\d+)", args)
    return int(m.group(1)) if m else None


def _h32(v: int) -> str:
    return f"0x{v & 0xffffffff:08x}"


def document(kind: str, stage_dir: pathlib.Path, session: str, rows: list, skipped: dict, **extra) -> dict:
    return {"format": TABLES, "version": VERSION, "kind": kind,
            "run": {"session": session, "stage": stage_dir.name, "tool": TOOL},
            "note": "per job, what the kept files say: measurements of the hardware, not a simulator "
                    "prediction and not a rule",
            "replay": ({"status": "replayed", **REPLAYED[kind]} if kind in REPLAYED
                       else {"status": "refused", "reason": RULE_REASON[kind]}),
            "rows": rows, "skipped": skipped, **extra}


def write(path: pathlib.Path, doc: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=1) + "\n")


def _void(c: dict, txt: str | None) -> str | None:
    """Why a job cannot be read (the scorers' rule: tested before any reading)."""
    if txt is None:
        return "no output kept"
    if len(txt.strip()) < 20:
        return "empty output"
    if c.get("class") in ("hang", "fault", "fail", "skipped"):
        return f"class {c.get('class')}"
    rc = c.get("rc", "")
    if rc == "":
        return "no rc recorded"
    if int(rc) in (2, 124, 125, 126, 127) or int(rc) >= 128:
        return f"rc {rc} is not a result of the tool"
    if re.search(r"hung", txt):
        return "hang"
    return None


# ---------------------------------------------------------------------------------------------- DPM
def counts_before_aborts(job: cv.Job) -> dict | None:
    """The 0x072c low half in the sample before each rising edge of 0x0658 bit 0, and the whole-job peak
    (closing-r3-geo score/dpm3.py counts_before_aborts); None when the job did not sample 0x072c."""
    if "0x072c" not in job.regs:
        return None
    i58, i2c = job.regs.index("0x0658"), job.regs.index("0x072c")
    s58 = [v[i58] for _, v in job.rows]
    s2c = [v[i2c] for _, v in job.rows]
    edges = [i for i in range(len(s58)) if s58[i] & 1 and (i == 0 or not s58[i - 1] & 1)]
    return {"before": [s2c[max(i - 1, 0)] & 0xffff for i in edges],
            "peak": max((v & 0xffff) for v in s2c) if s2c else 0}


def _runs(job: cv.Job) -> tuple[list, list]:
    """(status 0x0724 low half at each partial render's start, the peak of each TA run)."""
    ip, ist = job.regs.index("0x0658"), job.regs.index("0x0724")
    prs, peaks, cur, inpr = [], [], 0, False
    for _, v in job.rows:
        if v[ip] & 1:
            if not inpr:
                prs.append(v[ist] & 0xffff)
                peaks.append(cur)
                cur, inpr = 0, True
            continue
        inpr = False
        cur = max(cur, v[ist] & 0xffff)
    peaks.append(cur)
    return prs, peaks


def _knob(job: cv.Job, txt: str) -> int | None:
    """This job's first 0x0624 value: the first row at or after the tool's start whose 0x0724 low half is
    non-zero (the previous job's value shows before that)."""
    m = re.search(r"^timeline: .* start (\d+) end", txt, re.M)
    if not m or "0x0624" not in job.regs:
        return None
    i24, i4 = job.regs.index("0x0624"), job.regs.index("0x0724")
    return next((v[i24] for t, v in job.rows if t >= int(m.group(1)) and v[i4] & 0xffff), None)


def _buf09(stage_dir: pathlib.Path, name: str) -> list[int] | None:
    b = _gz(stage_dir, f"{name}.after.buf09.bin.gz")
    return list(struct.unpack("<59I", b[:236])) if b and len(b) >= 236 else None


def counts_row(stage_dir: pathlib.Path, c: dict) -> dict | str:
    """The row of a usable job or the reason it is not one."""
    n = c["name"]
    txt = _text(stage_dir, f"{n}.txt.gz")
    why = _void(c, txt)
    if why:
        return why
    job = cv.parse_job(txt)
    args = c.get("args", "")
    k = _opt(args, "-n") or 1
    early = [int(x) for x in re.findall(r"^tri \d+x\d+ #(\d+): overflowed", txt, re.M) if int(x) < k]
    if early:
        return f"a kick lost: render(s) {early} overflowed before the last (E773's rule)"
    if "0x0658" not in job.regs or "0x0724" not in job.regs:
        return "no timeline"
    knob = _knob(job, txt)
    if knob is None:
        return "no status rise: the job's 0x0624 value is unknown"
    P = int(c["P"], 16) if c.get("P", "-") not in ("-", "") else None
    if P is not None and knob != P - 0x22:
        return f"knob did not land: 0x0624 {knob:#x}, wanted {P - 0x22:#x}"
    prs, peaks = _runs(job)
    cnt = counts_before_aborts(job)
    b9 = _buf09(stage_dir, n)
    return {"id": n, "set": c.get("set", ""), "P": P, "knob0624": knob, "partial_renders": len(prs),
            "thr0": prs[0] if prs else None, "peaks": peaks, "need": max(peaks) if peaks else None,
            "counts_before_aborts": None if cnt is None else cnt["before"],
            "dw36": None if b9 is None else b9[36], "dw37": None if b9 is None else b9[37],
            "dw38": None if b9 is None else b9[38],
            "width": _opt(args, "--width"), "height": _opt(args, "--height"),
            "vertices": _opt(args, "--vertices"), "raw": f"{stage_dir.name}/{n}.txt.gz",
            "raw_sha256": _sha(stage_dir, f"{n}.txt.gz")}


def counts_table(stage_dir: pathlib.Path, session: str) -> dict:
    rows, skipped = [], {}
    for c in read_cases(stage_dir):
        r = counts_row(stage_dir, c)
        if isinstance(r, str):
            skipped[c["name"]] = r
        else:
            rows.append(r)
    return document("counts", stage_dir, session, rows, skipped)


def dword36_table(stages: list[tuple[str, pathlib.Path]], session: str) -> dict:
    """E803's table: dword 36 of the control block against the count before the LAST abort (a reading of
    the table, `agrees` is dword 36 = max(last count - 2, 0), E803's H-last; the rule is not part of the
    data)."""
    rows, skipped = [], {}
    for name, d in stages:
        for r in counts_table(d, session)["rows"]:
            b = r["counts_before_aborts"]
            if b is None or r["dw36"] is None:
                skipped[f"{name}/{r['id']}"] = "no abort sampled or no control block"
                continue
            rows.append({"stage": name, "id": r["id"], "set": r["set"], "P": r["P"], "width": r["width"],
                         "height": r["height"], "counts_before_aborts": b, "last_count": b[-1] if b else None,
                         "dw36": r["dw36"], "dw38": r["dw38"],
                         "agrees": r["dw36"] == (max(b[-1] - 2, 0) if b else 0)})
    doc = document("dword36", stages[0][1], session, rows, skipped,
                   totals={"jobs": len(rows), "agree": sum(r["agrees"] for r in rows)})
    doc["run"]["stage"] = ",".join(n for n, _ in stages)
    return doc


# ---------------------------------------------------------------------------------------------- depth
def depth_row(stage_dir: pathlib.Path, c: dict) -> dict | str:
    n = c["name"]
    txt = _text(stage_dir, f"{n}.txt.gz")
    why = _void(c, txt)
    if why:
        return why
    dumps = sorted(p.name[len(n) + 1:-len(".param.bin.gz")] for p in stage_dir.glob(f"{n}.*.param.bin.gz")
                   if not p.name.startswith(f"{n}.after."))
    label = dumps[0] if dumps else None
    param, tadata = (_gz(stage_dir, f"{n}.{label}.{k}.bin.gz") for k in ("param", "tadata"))
    if label is None or param is None or tadata is None:
        return "no render dump"
    try:
        o = pbdump.first_object(param, tadata)
    except Exception as e:
        return f"the dump does not decode ({str(e)[:40]})"
    if o is None:
        return "no object written"
    big = 0
    for i, w in enumerate(o["packed"]):
        big |= w << (32 * i)
    nv = len(o["vertices"])
    return {"id": n, "set": c.get("set", ""), "dump": label, "vertices": nv,
            "depth_words": [_h32((big >> (80 * v + 48)) & 0xffffffff) for v in range(nv)],
            "rhw": [_h32(w) for w in o["PB_OBJ.RHW"]], "raw": f"{stage_dir.name}/{n}.{label}.param.bin.gz",
            "raw_sha256": _sha(stage_dir, f"{n}.{label}.param.bin.gz")}


def depth_table(stage_dir: pathlib.Path, session: str) -> dict:
    rows, skipped = [], {}
    for c in read_cases(stage_dir):
        r = depth_row(stage_dir, c)
        if isinstance(r, str):
            skipped[c["name"]] = r
        else:
            rows.append(r)
    return document("depth", stage_dir, session, rows, skipped)


# ---------------------------------------------------------------------------------------------- PB pages
def pb_pages_table(stage_dir: pathlib.Path, session: str) -> dict:
    """The non-zero 4 KiB pages of each job's parameter buffer dump (closing4/render4x/pb_pages.py). model_nonzero is
    the post hoc reading of the 4x page need (E828) [post hoc]: ceil(tiles / 8) pages and 4 more, tiles of 32 x 16; it is the
    reading's number, not part of the measurement."""
    rows, skipped = [], {}
    for c in read_cases(stage_dir):
        n = c["name"]
        param = _gz(stage_dir, f"{n}.tri.param.bin.gz")
        if param is None:
            skipped[n] = f"no dump (class {c.get('class')})"
            continue
        txt = _text(stage_dir, f"{n}.txt.gz") or ""
        nz = [i for i in range(len(param) // PAGE) if any(param[i * PAGE:(i + 1) * PAGE])]
        runs: list[list[int]] = []
        for i in nz:
            if runs and runs[-1][1] == i - 1:
                runs[-1][1] = i
            else:
                runs.append([i, i])
        w, h = _opt(c["args"], "--width"), _opt(c["args"], "--height")
        tiles = math.ceil(w / TILE_W) * math.ceil(h / TILE_H)
        m = re.search(r"rgn:(\d+)", c.get("knobs", ""))
        ta = re.search(r"render memory to .*\((\d+), (\d+) bytes\)", txt)
        d = re.search(r"^diff: (\d+) of (\d+) pixels", txt, re.M)
        rows.append({"id": n, "set": c.get("set", ""), "width": w, "height": h,
                     "arrays": int(m.group(1)) if m else None, "pages": len(param) // PAGE,
                     "nonzero": len(nz), "runs": runs, "tiles": tiles,
                     "model_nonzero": math.ceil(tiles / 8) + 4,
                     "ta_data_bytes": int(ta.group(2)) if ta else None,
                     "wrong": int(d.group(1)) if d else None, "pixels": int(d.group(2)) if d else None,
                     "raw": f"{stage_dir.name}/{n}.tri.param.bin.gz",
                     "raw_sha256": _sha(stage_dir, f"{n}.tri.param.bin.gz")})
    return document("pbpages", stage_dir, session, rows, skipped)


# ---------------------------------------------------------------------------------------------- ZLS
def _mort(x: int, y: int) -> int:
    r = 0
    for k, (v, b) in enumerate([(y, 0), (x, 0), (y, 1), (x, 1), (y, 2), (x, 2), (y, 3), (x, 3)]):
        r |= ((v >> b) & 1) << k
    return r | (((x >> 4) & 1) << 8)


def _pitch(w: int) -> int:
    """The tile row pitch minus 1, at least 1 (r3_geo.pitch_g: the depth pitch the jobs were run with)."""
    return max(1, (w + TILE_W - 1) // TILE_W - 1)


def dword_index(x: int, y: int, w: int, h: int) -> int:
    return 512 * ((y // TILE_H) * (_pitch(w) + 1) + x // TILE_W) + _mort(x % TILE_W, y % TILE_H)


def zls_row(stage_dir: pathlib.Path, c: dict) -> dict | str:
    n = c["name"]
    txt = _text(stage_dir, f"{n}.txt.gz")
    why = _void(c, txt)
    raw = _gz(stage_dir, f"{n}.depth.1.bin.gz")
    if why or raw is None or len(raw) % 4:
        return why or "no depth dump"
    w, h = _opt(c["args"], "--width"), _opt(c["args"], "--height")
    tw, th = (w + TILE_W - 1) // TILE_W, (h + TILE_H - 1) // TILE_H
    words = struct.unpack(f"<{len(raw) // 4}I", raw)
    need = 512 * ((th - 1) * (_pitch(w) + 1) + tw)
    if len(words) < need:
        return f"dump has {len(words)} dwords, the tiles need {need}"
    st, dead = [], 0
    for y in range(th * TILE_H):
        for x in range(tw * TILE_W):
            v = words[dword_index(x, y, w, h)]
            if v == FILL:
                dead += 1
            elif v != BG:
                st.append((x, y))
    full = "--tri-full" in c["args"]
    diff = re.search(rf"^diff: 0 of {w * h} pixels", txt, re.M) is not None
    return {"id": n, "set": c.get("set", ""), "width": w, "height": h, "full_screen": full,
            "stored": len(st), "extent": [max((x for x, _ in st), default=-1) + 1,
                                          max((y for _, y in st), default=-1) + 1],
            "unwritten": dead, "diff_zero": diff, "raw": f"{stage_dir.name}/{n}.depth.1.bin.gz",
            "raw_sha256": _sha(stage_dir, f"{n}.depth.1.bin.gz")}


def zls_table(stage_dir: pathlib.Path, session: str) -> dict:
    rows, skipped = [], {}
    for c in read_cases(stage_dir):
        r = zls_row(stage_dir, c)
        if isinstance(r, str):
            skipped[c["name"]] = r
        else:
            rows.append(r)
    return document("zls", stage_dir, session, rows, skipped)


# ---------------------------------------------------------------------------------------------- CLI
GEO_STAGES = {"depth": ["g-da", "g-db", "g-dc", "g-dd"],
              "counts": ["g-c4", "g-c5", "g-c6", "g-c7", "g-d36", "g-qf", "g-qh"],
              "dword36": ["g-d36", "g-c4", "g-c5", "g-c6", "g-c7"],
              "pbpages": ["k-f4"], "zls": ["g-z"]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("kind", choices=sorted(GEO_STAGES))
    ap.add_argument("--session", required=True, type=pathlib.Path)
    ap.add_argument("--out", required=True, type=pathlib.Path)
    ap.add_argument("stages", nargs="*")
    a = ap.parse_args(argv)
    label = "/".join(a.session.parts[-2:])
    stages = a.stages or GEO_STAGES[a.kind]
    if a.kind == "dword36":
        t = dword36_table([(s, find_stage(a.session, s)) for s in stages], label)
        write(a.out / "dword36.table.json", t)
        print(f"dword36: {t['totals']}")
        return 0
    fn = {"depth": depth_table, "counts": counts_table, "pbpages": pb_pages_table, "zls": zls_table}[a.kind]
    sub = {"depth": "depth-words", "counts": "counts", "pbpages": "pb-pages", "zls": "zls-extents"}[a.kind]
    for s in stages:
        try:
            d = find_stage(a.session, s)
        except FileNotFoundError:
            print(f"{s}: not in this session")
            continue
        t = fn(d, label)
        write(a.out / sub / f"{s}.table.json", t)
        print(f"{s}: {len(t['rows'])} rows, {len(t['skipped'])} skipped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
