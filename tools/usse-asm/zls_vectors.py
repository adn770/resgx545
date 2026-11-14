#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Unit vectors of the ZLS store, load and control word (doc/specs/vectors.md section 5, 12.4).

    zls_vectors.py --data DATA --out OUT

Three files under `OUT/`, in directories of their own so that the digest of the 12.0 dataset (which
holds `unit-vectors/zls/`) does not change: `zls-store-format/zls-store-format-dumps.vec.json` (the
11 depth buffers of E466 and E490 as `zls-format` vectors), `zls-load/zls-load-copy.vec.json` (the
30 cases of E467 as `zls-load` vectors) and `zls-ctl/zls-ctl.vec.json` (the control words of E337,
E411 and E467 as `zls-ctl` vectors). The expectations are the records' own numbers (the dump counts of E490, the lines of
load-copy/output.txt, the per-page counts of control-bits/output.txt, the bit tables of E337 and
E411), made by this script: the fields of a flipped control come from the bit arithmetic of the
records' reading (the same arithmetic as the Rust decoder, so they are readings, not measurements),
the stored pages from the run's own lines; nothing is taken from the Rust model. No numpy.
"""
import argparse
import ast
import gzip
import hashlib
import json
import pathlib
import re
import struct

TOOL = "zls_vectors.py 2"
FILL = 0xDEADBEEF
CONTROL = 0x0017100C
CONTROL_FIELDS = {"g": 1, "fmt": 0, "load": False, "load_depth": False, "load_stencil": False,
                  "store_depth": True, "store_stencil": True, "negate": False}


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def left_the_fill(path):
    raw = gzip.decompress(pathlib.Path(path).read_bytes())
    n = len(raw) // 4
    return sum(1 for v in struct.unpack("<%dI" % n, raw[:4 * n]) if v != FILL)


# E490: the dwords that left the fill in the x and the y ramp, by case (format 3, 5, 6: layouts
# only counted; format 3 is a lower bound, the buffer ended)
E490_COUNTS = {"f0": (786432, 786432), "f1": (786432, 786432), "f2": (393216, 393216),
               "f3": (965120, 965120), "f4": (0, 0), "f5": (96580, 84480), "f6": (86084, 73760),
               "f7": (0, 0), "b19_0": (786432, 786432), "b19_1": (786432, 786432),
               "b19_2": (393216, 393216)}


def format_vectors(data):
    data = pathlib.Path(data)
    d = "zls/store-format-dumps/dumps/"

    def ref(axis):
        p = d + "f0-ramp%s.bin.gz" % axis
        return {"path": p, "sha256": sha(data / p), "g": 33}

    out = []
    for case, (nx, ny) in E490_COUNTS.items():
        fmt = int(case[-1])
        ctl = CONTROL | 1 << 8 | (1 << 19 if case.startswith("b19") else 0) | fmt << 24
        init = {"task": "zls-format", "w": 1024, "h": 768, "ctl": "0x%08x" % ctl, "fill": "0xdeadbeef",
                "stencil": False}
        for axis in "xy":
            p = d + "%s-ramp%s.bin.gz" % (case, axis)
            init[axis] = {"path": p, "sha256": sha(data / p)}
            n = left_the_fill(data / p)
            assert n == (nx if axis == "x" else ny), (case, axis, n)
        init["depth_x"] = {"ramp": 1024} if case == "f0" else ref("x")
        init["depth_y"] = {"ramp": 768} if case == "f0" else ref("y")
        v = {"id": "zls-format__" + case, "init": init,
             "provenance": {"case": case, "records": ["E466", "E490"], "rebuilt": False,
                            "table": "zls/store-format-dumps", "questions": ["Q069", "Q120"],
                            "depth_input": "geometry within 1e-5 (E490)" if case == "f0"
                            else "the float the format-0 run stored at the pixel (E490)"}}
        if fmt in (3, 5, 6):
            v["expect"] = {"refuse": ["Q120"], "stored": nx + ny}
        else:
            v["expect"] = {"matched": nx + ny, "stored": nx + ny, "refused": {}}
        out.append(v)
    return out


def parse_load_line(line, part):
    """One result line of load-copy/output.txt as a `zls-load` vector (without its id)."""
    base = {"task": "zls-load", "w": 256, "h": 128, "z": "0x3f000000", "clear": "0x3f800000",
            "depth_fill": "index", "stencil_fill": "index"}
    m = re.search(r"ctl=(0x[0-9a-f]+)", line)
    base["ctl"] = m.group(1)
    exp = {}
    if part == "A":
        base["test"] = "never"
        names = {"0 (the clear value of a stencil, or loaded dword 0)": "zero", "the loaded dword": "loaded",
                 "1.0 (the clear value)": "clear", "other": "other"}
        for key, label in (("depth store", "depth"), ("stencil store", "stencil")):
            mm = re.search(key + r" \((\d+), (\{[^}]*\})\)", line)
            cl = {names[k]: n for k, n in ast.literal_eval(mm.group(2)).items()}
            exp[label] = {"stored": int(mm.group(1)), "classes": cl}
    else:
        values = dict(ast.literal_eval(re.search(r"stored depth (\[.*\])", line).group(1)))
        exp["depth"] = {"stored": sum(values.values()), "values": values}
        if part == "B":
            base["test"] = "less"
            base["depth_fill"] = re.match(r"(bit:\d+)", line).group(1)
            exp["drawn"] = int(re.search(r"triangle pixels \['(\d+)'\]", line).group(1))
        else:
            base["test"] = "never"
            base["depth_fill"] = re.match(r"load (0x[0-9a-f]+)", line).group(1)
            base["stencil_fill"] = "0xdeadbeef"
    return {"init": base, "expect": exp}


def load_vectors(data):
    text = (pathlib.Path(data) / "zls/load-copy/output.txt").read_text().splitlines()
    out, part, k = [], None, 0
    for line in text:
        if line.startswith("## A"):
            part = "A"
        elif line.startswith("## B"):
            part = "B"
        elif line.startswith("## C"):
            part = "C"
        elif part and "ctl=0x" in line and "job: ok" in line:
            v = parse_load_line(line, part)
            k += 1
            v["id"] = "zls-load__%s%02d-%s" % (part, k, v["init"]["ctl"][2:])
            v["provenance"] = {"records": ["E467"], "table": "zls/load-copy", "rebuilt": False,
                               "line": line.split(" job:")[0], "questions": ["Q121", "Q243"]}
            if part == "A" and "dword 0)" in line:
                pass
            out.append(v)
    return out


def flip_fields(bit):
    """The fields of CONTROL with `bit` flipped, by the bit arithmetic of the records' reading
    (E411's table of single flips and what E465, E466 and E467 name the bits); bit 0 changes none
    (it stops the colour image: `writes_pixels`)."""
    f = dict(CONTROL_FIELDS)
    if bit == 0:
        pass
    elif bit == 1:
        f["load"] = True
    elif bit == 2:
        f["store_depth"] = f["store_stencil"] = False
    elif 3 <= bit <= 11:
        f["g"] = (CONTROL >> 3 & 0x1FF) ^ (1 << (bit - 3))
    elif bit == 17:
        f["store_stencil"] = False
    elif bit == 18:
        f["store_depth"] = False
    elif bit == 19:
        f["negate"] = True
    elif bit in (24, 25, 26):
        f["fmt"] = {24: 1, 25: 2, 26: 4}[bit]
    return f


# E337's five values (CAP) read with E467's bits: the load bits 1, 13 and 14, the store enables
# (the pitch and the format are left out: the closed driver's G and format are not what E337 states)
READ = {k: v for k, v in CONTROL_FIELDS.items() if k not in ("g", "fmt")}
E337 = {0x0017100C: dict(READ),
        0x0017700E: {**READ, "load": True, "load_depth": True, "load_stencil": True},
        0x0017300E: {**READ, "load": True, "load_stencil": True},
        0x0011700A: {**READ, "load": True, "load_depth": True, "load_stencil": True,
                     "store_depth": False, "store_stencil": False},
        0x00140008: {**READ, "store_depth": False, "store_stencil": False}}
# E467's ten controls: the load-only ones store nothing (their load bits are not stated here: the
# record labels 0x0011d10a "bits 1, 13, 14" though 0x11710a + 0x6000 carries into bit 15 and clears
# bit 13; see the correction of E467)
E467 = {0x17110C: {"load": False}, 0x17110E: {"load": True}, 0x17310C: {"load": False},
        0x17510C: {"load": False}, 0x17710C: {"load": False},
        0x17310E: {"load": True, "load_depth": False, "load_stencil": True},
        0x17510E: {"load": True, "load_depth": True, "load_stencil": False},
        0x17710E: {"load": True, "load_depth": True, "load_stencil": True},
        0x11D10A: {"load": True, "store_depth": False, "store_stencil": False},
        0x11710A: {"load": True, "store_depth": False, "store_stencil": False}}


def parse_flip_runs(text):
    """Part A of control-bits/output.txt: bit -> {ok, pages, wrong}, from the lines `== bitN-rK:`,
    `job: ok|failed`, `scratch page P: N changed` and `diff: W of 4096 pixels`. The two runs of a
    bit must agree on the job's outcome and on every page (E411: "the same stored pages in both
    runs"); `wrong` is the wrong pixel count when both runs give it, else None."""
    runs = {}
    cur = None
    for line in text.splitlines():
        if line.startswith("## B"):
            break
        m = re.match(r"== bit(\d+)-r(\d)", line)
        if m:
            cur = {"ok": None, "pages": {}, "wrong": None}
            runs.setdefault(int(m.group(1)), []).append(cur)
        elif line.startswith("== "):
            cur = None
        elif cur is not None:
            if line.startswith("job:"):
                cur["ok"] = line.startswith("job: ok")
            m = re.match(r"scratch page (\d+): (\d+) changed", line)
            if m:
                cur["pages"][int(m.group(1))] = int(m.group(2))
            m = re.match(r"diff: (\d+) of 4096 pixels", line)
            if m:
                cur["wrong"] = int(m.group(1))
    out = {}
    for bit, rs in runs.items():
        assert len(rs) == 2, (bit, len(rs))
        a, b = rs
        assert a["ok"] == b["ok"] and a["ok"] is not None, bit
        assert a["pages"] == b["pages"], (bit, a["pages"], b["pages"])
        out[bit] = {"ok": a["ok"], "pages": a["pages"], "wrong": a["wrong"] if a["wrong"] == b["wrong"] else None}
    return out


def parse_flip_faults(text):
    """bit -> the page (address & ~0xfff) of the first `BIF fault S at A` line after each case
    marker `resgx545 case bitN-rK` of control-bits/kernel.log; the two runs of a bit must agree."""
    pages, cur = {}, None
    for line in text.splitlines():
        m = re.search(r"resgx545 case bit(\d+)-r\d", line)
        if m:
            cur = int(m.group(1))
            pages.setdefault(cur, [])
            pages[cur].append(None)
            continue
        m = re.search(r"sgxfive: BIF fault 0x[0-9a-f]+ at (0x[0-9a-f]+)", line)
        if m and cur is not None and pages[cur][-1] is None:
            pages[cur][-1] = int(m.group(1), 16) & ~0xfff
    out = {}
    for bit, ps in pages.items():
        if any(p is not None for p in ps):
            assert len(set(ps)) == 1, (bit, ps)
            out[bit] = ps[0]
    return out


def flip_expect(bit, run, fault_page=None):
    """What the records state of CONTROL with `bit` flipped. A faulted job (bits 5 to 11: the store
    reaches a page nothing maps past the 16-page scratch and the tool's colour buffer, E1070) is a
    fault at the page E411's kernel log names; the 16-bit format at G = 1 and format 4 are refused
    by question; the rest carries the readings of the changed field, whether the image was written
    (all 4096 pixels right, or all wrong with bit 0) and the pages the run stored."""
    if not run["ok"]:
        return {"outcome": "fault"} if fault_page is None else {"outcome": "fault", "addr": "0x%08x" % fault_page}
    if bit in (25, 26):
        # the run stored pages the model does not decode; naming them makes the vector compare the
        # store, so a model that stopped refusing is caught (a mismatch of pages), not matched empty
        return {"refuse": ["Q071" if bit == 25 else "Q120"],
                "pages": {str(p): n for p, n in sorted(run["pages"].items())}}
    f = flip_fields(bit)
    e = {k: v for k, v in f.items() if k not in ("g", "fmt")}
    if bit in (3, 4):
        e["g"] = f["g"]
    if bit == 24:
        e["fmt"] = f["fmt"]
    if bit == 0 and run["wrong"] == 4096:
        e["writes_pixels"] = False
    elif run["wrong"] == 0:
        e["writes_pixels"] = True
    e["pages"] = {str(p): n for p, n in sorted(run["pages"].items())}
    return e


def ctl_vectors(data):
    runs = parse_flip_runs((pathlib.Path(data) / "zls/control-bits/output.txt").read_text())
    faults = parse_flip_faults((pathlib.Path(data) / "zls/control-bits/kernel.log").read_text())
    out = []

    def add(vid, ctl, expect, rec, note, init=None):
        out.append({"id": "zls-ctl__" + vid, "init": {"task": "zls-ctl", "ctl": "0x%08x" % ctl, **(init or {})},
                    "expect": expect,
                    "provenance": {"records": rec, "rebuilt": False, "note": note, "questions": ["Q071"],
                                   "basis": "a script: the records' bit arithmetic and the run's own page lines"}})

    for bit in range(32):
        add("flip-%02d" % bit, CONTROL ^ 1 << bit, flip_expect(bit, runs[bit], faults.get(bit)),
            ["E057", "E411", "E465", "E466"] + (["E1070"] if not runs[bit]["ok"] else []), "0x0017100c with bit %d flipped" % bit,
            {"arrangement": "e411-scratch", "w": 64, "h": 64, "stencil": True})
    for ctl, f in E337.items():
        add("driver-%08x" % ctl, ctl, f, ["E337", "E411", "E467"], "a value the closed driver writes")
    for ctl, f in E467.items():
        add("load-%08x" % ctl, ctl, f, ["E467"], "a control of the load run")
    return out


def wrap(raw, vectors):
    p = pathlib.Path(raw[0]) / raw[1]
    return {"format": "sgx545-vectors", "version": 1, "orphans": [],
            "run": {"raw": raw[1], "raw_sha256": sha(p), "tool": TOOL}, "vectors": vectors}


def write(path, doc):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    out = pathlib.Path(a.out)
    write(out / "zls-store-format/zls-store-format-dumps.vec.json",
          wrap((a.data, "zls/store-format-dumps/output.txt"), format_vectors(a.data)))
    write(out / "zls-load/zls-load-copy.vec.json", wrap((a.data, "zls/load-copy/output.txt"), load_vectors(a.data)))
    write(out / "zls-ctl/zls-ctl.vec.json", wrap((a.data, "zls/control-bits/output.txt"), ctl_vectors(a.data)))


if __name__ == "__main__":
    main()
