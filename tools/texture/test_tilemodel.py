# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""tools/texture/tilemodel.py: the 11.32 sampler model with E561's twiddled address reads E564's
kept an-t3b11 (a 64 x 64 chain read at level 0) exactly, where texmodel.py's plain Morton order
first differs at pixel 16 (the control that can fail), and gives E561's dwords of E441's levels.
The dump is read from RESGX545_DATA; the test skips without it."""
import gzip
import json
import os
import pathlib
import re
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "p1132/recompute"))
import texmodel  # noqa: E402
import tilemodel  # noqa: E402

DATA = pathlib.Path(os.environ["RESGX545_DATA"]) if os.environ.get("RESGX545_DATA") else None
DUMP = DATA / "texture/p1132/tx-lod/an-t3b11.txt.gz" if DATA else None
SPEC = json.loads((HERE / "p1132/gen/specs.json").read_text())["an-t3b11"]["spec"]


def kept():
    if DUMP is None or not DUMP.is_file():
        pytest.skip("SKIPPED, NOT PASSED: E564's an-t3b11 dump is not in RESGX545_DATA")
    rows = {int(n): [int(t, 16) for t in v.split()] for n, v in
            re.findall(r"row (\d+):(.*)$", gzip.decompress(DUMP.read_bytes()).decode(), re.M)}
    return [v for y in sorted(rows) for v in rows[y]]


def level0(m):
    """an-t3b11 (T3 bits 12:11 = 00 reads level 0, E1027) through the model's coordinates,
    address and blend at level 0."""
    sp = SPEC
    t = m.Tex(sp["t0"], sp["t1"], sp["base"], sp["t3"], sp.get("pages", 16), dict(m.RULES))
    mn = (sp["t0"] >> 10 & 3) in (1, 2)
    return [t.level_read(m.ev(sp["u"], x, y), m.ev(sp["v"], x, y), 0, mn)
            for y in range(m.H) for x in range(m.W)]


def test_the_tile_model_reads_e564s_an_t3b11_exactly():
    want = kept()
    assert len(want) == 2048
    assert level0(tilemodel.tm) == want


def test_texmodels_plain_order_fails_at_pixel_16_and_is_left_unchanged():
    want = kept()
    got = level0(texmodel)
    assert next(p for p, (a, b) in enumerate(zip(got, want)) if a != b) == 16
    assert texmodel.morton(16, 0, 64, 64) == 512 != tilemodel.tm.morton(16, 0, 64, 64) == 256


def test_the_tile_law_gives_e561s_dwords_and_the_plain_order_up_to_16():
    ti = tilemodel.tile_index
    assert [ti(x, y, n, n) for x, y, n in ((28, 84, 128), (14, 42, 64), (7, 21, 32))] \
        == [0x29B0, 0x8EC, 0x23B]
    for w, h in ((16, 16), (8, 8), (16, 64), (64, 16), (128, 16), (8, 128)):
        assert all(ti(x, y, w, h) == tilemodel.plain(x, y, w, h)
                   for y in range(h) for x in range(w)), (w, h)
