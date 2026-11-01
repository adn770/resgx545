# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""ta_scenes.py: the dumped triangle jobs of the ta tables as render scene vectors."""
from __future__ import annotations

import json
import os
import pathlib
import struct

import pytest

import ta_scenes as ts

HERE = pathlib.Path(__file__).resolve().parent
TOOL = os.environ.get("SGXFIVE_TEST", str(HERE.parent.parent / "userspace/libsgxfive/build/sgxfive-test"))


def test_a_case_line_becomes_a_probe_command_without_the_laptop_paths():
    args = ("probe --tri pixel --temps 32 --width 128 --height 128 --vertices 15 --blk 6=0x427f8000 "
            "--pixels --dump-render /tmp/x/dump /home/u/stage/p1131-green__0.bin")
    cmd, opts = ts.probe_command(args, "/w/pix.bin")
    assert cmd[:3] == ["probe", "--tri", "pixel"] and cmd[-1] == "/w/pix.bin"
    assert "--dump-render" not in cmd and "--pixels" not in cmd and "/tmp/x/dump" not in cmd
    assert opts == {"w": 128, "h": 128, "vertices": 15, "blk": {6: 0x427F8000}, "slots": []}


def test_a_case_with_a_slot_program_is_listed_as_excluded_not_built():
    args = "probe --tri pixpds:12 --slot vtxuse=/h/vtx_c4.bin --width 64 --height 64 /h/p.bin"
    assert ts.probe_command(args, "/w/pix.bin")[1]["slots"] == ["vtxuse"]


def test_the_windows_hold_every_nonzero_dword_of_the_modelled_pages():
    param = bytearray(0x8000)
    struct.pack_into("<2I", param, 0x0, 0x4000004, 0x30001)          # slot offset 0x1000
    struct.pack_into("<I", param, 0x1000, 0xC0000000)                 # slot offset 0x2000
    struct.pack_into("<I", param, 0x7000, 7)                          # past the window: not modelled
    sparse, outside = ts.window_words(bytes(param), 0x1000, ts.PB_BASE, 0x5000)
    assert sparse == {"0x1000": "0x4000004", "0x1004": "0x30001", "0x2000": "0xc0000000"}
    assert outside == 1


def test_a_scene_whose_object_header_differs_from_the_dump_is_excluded():
    blk = [0xDF43, 0x1D00200, 0x10F0, 7, 8, 9]
    good = {0x1000: 7, 0x1004: 8, 0x1008: 9}
    assert ts.check_header(blk, good) is None
    assert "word" in ts.check_header(blk, {0x1000: 7, 0x1004: 8, 0x1008: 10})


def test_a_probe_of_a_toml_table_becomes_the_same_command_and_options():
    probe = {"name": "ta-regions-sweep-x02", "slot": "pixel", "size": [128, 128], "blk": {"6": 0x42800000}}
    cmd, opts = ts.probe_of_toml(probe, "/w/pix.bin")
    assert cmd == ["probe", "--tri", "pixel", "--width", "128", "--height", "128", "--blk", "6=0x42800000", "/w/pix.bin"]
    assert opts == {"w": 128, "h": 128, "vertices": 3, "blk": {6: 0x42800000}, "slots": []}
    probe = {"name": "x", "slot": "pixel", "size": [64, 64], "vertices": 15}
    assert ts.probe_of_toml(probe, "/w/p")[0][3:] == ["--width", "64", "--height", "64", "--vertices", "15", "/w/p"]


def test_a_toml_probe_with_a_replaced_vertex_program_or_other_knobs_is_not_built():
    assert ts.probe_of_toml({"name": "a", "slot": "pixel", "size": [64, 64], "vtx_coords": 4}, "/p")[1]["slots"]
    assert ts.probe_of_toml({"name": "a", "slot": "pixel", "size": [64, 64], "vdm": {"3": 1}}, "/p")[1]["slots"]
    assert ts.probe_of_toml({"name": "a", "slot": "pixel", "size": [64, 64], "kpoke": ["x"]}, "/p")[1]["slots"]
    assert not ts.probe_of_toml({"name": "a", "slot": "pixel", "size": [64, 64]}, "/p")[1]["slots"]


def test_a_dump_with_no_object_has_nothing_to_check_the_rebuilt_words_against():
    blk = [0xDF43, 0x1D00200, 0x10F0, 7, 8, 9]
    assert ts.check_header(blk, {}) is None      # a culled job: header_checked is false
