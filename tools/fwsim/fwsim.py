#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""fwsim: the stock EDM microkernel in the simulator (pysgx.Sgx), with a hardware model and a
tracer, driven from the host side (the firmware-in-sim track, milestone M1).

A `Run` places the cut firmware as our driver places it (test_sgx_boot.layout, REV1), puts the
hardware model behind every register read (sgx_sim::hw: a run write, a cited seed of
seeds.toml, a landed rule or a reset value the kept snapshots agree on, else the run stops),
and drives the boot, ticks and kernel CCB commands. The firmware is never in this tree: it is
read at run time from the private data repository and the run skips without it.

Clean-room terms of the track: a trace and everything derived from it (run.toml, facts.txt,
output.txt) is written only under $RESGX545_DATA_PRIVATE/firmware/fwsim/; any other output
path is refused, here and in the simulator's file sink. A trace holds indices, addresses and
values, never instruction text; facts.txt holds counts and values only.

    tools/fwsim/fwsim.py idle --ticks 1000 --power --out $RESGX545_DATA_PRIVATE/firmware/fwsim/m1-idle
"""
from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import json
import os
import pathlib
import re
import shutil
import struct
import subprocess
import sys
import tomllib

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent
for p in (HERE, REPO / "crates" / "pysgx", REPO / "crates" / "pysgx" / "tests",
          REPO / "tools" / "fwcutter", REPO / "harness" / "ukernel-extract"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
import ccb  # noqa: E402
import facts  # noqa: E402
import fwformat  # noqa: E402
import fwload  # noqa: E402
import kept  # noqa: E402
import load  # noqa: E402

SEEDS = HERE / "seeds.toml"
# The start indices of PDS #13's four slots (E146; E003's CODE_WORD targets of buffer 4).
SLOTS = {6: 0, 1434: 1, 2766: 2, 3594: 3}
# HostCtl dwords (hw_spec 12): the init status, the timer clock, the host clock, the ticks.
INIT_STATUS, HW_RECOVERY_SAMPLE_RATE, UKERNEL_TIMER_CLOCK, HOST_CLOCK = 0x00, 0x14, 0x18, 0x34
EVENT_KICK, EVENT_TIMER, EVENT_KICK2 = 0xAC8 // 4, 0xACC // 4, 0xAE8 // 4
MISCINFO_GET_STRUCT_SIZES = 0x2
E_NUMBER = re.compile(r"(?<![A-Za-z0-9])E\d{3,4}(?!\d)")


class Refused(ValueError):
    """An output path or an input row fwsim does not take."""


def private_dir() -> pathlib.Path | None:
    """The private data repository ($RESGX545_DATA_PRIVATE or ../resgx545-data-private)."""
    d = pathlib.Path(os.environ.get("RESGX545_DATA_PRIVATE") or REPO.parent / "resgx545-data-private")
    return d if d.is_dir() else None


def find_fw() -> pathlib.Path | None:
    """The cut firmware file (as test_sgx_boot.find_fw), None when it is absent."""
    env = os.environ
    cands = []
    if env.get("RESGX545_FW"):
        cands.append(pathlib.Path(env["RESGX545_FW"]))
    if env.get("RESGX545_UKERNEL"):
        cands.append(pathlib.Path(env["RESGX545_UKERNEL"]).parent.parent / "sgx545_ukernel.fw")
    priv = private_dir()
    if priv:
        cands.append(priv / "firmware" / "images" / "sgx545_ukernel.fw")
    return next((c for c in cands if c.is_file()), None)


def fwsim_root(private: pathlib.Path) -> pathlib.Path:
    return private / "firmware" / "fwsim"


def checked_out(path: pathlib.Path, private: pathlib.Path) -> pathlib.Path:
    """`path` resolved, if it lies strictly under <private>/firmware/fwsim/; else Refused."""
    if ".." in pathlib.Path(path).parts:
        raise Refused(f"{path}: an output path may not hold '..'")
    root = fwsim_root(pathlib.Path(private)).resolve()
    full = pathlib.Path(path).resolve()
    if full == root or root not in full.parents:
        raise Refused(f"{path}: fwsim writes only under the private data's firmware/fwsim/ ({root})")
    return full


def load_seeds(path: pathlib.Path = SEEDS) -> dict:
    """seeds.toml, every row's citation checked: a row without an E-number is refused."""
    d = tomllib.loads(pathlib.Path(path).read_text())
    rows = [("reset", d.get("reset", {}))] + [("seed", r) for r in d.get("seed", [])]
    rows += [("rule", r) for r in d.get("rule", [])] + [("carry", d.get("carry", {})),
                                                         ("events", d.get("events", {}))]
    for kind, row in rows:
        if not E_NUMBER.search(str(row.get("cite", ""))):
            raise Refused(f"{path}: a {kind} row cites no record (E-number): {row}")
    for r in d.get("rule", []):
        if r.get("kind") != "count_ticks" or r.get("reg") != 0x0B14:
            raise Refused(f"{path}: no landed rule {r.get('kind')!r} for register {r.get('reg')}")
    return d


def layout() -> fwload.Layout:
    import test_sgx_boot
    return test_sgx_boot.layout()


class Run:
    """One firmware in the simulator under the hardware model. `trace`: None (no trace),
    "memory" (kept in memory, `events()`), or a path under <private>/firmware/fwsim/."""

    def __init__(self, fw: pathlib.Path, data: pathlib.Path, *, seeds: dict | None = None,
                 trace: str | pathlib.Path | None = None, private: pathlib.Path | None = None):
        self.pysgx = load.pysgx()
        self.seeds = seeds if seeds is not None else load_seeds()
        self.fw = fw
        self.lay = layout()
        self.boot_data = fwload.load(fwformat.unpack(fw.read_bytes()), self.lay)
        s = self.s = self.pysgx.Sgx()
        if trace == "memory":
            s.trace_to()
        elif trace is not None:
            priv = private or private_dir()
            if priv is None:
                raise Refused("a trace needs the private data repository")
            s.trace_to(checked_out(pathlib.Path(trace), priv), priv)
        rs = self.seeds["reset"]
        s.hw_enable(f"{', '.join(rs['datasets'])} ({rs['cite']})")
        for off, v in kept.stable_resets(data).items():
            s.hw_reset(off // 4, v)
        for r in self.seeds.get("seed", []):
            s.hw_seed(r["reg"] // 4, r["value"], r["cite"])
        for r in self.seeds.get("rule", []):
            s.hw_count_serv_events(r["value"], r["cite"])
        s.alu_specials_in_movs = True       # PDS #13 passes ir1.l and tim.l on with movs (R5)
        for i, image in self.boot_data.images.items():
            s.map(self.lay.addr[i], image)
        self.host = self.lay.addr[facts.HOST_CTL]
        self.booted = False

    # -- the host's side ------------------------------------------------------------------

    def boot(self, max_steps: int = 100_000) -> None:
        """The host's boot writes (boot_sequence.md B3, B4, C9-C12), the kick, the boot run;
        then the carried task state of the first tick entry (seeds.toml [carry])."""
        s = self.s
        s.store32(self.host + HW_RECOVERY_SAMPLE_RATE, 10)
        s.store32(self.host + UKERNEL_TIMER_CLOCK, 400000)
        for off, value in self.boot_data.scripts["part2"]:
            s.write_reg(off // 4, value)
        s.store32(self.host + HOST_CLOCK, 1000)
        s.store32(self.host + INIT_STATUS, 0)
        s.write_reg(EVENT_KICK2, 1)
        s.run(max_steps)
        c = self.seeds["carry"]
        p = list(c.get("p", [])) + [None] * (4 - len(c.get("p", [])))
        s.seed_carry(pclink=c.get("pclink"), p=p)
        self.booted = True

    def tick(self, max_steps: int = 200_000) -> None:
        e = self.seeds["events"]
        self.s.event_ir0, self.s.event_tim = e["tick_ir0"], e["tick_tim"]
        self.s.event(0)
        self.s.run(self.s.steps + max_steps)

    def submit(self, cmd: str, data: list[int], max_steps: int = 200_000, *, bump: bool = True) -> None:
        """The host's writes for one kernel CCB command (ccb.submit), then the kick (EVENT_KICK)
        with the kick's event inputs. `bump=False`: the kicker word is left as it is (E819 Q3)."""
        s, lay = self.s, self.lay
        e = self.seeds["events"]
        s.event_ir0, s.event_tim = e["kick_ir0"], e["kick_tim"]
        offset = s.load32(lay.addr[facts.CCB_CTL])
        kicker = s.load32(lay.addr[facts.KICKER])
        for target, off, value in ccb.submit(self.boot_data.kick, cmd, data, offset, kicker):
            if target == "ccb":
                for i, w in enumerate(struct.unpack("<8I", value)):
                    s.store32(lay.addr[facts.CCB] + off + 4 * i, w)
            elif target == "ccb_ctl.write_offset":
                s.store32(lay.addr[facts.CCB_CTL], value)
            elif target == "event_kicker":
                if bump:
                    s.store32(lay.addr[facts.KICKER], value)
            else:
                s.write_reg(off // 4, value)
        s.run(s.steps + max_steps)

    def get_misc_info(self) -> list[int]:
        misc = self.lay.addr[facts.MISC]
        self.s.store32(misc, MISCINFO_GET_STRUCT_SIZES)
        for i in range(1, 21):
            self.s.store32(misc + 4 * i, 0)
        self.submit("GETMISCINFO", ccb.get_misc_info(misc))
        return [self.s.load32(misc + 4 * i) for i in range(21)]

    def arm(self) -> None:
        """The kernel's boot and the arm each send a GETMISCINFO: K = 2 after them (E768)."""
        self.get_misc_info()
        self.get_misc_info()

    def power_idle(self) -> None:
        self.submit("POWER", ccb.power(ccb.POWERCMD_IDLE))

    # -- what the run shows ---------------------------------------------------------------

    def host_ctl(self) -> list[int]:
        return [self.s.load32(self.host + 4 * i) for i in range(17)]

    def ccb_offsets(self) -> tuple[int, int]:
        c = self.lay.addr[facts.CCB_CTL]
        return self.s.load32(c), self.s.load32(c + 4)

    def events(self) -> list[dict]:
        return [json.loads(line) for line in self.s.trace_events()]


def entries(evs: list[dict]) -> list[dict]:
    """The task entries of a stretch of trace."""
    return [e for e in evs if e["ev"] == "task"]


def summary(run: Run, evs: list[dict], phases: list[tuple[str, int, int, list[int], list[int]]],
            refusal: str | None) -> list[str]:
    """facts.txt: counts and values only (no instruction text, no index beyond E146's slots)."""
    out = [f"firmware sha256 {hashlib.sha256(run.fw.read_bytes()).hexdigest()}",
           "assumption alu_specials_in_movs = true (PDS #13 passes ir1 and tim on to its task; R5)",
           "[time] a kick's tim is set to the tick's word (seeds.toml [events]); E746 reads it as a "
           "sample of the counter"]
    for r in run.seeds.get("seed", []):
        out.append(f"seed 0x{r['reg']:04x} {r['name']} = 0x{r['value']:08x} ({r['cite']})")
    for r in run.seeds.get("rule", []):
        out.append(f"rule 0x{r['reg']:04x} {r['name']} {r['kind']} from 0x{r['value']:08x} ({r['cite']}) [infer]")
    c = run.seeds["carry"]
    out.append(f"carry at the first tick entry: pclink 0x{c['pclink']:x}, p {c['p']} ({c['cite']})")
    for name, lo, hi, before, after in phases:
        stretch = evs[lo:hi]
        w = [(e["reg"], e["value"]) for e in stretch if e["ev"] == "wr" and not e["host"]]
        out.append(f"phase {name}: passes {sum(e['ev'] == 'pass' for e in stretch)}, firmware register "
                   f"writes {len(w)}" + (": " + ", ".join(f"{r}={v}" for r, v in w[:64]) if w else ""))
        ch = [f"dword {i} 0x{b:x}->0x{a:x}" for i, (b, a) in enumerate(zip(before, after)) if a != b]
        out.append(f"phase {name}: HostCtl changed: {', '.join(ch) or 'none'}")
        slots = collections.Counter(SLOTS.get(e["pc"], "other") for e in entries(stretch))
        out.append(f"phase {name}: task entries by PDS #13 slot (E146): "
                   + ", ".join(f"{k}: {v}" for k, v in sorted(slots.items(), key=str)))
        ins = [e for e in entries(stretch) if e["pc"] == 6]
        for tag, e in (("first", ins[0]), ("last", ins[-1])) if ins else ():
            out.append(f"phase {name}: {tag} slot 0 entry pa0-pa2 {e['pa'][:3]}")
        reads = collections.Counter((e["reg"], e["source"]) for e in stretch if e["ev"] == "rd")
        out.append(f"phase {name}: firmware register reads: "
                   + (", ".join(f"{r} {s} x{n}" for (r, s), n in sorted(reads.items())) or "none"))
    out.append("refused reads: " + (", ".join(f"0x{i * 4:04x} x{n}" for i, n in
                                              sorted(run.s.hw_refused().items())) or "none"))
    out.append("answered reads by source: " + ", ".join(f"{k} {v}" for k, v in sorted(run.s.hw_answered().items())))
    if refusal:
        out.append(f"stopped: {refusal}")
    return out


def git_commit() -> str:
    r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True, text=True)
    dirty = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=REPO,
                           capture_output=True, text=True).stdout.strip()
    return r.stdout.strip() + ("-dirty" if dirty else "")


def idle(ticks: int, out: pathlib.Path, power: bool, data: pathlib.Path, fw: pathlib.Path,
         private: pathlib.Path) -> list[str]:
    """The M1 idle scenario: boot, arm (two GETMISCINFO), `ticks` tick passes, then optionally
    POWER IDLE. Writes run.toml, trace.jsonl.gz, facts.txt and output.txt into `out`."""
    out = checked_out(out, private)
    out.mkdir(parents=True, exist_ok=True)
    trace = out / "trace.jsonl"
    run = Run(fw, data, trace=trace, private=private)
    log, phases, refusal = [], [], None

    def phase(name, fn):
        nonlocal refusal
        before = run.host_ctl()
        try:
            fn()
        except Exception as e:      # the run's stop: listed, not hidden
            refusal = f"{name}: {type(e).__name__}"
        phases.append((name, before, run.host_ctl()))
        log.append(f"{name}: {'stopped' if refusal and refusal.startswith(name) else 'ok'}")
        return refusal is None

    ok = phase("boot", run.boot) and phase("arm", run.arm)
    ok = ok and phase(f"ticks x{ticks}", lambda: [run.tick() for _ in range(ticks)])
    if ok and power:
        phase("power idle", run.power_idle)
    run.s.finish_trace()
    with open(trace, "rb") as f, gzip.open(out / "trace.jsonl.gz", "wb") as g:
        shutil.copyfileobj(f, g)
    evs = [json.loads(line) for line in gzip.open(out / "trace.jsonl.gz", "rt")]
    trace.unlink()
    cut = _cuts(evs, [p[0] for p in phases], ticks)
    phases = [(name, lo, hi, b, a) for (name, b, a), (lo, hi) in zip(phases, cut)]
    lines = summary(run, evs, phases, refusal)
    (out / "facts.txt").write_text("\n".join(lines) + "\n")
    meta = {
        "scenario": "idle", "ticks": ticks, "power": power,
        "firmware_sha256": hashlib.sha256(fw.read_bytes()).hexdigest(),
        "resgx545_commit": git_commit(),
        "seeds_sha256": hashlib.sha256(SEEDS.read_bytes()).hexdigest(),
        "data": str(data.name), "passes": run.s.passes, "steps": run.s.steps,
    }
    (out / "run.toml").write_text("".join(f"{k} = {json.dumps(v)}\n" for k, v in meta.items()))
    log += [f"passes {run.s.passes}", f"refused {sum(run.s.hw_refused().values())}"]
    (out / "output.txt").write_text("\n".join(log) + "\n")
    return log


def _cuts(evs: list[dict], names: list[str], ticks: int) -> list[tuple[int, int]]:
    """Trace index ranges of the phases: the boot is one pass, the arm two, the ticks `ticks`,
    the power command one (a stop ends the phase it is in)."""
    want = {"boot": 1, "arm": 2, "power idle": 1}
    ends = [i + 1 for i, e in enumerate(evs) if e["ev"] in ("pass", "refusal")]
    cuts, lo, k = [], 0, 0
    for name in names:
        k += want.get(name, ticks)
        hi = ends[min(k, len(ends)) - 1] if ends else 0
        cuts.append((lo, hi))
        lo = hi
    return cuts


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("idle", help="boot, arm, N ticks (M1)")
    a.add_argument("--ticks", type=int, default=1000)
    a.add_argument("--power", action="store_true", help="then POWER IDLE")
    a.add_argument("--out", type=pathlib.Path, required=True)
    args = ap.parse_args(argv)
    private, fw, data = private_dir(), find_fw(), kept.data_dir()
    if private is None or fw is None or data is None:
        print("fwsim: needs the private firmware and both data repositories", file=sys.stderr)
        return 2
    for line in idle(args.ticks, args.out, args.power, data, fw, private):
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
