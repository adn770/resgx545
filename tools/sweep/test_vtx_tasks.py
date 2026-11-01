# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Tests for vtx_tasks.py: the vertices' x and slots as vtx_task.s computes them, and quads
read back from a raw.txt."""
import vtx_tasks as vt


def test_every_vertex_has_its_own_x_and_slot():
    vx = vt.vertex_x()
    assert len(vx) == 126 and sorted(vx.values()) == list(range(126))
    ys = {i: vt._f32((vt.CORNERS[i % 3][1] * 16 + i // 3) / (8 * vt.W) - 1) for i in range(126)}
    slots = {((x >> 10) ^ (ys[i] >> 20)) & 0xfff for x, i in vx.items()}
    assert len(slots) == 126


def test_quads_from_a_run():
    x = {i: x for x, i in vt.vertex_x().items()}
    lines = []
    for o, w in ((0x100, [x[0], x[1], vt.SENTINEL, vt.SENTINEL]),
                 (0x200, [x[1], x[0], vt.SENTINEL, vt.SENTINEL]),
                 (0x300, [x[2], vt.SENTINEL, vt.SENTINEL, vt.SENTINEL])):
        lines += [f"probe p__0: scratch +0x{o + 4 * k:03x} 0x{v:08x}" for k, v in enumerate(w)]
    assert vt.quads("\n".join(lines)) == [(0, 1), (2,)]
    assert vt.quads("\n".join(lines), "q") == []
