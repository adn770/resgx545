# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""output_room.py: where a tagged shader's output registers land (Q023, Q012)."""
from __future__ import annotations

import struct

import output_room


def f32(x: float) -> int:
    return struct.unpack("<I", struct.pack("<f", x))[0]


def test_own_float_is_the_pixels_centre_in_clip_space():
    assert output_room.own(20, 64) == 0xbeb80000          # (20 + 0.5) / 32 - 1
    assert output_room.own(0, 64) == f32(0.5 / 32 - 1)


def grid(fn, w=4, h=2):
    return [[fn(x, y) for x in range(w)] for y in range(h)]


def test_a_register_on_its_own_pixel_counts_as_own():
    g = grid(lambda x, y: output_room.own(x, 4) | 1)          # o0's tag 1 on every pixel
    res = output_room.classify(g, "x", 4)
    assert res[1] == {"pixels": 8, "own": 8}
    assert set(res) == {1}


def test_a_displaced_register_counts_as_a_pixel_but_not_own():
    # o2 (tag 3) written from x = 0 lands on the pixel at x = 2
    g = grid(lambda x, y: (output_room.own(0, 4) | 3) if x == 2 else output_room.own(x, 4) | 1)
    res = output_room.classify(g, "x", 4)
    assert res[3] == {"pixels": 2, "own": 0} and res[1] == {"pixels": 6, "own": 6}


def test_background_and_untagged_pixels_are_counted_apart():
    g = [[0xff203040, output_room.own(1, 4)]]
    res = output_room.classify(g, "x", 4)
    assert res["background"] == 1 and res[0] == {"pixels": 1, "own": 1}


def test_y_tags_compare_the_row():
    g = grid(lambda x, y: output_room.own(y, 4) | 2)
    assert output_room.classify(g, "y", 4)[2] == {"pixels": 8, "own": 8}


def test_report_lists_each_case_and_a_failed_one():
    raw = "\n".join(
        f"probe p__0: row {y}: " + " ".join(f"0x{output_room.own(x, 4) | 1:08x}" for x in range(4))
        for y in range(2)) + "\nprobe p__1: failed: job hung\n"
    text = output_room.report(raw, ["size 3, x", "size 3, y"], axis=["x", "y"], size=4)
    assert "size 3, x" in text and "tag 1: 8 pixels, 8 own" in text
    assert "size 3, y: FAILED job hung" in text


def test_axes_follow_the_label():
    assert output_room.axes(["size 0, tags from x", "size 0, tags from y", "U1 bit 3"]) == \
        ["x", "y", "x"]
