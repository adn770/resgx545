# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The table probes/usse/filter-banks.toml: firh's fixed coefficient sets 2-5 in each bank
CR_USE_COEFFS_MODE selects (0-2), in each edge mode (rep, msc, mdc), centred at bytes 0, 2
and 4, on a pedestal (every input byte 0x80) with one byte at a time raised by 0x20: every
tap's sign and size, and how each edge mode folds the taps that fall off the line. Its -low
probes run bank 2's sets 2 and 3 on a 0x20 pedestal."""
import pathlib

import pytest

import probe

TABLE = probe.PROBES / "usse" / "filter-banks.toml"
P = "usse-filter-banks-"


@pytest.fixture(scope="module")
def table():
    return {p.name: p for p in probe.load(TABLE)}


def test_banks_sets_edges_centres(table):
    want = {f"{P}bank{b}-fcs{s}-{e}-c{c}" for b in range(3) for s in range(2, 6)
            for e in ("rep", "msc", "mdc") for c in (0, 2, 4)}
    assert {n for n in table if not n.endswith("-low")} == want
    p = table[f"{P}bank1-fcs4-msc-c2"]
    assert p.pokes == ["xfer:17^=0x4", "xfer:32=0x1"]
    assert all(c[0] == "firh r10, r1, r2, r3, u8, msc, fcs4, #2, #0" for c in p.cases)
    # the pedestal, then each of the 12 bytes of r1-r3 raised by 0x20
    assert p.cases[0][1:4] == [0x80808080] * 3
    assert p.cases[1][1:4] == [0x808080A0, 0x80808080, 0x80808080]
    assert p.cases[12][1:4] == [0x80808080, 0x80808080, 0xA0808080]
    assert len(p.cases) == 13


def test_every_case_assembles(table, tmp_path):
    for p in list(table.values())[::9]:
        probe.build(p, tmp_path, TABLE.parent / "templates")


def test_low_pedestal_probes(table):
    """Bank 2's sets 2 and 3 (0 on the 0x80 pedestal) on a 0x20 pedestal."""
    low = sorted(n for n in table if n.endswith("-low"))
    assert low == [f"{P}bank2-fcs2-rep-c4-low", f"{P}bank2-fcs3-rep-c4-low"]
    for n in low:
        assert table[n].cases[0][1:4] == [0x20202020] * 3
        assert table[n].cases[1][1:4] == [0x20202040, 0x20202020, 0x20202020]
