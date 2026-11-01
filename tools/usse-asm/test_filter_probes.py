# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The firh tables probes/usse/filter-{sets,taps,gain,control}.toml: the eight coefficient
sets on the impulse inputs, with the USE filter block left alone (load0), loaded with the
values the closed driver writes for an NV12 stream (nv12) and loaded with distinct bytes 1-36
(ramp), through the transfer command's ten words and its load flag (xfer:17 bit 2): which
sets the block feeds, and which byte feeds which tap; one tap byte alone at a time; the
value of each byte; and the control word at eight values."""
import pathlib

import pytest

import probe

USSE = probe.PROBES / "usse"
SRC = USSE / "templates"


def _table(name):
    return {p.name: p for p in probe.load(USSE / f"{name}.toml")}


@pytest.fixture(scope="module")
def table():
    return _table("filter-sets")


def test_eight_sets_under_three_loads(table):
    names = {f"usse-filter-sets-firh-fcs{f}-{c}" for f in range(8)
             for c in ("load0", "nv12", "ramp")}
    assert names <= set(table)
    for f in range(8):
        for c in ("load0", "nv12", "ramp"):
            p = table[f"usse-filter-sets-firh-fcs{f}-{c}"]
            assert len(p.cases) == 17
            assert all(c0[0] == f"firh r10, r1, r2, r3, u8, rep, fcs{f}, #0, #0"
                       for c0 in p.cases)


def test_pokes(table):
    assert table["usse-filter-sets-firh-fcs0-load0"].pokes == []
    nv12 = table["usse-filter-sets-firh-fcs3-nv12"].pokes
    assert nv12[0] == "xfer:17^=0x4" and "xfer:32=0x3" in nv12
    assert "xfer:33=0x66" in nv12 and "xfer:41=0xdd655" in nv12
    ramp = table["usse-filter-sets-firh-fcs7-ramp"].pokes
    assert ramp[:2] == ["xfer:17^=0x4", "xfer:32=0x3"]
    word = [(4 * w + 4) << 24 | (4 * w + 3) << 16 | (4 * w + 2) << 8 | (4 * w + 1)
            for w in range(9)]
    assert ramp[2:] == [f"xfer:{33 + w}=0x{word[w]:08x}" for w in range(9)]


def test_every_case_assembles(table, tmp_path):
    for p in table.values():
        probe.build(p, tmp_path, SRC)


def test_order_probes(table):
    """Each tap byte of sets 0-2 alone at 1, with the centre moved to byte 4."""
    order = {n for n in table if "-firh-s4-" in n}
    assert len(order) == 3 * 8 and "usse-filter-sets-firh-s4-fcs2-w1b3" in order
    assert table["usse-filter-sets-firh-s4-fcs2-w1b3"].cases[0][0] == \
        "firh r10, r1, r2, r3, u8, rep, fcs2, #4, #0"


def test_taps_load_one_byte_at_a_time():
    # sets 1-5, each of the 36 data bytes (xfer:33-41) alone at 0x40, 0x0a9c (xfer:32) at 3,
    # as the cases of one probe (a case's own pokes); the sets 0-2 again with 0x0a9c at 3, 7
    taps = _table("filter-taps")
    assert set(taps) == {f"usse-filter-taps-firh-fcs{f}" for f in range(1, 6)} | \
        {f"usse-filter-taps-firh-fcs{f}-e{e}" for f in range(3) for e in (3, 7)}
    p = taps["usse-filter-taps-firh-fcs3"]
    assert p.pokes == ["xfer:17^=0x4", "xfer:32=0x3"]
    assert len(p.cases) == len(p.case_set) == 36 * 13
    # byte 2 of word 4: 13 cases per byte, the byte's cases after the (w, b) = (0, 0) ones
    assert p.case_set[(4 * 4 + 2) * 13]["pokes"] == [
        f"xfer:{33 + w}=0x{(0x40 << 16) if w == 4 else 0:08x}" for w in range(9)]
    assert all(c[0] == "firh r10, r1, r2, r3, u8, rep, fcs3, #0, #0" for c in p.cases)
    e7 = taps["usse-filter-taps-firh-fcs0-e7"]
    assert e7.pokes == ["xfer:17^=0x4", "xfer:32=0x7"]
    assert e7.case_set[0]["pokes"][0] == "xfer:33=0x00000004"        # the byte at 0x04


def test_gain_values_per_byte():
    # tap words (A, B): every byte at 1, 2, 0x80, 0xff; bias word: bytes 0-1 at those,
    # bytes 2-3 at 1 and 0x80; sets 0-2 (their groups: xfer:33-35, 36-38, 39-41)
    gain = _table("filter-gain")
    assert len(gain) == 3 * (8 * 4 + 2 * 4 + 2 * 2)
    p = gain["usse-filter-gain-firh-fcs1-w1b2-v80"]     # set 1's B word (xfer:37), byte 2
    assert p.pokes[:2] == ["xfer:17^=0x4", "xfer:32=0x3"]
    assert p.pokes[2:] == [f"xfer:{36 + i}=0x{0x800000 if i == 1 else 0:08x}" for i in range(3)]
    assert "usse-filter-gain-firh-fcs2-w2b3-v80" in gain
    assert "usse-filter-gain-firh-fcs2-w2b3-vff" not in gain
    assert len(p.cases) == 17
    assert [c[1:4] for c in p.cases[13:]] == [[0x10, 0, 0], [0xC0, 0, 0], [0, 0x10, 0],
                                             [0, 0xC0, 0]]


def test_control_probes():
    """Sets 0-2 each loaded with an identity filter (the centre tap 1, shift 0), 0x0a9c
    (xfer:32) at eight values, sets 0-5 run on the impulse inputs."""
    ctrl = _table("filter-control")
    assert len(ctrl) == 6 * 8 and "usse-filter-control-firh-fcs5-c0xffffffff" in ctrl
    assert ctrl["usse-filter-control-firh-fcs0-c0x0"].pokes == [
        "xfer:17^=0x4", "xfer:32=0x0", "xfer:33=0x00000001", "xfer:34=0x00000000",
        "xfer:35=0x00000000", "xfer:36=0x00000001", "xfer:37=0x00000000", "xfer:38=0x00000000",
        "xfer:39=0x00000001", "xfer:40=0x00000000", "xfer:41=0x00000000"]
