# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The alpha-test table probes/usse/alpha-test.toml: atst8 in a fill's pixel task, on sources
r1-r3 set from the case, in each feedback mode, its destination r10 and predicate p0 read
back (r11 set when p0 holds, r12 when not): what it tests and what it writes."""
import pathlib

import pytest

import probe

HERE = pathlib.Path(__file__).resolve().parent
TABLE = probe.PROBES / "usse" / "alpha-test.toml"
SRC0 = [0, 0x01000000, 0x7F000000, 0x80000000, 0xFF000000, 0x000000FF, 0x0000FF00,
        0x00FF0000, 0xFFFFFFFF]


@pytest.fixture(scope="module")
def table():
    return {p.name: p for p in probe.load(TABLE)}


def test_nfb_grid(table):
    p = table["usse-alpha-test-atst8-nfb"]
    ops = {c[0] for c in p.cases}
    assert len(ops) == 1
    op = ops.pop()
    assert op.startswith("and.skipinv.testtanz.chan0 !r0, p0, #0x00000001, #1\n"
                         "atst8 r10, p0, r1, r2, r3, nfb\n")
    assert "p0 mov.skipinv r11, #0x11111111" in op and "!p0 mov.skipinv r12, #0x22222222" in op
    assert len(p.cases) == 9 * 5 * 13
    assert {c[1] for c in p.cases} == set(SRC0)


def test_follow_ups(table):
    assert len(table["usse-alpha-test-atst8-src2-bits"].cases) == 32
    assert len(table["usse-alpha-test-atst8-bytes"].cases) == 12
    assert [c[3] >> 13 & 7 for c in table["usse-alpha-test-atst8-func"].cases] == [f for f in range(8)
                                                                      for _ in range(3)]
    modes = {c[0].split("\n")[1] for c in table["usse-alpha-test-atst8-modes"].cases}
    assert modes == {f"atst8 r10, p0, r1, r2, r3, {m}" for m in ("nfb", "fb", "optdwd",
                                                                  "twosided, nfb")}


def test_pcoeff_depthf(table):
    ops = [c[0].split("\n")[1] for c in table["usse-alpha-test-pcoeff-depthf"].cases]
    assert ops[0] == "nop" and "pcoeff r1, r2, r3" in ops and len(ops) == 6


def test_feedback_modes(table):
    for mode in ("fb", "optdwd"):
        p = table[f"usse-alpha-test-atst8-{mode}"]
        assert {c[0].split("\n")[1] for c in p.cases} == {f"atst8 r10, p0, r1, r2, r3, {mode}"}
        assert [c[1] for c in p.cases] == SRC0
