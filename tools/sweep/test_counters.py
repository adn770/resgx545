# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The visibility counters recorded around every sweep case and probe run: the wrapper, the
summary of a run's timeline, and the scan of finished runs for the cases that counted."""
from __future__ import annotations

import counters

OFFS = list(range(0x494, 0x4b8, 4))


def timeline(*rows, regs=OFFS, rc=0):
    head = "timeline: regs " + " ".join(f"{o:#06x}" for o in regs) + \
        f" samples 99 seconds 0 start 0 end 9 rc {rc}\n"
    return head + "".join(f"tl {t} " + " ".join(f"{v:08x}" for v in vals) + "\n"
                          for t, vals in rows)


def test_wrap():
    assert counters.wrap(["./t", "fill"], "./rt") == \
        ["./rt", "0", "0", "0x0494-0x04b4", "--", "./t", "fill"]


def test_with_counters_adds_the_range_once():
    assert counters.with_counters("0x0484-0x0490") == "0x0484-0x0490,0x0494-0x04b4"
    assert counters.with_counters("0x0480-0x04c0") == "0x0480-0x04c0"


def test_summary_none_without_a_timeline():
    assert counters.summary("job: ok\n") is None


def test_summary_zero():
    assert counters.summary("job: ok\n" + timeline((0, [0] * 9))) == ""


def test_summary_first_and_peak_of_each_register_that_counted():
    rows = [(0, [0] * 8 + [4]), (10, [0] * 8 + [0]), (20, [0, 0, 3] + [0] * 5 + [0xe])]
    assert counters.summary(timeline(*rows)) == "0x049c 0x0..0x3, 0x04b4 0x4..0xe"


def test_summary_picks_the_counters_out_of_a_wider_timeline():
    regs = [0x484, *OFFS, 0x4b8]
    text = timeline((0, [7] + [0] * 8 + [1] + [9]), regs=regs)
    assert counters.summary(text) == "0x04b4 0x1..0x1"


def test_scan_sweep_and_probe_runs(tmp_path, capsys):
    hot = timeline((0, [0] * 9), (5, [0] * 8 + [0xe]))
    cold = timeline((0, [0] * 9))
    sw = tmp_path / "s12" / "raw.txt"
    sw.parent.mkdir()
    sw.write_text("".join(f"=== case {cid}\n$ x\njob: ok\n{t}--- stderr\n--- rc 0 0.1 s\n"
                          for cid, t in (("base", cold), ("a", cold), ("b", hot))) +
                  "=== case c\n$ x\njob: ok\n--- stderr\n--- rc 0 0.1 s\n")
    pr = tmp_path / "tri" / "raw.txt"
    pr.parent.mkdir()
    pr.write_text(f"probe-case p__0\nprobe p__0: o0 0x1\n{cold}"
                  f"probe-case p__1\nprobe p__1: o0 0x1\n{hot}")
    assert counters.main(["scan", str(tmp_path)]) == 1
    out = capsys.readouterr().out.splitlines()
    assert f"{sw}: b (0x04b4 0x0..0xe) after a" in out
    assert f"{pr}: p__1 (0x04b4 0x0..0xe) after p__0" in out
    assert out[-1] == "6 cases: 5 recorded, 2 counted"


def test_scan_quiet_corpus_exits_0(tmp_path, capsys):
    (tmp_path / "raw.txt").write_text(f"probe-case p__0\n{timeline((0, [0] * 9))}")
    assert counters.main(["scan", str(tmp_path / "raw.txt")]) == 0
    assert capsys.readouterr().out.splitlines()[-1] == "1 cases: 1 recorded, 0 counted"
