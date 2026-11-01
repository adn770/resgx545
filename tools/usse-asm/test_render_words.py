# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Tests of render_words.py: the kernel's debugfs render_words by the glossary's names, the RT
data set's counts, the 11.10 tables and the readers of their scripts' output."""
from __future__ import annotations

import os
import pathlib
import tomllib

import pytest

import render_words

HERE = pathlib.Path(__file__).resolve().parent
DATA = pathlib.Path(os.environ.get("RESGX545_DATA", pathlib.Path.home() / "src" / "resgx545-data"))

# render_words after one render on a fresh context (the kernel's layout: the context page at
# 0x32411000, its CCB control at +0x100, the RT data set at +0x300)
WORDS = "\n".join([
    "ctx:0=0x00000000", "ctx:3=0x32400000", "ctx:4=0x32411100", "ctx:5=0x00000000",
    "rtds:0=0x3241120c", "rtds:1=0x00000001", "rtds:3=0x00000000", "rtds:4=0x00000000",
    "rtds:7=0x32411400",
    "pb:0=0x00000000", "pb:4=0x32823000",
    "kw:0=0x00000000", "kw:1=0x00000001", "kw:2=0x00000000", "kw:3=0x00000000",
    "rd:52=0x32411208", "rd:53=0x00000400", "rd:54=0x32411300",
]) + "\n"


def test_every_space_has_its_structures_size_in_names():
    assert len(render_words.names("ctx")) == 17
    assert len(render_words.names("rtds")) == 20
    assert len(render_words.names("pb")) == 15
    assert len(render_words.names("kw")) == 4
    assert len(render_words.names("rd")) == 123


def test_words_are_named_by_the_glossary_structures():
    assert render_words.name("rtds", 1) == "hw_rt_data_set.executed_count"
    assert render_words.name("rtds", 4) == "hw_rt_data_set.num_spm_renders"
    assert render_words.name("rtds", 7) == "hw_rt_data_set.hw_rt_data.hw_render_details_dev_vaddr"
    assert render_words.name("ctx", 5) == "hw_render_context.submitted_commands"
    assert render_words.name("pb", 4) == "hw_pb_desc.page_table_base"
    assert render_words.name("rd", 52) == "hw_render_details.access_dev_vaddr"
    assert render_words.name("rd", 54) == "hw_render_details.count_rt_data_set"
    assert render_words.name("rd", 0) == "hw_render_details.registers_3d.bif_3d_req_base"
    assert render_words.name("rd", 82) == "hw_render_details.status_3d[0].0"
    assert render_words.name("kw", 1) == "kernel.pending_count"
    with pytest.raises(KeyError):
        render_words.name("ta", 0)
    with pytest.raises(IndexError):
        render_words.name("kw", 4)


def test_parse_reads_each_line_as_its_space_and_word():
    w = render_words.parse(WORDS + "garbage\n")
    assert w["rtds"][1] == 1 and w["rd"][54] == 0x32411300 and w["kw"][1] == 1
    assert set(w) == {"ctx", "rtds", "pb", "kw", "rd"}


def test_counts_are_the_pending_and_the_executed_count():
    c = render_words.counts(render_words.parse(WORDS))
    assert c == {"pending": 1, "executed": 1, "oom": 0, "spm": 0, "submitted": 0}


def test_kernel_word_addresses_follow_the_context_page():
    a = render_words.kernel_addresses(render_words.parse(WORDS))
    assert a == {"page": 0x32411000, "access": 0x32411208, "pending": 0x3241120c,
                 "rt_status": 0x32411210, "bgpri": 0x32411214, "rtds": 0x32411300,
                 "pbdesc": 0x32411380}
    # rtds:0 points at the pending count, rd:52 at the access word, rd:54 at the set
    p = render_words.pointers(render_words.parse(WORDS))
    assert p["rtds:0"] == "kernel.pending_count"
    assert p["rd:52"] == "kernel.access"
    assert p["rd:54"] == "hw_rt_data_set"


def test_diff_names_the_words_that_changed():
    a = render_words.parse(WORDS)
    b = render_words.parse(WORDS.replace("rtds:1=0x00000001", "rtds:1=0x00000002"))
    assert render_words.diff(a, b) == [("rtds", 1, 1, 2)]
    assert render_words.diff_lines(a, b) == [
        "rtds:1 hw_rt_data_set.executed_count 0x00000001 -> 0x00000002"]


OUT = """## uname
7.3.0-resgx545
== one: tri -n 1 --words W
job: ok
tri: 1 renders ok
#### words 0
kw:1=0x00000000
rtds:1=0x00000000
#### end
ta3d 0: 00000000 00000001
#### words 1
kw:1=0x00000001
rtds:1=0x00000001
#### end
ta3d 1: 00000000 00000002
#### words held
kw:1=0x00000001
rtds:1=0x00000000
#### end
ta3d after: 00000000 00000003
cleanup: rtds 0x32411300 ctx 0x32411000 pbdesc 0x32411380 flags 0x00000000 ret 0
cleanup: before ta 0x32411380 3d 0x32411380
== two: tri -n 2 --geometry 1
job: ok
cleanup: rtds 0x32411300 ctx 0x32411000 pbdesc 0x32411380 flags 0x00000000 ret -110
"""


def test_case_words_reads_snapshots_ta3d_and_cleanup():
    c = render_words.case_words(OUT)
    assert list(c) == ["one", "two"]
    one = c["one"]
    assert one["words"][0]["kw"][1] == 0 and one["words"][1]["rtds"][1] == 1
    assert one["ta3d"][1] == [0, 2]
    assert one["words"]["held"]["rtds"][1] == 0 and one["ta3d"]["after"] == [0, 3]
    assert one["cleanup_ret"] == 0 and c["two"]["cleanup_ret"] == -110
    assert "job: ok" in one["lines"] and "tri: 1 renders ok" in one["lines"]
    assert c["two"]["words"] == {}


def test_report_lists_counts_by_snapshot_and_the_cleanup():
    text = render_words.report(OUT)
    assert "one: cleanup ret 0" in text
    assert "  1: pending 1 executed 1" in text
    assert text.index("  1: pending") < text.index("  held: pending 1 executed 0")
    assert "two: cleanup ret -110" in text


def test_the_11_10_tables_parse_and_name_their_scripts():
    t = render_words.tables()
    assert set(t) == set(render_words.TABLES)
    for path, text in t.items():
        d = tomllib.loads(text)
        unit, feature = path.split("/")
        assert d["name"] == f"{unit}-{feature}"
        assert d["script"] == f"{feature}.sh"
        assert all(len(line) <= 100 for line in text.splitlines())
    assert tomllib.loads(t["render/hold-hang"])["stage"] == ["vdm/state1"]


def test_the_overlay_tables_are_the_tools():
    probes = HERE.parents[1] / "probes"
    for path, text in render_words.tables().items():
        assert (probes / f"{path}.toml").read_text() == text
        assert (probes / path.split("/")[0] / "templates" / f"{path.split('/')[1]}.sh").exists()


@pytest.mark.skipif(not (DATA / "render" / "pending-counts" / "output.txt").exists(),
                    reason="no resgx545-data pending-counts run")
def test_every_completed_cleanup_had_equal_counts():
    c = render_words.case_words((DATA / "render" / "pending-counts" / "output.txt").read_text())
    for name, case in c.items():
        last = case["words"][max(case["words"])]
        n = render_words.counts(last)
        assert (n["pending"] == n["executed"]) == (case["cleanup_ret"] == 0), name
