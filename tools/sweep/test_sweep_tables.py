# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The sweep tables under probes/<unit>/: they load, their cases generate, and together they
cover every word of every space of the fill, copy and triangle jobs, the sizes the tool's own
jobs have, and every word and register of the kernel spaces."""
from __future__ import annotations

import tomllib

import pytest

import sweep

TOOL = sweep.DEFAULT_TOOL
PROBES = sweep.ROOT / "probes"
TABLES = sorted(PROBES.glob("*/*.toml"))
# {sweep name: (Sweep, table file)} over every table
SWEEPS = {s.name: (s, p) for p in TABLES for s in sweep.load_all(p)}


@pytest.fixture(scope="module")
def tool():
    if not TOOL.exists():
        pytest.skip(f"{TOOL} not built (make -C userspace/libsgxfive)")
    return TOOL


def _get(name):
    return SWEEPS[name][0]


def test_cases_of_a_transfer_sweep(tool):
    cases = sweep.cases(_get("transfer-command-words-xfer-fill"), sweep.tool_size_of(tool))
    assert len(cases) == 1 + 42 * 34         # the baseline and 34 pokes a word


def test_tables_cover_every_space_of_every_job(tool):
    covered: dict = {}
    for s, _ in SWEEPS.values():
        for space, first, last in sweep.resolve(s, sweep.tool_size_of(tool)):
            covered.setdefault((s.host, space), set()).update(range(first, last + 1))
    want = {("fill", "xfer"), ("copy", "xfer"), ("tri", "cmd"), ("tri", "vdm"),
            ("tri", "eos"), ("tri", "blk"), ("fill", "bg"), ("copy", "bg"), ("copy", "tex")}
    want |= {("tri", f"pds:{s}") for s in sweep.SLOTS["tri"]}
    want |= {(h, f"pds:{s}") for h in ("fill", "copy") for s in sweep.SLOTS["fill"]}
    for key in want:
        n = sweep.tool_size_of(tool)(*key)
        assert covered.get(key) == set(range(n)), key


def test_sweeps_are_named_after_their_table():
    assert len(SWEEPS) > 40
    for name, (s, path) in SWEEPS.items():
        prefix = f"{path.parent.name}-{path.stem}"
        assert name == prefix or name.startswith(prefix + "-"), (name, path)
        assert s.name == name


def _landings(action):
    """The kernel words the user words of `action` land in, as {(host, space): {index}}."""
    m = tomllib.loads((sweep.HERE / "kernel_masks.toml").read_text())
    hosts = {"xfer": ("fill", "copy"), "cmd": ("tri",)}
    out: dict = {}
    for w in m["word"]:
        if w["action"] != action:
            continue
        for land in w["lands"]:
            space, n = land.split(":")
            a, _, b = n.partition("-")
            for h in hosts[w["word"].split(":")[0]]:
                out.setdefault((h, space), set()).update(range(int(a), int(b or a) + 1))
    return out


def _kernel_cover(addr):
    covered: dict = {}
    for name, (s, path) in SWEEPS.items():
        if path.stem != "kernel-words" or name.endswith("-addr") != addr:
            continue
        for space, first, last in sweep.resolve(s, lambda h, sp: 0):
            covered.setdefault((s.host, space), set()).update(range(first, last + 1))
    return covered


def test_tables_cover_every_kernel_word_and_register():
    """Every kernel word is swept once: by the data sweeps, the address sweeps, or, when
    userspace passes it through unchanged, by the command-word sweeps."""
    data, addr, passed = _kernel_cover(False), _kernel_cover(True), _landings("pass")
    for host, space in (("tri", "ta"), ("tri", "rd"), ("fill", "tq"), ("copy", "tq")):
        d, a = data.get((host, space), set()), addr.get((host, space), set())
        assert not d & a, (host, space)
        assert not d & passed.get((host, space), set()), (host, space)
        assert d | a | passed.get((host, space), set()) == set(range(sweep.KSPACES[space])), (
            host, space)
    for host in sweep.HOSTS:
        s = _get(f"platform-untouched-registers-kreg-{host}")
        assert {o for sp, o, _ in sweep.resolve(s, lambda h, sp: 0)} == set(sweep.KREGS), host


def test_address_sweeps_stay_within_a_page():
    """The address sweeps flip bits 0-11 only and write no whole values."""
    for name, (s, _) in SWEEPS.items():
        if name.endswith("-kernel-addr"):
            assert s.bits and max(s.bits) <= 11 and not s.values, name


# the words that load the ISP registers the closed driver writes as constants (0x0400,
# 0x042c, 0x0800, 0x0418, 0x04e8 through the render command, 0x0520, 0x04dc through the
# render details): flipped on an opaque triangle without a depth test they change nothing
ISP_CONSTANTS = {("cmd", 11), ("cmd", 13), ("cmd", 17), ("cmd", 21), ("cmd", 22), ("rd", 19),
                 ("rd", 21)}


def test_the_isp_constants_are_swept_under_isp_scenes():
    """The ISP constants again, under a depth test (less, depth written), a translucent and a
    punch-through pass and a bit-exact depth equal, each scene set by ISP0 (blk:1) in the
    options, the visibility registers sampled."""
    scenes = {}
    for name in ("depth", "translucent", "punch", "equal"):
        s = _get(f"isp-constant-registers-tri-{name}")
        assert s.host == "tri" and s.timeline, name
        assert s.options[0] == "--poke" and s.options[1].startswith("blk:1="), name
        words = {(sp, n) for sp, a, b in sweep.resolve(s, lambda h, sp: 64)
                 for n in range(a, b + 1)}
        assert words == ISP_CONSTANTS, name
        scenes[int(s.options[1].split("=")[1], 0)] = name
    # 0x00800200: depth equal, against a background depth equal to the triangle's (0.3, the
    # viewport's z offset blk:10): the ISP compares bit-exactly, one ulp off removes it
    assert set(scenes) == {0x00400200, 0x02400200, 0x08400200, 0x00800200}


# every value of a PDS data field, as flips of the job's own value: the copy's DOUTI0
# (pds:prim:4) bits 4:0, 10:5, 16:11 and the fill's EMIT2 src0 (pds:pixev:8) bits 15:8
FIELDS = {"pds-douti-fields-copy-douti-bits4-0": ("copy", "pds:prim", 4, 0, 5),
          "pds-douti-fields-copy-douti-bits10-5": ("copy", "pds:prim", 4, 5, 6),
          "pds-douti-fields-copy-douti-bits16-11": ("copy", "pds:prim", 4, 11, 6),
          "pbe-emit": ("fill", "pds:pixev", 8, 8, 8)}


def test_pds_sweeps_flip_every_value_of_a_field():
    for name, (host, space, index, lo, width) in FIELDS.items():
        s = _get(name)
        assert s.host == host and s.bits == [], name
        assert [(r.space, r.first, r.last) for r in s.ranges] == [(space, index, index)], name
        assert s.values == [f"^=0x{v << lo:x}" for v in range(1, 1 << width)], name


# every value of the triangle's VDM fields, as flips of the stream's own value: the state
# word 1 (vdm:1) bits 11:9 and 15:13, the vertex-task word 0 (vdm:6) bits 31:28
VDM = {"vdm-state1-tri-vdm-state1-bits11-9": ("vdm", 1, 9, 3),
       "vdm-state1-tri-vdm-state1-bits15-13": ("vdm", 1, 13, 3),
       "vdm-vertex-tasks": ("vdm", 6, 28, 4)}


def test_vdm_sweeps_flip_every_value_of_a_field():
    for name, (space, index, lo, width) in VDM.items():
        s = _get(name)
        assert s.host == "tri" and s.bits == [], name
        assert [(r.space, r.first, r.last) for r in s.ranges] == [(space, index, index)], name
        assert s.values == [f"^=0x{v << lo:x}" for v in range(1, 1 << width)], name


# the ISP constants the firmware writes only from a 3D render (sweep.KREGS_3D), through the
# debugfs kreg, under transfer jobs, which leave them alone: copies that sample a texture
# (RGBA8888, the every-value source, UYVY through the colour-space block) and a fill
KREG3D = {"isp-render-only-registers-copy-kreg3d": "copy",
          "isp-render-only-registers-copy-every-kreg3d": "copy",
          "isp-render-only-registers-copy-uyvy-kreg3d": "copy",
          "isp-render-only-registers-fill-kreg3d": "fill"}


def test_the_render_only_registers_are_reached():
    for name, host in KREG3D.items():
        s = _get(name)
        assert s.host == host, name
        got = [o for sp, o, _ in sweep.resolve(s, lambda h, sp: 0)]
        assert got == list(sweep.KREGS_3D), name


# every value of the copy's background-object layer word's bytes (bg:10 = 0x202,
# BG.TSP_STORED_DWORDS and BG.TSP_DWORDS), which a bit-by-bit flip left unchanged
BG10 = {"isp-background-object-copy-bg10-bits7-0": 0,
        "isp-background-object-copy-bg10-bits15-8": 8}


def test_the_background_layer_word_is_swept_by_byte():
    for name, lo in BG10.items():
        s = _get(name)
        assert s.host == "copy" and s.bits == [], name
        assert [(r.space, r.first, r.last) for r in s.ranges] == [("bg", 10, 10)], name
        assert s.values == [f"^=0x{v << lo:x}" for v in range(1, 256)], name


# every value of MTECTL bits 7:0 (blk:15, 0x20 in our state block; bits 0 and 6 remove the
# triangle), on the triangle as drawn and mirrored (the viewport's y scale blk:9 negated, so
# its winding reverses)
MTECTL = {"mte-mtectl-tri-mtectl-bits7-0": [],
          "mte-mtectl-tri-mtectl-bits7-0-mirrored": ["--poke", "blk:9=0xc2000000"]}


def test_mtectl_is_swept_drawn_and_mirrored():
    for name, opts in MTECTL.items():
        s = _get(name)
        assert s.host == "tri" and s.options == opts and s.bits == [], name
        assert [(r.space, r.first, r.last) for r in s.ranges] == [("blk", 15, 15)], name
        assert s.values == [f"^=0x{v:x}" for v in range(1, 256)], name


# the words the closed driver leaves 0, as addresses. tri --scratch 16 maps 16 pages at the
# heap base + 0x1000 (0x3e001000); each address form aims at its own scratch page, so the page
# a job writes names the form: absolute, heap-relative, relative in 16-byte units, absolute
# and relative with bit 0 set, relative in 4 KiB pages.
HEAP, SCRATCH = 0x3e000000, 0x1000
FORMS = {2: lambda a: HEAP + a, 4: lambda a: a, 6: lambda a: a >> 4,
         8: lambda a: HEAP + a | 1, 10: lambda a: a | 1, 12: lambda a: a >> 12}
ZERO_WORDS = [("ta", 155, 156), ("ta", 158, 168), ("rd", 9, 9), ("rd", 19, 19)]


def test_the_zero_words_point_at_scratch_pages():
    s = _get("ta-zero-words")
    assert s.host == "tri" and s.options == ["--scratch", "16"] and s.bits == []
    assert [(r.space, r.first, r.last) for r in s.ranges] == ZERO_WORDS
    want = [f"=0x{f(SCRATCH + page * 0x1000):x}" for page, f in FORMS.items()]
    assert s.values == want
    pages = [SCRATCH + p * 0x1000 for p in FORMS]
    assert all(SCRATCH <= a < SCRATCH + 16 * 0x1000 for a in pages)
