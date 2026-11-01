# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""markers.py: fresh markers per job and the check that flags fixed-marker write tests."""
from __future__ import annotations

import pathlib

import markers
import probe

TEMPLATE = "phas #0, #0, pixel, end, parallel\n{OP}\nstad [r1,+#0], r2\n"


def _probe(name: str, cases: list, source: str = "temps.s") -> probe.Probe:
    return probe.Probe(name=name, question="q", source=source, params={}, inputs=["OP"],
                       cases=cases, hypotheses={})


def _src(tmp_path: pathlib.Path) -> pathlib.Path:
    (tmp_path / "temps.s").write_text(TEMPLATE)
    (tmp_path / "other.s").write_text(TEMPLATE)
    return tmp_path


def test_fresh_markers_are_distinct_reproducible_and_not_leftovers():
    a = markers.fresh_markers(500, 1135)
    assert a == markers.fresh_markers(500, 1135) and a != markers.fresh_markers(500, 1136)
    assert len(set(a)) == 500
    for m in a:
        assert m >> 28 == 7 and m & 0xffff not in (0, 0xffff)
        assert m >> 16 & 0xffff not in (0x7000, 0x7fff)


def test_the_same_marker_in_two_jobs_is_flagged(tmp_path):
    src = _src(tmp_path)
    p = _probe("x", [["mov.skipinv r2, #0x7E570002"], ["mov.skipinv r2, #0x7E570002"],
                     ["mov.skipinv r2, #0x7E570003"]])
    assert markers.fixed_marker_writes([p], src) == {(2, 0x7E570002): ["x__0", "x__1"]}


def test_a_marker_of_its_own_per_job_is_not_flagged(tmp_path):
    src = _src(tmp_path)
    ms = markers.fresh_markers(4, 7)
    p = _probe("x", [[f"mov.skipinv r2, #0x{m:08X}"] for m in ms])
    assert markers.fixed_marker_writes([p], src) == {}


def test_the_same_marker_in_two_probes_of_a_table_is_flagged(tmp_path):
    src = _src(tmp_path)
    a, b = (_probe(n, [["mov.skipinv r2, #0x7E570002"]]) for n in "ab")
    assert list(markers.fixed_marker_writes([a, b], src).values()) == [["a__0", "b__0"]]


def test_small_constants_and_the_scratch_pointer_are_not_markers(tmp_path):
    src = _src(tmp_path)
    p = _probe("x", [["mov.skipinv r1, #0x5CAF0000\nmov.skipinv r2, #5"]] * 2)
    assert markers.fixed_marker_writes([p], src) == {}


def test_only_the_register_write_templates_are_checked(tmp_path):
    src = _src(tmp_path)
    p = _probe("x", [["mov.skipinv r2, #0x7E570002"]] * 2, source="other.s")
    assert markers.fixed_marker_writes([p], src) == {}
    assert markers.fixed_marker_writes([p], src, sources=("other.s",))


# The tables of the register-write family that write one marker to one register in every job
# (the capture audit, D7): E484's persistence makes their read-back no proof of a landed write.
# A new table must not join this list: it takes its markers from fresh_markers.
FIXED = {"phas-high-a", "phas-high-b", "phas-high-c", "phas-high-d", "phas-high-e", "phas-low",
         "phas-mod", "temps-bound", "temps-bound2", "temps-bound3", "temps-max", "temps-past",
         "temps-sparse", "temps-wrap"}


def test_the_tables_with_fixed_markers_are_the_known_ones():
    flagged = set()
    for t in sorted(probe.PROBES.glob("*/*.toml")):
        if "[[probe]]" not in t.read_text():
            continue
        src = t.parent / "templates"
        if markers.fixed_marker_writes(probe.load(t), src if src.is_dir() else probe.PROBES_DIR):
            flagged.add(t.stem)
    assert flagged == FIXED, sorted(flagged ^ FIXED)


def test_fresh_halves_are_distinct_and_not_the_old_fixed_half():
    a = markers.fresh_halves(300, 1135)
    assert a == markers.fresh_halves(300, 1135) and len(set(a)) == 300
    assert all(0x1000 <= h < 0xf000 and h not in (0x7E57, 0x1E57) for h in a)
