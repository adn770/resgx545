#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Instruction vectors from probe readbacks.

Each case `sgxfive-test probe` ran becomes one vector: the program words, the task's initial
state, the readback and where it all came from. Programs are the bytes saved with the run
(`--bins DIR` of `<probe>__<case>.bin`, "recorded") or assembled again from the current probe
tables ("rebuilt"). The tables are probes/<unit>/<feature>.toml with their templates beside
them; a campaign run of one (DATA/<unit>/<feature>/<probe>/raw.txt) finds its own.

    vectors.py convert RAW... -o OUTDIR [--root DIR] [--bins DIR]
    vectors.py check FILE...
    vectors.py jobs VEC... --data DIR

A fill's vector carries the job it ran in (init.job): the transfer command's pokes as the run
printed them, and the USE filter coefficients they load (use_coeffs). `jobs` writes the same for
vector files converted before vectors carried it, as a sidecar under DIR/vectors/jobs/.

convert writes OUTDIR/<run>.vec.json per raw file; <run> is the raw file's directory relative
to --root (default: the current directory), with "/" turned into "_".
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import pathlib
import re
import struct
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import probe  # noqa: E402

FORMAT = "sgx545-vectors"
PDS_ATTRS = 16             # sa0-sa15: what a PDS probe may write (sgxfive-test PROBE_PDS_ATTRS)
VERSION = 1
INSTANCES = 2048                # the 64 x 32 fill
SCRATCH_BYTES = 0x10000
_SCRATCH_AT = re.compile(r"^probe (\S+): scratch at (0x[0-9a-f]+)")
_SCRATCH_LOW = re.compile(r"^probe (\S+): scratch also at (0x[0-9a-f]+)")
_PRESET = re.compile(r"^mov(?:\.\w+)*\s+(r\d+),\s+#(0x[0-9A-Fa-f]+|\d+)\s*$")
_HEX = re.compile(r"^0x[0-9a-f]+$")
_POKES = re.compile(r"^probe (\S+): pokes (.*)$")
_POKE = re.compile(r"^(xfer|bg):(\d+)(\^?)=(0x[0-9a-fA-F]+|\d+)$")
JOBS_FORMAT = "sgx545-vector-jobs"
_ISA_DIGITS = {"usse": 16, "pds": 8}


def _h32(v: int) -> str:
    return f"0x{v & 0xffffffff:08x}"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _words(data: bytes, isa: str) -> list[int]:
    width = 4 if isa == "pds" else 8
    return list(struct.unpack(f"<{len(data) // width}{'I' if width == 4 else 'Q'}", data))


def assemble_words(p: probe.Probe, i: int, text: str) -> list[int]:
    """The case's program, assembled with usse-asm (64-bit words) or pds-asm (32-bit)."""
    with tempfile.TemporaryDirectory() as d:
        out = pathlib.Path(d) / "case.bin"
        probe._assemble(text, out, p.isa)
        data = out.read_bytes()
    return _words(data, p.isa)


def use_words(bins: pathlib.Path | None, use: str = probe.USE_DUMP,
              dirs: list | None = None) -> tuple[list[int], str]:
    """A PDS probe's USE program: as sent (bins/<name>.bin) or assembled again."""
    rec = bins / (pathlib.Path(use).stem + ".bin") if bins else None
    if rec and rec.exists():
        return _words(rec.read_bytes(), "usse"), "recorded"
    with tempfile.TemporaryDirectory() as d:
        src = next((pathlib.Path(x) for x in dirs or template_dirs()
                    if (pathlib.Path(x) / use).is_file()),
                   probe.PROBES_DIR)
        return _words(probe.build_use(pathlib.Path(d), use, src).read_bytes(), "usse"), "rebuilt"


def presets(text: str) -> dict[str, str]:
    """Registers the program sets with immediates before its first other instruction."""
    regs: dict[str, str] = {}
    for line in text.splitlines():
        line = line.split(";")[0].strip()
        if not line or line.startswith("phas"):
            continue
        m = _PRESET.match(line)
        if not m:
            break
        regs[m.group(1)] = _h32(int(m.group(2), 0))
    return regs


def template_dirs(probes: pathlib.Path = probe.PROBES) -> list:
    """Every table's template directory, in the order of the units."""
    return sorted(probes.glob("*/templates"))


def tables_for(raw: pathlib.Path, base: list,
               probes: pathlib.Path = probe.PROBES) -> tuple[list, list]:
    """The probes a run used: its own table next to its directory (<dir>.toml) first, else the
    table of its unit and feature (DATA/<unit>/<feature>/<probe>/raw.txt), then the repo's;
    and the directories its templates are looked up in."""
    own = raw.parent.with_suffix(".toml")
    if own.is_file():
        mine, first = probe.load(own), [own.parent]
    else:
        table = probes / raw.parts[-4] / f"{raw.parts[-3]}.toml" if len(raw.parts) > 4 else None
        mine, first = (probe.load(table), [table.parent / "templates"]) \
            if table and table.is_file() else ([], [])
    names = {p.name for p in mine}
    return mine + [p for p in base if p.name not in names], first + template_dirs(probes)


def template_dir(p: probe.Probe, dirs: list) -> pathlib.Path:
    for d in dirs:
        if (pathlib.Path(d) / p.source).is_file():
            return pathlib.Path(d)
    raise probe.ProbeError(f"{p.name}: no template {p.source}")


def template_text(p: probe.Probe, dirs: list) -> str:
    return (template_dir(p, dirs) / p.source).read_text()


def _found(p: probe.Probe, dirs: list | None) -> pathlib.Path | None:
    """The directory a probe's template is in, None when it is not on disk (given as text)."""
    try:
        return template_dir(p, dirs or template_dirs())
    except probe.ProbeError:
        return None


def _readback(o: probe.Obs) -> dict:
    return {"failed": o.failed,
            "o0": None if o.o0 is None else _h32(o.o0),
            "mixed": [[_h32(v), c] for v, c in o.mixed],
            "scratch": {f"0x{off:03x}": _h32(v) for off, v in o.scratch},
            "pixels": None if o.pixels is None else [_h32(v) for v in o.pixels]}


def use_coeffs(pokes: list) -> dict:
    """The USE filter coefficients a fill's job loads (E078): the transfer command starts
    zeroed (sgxfive_transfer_cmd) and the pokes set (=) or flip (^=) its words; the firmware
    loads CR_USE_COEFFS_MODE from word 32 and the three groups from words 33-41 only when
    load_flags (word 17) has bit 2 (transfer.md 3.2). Without it nothing is loaded."""
    xfer = [0] * probe.POKE_WORDS["xfer"]
    for k in pokes:
        m = _POKE.match(k)
        if m and m.group(1) == "xfer":
            i, v = int(m.group(2)), int(m.group(4), 0)
            xfer[i] = xfer[i] ^ v if m.group(3) else v
    if not xfer[17] & 4:
        return {"load": False}
    return {"load": True, "mode": _h32(xfer[32]), "words": [_h32(w) for w in xfer[33:42]]}


def job(pokes: list) -> dict:
    """init.job: the pokes a fill ran with and the coefficients they load."""
    return {"pokes": list(pokes), "use_coeffs": use_coeffs(pokes)}


def case_probe(p: probe.Probe, i: int) -> probe.Probe:
    """Case i as it ran: with its case_set (pokes added, words replaced) where it has one."""
    return probe._view(p, i) if p.case_set else p


def _printed_pokes(raw: str) -> dict:
    return {m.group(1): m.group(2).split() for m in map(_POKES.match, raw.splitlines()) if m}


def jobs(raw: str, table: list) -> dict:
    """The job of every fill case of a run (label -> init.job): the pokes the run printed, or
    none where its table has none for the case. A case whose table has pokes but whose run
    printed none is left out: what it ran with is not known."""
    printed, obs, out = _printed_pokes(raw), probe.parse(raw), {}
    for p in table:
        if p.host != "fill":
            continue
        for i in range(len(p.cases)):
            label = f"{p.name}__{i}"
            if label in printed:
                out[label] = job(printed[label])
            elif label in obs and not case_probe(p, i).pokes:
                out[label] = job([])
    return out


def write_jobs(vec: pathlib.Path, data: pathlib.Path, table: list) -> pathlib.Path:
    """The sidecar of a vector file of the data repository `data`: its vectors/jobs/<the same
    path>.job.json, the jobs of its run (jobs()), found through the run's raw file."""
    batch = json.loads(pathlib.Path(vec).read_text())
    raw_rel = batch["run"]["raw"]
    raw_path = pathlib.Path(data) / raw_rel
    raw = raw_path.read_text()
    tbl, _ = tables_for(raw_path, table)
    rel = pathlib.Path(vec).resolve().relative_to((pathlib.Path(data) / "vectors").resolve())
    out = pathlib.Path(data) / "vectors" / "jobs" / rel.parent / \
        (rel.name.removesuffix(".vec.json") + ".job.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    side = {"format": JOBS_FORMAT, "version": VERSION,
            "run": {"raw": raw_rel, "raw_sha256": _sha(raw.encode()),
                    "tool": f"vectors.py {VERSION}"},
            "jobs": jobs(raw, tbl)}
    out.write_text(json.dumps(side, indent=1, sort_keys=True) + "\n")
    return out


def convert(raw: str, table: list, *, raw_name: str, templates: dict | None = None,
            words_for=assemble_words, bins: pathlib.Path | None = None,
            dirs: list | None = None) -> dict:
    """One batch from the text of a probe run: a vector per known case, in table order."""
    obs = probe.parse(raw)
    printed = _printed_pokes(raw)
    scratch_at = {m.group(1): m.group(2) for m in map(_SCRATCH_AT.match, raw.splitlines()) if m}
    scratch_low = {m.group(1): m.group(2) for m in map(_SCRATCH_LOW.match, raw.splitlines()) if m}
    by_label = {}
    for p in table:
        for i in range(len(p.cases)):
            by_label[f"{p.name}__{i}"] = (p, i)
    vecs = []
    for p in table:
        tmpl = (templates or {}).get(p.source)
        if tmpl is None:
            tmpl = template_text(p, dirs or template_dirs())
        for i, case in enumerate(p.cases):
            label = f"{p.name}__{i}"
            if label not in obs:
                continue
            text = probe.render(p, case, tmpl)
            rec = bins / f"{label}.bin" if bins else None
            if rec and rec.exists():
                words, source = _words(rec.read_bytes(), p.isa), "recorded"
            else:
                words, source = words_for(p, i, text), "rebuilt"
            digits = _ISA_DIGITS[p.isa]
            program = {"isa": p.isa, "entry": 0, "source": source,
                       "words": [f"0x{w:0{digits}x}" for w in words]}
            init = {"task": "pixel", "instances": INSTANCES, "temps": p.temps,
                    "pa0": "coords" if p.coords else "fill",
                    "scratch": {"base": scratch_at.get(label, "0x3e003000"),
                                "bytes": SCRATCH_BYTES, "fill": "0xd0000000|i"},
                    "regs": presets(text)}
            if label in scratch_low:
                init["scratch"]["low"] = scratch_low[label]
            cp = case_probe(p, i)
            # as jobs(): the pokes the run printed, none where the table has none; a case whose
            # table has pokes but whose run printed none carries no job (not known)
            if p.host == "fill" and (label in printed or not cp.pokes):
                init["job"] = job(printed.get(label, []))
            if p.isa == "pds":
                # the fill's PDS secondary: douta into sa0-sa15, which the fill's USE program
                # stores to scratch dwords 0-15; U0-U2 (data dwords 0-2) kick the secondary's
                program["data"] = probe.pds_data(p, template_dir(p, dirs or template_dirs()))
                uw, usrc = use_words(bins, p.use, dirs)
                init.update(task="pds-secondary", attrs=PDS_ATTRS, regs={},
                            use={"source": p.use, "recorded": usrc == "recorded",
                                 "words": [f"0x{w:016x}" for w in uw]})
            vecs.append({
                "id": label,
                "program": program,
                "init": init,
                "readback": _readback(obs[label]),
                "provenance": {"probe": p.name, "case": i, "table": p.table,
                               "template": p.source, "template_sha256": _sha(tmpl.encode()),
                               "inputs": {k: probe._fmt(v).lower() if isinstance(v, int)
                                          else v for k, v in zip(p.inputs, case)},
                               "params": dict(p.params),
                               "options": probe.tool_args(cp, src_dir=_found(p, dirs)),
                               "question": p.question},
            })
    orphans = [k for k in obs if k not in by_label]
    return {"format": FORMAT, "version": VERSION,
            "run": {"raw": raw_name, "raw_sha256": _sha(raw.encode()),
                    "converted": datetime.datetime.now().astimezone().isoformat(
                        timespec="seconds"),
                    "tool": f"vectors.py {VERSION}"},
            "vectors": vecs, "orphans": orphans}


def _hexstr(v, what: str, digits: int | None = None) -> None:
    if not isinstance(v, str) or not _HEX.match(v) or (digits and len(v) != digits + 2):
        raise ValueError(f"{what}: {v!r} is not a hex string")


def validate(batch: dict) -> None:
    if batch.get("format") != FORMAT:
        raise ValueError("not an sgx545-vectors file")
    if batch.get("version") != VERSION:
        raise ValueError(f"unknown version {batch.get('version')}")
    for v in batch.get("vectors", []):
        for key in ("id", "program", "init", "readback", "provenance"):
            if key not in v:
                raise ValueError(f"{v.get('id')}: no {key}")
        prog = v["program"]
        if prog.get("isa") not in _ISA_DIGITS:
            raise ValueError(f"{v['id']}: unknown isa {prog.get('isa')!r}")
        for w in prog["words"]:
            _hexstr(w, v["id"], _ISA_DIGITS[prog["isa"]])
        rb = v["readback"]
        if rb["o0"] is not None:
            _hexstr(rb["o0"], f"{v['id']} o0", 8)
        for off, val in rb["scratch"].items():
            _hexstr(off, f"{v['id']} scratch offset")
            _hexstr(val, f"{v['id']} scratch", 8)


def dump(path: pathlib.Path, batch: dict) -> None:
    validate(batch)
    pathlib.Path(path).write_text(json.dumps(batch, indent=1) + "\n")


def load(path: pathlib.Path) -> dict:
    batch = json.loads(pathlib.Path(path).read_text())
    validate(batch)
    return batch


def run_id(raw: pathlib.Path, root: pathlib.Path) -> str:
    rel = raw.resolve().parent.relative_to(root.resolve()) if raw.is_absolute() or \
        root.is_absolute() else raw.parent
    return str(rel).replace("/", "_")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("convert")
    c.add_argument("raw", nargs="+")
    c.add_argument("-o", required=True)
    c.add_argument("--root", default=".")
    c.add_argument("--bins", default=None)
    k = sub.add_parser("check")
    k.add_argument("files", nargs="+")
    j = sub.add_parser("jobs")
    j.add_argument("files", nargs="+")
    j.add_argument("--data", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "jobs":
        table = probe.load()
        for f in a.files:
            out = write_jobs(pathlib.Path(f), pathlib.Path(a.data), table)
            print(f"{out}: {len(json.loads(out.read_text())['jobs'])} jobs")
        return 0
    if a.cmd == "check":
        for f in a.files:
            b = load(pathlib.Path(f))
            print(f"{f}: {len(b['vectors'])} vectors, {len(b['orphans'])} orphans")
        return 0
    table = probe.load()
    out = pathlib.Path(a.o)
    out.mkdir(parents=True, exist_ok=True)
    root = pathlib.Path(a.root)
    for r in map(pathlib.Path, a.raw):
        rid = run_id(r.absolute(), root.absolute())
        bins = pathlib.Path(a.bins) if a.bins else (r.parent / "bins")
        tbl, dirs = tables_for(r, table)
        batch = convert(r.read_text(), tbl, raw_name=str(r.absolute().relative_to(
            root.absolute())), bins=bins if bins.is_dir() else None, dirs=dirs)
        dump(out / f"{rid}.vec.json", batch)
        n = len(batch["vectors"])
        print(f"{rid}: {n} vectors, {len(batch['orphans'])} orphans")
    return 0


if __name__ == "__main__":
    sys.exit(main())
