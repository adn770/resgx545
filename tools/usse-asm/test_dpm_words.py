# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Tests of dpm_words.py: the page table, the DPM status words and the DPM state page by the
glossary's names, the 11.9 tables and the readers of the 11.9 scripts' output."""
from __future__ import annotations

import os
import pathlib
import struct
import tomllib

import pytest

import dpm_words

HERE = pathlib.Path(__file__).resolve().parent
DATA = pathlib.Path(os.environ.get("RESGX545_DATA", pathlib.Path.home() / "src" / "resgx545-data"))


def _pt(entries: dict[int, int], pages: int) -> list[int]:
    """A page table: the host's chain over pages, with entries replaced."""
    pt = dpm_words.host_page_table(pages)
    for i, v in entries.items():
        pt[i] = v
    return pt


def test_the_host_chain_links_each_page_to_its_neighbours():
    pt = dpm_words.host_page_table(4)
    assert pt == [0, 0xffff0002, 0x00010003, 0x00020004, 0x0003ffff, 0]


def test_walk_of_the_host_chain_is_every_page_in_order():
    w = dpm_words.walk(dpm_words.host_page_table(0x422), 0x422)
    assert (w["head"], w["tail"], w["prev_of_tail"]) == (1, 0x422, 0x421)
    assert w["order"] == list(range(1, 0x423))
    assert w["bad"] == []
    assert dpm_words.page_runs(w["order"]) == "0x1-0x422"


def test_page_runs_read_back_as_pages():
    assert dpm_words.run_pages("0x3-0x5,0x1") == [3, 4, 5, 1]
    assert dpm_words.run_pages(dpm_words.page_runs([6, 2, 4, 3, 5, 1])) == [6, 2, 4, 3, 5, 1]
    assert dpm_words.run_pages("") == []


def test_walk_after_a_64x64_render_puts_its_two_pages_at_the_tail():
    # the 64x64 job of the free-list table: pages 1 and 2 freed in that order
    pt = _pt({1: 0x04220002, 2: 0x0001ffff, 3: 0xffff0004, 0x422: 0x04210001}, 0x422)
    w = dpm_words.walk(pt, 0x422)
    assert (w["head"], w["tail"], w["prev_of_tail"]) == (3, 2, 1)
    assert dpm_words.page_runs(w["order"]) == "0x3-0x422,0x1-0x2"


def test_walk_reports_a_previous_link_that_does_not_match():
    pt = _pt({3: 0x00070004}, 8)
    w = dpm_words.walk(pt, 8)
    assert w["bad"] == [3]


def test_status1_is_tail_and_head_and_status2_the_page_before_the_tail():
    assert dpm_words.free_list_word(0x00020003) == {"TAIL": 2, "HEAD": 3}
    assert dpm_words.status2_word(0x00000094) == {"PREV": 0x94, "HIGH": 0}


def test_status_check_agrees_with_the_walk():
    pt = _pt({1: 0x04220002, 2: 0x0001ffff, 3: 0xffff0004, 0x422: 0x04210001}, 0x422)
    w = dpm_words.walk(pt, 0x422)
    regs = {0x0700: 0x00020003, 0x070c: 0x00020003, 0x0710: 1, 0x071c: 1}
    assert dpm_words.status_check(regs, w) == []
    regs[0x0710] = 5
    assert dpm_words.status_check(regs, w) == ["0x0710 PREV 0x5, walk 0x1"]


def test_state_page_lists_by_macrotile_and_the_global_list():
    words = [0] * 1024
    words[0:2] = [0x00010002, 0x00000002]
    words[10:12] = [0x00030006, 0x0000000b]
    words[32:34] = [0x00010001, 0x00000001]
    lists = dpm_words.state_lists(words)
    assert lists == [
        {"index": 0, "list": "macrotile 0", "PAGE_COUNT": 1, "HEAD": 2, "TAIL": 2},
        {"index": 5, "list": "macrotile 5", "PAGE_COUNT": 3, "HEAD": 6, "TAIL": 0xb},
        {"index": 16, "list": "global", "PAGE_COUNT": 1, "HEAD": 1, "TAIL": 1},
    ]


def test_state_list_chains_follow_the_page_table():
    pt = _pt({6: 0xffff0009, 9: 0x0006000b, 0xb: 0x0009ffff}, 0x30)
    lst = {"index": 5, "list": "macrotile 5", "PAGE_COUNT": 3, "HEAD": 6, "TAIL": 0xb}
    assert dpm_words.list_chain(pt, lst) == [6, 9, 0xb]


@pytest.mark.parametrize("w,h,want", [
    (64, 64, {"tail": 0, "control": 0x1000, "otpm": 0x2000, "state": 0x3000, "rgn": 0x4000,
              "zls": 0x5000, "size": 0x6000}),
    (1024, 768, {"tail": 0, "control": 0x4000, "otpm": 0x5000, "state": 0x6000,
                 "rgn": 0x7000, "zls": 0xc000, "size": 0x11000}),
    (4096, 4096, {"tail": 0, "control": 0x40000, "otpm": 0x41000, "state": 0x42000,
                  "rgn": 0x43000, "zls": 0xa3000, "size": 0x103000}),
])
def test_tadata_layout_is_the_kernels(w, h, want):
    # sizes of the dumps: 0x6000, 0x11000 and 0x103000 bytes (the free-list table)
    assert dpm_words.tadata_layout(w, h) == want


def test_macrotile_of_a_tile_follows_the_kernels_layout():
    # 1024x768: 32 x 48 tiles, four macrotiles each way of 8 x 12 tiles
    assert dpm_words.mtile_grid(1024, 768) == (4, 8, 12)
    # numbered down, then across: so numbered, the state lists of the 1024x768 and 4096x4096
    # partial renders (dpm-free-list) are the macrotiles the images lose
    assert dpm_words.macrotile(0, 0, 1024, 768) == 0
    assert dpm_words.macrotile(8, 0, 1024, 768) == 4
    assert dpm_words.macrotile(0, 12, 1024, 768) == 1
    assert dpm_words.macrotile(31, 47, 1024, 768) == 15
    # 64x64: two each way of 4 x 4 tiles (whole 4-tile blocks)
    assert dpm_words.mtile_grid(64, 64) == (2, 4, 4)


FREE_LIST_OUT = """\
== full-64x64: probe --tri pixel 64x64 max 64x64 pb 0x422
probe dpm-free-list-green__0: o0 mixed 0xff203040 x3034 0xff00ff00 x1062
regs: reg 0x0700 0x00020003 reg 0x070c 0x00020003 reg 0x0710 0x00000001 reg 0x063c skip
ta3dctl: 00000001 00000002
pt: walk 1058 pages, tail 0x2 prev of tail 0x1 bad prev 0
pt: order 0x3-0x422,0x1-0x2
tadata state: nonzero 2 0x000=0x00010002 0x004=0x00000002
== next: x
"""


def test_free_list_reader_takes_registers_dumps_and_control_block():
    c = dpm_words.case_free_list(FREE_LIST_OUT)["full-64x64"]
    assert c["regs"] == {0x0700: 0x00020003, 0x070c: 0x00020003, 0x0710: 1}
    assert c["ta3dctl"] == [1, 2]
    assert c["walk"] == {"pages": 1058, "tail": 2, "prev_of_tail": 1, "bad": 0}
    assert c["order"] == "0x3-0x422,0x1-0x2"
    assert c["tadata"]["state"] == {0: 0x00010002, 4: 0x00000002}


def test_free_list_report_names_the_walk_the_status_and_the_lists():
    rep = dpm_words._free_list_report(FREE_LIST_OUT)
    assert rep.splitlines() == [
        "full-64x64: free list head 0x3 tail 0x2 prev 0x1; STATUS1 tail 0x2 head 0x3, "
        "STATUS2 PREV 0x1",
        "  macrotile 0: 1 pages, head 0x2, tail 0x2",
    ]


def test_ta3dctl_out_of_memory_words_by_name():
    w = [0] * 59
    w[35], w[39] = 0xc, 5
    named = dpm_words.ta3dctl_oom(w)
    assert named["abort_page_count0"] == 0xc
    assert named["abort_status_mtile"] == 5
    assert set(named) == {"saved_ta_global_list", "abort_page_count0", "abort_page_count1",
                          "threshold_ta_global_list", "zls_threshold_step",
                          "abort_status_mtile", "abort_rt_index"}


TILES_OUT = """\
== a: tri 64x64 pb 0x422 rd:3=0xf0100
job: ok
pixels: triangle 10 background 20 sentinel 0 other 0
tiles   0: GB
tiles   1: gS
== b: tri 64x64 pb 0x30 rd:3=0xf0000
job: failed: scene overflowed the parameter buffer, context kept (No space left on device)
pixels: triangle 4 background 0 sentinel 26 other 0
tiles   0: SB
tiles   1: sS
"""


def test_tile_reader_and_compare():
    t = dpm_words.case_tiles(TILES_OUT)
    assert t["a"]["map"] == ["GB", "gS"]
    assert t["a"]["pixels"] == {"triangle": 10, "background": 20, "sentinel": 0, "other": 0}
    assert t["b"]["overflow"] and not t["a"]["overflow"]
    # tiles with triangle in the reference, by what the case shows there
    assert dpm_words.tile_compare(t["a"]["map"], t["b"]["map"]) == {"G->S": 1, "g->s": 1}


TILES_SIZED = """\
== 1024x768-pb0x422-ctl0xf0100: tri
job: ok
pixels: triangle 10 background 20 sentinel 0 other 0
tiles   0: GGGGGGGGgB
== 1024x768-pb0x30-ctl0xf0100: tri
job: failed: scene overflowed the parameter buffer, context kept (No space left on device)
pixels: triangle 4 background 26 sentinel 0 other 0
tiles   0: BGGGGGGGgB
"""


def test_tiles_report_lists_the_lost_regions_by_macrotile():
    rep = dpm_words._tiles_report(TILES_SIZED)
    assert rep.splitlines() == [
        "1024x768-pb0x422-ctl0xf0100: ok; triangle 10 background 20 sentinel 0",
        "1024x768-pb0x30-ctl0xf0100: overflow; triangle 4 background 26 sentinel 0",
        "  macrotile 0: G->B 1",
    ]


def test_tiles_report_skips_a_case_without_a_size_or_a_reference():
    # case names without WxH (TILES_OUT's "a" and "b") are skipped, not a TypeError
    assert dpm_words._tiles_report(TILES_OUT) == "\n"


TIMELINE_OUT = """\
== pb30: regtimeline 3.0 0.2 0x0600-0x0750 -- tri (pb 0x30)
job: ok
timeline: regs 0x0630 0x0658 0x0720 0x0724 samples 10 seconds 3 start 0 end 9 rc 0
tl 100 00000000 00000000 00000000 00000005
tl 200 00000002 00000001 00000005 0000000e
tl 300 00000002 00000001 00000010 0000000d
tl 400 00000000 00000000 00000010 00000000
"""


def test_timeline_reader_finds_partial_render_stretches():
    tl = dpm_words.case_timelines(TIMELINE_OUT)["pb30"]
    assert tl["regs"] == [0x0630, 0x0658, 0x0720, 0x0724]
    assert tl["samples"][1] == (200, {0x0630: 2, 0x0658: 1, 0x0720: 5, 0x0724: 0xe})
    st = dpm_words.partial_stretches(tl)
    assert st == [{"start": 200, "end": 400, "ns": 200, "abort_mtile": 5,
                   "page_status": 0xe, "context_id": 2}]


def test_timeline_report_counts_the_partial_renders():
    rep = dpm_words._timeline_report(TIMELINE_OUT)
    assert rep.splitlines() == [
        "pb30: 4 samples, 1 partial renders",
        "  200 +0.00 ms abort mtile 0x5 page status 0x0000000e context 2",
    ]


def test_the_11_9_tables_parse_and_name_their_scripts():
    t = dpm_words.tables()
    assert set(t) == {"dpm/free-list", "dpm/partial-renders", "dpm/partial-timelines",
                      "dpm/state-base"}
    for path, text in t.items():
        d = tomllib.loads(text)
        unit, feature = path.split("/")
        assert d["name"] == f"{unit}-{feature}"
        assert d["script"] == f"{feature}.sh"
        assert all(len(line) <= 100 or line.startswith(("question", "cases"))
                   for line in text.splitlines())
    fl = tomllib.loads(t["dpm/free-list"])
    assert fl["probe"][0]["name"] == "dpm-free-list-green"
    assert fl["probe"][0]["dump_render"] is True


def test_the_overlay_tables_are_the_tools():
    probes = HERE.parents[1] / "probes"
    for path, text in dpm_words.tables().items():
        assert (probes / f"{path}.toml").read_text() == text


@pytest.mark.skipif(not (DATA / "dpm" / "free-list" / "output.txt").exists(),
                    reason="no resgx545-data free-list run")
def test_every_free_list_case_status_agrees_with_its_page_table():
    out = (DATA / "dpm" / "free-list" / "output.txt").read_text()
    for name, c in dpm_words.case_free_list(out).items():
        tail, prev = c["walk"]["tail"], c["walk"]["prev_of_tail"]
        head = dpm_words.run_pages(c["order"])[0]
        assert c["regs"][0x0700] >> 16 == tail, name
        assert c["regs"][0x0700] & 0xffff == head, name
        assert c["regs"][0x0710] & 0xffff == prev, name
        assert c["regs"][0x0700] == c["regs"][0x070c], name
        assert c["regs"][0x0710] == c["regs"][0x071c], name


@pytest.mark.skipif(not (DATA / "dpm" / "partial-renders" / "output.txt").exists()
                    or not (DATA / "dpm" / "free-list" / "output.txt").exists(),
                    reason="no resgx545-data partial-render runs")
def test_the_macrotiles_a_partial_render_image_loses_are_its_state_lists():
    tiles = dpm_words.case_tiles((DATA / "dpm" / "partial-renders" / "output.txt").read_text())
    lists = dpm_words.case_free_list((DATA / "dpm" / "free-list" / "output.txt").read_text())
    for size, pages, w, h in (("1024x768", "0x30", 1024, 768),
                              ("4096x4096", "0x100", 4096, 4096)):
        ref = tiles[f"{size}-pb0x422-ctl0xf0100"]["map"]
        case = tiles[f"{size}-pb{pages}-ctl0xf0100"]["map"]
        lost = {mt for mt, d in dpm_words.tile_compare_by_mtile(ref, case, w, h).items()
                if any(k[-1] not in "Gg" for k in d)}
        state = lists[f"pb{pages[2:]}-{size}"]["tadata"]["state"]
        words = [state.get(4 * k, 0) for k in range(2 * dpm_words.STATE_LISTS)]
        listed = {lst["index"] for lst in dpm_words.state_lists(words) if lst["index"] < 16}
        assert lost == listed, size
