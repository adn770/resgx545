# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""region_tiles.py: which 16 x 16 tiles of a 32 x 16 region a triangle covers, against the
control stream's PRIM_TILES field (the primitive word's bits 23:16, E180)."""
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


def _dumps(d, stems, prim=0x4490ffff):
    """A TA data dump with one streamed region (column 0, row 0) and a parameter dump whose
    stream starts with the primitive word prim, for each stem."""
    import struct
    td = bytearray(5 * 4096)
    td[4 * 4096:4 * 4096 + 4] = struct.pack("<I", 0x04000000)
    td[4 * 4096 + 4:4 * 4096 + 8] = struct.pack("<I", 0x2000)
    param = bytearray(3 * 4096)
    param[4096:4100] = struct.pack("<I", prim)
    param[4100:4104] = struct.pack("<I", 0xc0000000)
    d.mkdir(parents=True, exist_ok=True)
    for stem in stems:
        (d / f"{stem}.param.bin").write_bytes(param)
        (d / f"{stem}.tadata.bin").write_bytes(td)


def test_table_reads_the_sweep_dumps(tmp_path):
    """table() reads the ta-regions-sweep-* dumps of probes/ta/regions.toml and no others, and
    counts each region by its PRIM_TILES field."""
    _dumps(tmp_path, ("ta-regions-sweep-x00__0", "ta-regions-scene-two__0"))
    ((key, forms),) = rt.table(tmp_path).items()
    assert forms == {0x90: 1} and len(key) == 2


def test_table_reads_the_datasets_layout(tmp_path):
    """The ta-regions dataset keeps each probe's dumps in <probe>/dumps/: table() finds them
    under the directory it is given."""
    _dumps(tmp_path / "ta-regions-sweep-x00" / "dumps", ("ta-regions-sweep-x00__0",))
    _dumps(tmp_path / "ta-regions-sweep-y02" / "dumps", ("ta-regions-sweep-y02__0",), 0x44980701)
    _dumps(tmp_path / "ta-regions-scene-two" / "dumps", ("ta-regions-scene-two__0",))
    got = {}
    for c in rt.table(tmp_path).values():
        for form, n in c.items():
            got[form] = got.get(form, 0) + n
    assert got == {0x90: 1, 0x98: 1}


def test_the_key_is_the_prim_tiles_field():
    """PRIM_TILES, the primitive word's bits 23:16 (pbdump's CSTREAM fields), not the word's
    top half: bit 24 and the vertex count above it do not change the form."""
    assert rt.prim_tiles(0x44980701) == 0x98
    assert rt.prim_tiles(0x5c8a7fff) == 0x8a
    assert rt.prim_tiles(0x4a903f03) == rt.prim_tiles(0x4490ffff) == 0x90


def test_the_forms_of_the_tile_pairs():
    """E180: 0x80 the left tile only, 0x98 the right only, 0x90 both; with masks too wide for
    the word, 0x8a the left and 0x8c the right."""
    assert rt.TILE_FORMS == {(True, False): (0x80, 0x8a), (False, True): (0x98, 0x8c),
                             (True, True): (0x90,)}


def test_agreement_counts_the_regions_whose_form_the_tile_test_gives():
    import collections
    t = {(True, True): collections.Counter({0x90: 3, 0x98: 1}),
         (True, False): collections.Counter({0x80: 2, 0x8a: 1}),
         (False, True): collections.Counter({0x8c: 1, 0x8a: 1}),
         (False, False): collections.Counter({0x90: 1})}
    assert rt.agreement(t) == (7, 10)


def test_main_prints_the_fields_and_the_agreement(tmp_path, capsys):
    _dumps(tmp_path, ("ta-regions-sweep-x00__0",))
    assert rt.main([str(tmp_path)]) == 0
    out = capsys.readouterr().out.splitlines()
    assert out[0].endswith(": PRIM_TILES 0x90 1") and out[0].startswith("left ")
    pair = rt.tiles(rt.triangle("ta-regions-sweep-x00__0"), 0, 0)
    agree = int(0x90 in rt.TILE_FORMS.get(pair, ()))
    assert out[-1] == f"regions whose PRIM_TILES is their tile pair's form: {agree} of 1"
