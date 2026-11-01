# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""firh_banks.py: the fixed-bank families of firh, rebuilt from the data repository's vectors."""
from __future__ import annotations

import pytest

import firh_banks as F

DATA = F.data_dir()


def test_positions_fold_by_the_edge_mode():
    line = list(range(10, 22))
    assert [F.at(line, 0, i) for i in (-2, -1, 0, 11, 12, 13)] == [10, 10, 10, 21, 21, 21]
    assert [F.at(line, 1, i) for i in (-2, -1, 12, 13)] == [12, 11, 20, 19]
    assert [F.at(line, 2, i) for i in (-2, -1, 12, 13)] == [11, 10, 21, 20]


def test_the_bias_range_is_what_every_case_allows():
    # [64 64]/128 of 0x40 and 0x40 at shift 7: 64 + bias >> 7 == 64 for bias 0..127
    case = {"line": [0x40] * 12, "edge": 0, "s": 4, "byte": 0x40}
    assert F.interval([case], [64, 64], 0) == (0, 127)
    # 0x40 and 0x41 still giving 0x40 needs a bias below 64
    lifted = {"line": [0x40, 0x41] + [0x40] * 10, "edge": 0, "s": 0, "byte": 0x40}
    assert F.interval([case, lifted], [64, 64], 0) == (0, 63)
    # and one no bias fits empties it
    assert F.interval([case, {**case, "byte": 0x50}], [64, 64], 0) is None


def test_the_centres_are_e079_times_4_and_e293():
    assert F.CENTRES[(1, 2)][0] == [-8, 72, 72, -8]         # -2 18 18 -2
    assert F.CENTRES[(1, 4)][0] == [-8, 108, 36, -4]        # -2 27 9 -1
    assert F.CENTRES[(1, 5)][0] == [-8, 104, 36, -8]        # -2 26 9 -2
    assert F.CENTRES[(2, 4)][0] == [16, 32, 32, 32, 16]     # 4 8 8 8 4
    assert F.CENTRES[(2, 3)] == ([128, -256, 64, 64], -2)   # E293
    assert (F.WINDOW, F.SHIFT) == (5, 7)


@pytest.mark.skipif(not (DATA / "vectors" / "usse" / "filter-banks").is_dir(),
                    reason="no resgx545-data (set RESGX545_DATA)")
def test_the_simulator_s_table_is_rebuilt_from_the_data():
    fams = F.families(F.cases(DATA))
    sizes = {k: (n, len(f)) for k, (n, f) in fams.items()}
    assert sizes == {(1, 2): (130, 18), (1, 3): (130, 18), (1, 4): (130, 13), (1, 5): (130, 13),
                     (2, 2): (166, 7), (2, 3): (166, 7), (2, 4): (130, 11), (2, 5): (130, 11)}
    # the measured filter is a member, and the table in usse.rs is this one
    assert ([-8, 72, 72, -8], 0, 127) in fams[(1, 2)][1]
    assert F.rust(fams) == F.in_tree()
