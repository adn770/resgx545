# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""unit_vectors.py against the data repository: the unit vectors of 12.0 (zls-store, te-region,
ta-object, isp-tile) carry the counts their records state. Skips (with the reason) when the data
repository is absent."""
import json
import os
import pathlib

import pytest

import unit_vectors as uv

ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA = pathlib.Path(os.environ.get("RESGX545_DATA") or ROOT.parent / "resgx545-data")

pytestmark = pytest.mark.skipif(not (DATA / "zls/store-layout-dumps/recompute.txt").is_file(),
                                reason="no resgx545-data (set RESGX545_DATA)")


def vectors(fn):
    return fn(DATA)


def test_zls_store_has_the_18_cases_and_the_counts_of_e489():
    vs = vectors(uv.zls_store)
    assert len(vs) == 18
    assert sum(v["expect"]["stored"] for v in vs) == 3415552
    # 3279132 dwords at the rule's address: 3225000 for pixels of the target, 54132 past it in the
    # band, and 1124 of background past the band (E831: matched, none refused at these even sizes)
    assert sum(v["expect"]["matched"] for v in vs) == 3225000 + 54132 + 1124
    assert sum(v["expect"]["refused"].get("Q107", 0) for v in vs) == 128640 + 6656
    assert not any(set(v["expect"]["refused"]) - {"Q107"} for v in vs)
    assert all(v["provenance"]["questions"] == ["Q107"] for v in vs)
    assert all("E831" in v["provenance"]["records"] for v in vs)
    assert all(v["init"]["task"] == "zls-store" and len(v["init"]["x"]["sha256"]) == 64 for v in vs)


def test_zls_classes_follow_the_band_of_e831_and_leave_odd_sizes_to_q287():
    import struct

    def ramp(p, size):
        return struct.unpack("<I", struct.pack("<f", 0.25 + 0.5 * (p + 0.5) / (3 * size)))[0]

    def dumps(w, h, cells):
        # 34 x 18 or 35 x 18 at G = 3: one slot a tile, tiles (0, 0) and (1, 0) used
        ax, ay = [0xDEADBEEF] * 4096, [0xDEADBEEF] * 4096
        for (x, y, vx, vy) in cells:
            i = 512 * (y // 16 * 4 + x // 32) + uv_index(x % 32, y % 16)
            ax[i], ay[i] = vx, vy
        return ax, ay

    def uv_index(x, y):
        i = (x >> 4 & 1) << 8
        for b in range(4):
            i |= (y >> b & 1) << 2 * b | (x >> b & 1) << 2 * b + 1
        return i

    bg = 0x3F800000
    # 34 x 18: the band is x < 42, y < 22; a ramp inside it, background past it, and the reverse
    cells = [(41, 2, ramp(41, 34), ramp(2, 18)), (50, 3, bg, bg),
             (42, 2, ramp(42, 34), ramp(2, 18)), (41, 21, bg, bg)]
    c = uv.zls_classes(34, 18, 3, *dumps(34, 18, cells))
    assert (c["outside"], c["bg_outside"], c["other"]) == (1, 1, 2)
    # 35 x 18: 1.25 W = 43.75, rule A keeps column 43 (E903, odd widths; E885 odd heights)
    cells = [(43, 2, ramp(43, 35), ramp(2, 18)), (50, 3, bg, bg), (44, 4, bg, bg)]
    c = uv.zls_classes(35, 18, 3, *dumps(35, 18, cells))
    assert (c["outside"], c["bg_outside"], c["other"]) == (1, 2, 0) and "odd" not in c


def test_te_region_has_the_35_jobs_and_14656_pairs_with_no_mismatch():
    vs = vectors(uv.te_region)
    assert len(vs) == 35
    assert sum(v["expect"]["matched"] for v in vs) == 14656
    assert all(v["init"]["prims"] for v in vs)


def test_ta_object_has_the_completed_jobs_and_the_three_that_did_not():
    vs = vectors(uv.ta_object)
    done = [v for v in vs if "stored" in v["expect"]]
    failed = [v for v in vs if v["expect"].get("outcome") in ("hang", "fault")]
    assert (len(vs), len(done), len(failed)) == (59, 56, 3)
    assert sorted(v["expect"]["outcome"] for v in failed) == ["fault", "hang", "hang"]
    assert sum(1 for v in done if v["id"].startswith("ta-object__f2-")) == 12


def test_isp_tile_has_the_48_runs_and_the_786_tiles_of_e503():
    vs = vectors(uv.isp_tile)
    assert len(vs) == 48
    assert sum(v["expect"]["tiles"] for v in vs) == 786
    assert sum(v["expect"]["matched"] for v in vs) == 773
    assert sum(v["expect"]["refused"].get("Q141", 0) for v in vs) == 13


def test_written_files_are_the_vector_container_and_deterministic(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    uv.write_all(DATA, a)
    uv.write_all(DATA, b)
    fa = sorted(p.relative_to(a) for p in a.rglob("*.vec.json"))
    assert len(fa) >= 4
    for p in fa:
        assert (a / p).read_bytes() == (b / p).read_bytes()
        d = json.loads((a / p).read_text())
        assert d["format"] == "sgx545-vectors" and d["version"] == 1 and d["vectors"]


def test_pbe_emit_has_the_64_pack_modes_and_the_ten_colours_of_mode_0():
    vs = vectors(uv.pbe_emit)
    by = {v["id"]: v for v in vs}
    modes = [v for v in vs if v["id"].startswith("pbe-emit__packmode-")]
    assert len(modes) == 64
    # modes 0 to 3 carry the stored values, 22 and 34 are refused under Q012, the rest under Q044
    for m, stored in [(0, ["0xff203040", "0x80ff8040"]), (1, ["0xff403020", "0x804080ff"]),
                      (2, ["0x403020ff", "0x4080ff80"]), (3, ["0x2188", "0xfc08"])]:
        v = by["pbe-emit__packmode-%02d" % m]
        assert v["expect"]["stored"] == stored and "refuse" not in v["expect"]
        assert v["init"]["sideband"] == "0x%x" % (0x200 | m)
    assert by["pbe-emit__packmode-22"]["expect"]["refuse"] == ["Q012"]
    assert by["pbe-emit__packmode-34"]["expect"]["refuse"] == ["Q012"]
    assert by["pbe-emit__packmode-14"]["expect"]["refuse"] == ["Q044"]
    colours = [v for v in vs if v["id"].startswith("pbe-emit__colours-mode0-")]
    assert len(colours) == 10
    for v in colours:  # pack mode 0 stores the colour unchanged
        assert v["expect"]["stored"] == v["init"]["colours"]


def test_pack_values_reads_the_two_colours_of_a_mixed_line():
    assert uv.pack_values(["0xff203040x3034", "0x80ff8040x1062"], 4) == ["0xff203040", "0x80ff8040"]
    sixteen = ["0xdeadbeefx2048", "0x21882188x1496", "0xfc08fc08x510", "0xfc082188x24"]
    assert uv.pack_values(sixteen, 2) == ["0x2188", "0xfc08"]
