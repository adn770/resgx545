#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Hardware probes of the USSE instruction set, run as client fills on the sgxfive render node.

A table, probes/<unit>/<feature>.toml, lists probes: a program template (the table's
templates/*.s, our own assembly), its parameters, the input cases and, per hypothesis, the readback each case
should give. Every case is assembled with usse-asm into its own program, which
`sgxfive-test probe` runs as the shader of its own fill; the host reads o0 (and a scratch page)
back. A table entry with host = "tri" runs instead as one program (its slot) of the first
triangle's render (`sgxfive-test probe --tri`), with fixed helper programs in other slots. A
hypothesis that predicts every case is consistent; one consistent hypothesis settles the probe.

    probe.py [--table FILE] COMMAND        FILE: the table (probes/<unit>/<feature>.toml)
    probe.py list                          the probes and their questions
    probe.py build DIR [NAME...]           assemble every case into DIR
    probe.py run [--out DIR] [NAME...]     build, run on the laptop, report
    probe.py local [--mock] [NAME...]      the same with a local sgxfive-test
    probe.py eval RAW [NAME...]            report on a saved run (RAW: its output)

The laptop comes from SGX_TARGET_HOST and SGX_TARGET_SSH_OPTS, or tools/bringup/local.env;
`sgxfive-test` must be in its home directory (SGX_PROBE_TOOL overrides the path). Every case
runs inside regtimeline (SGX_PROBE_TIMELINE, default ./regtimeline) over the visibility
counters, after a "probe-case NAME" line, unless SGX_PROBE_COUNTERS=0; the report names the
cases where they counted (tools/sweep/counters.py scan finds them in saved runs).
"""
from __future__ import annotations

import argparse
import dataclasses
import os
import pathlib
import re
import math
import shlex
import shutil
import struct
import subprocess
import sys
import tempfile
import tomllib

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
PROBES = ROOT / "probes"
PROBES_DIR = PROBES / "usse" / "templates"      # the default template directory
sys.path.insert(0, str(ROOT / "tools" / "sweep"))
import counters  # noqa: E402
ASM = HERE / "usse-asm"
PDS_ASM = HERE / "pds-asm"
USE_DUMP = "sa_dump.s"       # the USE program of every PDS probe (its results to scratch)
LOCAL_ENV = ROOT / "kernel" / "scripts" / "local.env"
# The program slots of a "tri" probe's render (sgxfive_tri_probe.h), and those that are PDS.
TRI_SLOTS = ("pixev", "eot", "vtxpds", "vtxuse", "pixel", "pixtask", "pixpds", "state")
TRI_PDS = ("pixev", "vtxpds", "pixpds")
TRI_BLOCK_WORDS = 18             # the triangle's state block (sgxfive_render.h)
TRI_ADD_WORDS = {2: 1, 3: 1, 4: 1, 5: 1, 7: 2}   # presence bits blk_add may add (S.2)
TRI_SIZE = (64, 64)
TRI_MAX = 4096
TRI_CMD_WORDS = 26             # sgxfive_tri_probe.h: the render command's words
TRI_BLK2_WORDS = 32            # sgxfive_tri_probe.h: a second object's state block (obj2)
TRI_VDM_WORDS = 11             # sgxfive_render.h: the triangle's VDM stream
DUMPS = "dumps"                # tri: where dump_render probes' render memory goes
TRI_MAX_VERTICES = 126         # sgxfive_tri_probe.h: the vertex buffer and its spare room

NAME_RE = re.compile(r"[a-z0-9][a-z0-9-]*")
FILE_RE = re.compile(r"[a-z0-9][a-z0-9-]*__\d+")
PLACEHOLDER_RE = re.compile(r"\{([A-Z][A-Z0-9_]*)\}")
SCRATCH_FILL = 0xD0000000      # scratch dword i starts as SCRATCH_FILL | i (sgxfive-test)


class ProbeError(Exception):
    pass


@dataclasses.dataclass
class Probe:
    name: str
    question: str
    source: str
    params: dict
    inputs: list
    cases: list
    hypotheses: dict
    temps: int = 32
    labels: list = dataclasses.field(default_factory=list)
    coords: bool = False        # run as the copy shader: pa0 = (y << 16) | x
    pixels: bool = False        # read every pixel back
    table: str = ""             # the file name of the table it comes from
    isa: str = "usse"           # "pds": the fill's PDS secondary; `use` is the fill shader
    use: str = USE_DUMP         # a PDS probe's USE program
    host: str = "fill"          # "tri": a program of the first triangle's render
    slot: str = ""              # tri: the slot the cases replace (TRI_SLOTS)
    slots: dict = dataclasses.field(default_factory=dict)   # tri: {slot: fixed helper}
    size: tuple = TRI_SIZE      # tri: the render target, W x H
    max_size: tuple | None = None   # tri: the render context's maximum (None: size)
    vertices: int = 0           # tri: the triangle and copies of it (0: the one)
    vtx_coords: int = 0         # tri: more output dwords per vertex (--vtx-coords)
    copy_depth: bool = False    # tri: the copies at clip z = c / 16 (--copy-depth)
    blk: dict = dataclasses.field(default_factory=dict)  # tri: state block words (--blk)
    cmd: dict = dataclasses.field(default_factory=dict)  # tri: render command words (--cmd)
    vdm: dict = dataclasses.field(default_factory=dict)  # tri: VDM stream words (--vdm)
    vdm_xor: dict = dataclasses.field(default_factory=dict)  # tri: VDM words flipped
    dump_render: bool = False   # tri: the render's PB and TA data to DUMPS (--dump-render)
    kpoke: list = dataclasses.field(default_factory=list)  # tri: kernel words (--kpoke SPEC)
    obj2: dict = dataclasses.field(default_factory=dict)   # tri: a second object (--obj2),
                                                           # {first, blk, pixel}
    sideband: int | None = None  # tri, with an eot slot: its emitpix2's (--sideband)
    isp2: int | None = None      # tri: ISP word 2 in the state block (--isp2)
    blk_add: dict = dataclasses.field(default_factory=dict)  # tri: presence bit -> words
                                                             # added to the block (--blk-add)
    low: int = 0                # fill: the scratch mapped again at this first-MiB address
                                #       (--low; the kernel's debugfs sgx/vm_low)
    late: str = ""              # fill: "R:K=V", the host writes V to scratch dword K once
                                #       dword R leaves its fill, while the job runs (--late)
    pokes: list = dataclasses.field(default_factory=list)   # fill: words of its transfer
                                                            # command, xfer:N=V / ^=V
    case_set: list = dataclasses.field(default_factory=list)    # per case: more pokes, and
                                                                # cmd/blk/vdm words (a scan)
    raw: dict | None = dataclasses.field(default=None, repr=False, compare=False)
    first: int = 0              # the index of the first case in the file names (a case alone)


@dataclasses.dataclass(frozen=True)
class Obs:
    """What one fill gave: o0 (None unless uniform), the mixed values, the failure, the
    changed scratch dwords (offset, value), every pixel in raster order (with --pixels)."""
    o0: int | None = None
    mixed: tuple = ()
    failed: str | None = None
    scratch: tuple = ()
    pixels: tuple | None = None


@dataclasses.dataclass
class Verdict:
    consistent: list
    settled: str | None
    text: str


def _tri_fields(d: dict) -> dict:
    """The host fields of a table entry, checked: {} for a fill probe."""
    name, host = d["name"], d.get("host", "fill")
    tri_keys = {"slot", "slots", "size", "max_size", "vertices", "vtx_coords", "copy_depth",
                "blk", "cmd", "vdm", "vdm_xor", "sideband", "isp2", "blk_add", "dump_render",
                "kpoke", "obj2"} & set(d)
    if host == "fill":
        if tri_keys:
            raise ProbeError(f"{name}: {sorted(tri_keys)} need host = \"tri\"")
        return {}
    if host != "tri":
        raise ProbeError(f"{name}: unknown host {host!r}")
    slot, slots = d.get("slot", ""), dict(d.get("slots", {}))
    if slot not in TRI_SLOTS:
        raise ProbeError(f"{name}: slot {slot!r} is not one of {TRI_SLOTS}")
    if slot in slots or not set(slots) <= set(TRI_SLOTS):
        raise ProbeError(f"{name}: bad helper slots {sorted(slots)}")
    if d.get("coords") or "isa" in d or "use" in d:
        raise ProbeError(f"{name}: coords, isa and use are not for host = \"tri\"")
    size = tuple(d.get("size", TRI_SIZE))
    max_size = tuple(d["max_size"]) if "max_size" in d else None
    top = max_size or size
    if (len(size) != 2 or len(top) != 2 or any(v <= 0 or v % 2 for v in size) or
            any(v > TRI_MAX for v in top) or size[0] > top[0] or size[1] > top[1]):
        raise ProbeError(f"{name}: bad size {size} (max {top})")
    vertices = d.get("vertices", 0)
    if "vertices" in d and (vertices <= 0 or vertices % 3 or vertices > TRI_MAX_VERTICES):
        raise ProbeError(f"{name}: vertices {vertices} is not 3 to {TRI_MAX_VERTICES}, "
                         "whole triangles")
    vtx_coords = d.get("vtx_coords", 0)
    if "vtx_coords" in d and not 1 <= vtx_coords <= 11:
        raise ProbeError(f"{name}: vtx_coords {vtx_coords} is not 1 to 11")
    copy_depth = bool(d.get("copy_depth", False))
    if copy_depth and not vertices:
        raise ProbeError(f"{name}: copy_depth needs vertices (the copies)")
    try:
        blk = {int(k): int(v) for k, v in d.get("blk", {}).items()}
    except ValueError:
        raise ProbeError(f"{name}: blk {d.get('blk')} is not {{ word = value }}") from None
    if any(not 0 <= k < TRI_BLOCK_WORDS or not 0 <= v <= 0xffffffff for k, v in blk.items()):
        raise ProbeError(f"{name}: blk words 0-{TRI_BLOCK_WORDS - 1}, 32-bit values")
    try:
        cmd = {int(k): int(v) for k, v in d.get("cmd", {}).items()}
    except ValueError:
        raise ProbeError(f"{name}: cmd {d.get('cmd')} is not {{ word = value }}") from None
    if any(not 0 <= k < TRI_CMD_WORDS or not 0 <= v <= 0xffffffff for k, v in cmd.items()):
        raise ProbeError(f"{name}: cmd words 0-{TRI_CMD_WORDS - 1}, 32-bit values")
    vdm, vdm_xor = {}, {}
    for key, out in (("vdm", vdm), ("vdm_xor", vdm_xor)):
        try:
            out.update({int(k): int(v) for k, v in d.get(key, {}).items()})
        except ValueError:
            raise ProbeError(f"{name}: {key} {d.get(key)} is not {{ word = value }}") from None
        if any(not 0 <= k < TRI_VDM_WORDS or not 0 <= v <= 0xffffffff for k, v in out.items()):
            raise ProbeError(f"{name}: {key} words 0-{TRI_VDM_WORDS - 1}, 32-bit values")
    kpoke = d.get("kpoke", [])
    if not isinstance(kpoke, list) or any(
            not isinstance(k, str) or not re.fullmatch(r"(ta|rd|tq):\d+\^?=(0x[0-9a-fA-F]+|\d+)", k)
            for k in kpoke):
        raise ProbeError(f"{name}: kpoke {kpoke}: a list of ta:N=V, rd:N^=V, tq:N=V")
    sideband = d.get("sideband")
    if sideband is not None and ("eot" not in (slot, *slots) or
                                 not 0 <= sideband <= 0xffffffff):
        raise ProbeError(f"{name}: sideband {sideband} needs an eot slot and a 32-bit value")
    isp2 = d.get("isp2")
    if isp2 is not None and not 0 <= isp2 <= 0xffffffff:
        raise ProbeError(f"{name}: isp2 {isp2} is not a 32-bit value")
    blk_add = {}
    for k, v in d.get("blk_add", {}).items():
        words = tuple(v) if isinstance(v, list) else (v,)
        if (not k.isdigit() or int(k) not in TRI_ADD_WORDS or len(words) != TRI_ADD_WORDS[int(k)]
                or any(not isinstance(w, int) or not 0 <= w <= 0xffffffff for w in words)):
            raise ProbeError(f"{name}: blk_add {{ BIT = V }} for bits 2-5, {{ 7 = [V, V] }}")
        blk_add[int(k)] = words
    obj2 = {}
    if "obj2" in d:
        o = d["obj2"]
        try:
            first = int(o["first"])
            o2blk = {int(k): int(v) for k, v in o.get("blk", {}).items()}
        except (KeyError, TypeError, ValueError):
            raise ProbeError(f"{name}: obj2 {o} is not {{ first = N, blk = {{ W = V }}, "
                             "pixel = FILE }") from None
        if (set(o) - {"first", "blk", "pixel"} or first <= 0 or first % 3 or first >= vertices
                or any(not 0 <= k < TRI_BLK2_WORDS or not 0 <= v <= 0xffffffff
                       for k, v in o2blk.items())
                or not isinstance(o.get("pixel", ""), str)):
            raise ProbeError(f"{name}: obj2 {o}: first a triangle's vertex among the copies, "
                             f"blk words 0-{TRI_BLK2_WORDS - 1}, pixel a file")
        obj2 = {"first": first, "blk": o2blk, **({"pixel": o["pixel"]} if "pixel" in o else {})}
    return {"host": "tri", "slot": slot, "slots": slots, "size": size, "max_size": max_size,
            "vertices": vertices, "vtx_coords": vtx_coords, "copy_depth": copy_depth,
            "blk": blk, "cmd": cmd, "vdm": vdm, "vdm_xor": vdm_xor, "sideband": sideband,
            "isp2": isp2, "blk_add": blk_add, "dump_render": bool(d.get("dump_render", False)),
            "kpoke": kpoke, "obj2": obj2,
            "isa": "pds" if slot in TRI_PDS else "usse"}


def load(path: pathlib.Path | None = None) -> list[Probe]:
    """The probes of one table, or of every table under probes/."""
    paths = [path] if path else sorted(PROBES.glob("*/*.toml"))
    return [_probe(d, p.name) for p in paths
            for d in tomllib.loads(p.read_text()).get("probe", [])]


# What a case of a probe with case_set may set besides the probe's: pokes and kpoke are added, the
# words of cmd, blk, vdm and vdm_xor replace the probe's.
POKE_WORDS = {"xfer": 42, "bg": 17}      # sgxfive_xfer.h: the words of each poked object
CASE_SET_KEYS = {"pokes", "kpoke", "cmd", "blk", "vdm", "vdm_xor"}


def _probe(d: dict, table: str) -> Probe:
    if d.get("low") and d.get("host", "fill") != "fill":
        raise ProbeError(f"{d['name']}: low is a fill probe's")
    late = d.get("late", "")
    if late and (d.get("host", "fill") != "fill" or
                 not re.fullmatch(r"\d+:\d+=(0x[0-9a-fA-F]+|\d+)", late)):
        raise ProbeError(f"{d['name']}: late {late!r}: a fill probe's R:K=V")
    pokes = d.get("pokes", [])
    if any(not re.fullmatch(r"(xfer|bg):\d+\^?=(0x[0-9a-fA-F]+|\d+)", k) for k in pokes):
        raise ProbeError(f"{d['name']}: pokes {pokes}: only xfer:N or bg:N, =V or ^=V")
    for k in pokes:
        obj, idx = k.split(":")[0], int(re.match(r"\w+:(\d+)", k).group(1))
        if idx >= POKE_WORDS[obj]:
            raise ProbeError(f"{d['name']}: poke {k}: {obj}:0-{POKE_WORDS[obj] - 1}")
    case_set = d.get("case_set", [])
    if case_set and (len(case_set) != len(d["cases"]) or any(
            not isinstance(c, dict) or set(c) - CASE_SET_KEYS for c in case_set)):
        raise ProbeError(f"{d['name']}: case_set: one table per case, with only "
                         f"{sorted(CASE_SET_KEYS)}")
    p = Probe(name=d["name"], question=d["question"], source=d["source"],
              params=d.get("params", {}), inputs=d.get("inputs", []),
              cases=d["cases"], hypotheses=d.get("hypotheses", {}),
              temps=d.get("temps", 32), labels=d.get("labels", []),
              coords=d.get("coords", False), pixels=d.get("pixels", False),
              table=table, pokes=pokes, case_set=case_set, raw=d, low=d.get("low", 0),
              late=late, **{"isa": d.get("isa", "usse"), "use": d.get("use", USE_DUMP),
                            **_tri_fields(d)})
    for i in range(len(case_set)):
        _view(p, i)                         # a case's words are checked as the probe's are
    return p


def _view(p: Probe, i: int) -> Probe:
    """Case i of a probe with case_set, as a probe of its own (its files keep index i)."""
    d = {k: v for k, v in p.raw.items() if k != "case_set"}
    for k, v in p.case_set[i].items():
        d[k] = d.get(k, []) + v if k in ("pokes", "kpoke") else {**d.get(k, {}), **v}
    return dataclasses.replace(_probe({**d, "cases": [p.cases[i]]}, p.table), first=i)


def _fmt(v) -> str:
    if isinstance(v, int):
        return f"0x{v & 0xffffffff:08X}"
    return str(v)


def render(p: Probe, case: list, template: str) -> str:
    """The program text of one case: params, then the case's inputs, substituted."""
    if len(case) != len(p.inputs):
        raise ProbeError(f"{p.name}: case {case} does not give {p.inputs}")
    values = {k: str(v) for k, v in p.params.items()}
    values.update({k: _fmt(v) for k, v in zip(p.inputs, case)})

    def sub(m):
        if m.group(1) not in values:
            raise ProbeError(f"{p.name}: no value for {{{m.group(1)}}}")
        return values[m.group(1)]

    # params may themselves name inputs ({OP} = "... #{A}"): substitute twice
    return PLACEHOLDER_RE.sub(sub, PLACEHOLDER_RE.sub(sub, template))


def _assemble(text: str, out: pathlib.Path, isa: str = "usse") -> str:
    """Assemble text to out; the listing."""
    tool = PDS_ASM if isa == "pds" else ASM
    if not tool.exists():
        subprocess.run(["make", "-s", "-C", str(HERE)], check=True)
    r = subprocess.run([str(tool), "-l", "-o", str(out), "-"], input=text, capture_output=True,
                       text=True)
    if r.returncode:
        raise ProbeError(f"{out.name}: {r.stderr.strip()}\n{text}")
    return r.stdout


def build(p: Probe, outdir: pathlib.Path, src_dir: pathlib.Path = PROBES_DIR) -> list:
    """Assemble every case of p into outdir/<name>__<i>.bin."""
    outdir.mkdir(parents=True, exist_ok=True)
    template = (src_dir / p.source).read_text()
    files = []
    for i, case in enumerate(p.cases, p.first):
        f = outdir / f"{p.name}__{i}.bin"
        _assemble(render(p, case, template), f, p.isa)
        files.append(f)
    return files


def build_use(outdir: pathlib.Path, use: str = USE_DUMP,
              src_dir: pathlib.Path = PROBES_DIR, isa: str = "usse") -> pathlib.Path:
    """Assemble a PDS probe's USE program (sa_dump.s by default), or a tri probe's helper,
    into outdir/<name>.bin."""
    outdir.mkdir(parents=True, exist_ok=True)
    f = outdir / (pathlib.Path(use).stem + ".bin")
    _assemble((src_dir / use).read_text(), f, isa)
    return f


def _helpers(p: Probe) -> list:
    """The fixed programs a probe runs with: [(source, isa)]."""
    if p.host == "tri":
        return [(src, "pds" if slot in TRI_PDS else "usse") for slot, src in p.slots.items()] + \
            ([(p.obj2["pixel"], "usse")] if "pixel" in p.obj2 else [])
    return [(p.use, "usse")] if p.isa == "pds" else []


def build_helpers(ps: list, outdir: pathlib.Path, src_dir: pathlib.Path = PROBES_DIR) -> list:
    """Assemble the fixed programs of the probes ps into outdir, each once."""
    out: dict = {}
    for p in ps:
        for src, isa in _helpers(p):
            if src not in out:
                out[src] = build_use(outdir, src, src_dir, isa)
    return list(out.values())


_PDS_DATA: dict = {}


def _data_dwords(text: str) -> int:
    """The data dwords of a PDS program's text, as pds-asm lists them."""
    with tempfile.TemporaryDirectory() as d:
        listing = _assemble(text, pathlib.Path(d) / "x.bin", "pds")
    return sum(1 for ln in listing.splitlines() if ln.endswith("\tdata"))


def pds_data(p: Probe, src_dir: pathlib.Path = PROBES_DIR) -> int:
    """The data dwords of a PDS probe's program (its cases share the template's layout)."""
    key = (src_dir, p.source, p.name)
    if key not in _PDS_DATA:
        _PDS_DATA[key] = _data_dwords(render(p, p.cases[0], (src_dir / p.source).read_text()))
    return _PDS_DATA[key]


_LINE = re.compile(r"^probe (\S+): (.*)$")
_ROW = re.compile(r"^row (\d+): ([0-9a-f ]+)$")


def parse(text: str) -> dict:
    """sgxfive-test probe output -> {file label: Obs}."""
    acc: dict = {}
    for line in text.splitlines():
        m = _LINE.match(line)
        if not m:
            continue
        label, rest = m.groups()
        o = acc.setdefault(label, {"o0": None, "mixed": (), "failed": None, "scratch": [],
                                   "rows": {}})
        row = _ROW.match(rest)
        if row:
            o["rows"][int(row.group(1))] = tuple(int(v, 16) for v in row.group(2).split())
        elif rest.startswith("failed: "):
            o["failed"] = rest[len("failed: "):]
        elif rest.startswith("o0 mixed"):
            o["mixed"] = tuple((int(v, 16), int(c)) for v, c in
                               re.findall(r"(0x[0-9a-f]+) x(\d+)", rest))
        elif rest.startswith("o0 "):
            o["o0"] = int(rest.split()[1], 16)
        elif rest.startswith("scratch +"):
            off, val = rest[len("scratch +"):].split()
            o["scratch"].append((int(off, 16), int(val, 16)))
    def pixels(rows):
        if not rows:
            return None
        return tuple(x for y in sorted(rows) for x in rows[y])

    return {k: Obs(o0=v["o0"], mixed=v["mixed"], failed=v["failed"],
                   scratch=tuple(v["scratch"]), pixels=pixels(v["rows"]))
            for k, v in acc.items()}


def _near(want: dict, got: int) -> bool:
    """Is the binary32 value of got within the larger of want["ulp"] units in the last place
    of want["near"] (that of the smallest normal for a denormal or zero) and want["abs"]?"""
    x = struct.unpack("<f", struct.pack("<I", got & 0xffffffff))[0]
    if not math.isfinite(x):
        return False
    w = float(want["near"])
    ulp = 2.0 ** (max(math.frexp(w)[1] - 1 if w else -126, -126) - 23)
    return abs(x - w) <= max(want.get("ulp", 0) * ulp, want.get("abs", 0.0))


def _dword(want, got: int) -> bool:
    return _near(want, got) if isinstance(want, dict) else got == want & 0xffffffff


def quad_pixels(quad: list) -> list:
    """Every pixel of a "quad" expectation: coords.s gives pixel q the marks
    (0x45000000 + k * 0x06000000) | q << 12; the pixel at quad position j (TL, TR, BL, BR:
    even/odd x, even/odd y) is expected to hold mark quad[j][0] of the pixel at position
    quad[j][1] of its own 2x2 quad."""
    out = []
    for p in range(2048):
        x, y = p % 64, p // 64
        k, n = quad[(x & 1) + 2 * (y & 1)]
        q = ((y & ~1) + n // 2) * 64 + (x & ~1) + n % 2
        out.append((0x45000000 + k * 0x06000000) | q << 12)
    return out


def matches(expect, obs: Obs) -> bool:
    """Does obs agree with one expected readback: an int (o0), "fail" (the job failed), a
    list (the first scratch dwords, in order: what dump.s stores; an element may instead be a
    tolerance, {near = x, ulp = n, abs = e}) or a table with an "o0", "o0_not" (anything
    else), "near" (o0 within the tolerance its "ulp"/"abs" give), "most" (the value of at
    least 90% of the pixels), "pixels" (every pixel, in raster order; needs the probe's pixels
    flag), "quad" (every pixel, as quad_pixels gives it), a "scratch" ({offset: value},
    the exact set of changes) and/or "dwords" (the list form). A table with fail = true wants
    a job that failed, with only its "dwords" and "scratch" checked: what ran before the
    failure stored there."""
    if expect == "fail":
        return obs.failed is not None
    if isinstance(expect, dict) and expect.get("fail"):
        if obs.failed is None:
            return False
        return matches({k: v for k, v in expect.items() if k in ("dwords", "scratch")},
                       dataclasses.replace(obs, failed=None))
    if obs.failed is not None:
        return False
    if isinstance(expect, int):
        return obs.o0 == expect & 0xffffffff
    if isinstance(expect, list):
        got = dict(obs.scratch)
        return all(_dword(v, got.get(4 * i, SCRATCH_FILL | i)) for i, v in enumerate(expect))
    if "dwords" in expect and not matches(expect["dwords"], obs):
        return False
    if "o0" in expect and obs.o0 != expect["o0"] & 0xffffffff:
        return False
    if "near" in expect and (obs.o0 is None or not _near(expect, obs.o0)):
        return False
    if "most" in expect:
        top = obs.o0 if obs.o0 is not None else \
            (obs.mixed[0][0] if obs.mixed and obs.mixed[0][1] * 10 >= 2048 * 9 else None)
        if top != expect["most"] & 0xffffffff:
            return False
    if "pixels" in expect and (obs.pixels is None or
                               list(obs.pixels) != [v & 0xffffffff for v in expect["pixels"]]):
        return False
    if "quad" in expect and (obs.pixels is None or
                             list(obs.pixels) != quad_pixels(expect["quad"])):
        return False
    if "o0_not" in expect and (obs.o0 is None or obs.o0 == expect["o0_not"] & 0xffffffff):
        return False
    if "scratch" in expect:
        want = {int(k, 0): v & 0xffffffff for k, v in expect["scratch"].items()}
        if dict(obs.scratch) != want:
            return False
    return True


def describe(obs: Obs) -> str:
    if obs.failed is not None:
        s = f"failed ({obs.failed})"
    elif obs.o0 is not None:
        s = f"0x{obs.o0:08x}"
    else:
        s = "mixed " + " ".join(f"0x{v:08x}x{c}" for v, c in obs.mixed)
    if obs.scratch:
        s += " scratch " + " ".join(f"+0x{o:03x}=0x{v:08x}" for o, v in obs.scratch)
    return s


def verdict(p: Probe, obs: list) -> Verdict:
    lines = []
    for i, (case, o) in enumerate(zip(p.cases, obs)):
        label = p.labels[i] if i < len(p.labels) else \
            ", ".join(f"{k}={_fmt(v)}" for k, v in zip(p.inputs, case))
        lines.append(f"  [{i}] {label}: {describe(o)}")
    consistent = [h for h, exp in p.hypotheses.items()
                  if all(matches(e, o) for e, o in zip(exp, obs))]
    if not p.hypotheses:
        head = "recorded (no hypotheses)"
    elif len(consistent) == 1:
        head = f"SETTLED: {consistent[0]}"
    elif not consistent:
        head = "NONE of the hypotheses fits"
    else:
        head = "UNDECIDED between " + ", ".join(consistent)
    text = f"{p.name}: {head}\n  question: {p.question}\n" + "\n".join(lines)
    return Verdict(consistent=consistent, settled=consistent[0] if len(consistent) == 1
                   else None, text=text)


def report(table: list, out: str) -> str:
    obs = parse(out)
    per_case = dict(counters.cases(out))
    texts = []
    for p in table:
        got = [obs.get(f"{p.name}__{i}") for i in range(len(p.cases))]
        if any(g is None for g in got):
            texts.append(f"{p.name}: not run")
            continue
        text = verdict(p, got).text
        hot = [f"[{i}] {s}" for i in range(len(p.cases))
               if (s := counters.summary(per_case.get(f"{p.name}__{i}", "")))]
        if hot:
            text += "\n  counters: " + "; ".join(hot)
        texts.append(text)
    return "\n\n".join(texts) + "\n"


def tool_args(p: Probe, use: str | None = None, src_dir: pathlib.Path | None = None) -> list:
    """The options of `sgxfive-test probe` a probe runs with; `use` is where a PDS probe's
    USE program (build_use) is, by default its file name; `src_dir` holds its templates."""
    head = ["--temps", str(p.temps)] + (["--coords"] if p.coords else []) + \
        (["--pixels"] if p.pixels else [])
    if p.host == "tri":
        return head + _tri_args(p, src_dir)
    use = use or pathlib.Path(p.use).stem + ".bin"
    pds = ["--pds", str(pds_data(p, src_dir or PROBES_DIR)), "--use", use] if p.isa == "pds" else []
    low = ["--low", hex(p.low)] if p.low else []
    low += ["--late", p.late] if p.late else []
    return head + pds + low + [a for k in p.pokes for a in ("--poke", k)]


def _tri_args(p: Probe, src_dir: pathlib.Path | None = None) -> list:
    """The --tri options: the case slot (with its data dwords), the size, the helpers."""
    slot = f"{p.slot}:{pds_data(p, src_dir or PROBES_DIR)}" if p.slot in TRI_PDS else p.slot
    args = ["--tri", slot, "--width", str(p.size[0]), "--height", str(p.size[1])]
    if p.max_size:
        args += ["--max-width", str(p.max_size[0]), "--max-height", str(p.max_size[1])]
    if p.vertices:
        args += ["--vertices", str(p.vertices)]
    if p.vtx_coords:
        args += ["--vtx-coords", str(p.vtx_coords)]
    if p.copy_depth:
        args += ["--copy-depth"]
    for k, v in sorted(p.blk.items()):
        args += ["--blk", f"{k}=0x{v:08x}"]
    for k, v in sorted(p.cmd.items()):
        args += ["--cmd", f"{k}=0x{v:08x}"]
    for k, v in sorted(p.vdm.items()):
        args += ["--vdm", f"{k}=0x{v:08x}"]
    for k, v in sorted(p.vdm_xor.items()):
        args += ["--vdm", f"{k}^=0x{v:08x}"]
    if p.dump_render:
        args += ["--dump-render", DUMPS]
    for k in p.kpoke:
        args += ["--kpoke", k]
    if p.sideband is not None:
        args += ["--sideband", f"0x{p.sideband:08x}"]
    if p.isp2 is not None:
        args += ["--isp2", f"0x{p.isp2:08x}"]
    for k, words in sorted(p.blk_add.items()):
        args += ["--blk-add", f"{k}=" + ",".join(f"0x{w:08x}" for w in words)]
    if p.obj2:
        args += ["--obj2", str(p.obj2["first"])]
        for k, v in sorted(p.obj2["blk"].items()):
            args += ["--obj2-blk", f"{k}=0x{v:08x}"]
        if "pixel" in p.obj2:
            args += ["--obj2-pixel", pathlib.Path(p.obj2["pixel"]).stem + ".bin"]
    for name, src in p.slots.items():
        f = pathlib.Path(src).stem + ".bin"
        if name in TRI_PDS:
            f += f":{_data_dwords(((src_dir or PROBES_DIR) / src).read_text())}"
        args += ["--slot", f"{name}={f}"]
    return args


def _with_use(args: tuple, where: str) -> list:
    """A group's options with the helpers' files (--use, --slot) under `where`."""
    out = []
    for i, a in enumerate(args):
        prev = args[i - 1] if i else ""
        if prev in ("--use", "--dump-render", "--obj2-pixel"):
            a = f"{where}/{a}"
        elif prev == "--slot":
            name, f = a.split("=", 1)
            a = f"{name}={where}/{f}"
        out.append(a)
    return out


def _groups(table: list, src_dir: pathlib.Path | None = None) -> dict:
    by: dict = {}
    for p in table:
        # a probe with words of its own per case (case_set) runs each case as a probe of its
        # own (file index kept)
        views = [_view(p, i) for i in range(len(p.cases))] if p.case_set else [p]
        for v in views:
            by.setdefault(tuple(tool_args(v, src_dir=src_dir)), []).append(v)
    return by


def run_local(table: list, tool: list, work: pathlib.Path,
              src_dir: pathlib.Path = PROBES_DIR) -> str:
    """Build and run with a local sgxfive-test (tool: its argv prefix, e.g. with --mock)."""
    out = []
    (work / DUMPS).mkdir(parents=True, exist_ok=True)
    for args, ps in _groups(table, src_dir).items():
        if build_helpers(ps, work, src_dir) or any(p.dump_render for p in ps):
            args = _with_use(args, str(work))
        # one process per case: the kernel bans a file after its faults (recovery), and a
        # probe may fault on purpose
        for f in (f for p in ps for f in build(p, work, src_dir)):
            r = subprocess.run([*tool, "probe", *args, str(f)],
                               capture_output=True, text=True, timeout=600)
            if r.returncode:
                raise ProbeError(f"sgxfive-test failed ({r.returncode}): {r.stderr}")
            out.append(r.stdout)
    return "".join(out)


def save_dumps(work: pathlib.Path, out: pathlib.Path) -> None:
    """Keep the render dumps the dump_render probes left (work/DUMPS) with the run."""
    if (work / DUMPS).is_dir():
        shutil.copytree(work / DUMPS, out / DUMPS, dirs_exist_ok=True)


def save_bins(work: pathlib.Path, out: pathlib.Path) -> None:
    """Keep the assembled cases with the run (out/bins), so its vectors are "recorded"."""
    (out / "bins").mkdir(parents=True, exist_ok=True)
    for f in sorted(work.glob("*.bin")):
        shutil.copyfile(f, out / "bins" / f.name)


def _local_env() -> dict:
    env = {}
    if LOCAL_ENV.exists():
        for line in LOCAL_ENV.read_text().splitlines():
            m = re.match(r'^(\w+)=\$\{\w+:-"?(.*?)"?\}$', line.strip())
            if m:
                env[m.group(1)] = m.group(2)
    return env


def target() -> tuple:
    env = _local_env()
    host = os.environ.get("SGX_TARGET_HOST", env.get("SGX_TARGET_HOST"))
    opts = os.environ.get("SGX_TARGET_SSH_OPTS", env.get("SGX_TARGET_SSH_OPTS", ""))
    if not host:
        raise ProbeError("set SGX_TARGET_HOST (or tools/bringup/local.env)")
    return host, shlex.split(opts)


def run_remote(table: list, work: pathlib.Path, src_dir: pathlib.Path = PROBES_DIR) -> str:
    host, opts = target()
    tool = os.environ.get("SGX_PROBE_TOOL", "./sgxfive-test")
    rdir = "sgxprobes"
    run = f"{tool} probe"
    mark = ""
    if os.environ.get("SGX_PROBE_COUNTERS", "1") != "0":
        rt = os.environ.get("SGX_PROBE_TIMELINE", "./regtimeline")
        run = "sudo -n " + shlex.join(counters.wrap([tool, "probe"], rt))
        mark = 'echo "probe-case $(basename $f .bin)"; '
    dumps = any(p.dump_render for p in table)
    if (dumps or any(p.kpoke for p in table)) and not run.startswith("sudo "):
        run = "sudo -n " + run          # debugfs: the render dumps and kpoke are root's
    out = []
    subprocess.run(["ssh", *opts, host, f"rm -rf {rdir} && mkdir -p {rdir}/{DUMPS}"],
                   check=True)
    for args, ps in _groups(table, src_dir).items():
        files = [f for p in ps for f in build(p, work, src_dir)]
        names = " ".join(f"{rdir}/{f.name}" for f in files)
        helpers = build_helpers(ps, work, src_dir)
        if helpers:
            files += helpers
        if helpers or dumps:
            args = _with_use(args, rdir)
        subprocess.run(["scp", "-q", *opts, *map(str, files), f"{host}:{rdir}/"], check=True)
        # one process per case (see run_local)
        r = subprocess.run(["ssh", *opts, host, f"for f in {names}; do {mark}"
                            f"{run} {' '.join(args)} $f || exit 1; done"],
                           capture_output=True, text=True, timeout=3600)
        if r.returncode:
            raise ProbeError(f"sgxfive-test failed ({r.returncode}): {r.stderr}")
        out.append(r.stdout)
    if dumps:
        subprocess.run(["scp", "-q", "-r", *opts, f"{host}:{rdir}/{DUMPS}", str(work)],
                       check=True)
    return "".join(out)


def _select(table: list, names: list) -> list:
    if not names:
        return table
    sel = [p for p in table if p.name in names or any(
        n.endswith("*") and p.name.startswith(n[:-1]) for n in names)]
    if not sel:
        raise ProbeError(f"no probe named {names}")
    return sel


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--table", required=True,
                    help="the probe table, probes/<unit>/<feature>.toml")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    b = sub.add_parser("build")
    b.add_argument("dir")
    b.add_argument("names", nargs="*")
    r = sub.add_parser("run")
    r.add_argument("--out", default=None,
                   help="directory for raw.txt, report.txt and bins/ (the cases sent)")
    r.add_argument("names", nargs="*")
    lo = sub.add_parser("local")
    lo.add_argument("--tool", default=str(ROOT / "userspace/libsgxfive/build/sgxfive-test"))
    lo.add_argument("--mock", action="store_true")
    lo.add_argument("names", nargs="*")
    e = sub.add_parser("eval")
    e.add_argument("raw")
    e.add_argument("names", nargs="*")
    a = ap.parse_args(argv)
    try:
        table = load(pathlib.Path(a.table))
        src = pathlib.Path(a.table).parent / "templates"
        if a.cmd == "list":
            for p in table:
                print(f"{p.name:24} {len(p.cases):3} cases  {p.question}")
            return 0
        sel = _select(table, a.names)
        if a.cmd == "build":
            for p in sel:
                build(p, pathlib.Path(a.dir), src)
            return 0
        if a.cmd == "eval":
            print(report(sel, pathlib.Path(a.raw).read_text()), end="")
            return 0
        with tempfile.TemporaryDirectory() as d:
            if a.cmd == "local":
                out = run_local(sel, [a.tool] + (["--mock"] if a.mock else []),
                                pathlib.Path(d), src)
            else:
                out = run_remote(sel, pathlib.Path(d), src)
            rep = report(sel, out)
            if a.cmd == "run" and a.out:
                o = pathlib.Path(a.out)
                o.mkdir(parents=True, exist_ok=True)
                (o / "raw.txt").write_text(out)
                (o / "report.txt").write_text(rep)
                save_bins(pathlib.Path(d), o)
                save_dumps(pathlib.Path(d), o)
        print(rep, end="")
        return 0
    except ProbeError as err:
        print(f"probe.py: {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
