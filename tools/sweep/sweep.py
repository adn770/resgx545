#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Sweep probes: every bit of every word of a job's space, run on the sgxfive render node.

A table (probes/<unit>/<feature>.toml) names a host command of sgxfive-test (fill, copy or tri, with its
options) and the spaces to sweep (cmd, xfer, vdm, eos, blk, pds:SLOT, tex, bg; by default
every word of each, the sizes of the job the tool builds). Each word gets a flip of every bit
(SPACE:N^=1<<b, relative to what the job writes) and the extra values (=0 and =0xffffffff by
default), each as its own sgxfive-test run with one --poke, after a baseline run without
pokes. The results are recorded raw (raw.txt) and classified mechanically against the
baseline (report.txt): unchanged, changed (n pixels), outside (writes outside the target),
scratch (writes into the pages of tri --scratch), fault, hang, cancelled, overflow, rejected,
usage, error. Nothing in a table says what a word
is expected to do; the names come later, from the results. The report marks the cases on the
words the kernel checks, masks or overrides (kernel_masks.toml) as having reached the GPU or
not.

The kernel spaces (ta, rd: the firmware command of a triangle's render; tq: a fill's or copy's
transfer command) are the words the kernel builds itself, poked through the kernel fork's
debugfs kpoke; kreg is the registers its debugfs kreg may write. Their cases run the host job
unpoked, with the kernel poke armed (or the register written) around it.

    sweep.py list                          the tables and their case counts
    sweep.py cases TABLE                   the cases of a table, one a line
    sweep.py run TABLE [--out DIR] [--mock | --local] [--max-errors N] [--limit N]
                                           run (resuming DIR/raw.txt) and report
    sweep.py report DIR [--table TABLE]    the report of a saved run

Without --mock or --local the cases run on the laptop over ssh, one process per case on a
fresh context: SGX_TARGET_HOST and SGX_TARGET_SSH_OPTS (or tools/bringup/local.env), the
tool at SGX_SWEEP_TOOL (default ./sgxfive-test), regtimeline at SGX_SWEEP_TIMELINE (default
./regtimeline), debugfs at SGX_SWEEP_DEBUGFS (default /sys/kernel/debug/dri/0/sgx). Every case
records the visibility counters (counters.py) unless SGX_SWEEP_COUNTERS=0; the report's
counters line names the cases where they counted.
"""
from __future__ import annotations

import argparse
import collections
import dataclasses
import os
import pathlib
import re
import shlex
import subprocess
import sys
import time
import tomllib
from typing import Callable

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import counters as counters_mod  # noqa: E402

ROOT = HERE.parent.parent
TABLES = ROOT / "probes"
MASKS = HERE / "kernel_masks.toml"
DEFAULT_TOOL = ROOT / "userspace" / "libsgxfive" / "build" / "sgxfive-test"
DEFAULT_PB_PAGES = 0x422     # the kernel's parameter buffer size, in pages
LOCAL_ENV = ROOT / "kernel" / "scripts" / "local.env"

HOSTS = ("fill", "copy", "tri")
SPACES = ("cmd", "xfer", "vdm", "eos", "blk", "pds", "tex", "bg")
# The kernel fork's debugfs kpoke spaces, their words (sgxfive_kpoke_words) and the jobs they
# apply to (a render's TA command and render details; a transfer that is not a dummy).
KSPACES = {"ta": 176, "rd": 123, "tq": 306}
KHOSTS = {"ta": ("tri",), "rd": ("tri",), "tq": ("fill", "copy")}
# The registers its debugfs kreg may write (sgxfive_kreg_allowed): those the firmware never
# reaches, and those only a 3D render's details load (they hold through a fill or a copy).
KREGS = (0x0810, 0x0814, 0x0818, 0x0a78, 0x0abc)
KREGS_3D = (0x0418, 0x04dc, 0x04e8, 0x0520, 0x0800)
# The PDS slots of each host's job (include/sgxfive_poke.h, the libsgxfive README).
SLOTS = {"fill": ("prim", "sec", "pixev"), "copy": ("prim", "sec", "pixev"),
         "tri": ("vtx", "state", "eos", "prim", "bgprim", "sec", "pixev")}
CLASSES = ("unchanged", "changed", "outside", "scratch", "fault", "hang", "cancelled", "overflow",
           "rejected", "usage", "error")
KEYS = {"name", "about", "host", "options", "mock_options", "range", "bits", "values",
        "repeat", "timeout", "sudo", "timeline", "pb_pages"}
# What a table of several kinds adds around its sweeps (campaign.py): the probes, a script, what
# the target must offer, the kept never-run probes; and [[sweep]], the sweeps of a table that
# holds several.
TABLE_KEYS = {"probe", "sweep", "script", "kind", "baseline", "needs", "open"}
VALUE_RE = re.compile(r"^\^?=(0x[0-9a-fA-F]+|\d+)$")
REGS_RE = re.compile(r"^0x[0-9a-fA-F]+(-0x[0-9a-fA-F]+)?(,0x[0-9a-fA-F]+(-0x[0-9a-fA-F]+)?)*$")


class SweepError(Exception):
    pass


@dataclasses.dataclass(frozen=True)
class Range:
    space: str                  # "xfer", "pds:prim", ...
    first: int | None           # None: from 0
    last: int | None            # None: to the space's end


@dataclasses.dataclass
class Sweep:
    name: str
    about: str
    host: str
    options: list
    mock_options: list
    ranges: list
    bits: list
    values: list
    repeat: int = 1
    timeout: float = 60.0       # seconds a case may take, over ssh included
    sudo: bool = False          # run the tool as root (--regs reads /dev/mem)
    timeline: dict | None = None    # {regs = "LO-HI,...", total = s, lead = s}
    pb_pages: list = dataclasses.field(default_factory=list)

    @property
    def kpoke(self) -> bool:
        """Some range is a kernel-poke space (debugfs kpoke)."""
        return any(r.space in KSPACES for r in self.ranges)

    @property
    def kreg(self) -> bool:
        """Some range is the kernel's registers (debugfs kreg)."""
        return any(r.space == "kreg" for r in self.ranges)

    @property
    def kernel(self) -> bool:
        return self.kpoke or self.kreg


@dataclasses.dataclass(frozen=True)
class Case:
    id: str
    pokes: list
    pb: int | None = None


@dataclasses.dataclass(frozen=True)
class Record:
    """One case's run, as raw.txt keeps it."""
    id: str
    cmd: str
    rc: int
    out: str
    err: str
    secs: float


@dataclasses.dataclass(frozen=True)
class Result:
    job: str | None = None
    hash: str | None = None
    diff: int | None = None
    outside: int | None = None
    scratch: tuple = ()           # (pages written, dwords) from tri --scratch


@dataclasses.dataclass(frozen=True)
class Verdict:
    cls: str
    detail: str = ""


@dataclasses.dataclass(frozen=True)
class Mask:
    """What the kernel does with one word userspace submits (kernel_masks.toml)."""
    action: str                 # pass, validate, mask, override
    lands: list                 # where it lands in the kernel's command: tq:N, ta:N, rd:N
    ref: str                    # file:line in the kernel fork's sgxfive/
    note: str = ""
    mask: int | None = None     # validate: the bits that pass; mask: the bits that survive


@dataclasses.dataclass(frozen=True)
class PixelDiff:
    """One image against another: how many pixels differ (None: different sizes), the box
    holding them (x0, y0, x1, y1) and the new values with their counts, most frequent first."""
    count: int | None
    box: tuple | None = None
    values: list = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class RunResult:
    done: int
    total: int
    stopped: str | None = None


# ---- tables ------------------------------------------------------------------------------

def _space_ok(space: str, host: str) -> bool:
    if space in KSPACES:
        return host in KHOSTS[space]
    if space == "kreg":
        return True
    head, _, slot = space.partition(":")
    if head == "pds":
        return slot in SLOTS[host]
    return head in SPACES and not slot


def load(path: pathlib.Path) -> Sweep:
    """The sweep of a table that holds one (its keys at the top, then [[range]])."""
    d = tomllib.loads(pathlib.Path(path).read_text())
    return _build(d.get("name", pathlib.Path(path).stem), d, TABLE_KEYS)


def load_all(path: pathlib.Path) -> list:
    """The sweeps of a table: its one sweep as load() reads it, or each [[sweep]] (with its own
    name, host, options and [[sweep.range]]) of a table that holds several."""
    d = tomllib.loads(pathlib.Path(path).read_text())
    if "sweep" not in d:
        return ([_build(d.get("name", pathlib.Path(path).stem), d, TABLE_KEYS)]
                if "range" in d else [])
    if "range" in d:
        raise SweepError(f"{pathlib.Path(path).name}: [[range]] and [[sweep]] in one table")
    out = [_build(e.get("name", ""), e) for e in d["sweep"]]
    if len({s.name for s in out}) != len(out) or not all(s.name for s in out):
        raise SweepError(f"{pathlib.Path(path).name}: each [[sweep]] has its own name")
    return out


def _build(name: str, d: dict, extra=frozenset()) -> Sweep:
    if set(d) - KEYS - extra:
        raise SweepError(f"{name}: unknown keys {sorted(set(d) - KEYS - extra)}")
    host = d.get("host")
    if host not in HOSTS:
        raise SweepError(f"{name}: host {host!r} is not one of {HOSTS}")
    ranges = []
    for r in d.get("range", []):
        space = r.get("space", "")
        if not _space_ok(space, host):
            raise SweepError(f"{name}: no space {space!r} in a {host} job")
        idx = r.get("indices", "all")
        if idx == "all":
            ranges.append(Range(space, None, None))
        elif (isinstance(idx, list) and len(idx) == 2 and all(isinstance(i, int) for i in idx)
              and 0 <= idx[0] <= idx[1]):
            ranges.append(Range(space, idx[0], idx[1]))
        else:
            raise SweepError(f"{name}: indices {idx!r} is not \"all\" or [first, last]")
    bits = d.get("bits", list(range(32)))
    if not all(isinstance(b, int) and 0 <= b < 32 for b in bits):
        raise SweepError(f"{name}: bits {bits} are not 0 to 31")
    values = d.get("values", ["=0", "=0xffffffff"])
    if not all(isinstance(v, str) and VALUE_RE.match(v) and int(v.lstrip("^="), 0) < 1 << 32
               for v in values):
        raise SweepError(f"{name}: values {values} are not \"=V\" or \"^=V\"")
    repeat = d.get("repeat", 1)
    if not isinstance(repeat, int) or repeat < 1:
        raise SweepError(f"{name}: repeat {repeat} is not a count")
    pb = d.get("pb_pages", [])
    if not all(isinstance(p, int) and 0x23 <= p <= 0x422 for p in pb):
        raise SweepError(f"{name}: pb_pages {pb} are not 0x23 to 0x422")
    if not ranges and not pb:
        raise SweepError(f"{name}: no range and no pb_pages: nothing to sweep")
    tl = d.get("timeline")
    if tl is not None and (not REGS_RE.match(str(tl.get("regs", ""))) or
                           set(tl) - {"regs", "total", "lead"}):
        raise SweepError(f"{name}: timeline {tl} needs regs = \"LO-HI,...\" (total, lead)")
    return Sweep(name=name, about=d.get("about", ""), host=host,
                 options=[str(o) for o in d.get("options", [])],
                 mock_options=[str(o) for o in d.get("mock_options", [])], ranges=ranges,
                 bits=list(bits), values=list(values), repeat=repeat,
                 timeout=float(d.get("timeout", 60.0)), sudo=bool(d.get("sudo", False)),
                 timeline=tl, pb_pages=list(pb))


SizeOf = Callable[[str, str], int]


def resolve(s: Sweep, size_of: SizeOf) -> list:
    """The ranges as (space, first, last), "all" from the job's size (a kernel space's from
    the kernel); the registers of kreg one (kreg, offset, offset) each."""
    out = []
    for r in s.ranges:
        if r.space == "kreg":
            # "all" is the registers the firmware never reaches, as sweeps 9 and 11 ran
            # them; an explicit range reaches the render-only ones too
            pool = KREGS if r.first is None and r.last is None else sorted(KREGS + KREGS_3D)
            regs = [o for o in pool if (r.first is None or o >= r.first) and
                    (r.last is None or o <= r.last)]
            if not regs:
                raise SweepError(f"{s.name}: no kreg register in {r.first:#x}-{r.last:#x}")
            out += [("kreg", o, o) for o in regs]
            continue
        n = KSPACES[r.space] if r.space in KSPACES else size_of(s.host, r.space)
        first = 0 if r.first is None else r.first
        last = n - 1 if r.last is None else r.last
        if last >= n:
            raise SweepError(f"{s.name}: {r.space}:{last} is past the job's {n} words")
        out.append((r.space, first, last))
    return out


def cases(s: Sweep, size_of: SizeOf) -> list:
    """The baseline (once per PB size, if any), then every bit and value of every word."""
    pokes = []
    for space, first, last in resolve(s, size_of):
        for i in range(first, last + 1):
            word = f"kreg:{i:#06x}" if space == "kreg" else f"{space}:{i}"
            pokes += [f"{word}^={1 << b:#x}" for b in s.bits]
            pokes += [f"{word}{v}" for v in s.values]
    out = []
    for pb in s.pb_pages or [None]:
        pre = f"pb={pb:#x}:" if pb is not None else ""
        for p in [None] + pokes:
            for r in range(s.repeat):
                rid = (p or "baseline") + (f"#{r}" if r else "")
                out.append(Case(pre + rid, [p] if p else [], pb))
    return out


# ---- what the kernel does with each word ------------------------------------------------

MASK_ACTIONS = ("pass", "validate", "mask", "override")
MASK_KEYS = {"word", "action", "lands", "ref", "note", "mask"}
_masks_cache: dict = {}


def load_masks(path=MASKS) -> dict:
    """kernel_masks.toml as {word: Mask}, words in the file's order."""
    path = pathlib.Path(path)
    if path in _masks_cache:
        return _masks_cache[path]
    d = tomllib.loads(path.read_text())
    out = {}
    for w in d.get("word", []):
        name = w.get("word", "")
        if set(w) - MASK_KEYS or not re.fullmatch(r"(xfer|cmd):\d+", name) or name in out:
            raise SweepError(f"{path.name}: bad or repeated word {w}")
        action, mask = w.get("action"), w.get("mask")
        lands = w.get("lands", [])
        if (action not in MASK_ACTIONS or (action == "mask" and mask is None) or
                not lands or not all(re.fullmatch(r"(tq|ta|rd):\d+", x) for x in lands) or
                not re.fullmatch(r"[A-Za-z0-9_./-]+\.[ch]:\d+", w.get("ref", ""))):
            raise SweepError(f"{path.name}: bad entry {w}")
        out[name] = Mask(action, list(lands), w["ref"], w.get("note", ""), mask)
    _masks_cache[path] = out
    return out


def reach(w: Mask | None, op: str, cls: str) -> str | None:
    """Whether a case on a word the kernel checks, masks or overrides reached the GPU; None
    for a word it passes on (or does not know) and for a case that says nothing (usage,
    error)."""
    if w is None or w.action == "pass" or cls in ("usage", "error"):
        return None
    if cls == "rejected" or w.action == "override":
        return "never reached the GPU"
    if w.action == "mask":
        if op.startswith("^="):
            return "reached" if int(op[2:], 0) & w.mask else "never reached the GPU"
        return f"reached, bits {w.mask:#x} only"
    return "reached"


# ---- the tool ----------------------------------------------------------------------------

def _head(poke: str) -> str:
    return poke.split(":", 1)[0]


def tool_args(s: Sweep, c: Case) -> list:
    """The tool's command line: the host and its userspace pokes (the kernel's are armed
    around it, kernel_script)."""
    args = [s.host, *s.options]
    for p in c.pokes:
        if _head(p) not in KSPACES and _head(p) != "kreg":
            args += ["--poke", p]
    return args


def local_argv(s: Sweep, c: Case, tool, mock: bool) -> list:
    head = [str(tool)]
    if mock:
        head += ["--mock", *s.mock_options]
        if c.pb is not None:
            head.append(f"--mock-pb-pages={c.pb:#x}")
    return head + tool_args(s, c)


def tool_size_of(tool) -> SizeOf:
    """The size of a space in a host's job, from the tool's own check of a poke past it."""
    cache: dict = {}

    def size_of(host: str, space: str) -> int:
        if (host, space) not in cache:
            r = subprocess.run([str(tool), "--mock", host, "--poke", f"{space}:0xffffffff=0"],
                               capture_output=True, text=True, timeout=30)
            m = re.search(r"out of range \((\d+) words\)", r.stderr)
            if r.returncode != 2 or not m:
                raise SweepError(f"no {space} in a {host} job: {r.stderr.strip()}")
            cache[host, space] = int(m.group(1))
        return cache[host, space]
    return size_of


def target_cmd(s: Sweep, c: Case, tool: str, timeline: str, dbg: str,
               kreg_base: dict | None = None, counters: bool = False) -> str:
    """The shell command of a case on the device: the tool (inside regtimeline, as root,
    as the table says, or over the visibility counters with counters), inside kernel_script
    for a table of kernel spaces."""
    argv = [str(tool), *tool_args(s, c)]
    if s.timeline:
        argv = timeline_argv(s, argv, timeline, counters)
    elif counters:
        argv = counters_mod.wrap(argv, timeline)
    if s.sudo or s.timeline or counters:
        argv = ["sudo", "-n", *argv]
    cmd = shlex.join(argv)
    return kernel_script(s, c, cmd, dbg, kreg_base or {}) if s.kernel else cmd


def kernel_script(s: Sweep, c: Case, cmd: str, dbg: str, kreg_base: dict) -> str:
    """cmd with the case's kernel pokes armed around it (sudo for debugfs, the tool as the
    table says). kpoke: "clear" and the poke before, "kpoke left: ..." (what the job did not
    take; "none") and "clear" after. kreg: "kreg: OFF=V ..." (every register, before), then
    each poked register set back to its baseline value (kreg_base: a case cut off leaves its
    poke), poked, "kreg OFF: was V reads V" and after the job "kreg OFF: after the job V",
    and set back to what it was. A poke that cannot be armed fails the case with rc 3."""
    q = shlex.quote
    sh = [f"d={q(dbg)}",
          'put() { f=$1; shift; printf \'%s\\n\' "$@" | sudo -n tee "$d/$f" >/dev/null; }',
          'reg() { sudo -n cat "$d/kreg" | awk -v o="$1" \'$1 == o { print $2 }\'; }',
          'die() { echo "sweep.py: $1" >&2; exit 3; }']
    kp = [p for p in c.pokes if _head(p) in KSPACES]
    kr = [p.split(":", 1)[1] for p in c.pokes if _head(p) == "kreg"]
    if s.kpoke:
        sh.append(" ".join(["put kpoke clear", *map(q, kp), "|| die 'kpoke not armed'"]))
    if s.kreg:
        sh.append('echo "kreg: $(sudo -n cat "$d/kreg" | '
                  'awk \'{ printf "%s%s=%s", s, $1, $2; s = " " }\')"')
    for p in kr:
        off = int(re.match(r"0x[0-9a-fA-F]+", p).group(0), 16)
        o = f"{off:#06x}"
        if off in kreg_base:
            sh.append(f"put kreg {o}={kreg_base[off]:#010x} || die 'kreg {o} not set back'")
        sh += [f"was_{off}=$(reg {o})",
               f"put kreg {q(p)} || die {q(f'kreg {p} not written')}",
               f'echo "kreg {o}: was $was_{off} reads $(reg {o})"']
    sh += [cmd, "rc=$?"]
    for p in kr:
        off = int(re.match(r"0x[0-9a-fA-F]+", p).group(0), 16)
        o = f"{off:#06x}"
        sh += [f'echo "kreg {o}: after the job $(reg {o})"',
               f'put kreg "{o}=$was_{off}" || echo "sweep.py: kreg {o} not restored" >&2']
    if s.kpoke:
        sh += ['l=$(sudo -n cat "$d/kpoke" | tr \'\\n\' \' \')',
               'echo "kpoke left: ${l:-none}"',
               "put kpoke clear || echo 'sweep.py: kpoke not cleared' >&2"]
    sh.append('exit "$rc"')
    return "; ".join(sh)       # one line: raw.txt keeps a case's command on its own


def _debugfs() -> str:
    return os.environ.get("SGX_SWEEP_DEBUGFS", "/sys/kernel/debug/dri/0/sgx")


class LocalExec:
    """Runs cases with a local sgxfive-test, against the mock or a local device. The mock
    has no kernel: a kernel poke's case runs the host job unpoked."""

    kreg_base = None            # run(): the registers of the baseline (kreg tables)

    def __init__(self, tool, mock: bool = True):
        self.tool, self.mock = tool, mock

    def __call__(self, s: Sweep, c: Case) -> Record:
        if s.kernel and not self.mock:
            cmd = target_cmd(s, c, str(self.tool), os.environ.get(
                "SGX_SWEEP_TIMELINE", str(HERE / "regtimeline")), _debugfs(), self.kreg_base)
            return _exec(c, ["sh", "-c", cmd], s.timeout, cmd)
        argv = local_argv(s, c, self.tool, self.mock)
        if s.timeline and not self.mock:
            argv = timeline_argv(s, argv, os.environ.get("SGX_SWEEP_TIMELINE",
                                                         str(HERE / "regtimeline")))
        if s.sudo and not self.mock:
            argv = ["sudo", "-n", *argv]
        return _exec(c, argv, s.timeout, shlex.join(argv))

    def setup(self, s: Sweep, pb: int | None) -> None:
        if pb is not None and not self.mock:
            _write_pb(pb, lambda cmd: subprocess.run(["sh", "-c", cmd], check=True))


def timeline_argv(s: Sweep, argv: list, rt: str, counters: bool = False) -> list:
    tl = s.timeline or {}
    regs = counters_mod.with_counters(tl["regs"]) if counters else tl["regs"]
    return [rt, str(tl.get("total", 2.0)), str(tl.get("lead", 0.2)), regs, "--", *argv]


def _write_pb(pb: int, sh) -> None:
    sh(f"echo {pb:#x} | sudo -n tee {_debugfs()}/render_pb_pages >/dev/null")


def _exec(c: Case, argv: list, timeout: float, cmd: str) -> Record:
    t0 = time.monotonic()
    try:
        r = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
        rc, so, se = r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired as e:
        rc, so = -1000, _text(e.stdout)
        se = _text(e.stderr) + f"sweep.py: timed out after {timeout:g} s\n"
    return Record(c.id, cmd, rc, so, se, time.monotonic() - t0)


def _text(b) -> str:
    return b.decode(errors="replace") if isinstance(b, bytes) else (b or "")


def _local_env() -> dict:
    env = {}
    if LOCAL_ENV.exists():
        for line in LOCAL_ENV.read_text().splitlines():
            m = re.match(r'^(\w+)=\$\{\w+:-"?(.*?)"?\}$', line.strip())
            if m:
                env[m.group(1)] = m.group(2)
    return env


class SshExec:
    """Runs cases on the laptop, one ssh command each over a shared connection."""

    kreg_base = None            # run(): the registers of the baseline (kreg tables)

    def __init__(self):
        env = _local_env()
        self.host = os.environ.get("SGX_TARGET_HOST", env.get("SGX_TARGET_HOST"))
        if not self.host:
            raise SweepError("set SGX_TARGET_HOST (or tools/bringup/local.env)")
        opts = os.environ.get("SGX_TARGET_SSH_OPTS", env.get("SGX_TARGET_SSH_OPTS", ""))
        ctl = pathlib.Path("/tmp") / "sgxsweep-%C"      # short: Unix socket paths <= 104 bytes
        self.ssh = ["ssh", *shlex.split(opts), "-o", "ControlMaster=auto",
                    "-o", f"ControlPath={ctl}", "-o", "ControlPersist=120", self.host]
        self.tool = os.environ.get("SGX_SWEEP_TOOL",
                                   os.environ.get("SGX_PROBE_TOOL", "./sgxfive-test"))
        self.timeline = os.environ.get("SGX_SWEEP_TIMELINE", "./regtimeline")
        self.counters = os.environ.get("SGX_SWEEP_COUNTERS", "1") != "0"

    def __call__(self, s: Sweep, c: Case) -> Record:
        cmd = target_cmd(s, c, self.tool, self.timeline, _debugfs(), self.kreg_base,
                         self.counters)
        return _exec(c, [*self.ssh, cmd], s.timeout, cmd)

    def setup(self, s: Sweep, pb: int | None) -> None:
        if pb is not None:
            _write_pb(pb, lambda cmd: subprocess.run([*self.ssh, cmd], check=True,
                                                     timeout=60))


# ---- results -----------------------------------------------------------------------------

def parse_result(out: str) -> Result:
    job = re.search(r"^job: (.*)$", out, re.M)
    h = re.search(r"^target: \d+x\d+ hash (0x[0-9a-f]+)$", out, re.M)
    diff = re.search(r"^diff: (\d+) of \d+ pixels", out, re.M)
    outside = re.search(r"^outside: (\d+) dwords$", out, re.M)
    pages = tuple(int(m) for m in re.findall(r"^scratch page (\d+): \d+ changed", out, re.M))
    dwords = re.search(r"^scratch: (\d+) dwords changed$", out, re.M)
    return Result(job=job and job.group(1), hash=h and h.group(1),
                  diff=diff and int(diff.group(1)), outside=outside and int(outside.group(1)),
                  scratch=(pages, int(dwords.group(1))) if dwords and pages else ())


def _kpoke_key(text: str) -> tuple | None:
    """("ta", 3, True, 1) from "ta:3^=0x1" or the kernel's "ta:3^=0x00000001"."""
    m = re.fullmatch(r"(\w+):(0x[0-9a-fA-F]+|\d+)(\^?)=(0x[0-9a-fA-F]+|\d+)", text)
    return m and (m[1], int(m[2], 0), bool(m[3]), int(m[4], 0))


def kpoke_left(out: str) -> list | None:
    """The kernel pokes still armed after the job (kernel_script), None without the line."""
    m = re.search(r"^kpoke left: (.*)$", out, re.M)
    if not m:
        return None
    return [_kpoke_key(x) for x in m.group(1).split() if x != "none"]


def kreg_values(out: str) -> dict:
    """{offset: value} of every kreg register, as kernel_script found them before a case."""
    m = re.search(r"^kreg: (.*)$", out, re.M)
    vals = {}
    for x in (m.group(1).split() if m else []):
        k, _, v = x.partition("=")
        if re.fullmatch(r"0x[0-9a-fA-F]+", k) and re.fullmatch(r"0x[0-9a-fA-F]+", v):
            vals[int(k, 16)] = int(v, 16)
    return vals


def kreg_results(out: str) -> dict:
    """{offset: (was, reads after the write, after the job)} of the registers a case poked."""
    res = {}
    for m in re.finditer(r"^kreg (0x[0-9a-f]+): was (0x[0-9a-f]+) reads (0x[0-9a-f]+)$",
                         out, re.M):
        a = re.search(rf"^kreg {m[1]}: after the job (0x[0-9a-f]+)$", out, re.M)
        if a:
            res[int(m[1], 16)] = (int(m[2], 16), int(m[3], 16), int(a[1], 16))
    return res


JOB_FAILURES = (("failed: job faulted", "fault"), ("failed: job hung", "hang"),
                ("failed: job cancelled", "cancelled"),
                ("failed: scene overflowed", "overflow"))


def classify(rc: int, out: str, base: Result) -> Verdict:
    """One case against the baseline's result. "error" is everything that is not the job's
    own result: the tool or the connection failed, or a wait gave up without the kernel's
    recovery having finished the job."""
    if rc == 2:
        return Verdict("usage")
    res = parse_result(out)
    if rc not in (0, 1):
        return Verdict("error", f"rc {rc}" + ("" if res.job else ", no job line"))
    if res.job is None:
        return Verdict("error", f"rc {rc}, no job line")
    if res.job.startswith("rejected"):
        m = re.match(r"rejected \((.*)\)$", res.job)
        return Verdict("rejected", m.group(1) if m else res.job)
    for prefix, cls in JOB_FAILURES:
        if res.job.startswith(prefix):
            return Verdict(cls)
    if res.job != "ok":
        return Verdict("error", res.job)
    out_n = res.outside or 0
    extra = out_n != (base.outside or 0)
    sc = ""
    if res.scratch and res.scratch != base.scratch:
        sc = f"pages {', '.join(map(str, res.scratch[0]))} ({res.scratch[1]} dwords)"
    if res.hash != base.hash:
        return Verdict("changed", f"{res.diff} pixels" + (f", {out_n} outside" if extra
                                                          else "") +
                       (f", scratch {sc}" if sc else ""))
    if extra:
        return Verdict("outside", f"{out_n} dwords")
    if sc:
        return Verdict("scratch", sc)
    return Verdict("unchanged")


def format_record(r: Record) -> str:
    out = r.out if not r.out or r.out.endswith("\n") else r.out + "\n"
    err = r.err if not r.err or r.err.endswith("\n") else r.err + "\n"
    return (f"=== case {r.id}\n$ {r.cmd}\n{out}--- stderr\n{err}"
            f"--- rc {r.rc} {r.secs:.3f} s\n")


def parse_raw(text: str) -> dict:
    """The finished cases of a raw.txt, by id (a case cut off before its rc line is not)."""
    recs = {}
    blocks = re.split(r"^=== case ", text, flags=re.M)
    for b in blocks[1:]:
        m = re.match(r"(?P<id>[^\n]*)\n\$ (?P<cmd>[^\n]*)\n(?P<out>.*?)--- stderr\n"
                     r"(?P<err>.*?)--- rc (?P<rc>-?\d+) (?P<secs>[\d.]+) s\n", b, re.S)
        if m:
            recs[m["id"]] = Record(m["id"], m["cmd"], int(m["rc"]), m["out"], m["err"],
                                   float(m["secs"]))
    return recs


# ---- running -----------------------------------------------------------------------------

def run(s: Sweep, execu, out_dir, size_of: SizeOf, max_errors: int = 5,
        limit: int | None = None, log=None, masks: dict | None = None,
        cs: list | None = None) -> RunResult:
    """Run the cases not yet in out_dir/raw.txt, appending each as it finishes; write the
    report. Stops after max_errors errors in a row, or after limit new cases, and before
    any poke when the baseline failed (a sweep of PB sizes alone has no pokes: its first
    case is only the reference)."""
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    raw = out_dir / "raw.txt"
    done = parse_raw(raw.read_text()) if raw.exists() else {}
    cs = cs if cs is not None else cases(s, size_of)
    stopped, errors, new, pb_now = None, 0, 0, None
    try:
        with raw.open("a") as f:
            for c in cs:
                if c.id in done:
                    continue
                if limit is not None and new >= limit:
                    break
                if s.kreg and hasattr(execu, "kreg_base") and cs[0].id in done:
                    execu.kreg_base = kreg_values(done[cs[0].id].out)
                if c.pb != pb_now and hasattr(execu, "setup"):
                    execu.setup(s, c.pb)
                    pb_now = c.pb
                rec = execu(s, c)
                f.write(format_record(rec))
                f.flush()
                done[c.id] = rec
                new += 1
                v = classify(rec.rc, rec.out, _baseline(s, cs, done) or parse_result(rec.out))
                if log:
                    log(f"{c.id}: {v.cls} {v.detail}".rstrip())
                if c.id == cs[0].id and s.ranges and v.cls != "unchanged":
                    _write_report(s, cs, done, out_dir, masks=masks)
                    raise SweepError(f"{s.name}: the baseline is {v.cls} {v.detail}; "
                                     "no reference to compare with")
                errors = errors + 1 if v.cls == "error" else 0
                if errors >= max_errors:
                    stopped = f"stopped: {errors} errors in a row, the last {c.id}"
                    break
    finally:
        if pb_now is not None and hasattr(execu, "setup"):
            execu.setup(s, DEFAULT_PB_PAGES)    # the kernel default again, whatever happened
    _write_report(s, cs, done, out_dir, stopped, masks)
    return RunResult(done=sum(c.id in done for c in cs), total=len(cs), stopped=stopped)


def parse_pixels(out: str) -> list | None:
    """The target's pixels from --pixels output ("row Y: 0x... 0x..."), row by row."""
    rows = re.findall(r"^row \d+:((?: 0x[0-9a-f]{8})*)$", out, re.M)
    return [[int(v, 16) for v in r.split()] for r in rows] if rows else None


def pixel_diff(base: list, img: list) -> PixelDiff:
    if len(base) != len(img) or any(len(a) != len(b) for a, b in zip(base, img)):
        return PixelDiff(None)
    pts = [(x, y, v) for y, (ra, rb) in enumerate(zip(base, img))
           for x, (a, v) in enumerate(zip(ra, rb)) if a != v]
    if not pts:
        return PixelDiff(0)
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    vals = collections.Counter(p[2] for p in pts).most_common()
    return PixelDiff(len(pts), (min(xs), min(ys), max(xs), max(ys)), vals)


def changed_cases(s: Sweep, cs: list, done: dict) -> list:
    """The baseline and every case whose image differs from it, in table order."""
    base = _baseline(s, cs, done)
    if base is None:
        raise SweepError(f"{s.name}: no baseline in the run")
    return [cs[0]] + [c for c in cs[1:] if c.id in done and
                      classify(done[c.id].rc, done[c.id].out, base).cls == "changed"]


def rerun(s: Sweep, execu, src_dir, size_of: SizeOf, out_dir=None, log=None) -> RunResult:
    """Run the baseline and the changed cases of src_dir's run again with --pixels, into
    src_dir/pixels, and report each case's pixels against the baseline's (the run's own
    report counts them against the CPU reference instead)."""
    src_dir = pathlib.Path(src_dir)
    out_dir = pathlib.Path(out_dir) if out_dir else src_dir / "pixels"
    done = parse_raw((src_dir / "raw.txt").read_text())
    cs = changed_cases(s, cases(s, size_of), done)
    s2 = dataclasses.replace(s, options=[*s.options, "--pixels"])
    res = run(s2, execu, out_dir, size_of, log=log, cs=cs)
    redone = parse_raw((out_dir / "raw.txt").read_text())
    base = parse_pixels(redone[cs[0].id].out) if cs[0].id in redone else None
    lines = [f"sweep {s.name}: the changed cases again, every pixel against the baseline's",
             f"cases: {res.done} of {res.total}", ""]
    for c in cs[1:]:
        r = redone.get(c.id)
        img = parse_pixels(r.out) if r else None
        if r is None or img is None or base is None:
            why = "not run" if r is None else \
                classify(r.rc, r.out, parse_result(redone[cs[0].id].out)).cls
            lines.append(f"{c.id}: no pixels ({why})")
            continue
        d = pixel_diff(base, img)
        if d.count is None:
            lines.append(f"{c.id}: the target's size differs from the baseline's")
        elif d.count == 0:
            lines.append(f"{c.id}: same pixels as the baseline this time")
        else:
            x0, y0, x1, y1 = d.box
            vals = ", ".join(f"0x{v:08x} x{n}" for v, n in d.values[:3])
            more = f", +{len(d.values) - 3} more values" if len(d.values) > 3 else ""
            lines.append(f"{c.id}: {d.count} pixels differ from the baseline, in "
                         f"({x0},{y0})-({x1},{y1}); new values {vals}{more}")
    (out_dir / "report.txt").write_text("\n".join(lines) + "\n")
    return res


def _baseline(s: Sweep, cs: list, done: dict) -> Result | None:
    rec = done.get(cs[0].id)
    return parse_result(rec.out) if rec else None


def _write_report(s, cs, done, out_dir, stopped=None, masks=None) -> None:
    (out_dir / "report.txt").write_text(report(s, cs, done, stopped, masks))


def _word(cid: str) -> tuple:
    """("pb=0x30:xfer:3", "^=0x1") from "pb=0x30:xfer:3^=0x1#2"; the baseline as itself."""
    m = re.match(r"^(pb=0x[0-9a-f]+:)?(.*?)(\^?=[^=]*)?$", cid.split("#")[0])
    return (m.group(1) or "") + m.group(2), m.group(3) or ""


def report(s: Sweep, cs: list, done: dict, stopped: str | None = None,
           masks: dict | None = None) -> str:
    """The summary, then a line per word with every case that was not unchanged; on a word
    the kernel checks, masks or overrides, each case says whether it reached the GPU, and
    the line ends with what the kernel does and how many of its cases reached it. A kernel
    word's line ends with how many of its pokes the kernel applied (and the userspace word
    it carries, if any); a register's with what the writes did to it."""
    masks = load_masks() if masks is None else masks
    carries = {x: name for name, w in masks.items() for x in w.lands}
    base = _baseline(s, cs, done)
    base_regs = kreg_values(done[cs[0].id].out) if cs[0].id in done else {}
    regs: dict = {}                 # kreg word -> [(op, (was, reads, after))]
    counts = dict.fromkeys(CLASSES, 0)
    per: dict = {}                  # word -> op -> [(verdict text, reach) per repeat]
    secs = 0.0
    for c in cs:
        rec = done.get(c.id)
        if not rec:
            continue
        secs += rec.secs
        if c is cs[0]:
            continue                # the reference: its own line
        v = classify(rec.rc, rec.out, base or Result())
        counts[v.cls] += 1
        word, op = _word(c.id)
        bare = word.split(":", 1)[1] if word.startswith("pb=") else word
        if _head(bare) in KSPACES:
            r = kreach(rec.out, c.pokes, v.cls)
        else:
            r = reach(masks.get(bare), op, v.cls)
        if _head(bare) == "kreg":
            got = kreg_results(rec.out).get(int(bare.split(":")[1], 16))
            if got:
                regs.setdefault(word, []).append((op, got))
        per.setdefault(word, {}).setdefault(op, []).append(
            (v.cls + (f" ({v.detail})" if v.detail else ""), r))
    n = sum(c.id in done for c in cs)
    lines = [f"sweep {s.name}: {s.about}",
             f"host: {' '.join([s.host, *s.options])}",
             f"cases: {n} of {len(cs)} run, {secs:.1f} s",
             f"baseline: {(base.job, base.hash) if base else 'not run'}",
             "summary: " + ", ".join(f"{k} {v}" for k, v in counts.items() if v)]
    sums = [(c.id, counters_mod.summary(done[c.id].out)) for c in cs if c.id in done]
    if any(x is not None for _, x in sums):
        hot = [f"{cid} ({x})" for cid, x in sums if x]
        lines.append(f"counters: {sum(x is not None for _, x in sums)} recorded, "
                     f"{len(hot)} counted" + (": " + "; ".join(hot) if hot else ""))
    if stopped:
        lines.append(stopped)
    lines.append("")
    for word, ops in per.items():
        parts, reached, known = [], 0, 0
        kword = _head(word.split(":", 1)[1] if word.startswith("pb=") else word) in KSPACES
        for op, vs in ops.items():
            texts = [t for t, _ in vs]
            reaches = {r for _, r in vs}
            text = texts[0] if len(set(texts)) == 1 else "/".join(texts)
            for _, r in vs:
                known += r is not None
                reached += bool(r and r.startswith("reached"))
            if text != "unchanged" or len(set(texts)) > 1:
                tag = f" [{reaches.pop()}]" if len(reaches) == 1 and None not in reaches \
                    else ""
                if kword and tag == " [reached]":
                    tag = ""                # the kernel word's usual case: its end says
                parts.append(f"{op} {text}".strip() + tag)
        line = f"{word}: " + ("; ".join(parts) if parts else "all unchanged")
        bare = word.split(":", 1)[1] if word.startswith("pb=") else word
        if kword and known:
            line += f" [kpoke applied in {reached} of {known}" + \
                (f"; carries {carries[bare]}]" if bare in carries else "]")
        if word in regs:
            line += _kreg_summary(base_regs.get(int(bare.split(":")[1], 16)), regs[word])
        w = masks.get(bare)
        if w is not None and w.action != "pass":
            what = w.action + (f" {w.mask:#x}" if w.action == "mask" else "") + \
                (f" ({w.note})" if w.note else "")
            line += (f" [kernel: {what}, lands {','.join(w.lands)}, {w.ref}; "
                     f"reached the GPU in {reached} of {known}]")
        lines.append(line)
    return "\n".join(lines) + "\n"


def kreach(out: str, pokes: list, cls: str) -> str | None:
    """Whether a kernel poke reached the GPU: the kernel takes it into the next job of its
    kind, so one still armed after the job did not (the job was refused before, or there
    was none); None when the case says nothing (usage, error, no kpoke line)."""
    left = kpoke_left(out)
    if left is None or cls in ("usage", "error") or not pokes:
        return None
    return "never reached the GPU" if any(_kpoke_key(p) in left for p in pokes) \
        else "reached"


def _kreg_summary(was: int | None, cases: list) -> str:
    """What a register's writes did: the flips (^=) that read back and those that did not,
    and how many of the jobs left it other than they found it."""
    took = ign = 0
    for op, (w, reads, _) in cases:
        if op.startswith("^="):
            v = int(op[2:], 0)
            took |= v & (reads ^ w)
            ign |= v & ~(reads ^ w)
    changed = sum(reads != after for _, (_, reads, after) in cases)
    return (" [register: was " + (f"{was:#010x}" if was is not None else "?") +
            f"; flips that took {took:#010x}, did not {ign:#010x}; "
            f"the job changed it in {changed} of {len(cases)}]")


# ---- command line ------------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("list", "cases", "run", "report", "rerun"):
        p = sub.add_parser(name)
        p.add_argument("--tool", default=str(DEFAULT_TOOL),
                       help="the local sgxfive-test (sizes; --mock and --local runs)")
        if name in ("cases", "run"):
            p.add_argument("table")
        if name == "run":
            p.add_argument("--out", default=None, help="default: debug/sweeps/NAME")
            g = p.add_mutually_exclusive_group()
            g.add_argument("--mock", action="store_true", help="the local tool on the mock")
            g.add_argument("--local", action="store_true", help="the local tool, no mock")
            p.add_argument("--max-errors", type=int, default=5)
            p.add_argument("--limit", type=int, default=None)
            p.add_argument("-v", "--verbose", action="store_true")
        if name == "rerun":
            p.add_argument("dir", help="a finished run: its changed cases run again")
            p.add_argument("--table", default=None, help="default: DIR/table.toml")
            g = p.add_mutually_exclusive_group()
            g.add_argument("--mock", action="store_true", help="the local tool on the mock")
            g.add_argument("--local", action="store_true", help="the local tool, no mock")
        if name == "report":
            p.add_argument("dir")
            p.add_argument("--table", default=None, help="default: DIR/table.toml")
    a = ap.parse_args(argv)
    try:
        size_of = tool_size_of(a.tool)
        if a.cmd == "list":
            for p in sorted(TABLES.glob("*/*.toml")):
                for s in load_all(p):
                    print(f"{s.name:24} {len(cases(s, size_of)):6} cases  {s.about}")
            return 0
        if a.cmd == "cases":
            s = load(pathlib.Path(a.table))
            for c in cases(s, size_of):
                print(f"{c.id}\t{shlex.join(tool_args(s, c))}")
            return 0
        if a.cmd == "report":
            d = pathlib.Path(a.dir)
            s = load(pathlib.Path(a.table) if a.table else d / "table.toml")
            done = parse_raw((d / "raw.txt").read_text())
            print(report(s, cases(s, size_of), done), end="")
            return 0
        if a.cmd == "rerun":
            d = pathlib.Path(a.dir)
            s = load(pathlib.Path(a.table) if a.table else d / "table.toml")
            execu = LocalExec(a.tool, mock=True) if a.mock else \
                LocalExec(a.tool, mock=False) if a.local else SshExec()
            res = rerun(s, execu, d, size_of)
            print(f"{s.name}: {res.done} of {res.total} cases again in {d / 'pixels'}")
            return 0
        path = pathlib.Path(a.table)
        s = load(path)
        out = pathlib.Path(a.out) if a.out else ROOT / "debug" / "sweeps" / s.name
        out.mkdir(parents=True, exist_ok=True)
        (out / "table.toml").write_text(path.read_text())
        execu = LocalExec(a.tool, mock=True) if a.mock else \
            LocalExec(a.tool, mock=False) if a.local else SshExec()
        res = run(s, execu, out, size_of, max_errors=a.max_errors, limit=a.limit,
                  log=(lambda m: print(m, flush=True)) if a.verbose else None)
        print(f"{s.name}: {res.done} of {res.total} cases in {out}"
              + (f"; {res.stopped}" if res.stopped else ""))
        return 1 if res.stopped else 0
    except SweepError as err:
        print(f"sweep.py: {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
