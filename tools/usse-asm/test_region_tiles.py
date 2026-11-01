# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""region_tiles.py: which 16 x 16 tiles of a 32 x 16 region a triangle covers, against the
form of the region's stream entry."""
from __future__ import annotations

import region_tiles as rt


def test_the_two_tests():
    """Touching counts everywhere but in the bounding-box test on the line between the tiles:
    a triangle whose leftmost point is on x 16 is the right tile's only, one up to x 16 meets
    both, one touching x 32 or the bottom meets the right tile, and an edge through the
    corner at x 16 meets the left tile too."""
    assert rt.tiles([(16, 0), (40, 0), (16, 16)], 0, 0) == (False, True)
    assert rt.tiles([(0, 0), (16, 0), (0, 16)], 0, 0) == (True, True)
    assert rt.tiles([(-8, 0), (0, 0), (-8, 16)], 0, 0) == (True, False)
    assert rt.tiles([(32, 0), (40, 0), (40, 16)], 0, 0) == (False, True)
    assert rt.tiles([(20, 16), (28, 16), (24, 24)], 0, 0) == (False, True)
    assert rt.tiles([(12, 24), (24, 24), (24, 0)], 0, 0) == (True, True)    # edge via (16, 16)
    assert rt.tiles([(0, 0), (32, 0), (0, 16)], 0, 0) == (True, True)
    assert rt.tiles([(0, 0), (8, 0), (0, 8)], 0, 0) == (True, False)


def test_triangle_of_a_sweep_name():
    """ta-regions-sweep-x06: our triangle on 128 x 128 shifted 6 pixels in x."""
    assert rt.triangle("ta-regions-sweep-x06__0") == [(22.0, 16.0), (118.0, 40.0), (46.0, 112.0)]
    assert rt.triangle("ta-regions-sweep-y04__0")[0] == (16.0, 20.0)


def test_table_reads_the_sweep_dumps(tmp_path):
    """table() reads the ta-regions-sweep-* dumps of probes/ta/regions.toml and no others."""
    import struct
    td = bytearray(5 * 4096)
    td[4 * 4096:4 * 4096 + 4] = struct.pack("<I", 0x04000000)
    td[4 * 4096 + 4:4 * 4096 + 8] = struct.pack("<I", 0x2000)
    param = bytearray(3 * 4096)
    param[4096:4100] = struct.pack("<I", 0x4490ffff)
    param[4100:4104] = struct.pack("<I", 0xc0000000)
    for stem in ("ta-regions-sweep-x00__0", "ta-regions-scene-two__0"):
        (tmp_path / f"{stem}.param.bin").write_bytes(param)
        (tmp_path / f"{stem}.tadata.bin").write_bytes(td)
    ((key, forms),) = rt.table(tmp_path).items()
    assert forms == {"4490": 1} and len(key) == 2
