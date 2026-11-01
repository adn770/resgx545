# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Tests for fwload.py — the reference loader (doc/specs/fw_format.md §3-§6).

The capture tests are the format's completeness proof: with the addresses the harness
handed srvinit, the loader must reproduce what srvinit uploaded and passed to the kernel.
"""
import hashlib
import pathlib
import struct
import sys

import pytest

import facts
import fwcutter
import fwformat as F
import fwload
import needs

HERE = pathlib.Path(__file__).resolve().parent
HARNESS = HERE.parent.parent / "harness" / "ukernel-extract"
sys.path.insert(0, str(HARNESS))
import initinfo  # noqa: E402

# The 32-bit immediate's three fields (format §4): e[20:0], e[40:36], e[49:44].
LIMM_MASK = 0x0003F1F0001FFFFF
# A synthetic instruction word, taken from no program: every bit outside the immediate set,
# the placeholder 0xDEADBEEF inside.
SYN_LIMM = 0xFFFF7F5FFFEDBEEF
# The emitpix2 sideband's three fields (format §9.4): e[27:22], e[40:35], e[55:54]; and a
# synthetic word with every other bit set.
SB_MASK = 0x00C001F80FC00000
SYN_EMITPIX = 0xFF3FFE07F03FFFFF


def test_limm_fields():
    assert fwload.limm_set(0, 0xFFFFFFFF) == LIMM_MASK
    assert SYN_LIMM & ~LIMM_MASK == (1 << 64) - 1 - LIMM_MASK
    assert fwload.limm_get(SYN_LIMM) == 0xDEADBEEF


@pytest.mark.parametrize("imm", [0, 0x1000, 0x0E800F00, 0xF0005000, 0xFFFFFFFF])
def test_limm_patches_only_the_immediate(imm):
    insn = fwload.limm_set(SYN_LIMM, imm)
    assert fwload.limm_get(insn) == imm
    assert insn & ~LIMM_MASK == SYN_LIMM & ~LIMM_MASK


def test_limm_round_trips_every_bit():
    for bit in range(32):
        insn = fwload.limm_set(SYN_LIMM, 1 << bit)
        assert fwload.limm_get(insn) == 1 << bit
        assert bin(insn & LIMM_MASK).count("1") == 1


# A synthetic firmware: one 16-byte "ukernel", one PDS program, one data buffer.
def tiny() -> F.Firmware:
    return F.Firmware(
        ddk=(1, 7, 862890), build_options=0x60218,
        images={0: struct.pack("<QQ", 0, SYN_LIMM)},
        buffers=[F.Buffer(0, 2, 0, 16, 8), F.Buffer(1, 2, 3, 0x40, 16),
                 F.Buffer(9, 3, 0, 0x20, 32)],
        patches=[
            F.Expr(0, F.ENC_USSE_LIMM, F.K_ADDR_SHR4, 0, 8, 1, 0),
            F.Expr(1, F.ENC_WORD32, F.K_CODE_WORD, 0, 0, 0x1ac, 0x0800000F),
            F.Expr(1, F.ENC_WORD32, F.K_PDS_CTL, 0, 4, 1, 0x100),
            F.Expr(1, F.ENC_WORD32, F.K_PDS_ROWS, 0, 8, 1, 0),
            F.Expr(9, F.ENC_WORD32, F.K_PD_PHYS, 0, 0, 0, 0),
            F.Expr(9, F.ENC_WORD32, F.K_ADDR, 0, 4, 9, 0x10),
            F.Expr(9, F.ENC_WORD32, F.K_CONST, 0, 8, 0, 0x3C0003F),
        ],
        values={1: [F.Expr(0xFF, F.ENC_CODE_BASE, F.K_HEAP, 3, 0xA48, 2, 0),
                    F.Expr(0xFF, F.ENC_CODE_BASE, F.K_HEAP, 1, 0xA10, 4, 0x80000)],
                3: [F.Expr(0xFF, F.ENC_WORD32, F.K_HEAP, 0, 12, 6, 0)]},
        meta=list(range(F.META_WORDS)),
    )


TINY_LAYOUT = fwload.Layout(addr={0: 0xE8001000, 1: 0xE800E000, 9: 0xF0005000},
                            heap_base={2: 0xE8000000, 4: 0xF4000000, 6: 0xE4000000},
                            pd_phys=0x2345000)


def test_every_expression_kind():
    boot = fwload.load(tiny(), TINY_LAYOUT)
    assert struct.unpack("<QQ", boot.images[0])[1] == 0xFFFC3F4FFFE00E00   # E800E000 >> 4
    assert struct.unpack("<3I", boot.images[1][:12]) == (
        0x08003ACF,                    # code word: (0x1ac + uk_off 0x200) << 4 | tag
        (3 << 23) | 0x100,             # emitpds control: 3 data rows
        3)
    assert len(boot.images[1]) == 0x40 and len(boot.images[9]) == 0x20
    assert struct.unpack("<3I", boot.images[9][:12]) == (0x2345000, 0xF0005010, 0x3C0003F)
    assert boot.scripts["part2"] == [(0xA48, 0x07D00000), (0xA10, 0x03E81000)]
    assert boot.dev_data[12] == 0xE4000000 and len(boot.dev_data) == 24


BAD_LAYOUTS = [
    dict(addr={0: 0xE8001004, 1: 0xE800E000, 9: 0xF0005000}),     # ukernel not 8-aligned
    dict(addr={0: 0xE8001000, 1: 0xE800E008, 9: 0xF0005000}),     # PDS not 16-aligned
    dict(addr={0: 0xE8001000, 9: 0xF0005000}),                    # a buffer has no address
    dict(heap_base={2: 0xE9000000, 4: 0, 6: 0}),                  # ukernel below code base
]


@pytest.mark.parametrize("bad", BAD_LAYOUTS)
def test_layout_constraints(bad):
    fields = dict(addr=TINY_LAYOUT.addr, heap_base=TINY_LAYOUT.heap_base, pd_phys=0)
    with pytest.raises(fwload.LayoutError):
        fwload.load(tiny(), fwload.Layout(**{**fields, **bad}))


def test_meta_is_named():
    boot = fwload.load(tiny(), TINY_LAYOUT)
    assert boot.kick["TA"] == 0 and boot.kick["FLUSHPDCACHE"] == 10
    assert boot.struct_sizes["COMMAND"] == 23
    assert boot.edm_task_regs == (24, 25) and boot.cache_control == 30


# --- against the harness captures -------------------------------------------------------

sys.path.insert(0, str(HERE.parent / "records"))
import datasets  # noqa: E402

# the layout captures: a dataset of the private data repository
EXTRACTED = (datasets.repos().get("data-private", pathlib.Path("/nonexistent"))
             / "firmware" / "layout")
# Harness fakedrm.c: srvinit's allocation order and a page-granular bump allocator.
ALLOC_ORDER = [6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 1, 2, 3, 4, 5]
LAYOUTS = {
    "layout_base": dict(start=0x1000, shift=0, pd_phys=0x1000),
    "layout_moved": dict(start=0x5000, shift=0x100000, pd_phys=0x2345000),
}
SGXCONFIG_BASES = {2: 0xE8000000, 3: 0xF0000000, 4: 0xF4000000, 5: 0xFC000000, 6: 0xE4000000}


def harness_layout(start: int, shift: int, pd_phys: int) -> fwload.Layout:
    bases = {h: b + shift for h, b in SGXCONFIG_BASES.items()}
    nxt = {h: b + start for h, b in bases.items()}
    by_id = {b.id: b for b in facts.BUFFERS}
    addr = {}
    for i in ALLOC_ORDER:
        b = by_id[i]
        a = (nxt[b.heap] + max(b.align, 0x1000) - 1) & ~(max(b.align, 0x1000) - 1)
        addr[i] = a
        nxt[b.heap] = a + ((b.size + 0xFFF) & ~0xFFF)
    return fwload.Layout(addr=addr, heap_base=bases, pd_phys=pd_phys)


def capture_file(layout: str, buffer_id: int) -> bytes:
    n = ALLOC_ORDER.index(buffer_id)
    (path,) = (EXTRACTED / layout).glob(f"alloc{n:02d}_*.bin")
    return path.read_bytes()


BLOB = fwcutter.default_input()


@pytest.fixture(scope="module")
def fw():
    if BLOB is None:
        pytest.skip("SKIPPED, NOT PASSED: libsrv_init.so not found; set RESGX545_CDV_LIBS")
    return F.unpack(F.pack(fwcutter.cut(BLOB.read_bytes())))


@pytest.mark.parametrize("layout", LAYOUTS)
def test_loader_reproduces_capture(fw, layout):
    if not (EXTRACTED / layout).is_dir():
        pytest.skip(f"SKIPPED, NOT PASSED: capture {layout} not present (RESGX545_DATA_PRIVATE)")
    boot = fwload.load(fw, harness_layout(**LAYOUTS[layout]))

    for b in facts.BUFFERS:
        cap = capture_file(layout, b.id)
        assert boot.images[b.id] == cap[:b.size], f"buffer {b.id}"
        assert not any(cap[b.size:]), f"buffer {b.id} tail"

    info = initinfo.parse((EXTRACTED / layout / "devinitpart2_in.bin").read_bytes())
    assert boot.scripts == info.scripts
    assert boot.dev_data == info.dev_data
    assert boot.kick == info.kick
    assert boot.struct_sizes == info.struct_sizes
    assert boot.edm_task_regs == info.edm_task_regs
    assert boot.clkgate == info.clkgate
    assert boot.cache_control == info.cache_control
    assert fw.build_options == info.build_options


# The 9 ukernel patch sites (format §4, E002): byte offset -> the immediate at layout_base.
UKERNEL_SITES = {0xD60: 0x01001000, 0xD70: 0x0E800F00, 0xD78: 0xF0005000, 0xDB0: 0x00800100,
                 0xDC0: 0x0E801000, 0xE40: 0xE8011000, 0xE50: 6, 0xBAF8: 0x01800100,
                 0xBB10: 0x0E801200}


def test_ukernel_patch_sites(fw):
    boot = fwload.load(fw, harness_layout(**LAYOUTS["layout_base"]))
    tmpl, out = fw.images[facts.UKERNEL], boot.images[facts.UKERNEL]
    sites = [e.offset for e in fw.patches if e.buffer == facts.UKERNEL]
    assert sites == sorted(UKERNEL_SITES)
    for off, imm in UKERNEL_SITES.items():
        (t,), (r,) = struct.unpack_from("<Q", tmpl, off), struct.unpack_from("<Q", out, off)
        assert fwload.limm_get(t) == 0xDEADBEEF and fwload.limm_get(r) == imm, hex(off)
        assert t & ~LIMM_MASK == r & ~LIMM_MASK, hex(off)
    # only the immediates change: 52 bytes in all
    assert len(out) == len(tmpl) == 0xCF68
    assert sum(a != b for a, b in zip(tmpl, out)) == 52


def test_layouts_differ_in_every_address_kind(fw):
    a, b = (fwload.load(fw, harness_layout(**LAYOUTS[k])) for k in LAYOUTS)
    for e in fw.patches + [e for v in fw.values.values() for e in v]:
        if e.kind not in (F.K_CONST, F.K_PDS_CTL, F.K_PDS_ROWS):
            ev = [fwload.evaluate(e, x.layout, fw) for x in (a, b)]
            assert ev[0] != ev[1], e


def test_cli_writes_images_and_scripts(fw, tmp_path):
    import json
    import subprocess
    lay = harness_layout(**LAYOUTS["layout_base"])
    doc = {"addr": {facts.BUFFER_NAMES[i]: hex(a) for i, a in lay.addr.items()},
           "heap_base": {str(h): hex(b) for h, b in lay.heap_base.items()},
           "pd_phys": hex(lay.pd_phys)}
    (tmp_path / "layout.json").write_text(json.dumps(doc))
    (tmp_path / "fw").write_bytes(F.pack(fw))
    out = subprocess.run([sys.executable, str(HERE / "fwload.py"), str(tmp_path / "fw"),
                          str(tmp_path / "layout.json"), "-o", str(tmp_path / "img")],
                         capture_output=True, text=True, check=True).stdout
    assert "0x0a68 = 0xe800e000" in out and "init script part2 (38 writes)" in out
    assert (tmp_path / "img" / "00_ukernel.bin").read_bytes() == fwload.load(fw, lay).images[0]


# --- format v2: transfer-queue templates (format §9) -------------------------------------

def test_emitpix_sb_scatter():
    assert fwload.emitpix_sb_set(0, 0x3FFF) == SB_MASK
    assert fwload.emitpix_sb_set(SYN_EMITPIX, 0x200) == 0xFF3FFE47F03FFFFF
    for bit in range(14):
        insn = fwload.emitpix_sb_set(SYN_EMITPIX, 1 << bit)
        assert fwload.emitpix_sb_get(insn) == 1 << bit
        assert insn & ~SB_MASK == SYN_EMITPIX


def test_fill_params():
    # 64 x 32 at A with a 256-byte stride
    assert fwload.fill_params(0xF0200000, 64, 32, 256, 0xFF336699) == [
        0xFF336699, 0x00000000, 0x001F003F, 0x001F8000, 0xF0200000, 0x00000200, 0, 0, 0]
    assert fwload.fill_params(0, 8192, 8192, 0x8000, 0)[2:4] == [0x1FFF1FFF, 0x0FFF8000]


def test_fill_params_sub_rectangle():
    # A rectangle inside a padded surface: dest stays pixel (0, 0); the PBE clip window is
    # [x, x + width) x [y, y + height), inclusive in the words.
    assert fwload.fill_params(0xF0200000, 32, 16, 320, 0x11223344, x=8, y=4) == [
        0x11223344, 0x00040008, 0x00130027, 0x00278000, 0xF0200000, 0x00000200, 0, 0, 0]
    assert fwload.fill_params(0, 1, 1, 0x8000, 0, x=8191, y=8191)[1:3] == [
        0x1FFF1FFF, 0x1FFF1FFF]


# (dest, width, height, stride, colour) that fill_params refuses.
BAD_FILLS = [
    (0xF0200000, 0, 32, 256, 0), (0xF0200000, 64, 0, 256, 0),
    (0xF0200000, 8193, 1, 0x8008, 0), (0xF0200000, 64, 8193, 256, 0),
    (0xF0200000, 64, 32, 252, 0),            # pixel stride odd
    (0xF0200000, 64, 32, 248, 0),            # stride below the width
    (0xF0200000, 64, 32, 0x8008, 0),         # LINESTRIDE overflows 12 bits
    (0xF0200002, 64, 32, 256, 0),            # address not a multiple of 4
    (0xFFFFF000, 64, 32, 256, 0),            # surface past 4 GiB
    (0xF0200000, 64, 32, 256, 0, 1, 0),      # x + width past the stride
    (0xF0200000, 8, 8, 0x8000, 0, 8190, 0),  # x + width past 8192
    (0xF0200000, 8, 8, 256, 0, 0, 8190),     # y + height past 8192
    (0xFFFF0000, 8, 8, 256, 0, 0, 255),      # rows past 4 GiB
    (-4, 64, 32, 256, 0),                    # negative destination
    (0xF0200000, 64, 32, 256, -1),           # colour below 0
    (0xF0200000, 64, 32, 256, 1 << 32),      # colour above 32 bits
]


@pytest.mark.parametrize("bad", BAD_FILLS)
def test_fill_params_rejects(bad):
    with pytest.raises(fwload.ParamError):
        fwload.fill_params(*bad)


FILL = (0xF0200000, 64, 32, 256, 0xFF336699)
PARAMS = fwload.fill_params(*FILL)


def tiny_v2() -> F.Firmware:
    """tiny() plus a USE program, an EOT-like program and a PDS program."""
    fw = tiny()
    fw.meta[F.META_TRANSFERCMD_SIZE] = 0x4C8
    fw.tq_meta = [F.TQMeta(0, 4, 0, 0, 0x10, 8, 0, F.TQ_NO_STRADDLE),
                  F.TQMeta(2, 4, 4, 0, 0x38, 8, 0, F.TQ_NO_STRADDLE),
                  F.TQMeta(4, 6, 0, 0, 0x18, 16, 0x10, 0)]
    fw.tq_images = {0: struct.pack("<QQ", 0x1111, SYN_LIMM),
                    2: bytes(48) + struct.pack("<Q", SYN_EMITPIX)}
    fw.tq_patches = [
        F.Expr(0, F.ENC_USSE_LIMM, F.K_PARAM, 0, 8, 0, 0),
        F.Expr(2, F.ENC_WORD32, F.K_CONST, 0, 16, 0, 1 << 21),
        F.Expr(2, F.ENC_USSE_LIMM, F.K_PARAM, 0, 16, 2, 0),
        F.Expr(2, F.ENC_EMITPIX_SB, F.K_PARAM, 0, 48, 5, 0),
        F.Expr(4, F.ENC_WORD32, F.K_DOUTU, 0, 0, 0, 0),
        F.Expr(4, F.ENC_WORD32, F.K_DOUTU, 0, 4, 2, 0),
        F.Expr(4, F.ENC_WORD32, F.K_HEAP, 0, 8, 6, 0),
        F.Expr(4, F.ENC_WORD32, F.K_ADDR, 0, 12, 2, 4),
        F.Expr(4, F.ENC_WORD32, F.K_PARAM, 0, 16, 4, 1),
    ]
    fw.values[F.V_TQ_CMD] = [
        F.Expr(0xFF, F.ENC_WORD32, F.K_CONST, 0, 0x4, 0, 0x200),
        F.Expr(0xFF, F.ENC_WORD32, F.K_ADDR, 0, 0x24, 4, 0),
        F.Expr(0xFF, F.ENC_WORD32, F.K_HEAP, 0, 0x3C, 6, 0),
        F.Expr(0xFF, F.ENC_WORD32, F.K_PARAM, 0, 0x40, 4, 0),
    ]
    return fw


TINY_V2_LAYOUT = fwload.Layout(addr=TINY_LAYOUT.addr, heap_base=TINY_LAYOUT.heap_base,
                               pd_phys=TINY_LAYOUT.pd_phys,
                               tq_addr={0: 0xF4000000, 2: 0xF4000040, 4: 0xE4000040})


def test_tq_every_kind():
    tq = fwload.build_tq(tiny_v2(), TINY_V2_LAYOUT, PARAMS)
    assert sorted(tq.images) == [0, 2, 4]
    assert [len(tq.images[i]) for i in (0, 2, 4)] == [0x10, 0x38, 0x18]
    fill = struct.unpack("<QQ", tq.images[0])
    assert fill == (0x1111, fwload.limm_set(SYN_LIMM, 0xFF336699))
    eot = tq.images[2]
    assert struct.unpack_from("<Q", eot, 16)[0] == fwload.limm_set(1 << 21, 0x001F003F)
    assert struct.unpack_from("<Q", eot, 48)[0] == 0xFF3FFE47F03FFFFF
    assert struct.unpack("<6I", tq.images[4]) == (
        0x00000000,                    # DOUTU of template 0 at the heap base, 0 temps
        0x01000080,                    # template 2: 0x40 bytes in, 4 temps
        0xE4000000, 0xF4000044, 0xF0200001, 0)
    assert tq.cmd == [(0x4, 0x200), (0x24, 0xE4000040), (0x3C, 0xE4000000),
                      (0x40, 0xF0200000)]


def test_fill_is_fill_params_then_build():
    a = fwload.fill(tiny_v2(), TINY_V2_LAYOUT, *FILL)
    assert a == fwload.build_tq(tiny_v2(), TINY_V2_LAYOUT, PARAMS)
    assert a.params == PARAMS


def test_build_tq_needs_tq_content():
    with pytest.raises(F.FormatError):
        fwload.build_tq(tiny(), TINY_V2_LAYOUT, PARAMS)


BAD_TQ_LAYOUTS = {
    "template without address": dict(tq_addr={0: 0xF4000000, 2: 0xF4000040}),
    "misaligned": dict(tq_addr={0: 0xF4000004, 2: 0xF4000040, 4: 0xE4000040}),
    "below its heap": dict(tq_addr={0: 0xF4000000, 2: 0xF4000040, 4: 0xE3FFFFF0}),
    "straddles a page": dict(tq_addr={0: 0xF4000FF8, 2: 0xF4000040, 4: 0xE4000040}),
    "DOUTU target too far": dict(tq_addr={0: 0xF4080000, 2: 0xF4000040, 4: 0xE4000040}),
    "missing heap": dict(heap_base={2: 0xE8000000, 4: 0xF4000000}),
    "past 4 GiB": dict(tq_addr={0: 0xF4000000, 2: 0xF4000040, 4: 0xFFFFFFF0},
                       heap_base={2: 0xE8000000, 4: 0xF4000000, 6: 0xFFFFF000}),
}


@pytest.mark.parametrize("name", BAD_TQ_LAYOUTS)
def test_tq_layout_constraints(name):
    import dataclasses
    lay = dataclasses.replace(TINY_V2_LAYOUT, **BAD_TQ_LAYOUTS[name])
    with pytest.raises(fwload.LayoutError):
        fwload.build_tq(tiny_v2(), lay, PARAMS)


def test_build_tq_builds_only_the_placed_templates():
    # a v3 file, a layout for the fill alone: the copy templates are not built
    tq = fwload.fill(tiny_v3(), TINY_V2_LAYOUT, *FILL)
    assert sorted(tq.images) == [0, 2, 4]
    assert tq == fwload.fill(tiny_v2(), TINY_V2_LAYOUT, *FILL)


def test_a_patch_naming_an_unplaced_template_fails():
    import dataclasses
    # template 4 (placed) takes the DOUTU word of template 0 (not placed)
    lay = dataclasses.replace(TINY_V3_LAYOUT, tq_addr={
        i: a for i, a in TINY_V3_LAYOUT.tq_addr.items() if i != 0})
    with pytest.raises(fwload.LayoutError):
        fwload.copy(tiny_v3(), lay, *COPY)
    # so does a command word naming one (ADDR of template 4)
    lay = dataclasses.replace(TINY_V3_LAYOUT, tq_addr={7: 0xF4000080, 8: 0xE4000080})
    with pytest.raises(fwload.LayoutError):
        fwload.build_tq(tiny_v3(), lay, COPY_PARAMS)


def test_an_operation_needs_its_templates_placed():
    import dataclasses
    lay = dataclasses.replace(TINY_V3_LAYOUT, tq_addr={
        i: a for i, a in TINY_V3_LAYOUT.tq_addr.items() if i != 7})
    fwload.tq_check(tiny_v3(), lay, need=(0, 2, 4))
    with pytest.raises(fwload.LayoutError):
        fwload.tq_check(tiny_v3(), lay, need=(7,))
    # a needed template the file does not have is not the layout's fault
    fwload.tq_check(tiny_v2(), TINY_V2_LAYOUT, need=fwload.FILL_TEMPLATES)


def test_no_straddle_is_per_template():
    import dataclasses
    # template 4 has no NO_STRADDLE flag: it may cross a page
    lay = dataclasses.replace(TINY_V2_LAYOUT, tq_addr={**TINY_V2_LAYOUT.tq_addr,
                                                       4: 0xE4000FF0})
    assert fwload.build_tq(tiny_v2(), lay, PARAMS).cmd[1] == (0x24, 0xE4000FF0)


# --- format v3: the copy (format §10) ----------------------------------------------------

def test_copy_params():
    # 64 x 32 from 0xF0300000 (stride 256) to the fill's surface
    assert fwload.copy_params(0xF0300000, 0xF0200000, 64, 32, 256, 256) == [
        0, 0x00000000, 0x001F003F, 0x001F8000, 0xF0200000, 0x00000200,
        0x000E0E00, 0xCC03F01F, 0xF0300000]


# T0 for source strides in bytes (test_tqcapture.py checks the captured strides, E004)
@pytest.mark.parametrize("stride,t0", [(256, 0x000E0E00), (260, 0x00100000),
                                       (264, 0x00100200), (288, 0x00100E00),
                                       (320, 0x00120E00), (512, 0x001E0E00)])
def test_copy_t0_stride(stride, t0):
    assert fwload.copy_params(0xF0300000, 0xF0200000, 64, 32, stride, 256)[6] == t0


def test_copy_params_limits_and_rectangle():
    p = fwload.copy_params(0, 0, 4096, 4096, 0x8000, 0x4000)
    assert p[6:8] == [0x07FE0E00, 0xCCFFFFFF]
    # the destination rectangle is at (x, y); the source address is its first texel
    p = fwload.copy_params(0xF0300104, 0xF0200000, 32, 16, 320, 320, x=8, y=4)
    assert p[1:6] == fwload.fill_params(0xF0200000, 32, 16, 320, 0, 8, 4)[1:6]
    assert p[0] == 0 and p[7:] == [0xCC01F00F, 0xF0300104]


# (src, dst, width, height, src_stride, dst_stride[, x, y]) that copy_params refuses.
BAD_COPIES = [
    (0xF0300000, 0xF0200000, 0, 32, 256, 256),
    (0xF0300000, 0xF0200000, 64, 0, 256, 256),
    (0xF0300000, 0xF0200000, 4097, 1, 0x8000, 0x8000),     # texture width > 4096
    (0xF0300000, 0xF0200000, 1, 4097, 256, 256),           # texture height > 4096
    (0xF0300002, 0xF0200000, 64, 32, 256, 256),            # source not 4-byte aligned
    (0xF0300000, 0xF0200000, 64, 32, 258, 256),            # source stride not whole texels
    (0xF0300000, 0xF0200000, 64, 32, 252, 256),            # source stride below the width
    (0xF0300000, 0xF0200000, 64, 32, 0x8004, 256),         # STRIDE overflows 13 bits
    (0xFFFFF000, 0xF0200000, 64, 32, 256, 256),            # source past 4 GiB
    (0xF0300000, 0xF0200000, 64, 32, 256, 260),            # odd destination pixel stride
    (0xF0300000, 0xF0200000, 64, 32, 256, 256, 1, 0),      # x + width past the stride
    (0xF0300000, 0xFFFFF000, 64, 32, 256, 256),            # destination past 4 GiB
    (-4, 0xF0200000, 64, 32, 256, 256),                    # negative source
    (0xF0300000, -4, 64, 32, 256, 256),                    # negative destination
]


@pytest.mark.parametrize("bad", BAD_COPIES)
def test_copy_params_rejects(bad):
    with pytest.raises(fwload.ParamError):
        fwload.copy_params(*bad)


COPY = (0xF0300000, 0xF0200000, 64, 32, 256, 256)
COPY_PARAMS = fwload.copy_params(*COPY)


TINY_CODE = (0xC0DE0001, 0xC0DE0002, 0xC0DE0003, 0xC0DE0004)   # stands for PDS code


def tiny_v3() -> F.Firmware:
    """tiny_v2() plus a copy shader (7) and a texturing PDS primary (8) that takes it."""
    fw = tiny_v2()
    fw.tq_meta += [F.TQMeta(7, 4, 0, 0, 0x10, 8, 0, F.TQ_NO_STRADDLE),
                   F.TQMeta(8, 6, 0, 1, 0x40, 16, 0x30, F.TQ_NO_STRADDLE)]
    fw.tq_images[7] = struct.pack("<QQ", 0x2222, 0x3333333333333333)
    fw.tq_images[8] = bytes(48) + struct.pack("<4I", *TINY_CODE)
    fw.tq_patches += [
        F.Expr(8, F.ENC_WORD32, F.K_DOUTU, 0, 0, 7, 0),
        F.Expr(8, F.ENC_WORD32, F.K_CONST, 0, 4, 0, 0x02000004),
        F.Expr(8, F.ENC_WORD32, F.K_PARAM, 0, 24, 8, 0),
        F.Expr(8, F.ENC_WORD32, F.K_PARAM, 0, 32, 6, 0),
        F.Expr(8, F.ENC_WORD32, F.K_PARAM, 0, 36, 7, 0),
    ]
    return fw


TINY_V3_LAYOUT = fwload.Layout(addr=TINY_LAYOUT.addr, heap_base=TINY_LAYOUT.heap_base,
                               pd_phys=TINY_LAYOUT.pd_phys,
                               tq_addr={**TINY_V2_LAYOUT.tq_addr, 7: 0xF4000080,
                                        8: 0xE4000080})


def test_tq_v3_parameters():
    tq = fwload.copy(tiny_v3(), TINY_V3_LAYOUT, *COPY)
    assert tq.params == COPY_PARAMS
    assert sorted(tq.images) == [0, 2, 4, 7, 8]
    assert tq.images[7] == tiny_v3().tq_images[7]
    assert struct.unpack("<16I", tq.images[8]) == (
        0x00000100, 0x02000004, 0, 0, 0, 0, 0xF0300000, 0, 0x000E0E00, 0xCC03F01F, 0, 0,
        *TINY_CODE)
    assert tq.cmd == [(0x4, 0x200), (0x24, 0xE4000040), (0x3C, 0xE4000000),
                      (0x40, 0xF0200000)]
    assert tq == fwload.build_tq(tiny_v3(), TINY_V3_LAYOUT, COPY_PARAMS)


def test_copy_needs_the_copy_templates():
    with pytest.raises(F.FormatError):
        fwload.copy(tiny_v2(), TINY_V3_LAYOUT, *COPY)
    with pytest.raises(F.FormatError):
        fwload.copy(tiny(), TINY_V3_LAYOUT, *COPY)


def test_build_tq_takes_nine_parameters():
    with pytest.raises(fwload.ParamError):
        fwload.build_tq(tiny_v3(), TINY_V3_LAYOUT, COPY_PARAMS[:6])


# --- the real templates, in the fill recipe's layout ---------------------------------------

UM = fwcutter.default_um_input()


@pytest.fixture(scope="module")
def fw2():
    if BLOB is None or UM is None:
        pytest.skip("SKIPPED, NOT PASSED: libsrv libraries not found; set RESGX545_CDV_LIBS")
    return F.unpack(F.pack(fwcutter.cut(BLOB.read_bytes(), UM.read_bytes())))


# The fill recipe's layout: where it puts the seven programs.
RECIPE_LAYOUT = fwload.Layout(
    addr={}, heap_base={4: 0xF4000000, 6: 0xE4000000},
    tq_addr={facts.TQ_PDS_PRIM: 0xE4000000, facts.TQ_PDS_SEC: 0xE4000020,
             facts.TQ_PDS_PIXEVENT: 0xE4000040, facts.TQ_USE_FILL: 0xF4000000,
             facts.TQ_USE_SEC: 0xF4000010, facts.TQ_USE_EOT: 0xF4000020,
             facts.TQ_USE_EOR: 0xF4000060})


def words(b: bytes) -> list[int]:
    return list(struct.unpack(f"<{len(b) // 4}I", b))


def words64(b: bytes) -> list[int]:
    return list(struct.unpack(f"<{len(b) // 8}Q", b))


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def doutu(off: int, temps: int) -> int:
    """DOUTU word 0 of USE code `off` bytes above its heap base (format §9.4)."""
    return ((off << 1) & 0xFFFF0) | ((off >> 19) & 0xF) | ((temps + 3) >> 2) << 24


def only_patched(img: bytes, tmpl: bytes, patched: set[int]) -> None:
    """Every dword of `img` outside `patched` is the template's."""
    a, b = words(img), words(tmpl.ljust(len(img), b"\0"))
    assert len(a) == len(b)
    assert [i for i in range(len(a)) if a[i] != b[i] and i not in patched] == []


# SHA-256 of each program as the fill recipe patches it. The tests store
# no program words: these hashes pin the rest. USE_SEC and USE_EOR are not patched and keep
# their template hashes (format §9.2).
FILL_SHA256 = {
    facts.TQ_USE_FILL: "a724e0f6998bc24c605ed61d8605a336b97c7153261c5dfc24e47e50106c8299",
    facts.TQ_USE_SEC: "74c3e748098b2bb8929d17726a235565ab9d36ace0bd4897604ecc6e1847cece",
    facts.TQ_USE_EOT: "3711711128476f6e424409b2bf87c789f6459330733a615508d225deb23e51be",
    facts.TQ_USE_EOR: "dfbb3b5d76d2776de4aad6a5760a52b7253d9f9a0dc3eb7090dbe1b1a4ccddaa",
    facts.TQ_PDS_PRIM: "6f15f70d4bc646b9c239d59711f978e15065d7d2b6daf64904dc004f18637017",
    facts.TQ_PDS_SEC: "6f055bdbc0e3d5cb833ce75c86399068577f2f090cd1d289a2d9cc00841a7131",
    facts.TQ_PDS_PIXEVENT: "5374d201a3c6b0f889efb0b9584994d34d592024d447030fe7334d3b876d8064",
}
# The fill recipe's USE programs, as offsets from the PIXELSHADER base.
USE_OFF = {i: a - 0xF4000000 for i, a in RECIPE_LAYOUT.tq_addr.items() if a >= 0xF4000000}


def test_recipe_words(fw2):
    tq = fwload.fill(fw2, RECIPE_LAYOUT, *FILL)
    img, tmpl = tq.images, fw2.tq_images
    assert {i: len(b) for i, b in img.items()} == {
        m.id: m.size for m in fw2.tq_meta if m.id in fwload.FILL_TEMPLATES}
    # the colour, into the immediate of the fill shader's second instruction
    fill = words64(img[facts.TQ_USE_FILL])
    assert len(fill) == 2 and fwload.limm_get(fill[1]) == 0xFF336699
    only_patched(img[facts.TQ_USE_FILL], tmpl[facts.TQ_USE_FILL], {2, 3})
    # the EOT: PBE words 0-3 into r0-r3, then the sideband
    eot = words64(img[facts.TQ_USE_EOT])
    assert len(eot) == 7
    assert [fwload.limm_get(q) for q in eot[1:5]] == PARAMS[1:5]
    assert [(q & 0xFFFFFFFF) >> 21 for q in eot[1:5]] == [0, 1, 2, 3]
    assert fwload.emitpix_sb_get(eot[6]) == PARAMS[5] == 0x200
    only_patched(img[facts.TQ_USE_EOT], tmpl[facts.TQ_USE_EOT], {2, 3, 4, 5, 6, 7, 8, 9, 12, 13})
    assert img[facts.TQ_USE_SEC] == tmpl[facts.TQ_USE_SEC]
    assert img[facts.TQ_USE_EOR] == tmpl[facts.TQ_USE_EOR]
    # the PDS data segments: U0-U2 of each kick, the pixel-event tasks
    for pds, use in ((facts.TQ_PDS_PRIM, facts.TQ_USE_FILL), (facts.TQ_PDS_SEC, facts.TQ_USE_SEC)):
        assert words(img[pds])[:3] == [doutu(USE_OFF[use], 0), 4, 0]
        only_patched(img[pds], tmpl[pds], {0, 1, 2})
    pix = words(img[facts.TQ_PDS_PIXEVENT])
    eot_u0 = doutu(USE_OFF[facts.TQ_USE_EOT], 4)
    assert pix[:6] == [eot_u0, 0x00800000, 0, eot_u0, doutu(USE_OFF[facts.TQ_USE_EOR], 1),
                       0x00C00000]
    assert pix[12] == 0x00800000
    only_patched(img[facts.TQ_PDS_PIXEVENT], tmpl[facts.TQ_PDS_PIXEVENT], {0, 1, 2, 3, 4, 5, 12})
    assert {i: sha(b) for i, b in img.items()} == FILL_SHA256
    assert dict(tq.cmd) == {
        0x004: 0x200, 0x008: 0x3F800000, 0x00C: 3, 0x014: 0x100, 0x01C: 0x80000000,
        0x020: 0x88, 0x024: 0xE4000040, 0x028: 5, 0x02C: 1, 0x038: 0x80,
        0x03C: 0xE4000000, 0x194: 0x07C00000}


def test_cmd_pixel_pds_words_follow_meta(fw2):
    meta = {m.id: m for m in fw2.tq_meta}[facts.TQ_PDS_PIXEVENT]
    cmd = dict(fwload.fill(fw2, RECIPE_LAYOUT, *FILL).cmd)
    assert cmd[0x28] == meta.pds_data >> 4
    assert cmd[0x2C] == (4 * meta.pds_attrs + 15) >> 4


USSE_DIS = HERE.parent / "usse-dis"


def disasm(tool: str, img: bytes, tmp_path, *args: str) -> list[str]:
    path = tmp_path / "prog.bin"
    path.write_bytes(img)
    import subprocess
    out = subprocess.run([tool, str(path), *args], capture_output=True, text=True,
                         check=True).stdout
    # "<index>: 0x<hex>\t<text>"
    return [ln.split("\t", 1)[1].strip() for ln in out.splitlines() if "\t" in ln]


@pytest.fixture(scope="module")
def pds_dis():
    import subprocess
    if not needs.needs_dis():
        pytest.skip("needs the disassemblers (tools/usse-dis)")
    subprocess.run(["make", "-s", "-C", str(USSE_DIS), "pds-dis"], check=True)
    return lambda img, ndata, tmp: disasm(str(USSE_DIS / "pds-dis"), img, tmp,
                                          str(ndata))[ndata:]


@pytest.fixture
def use_dis(tmp_path):
    import subprocess
    if not needs.needs_dis():
        pytest.skip("needs the disassemblers (tools/usse-dis)")
    subprocess.run(["make", "-s", "-C", str(USSE_DIS), "usse-dis"], check=True)
    return lambda img: disasm(str(USSE_DIS / "usse-dis"), img, tmp_path)


def undecoded(line: str) -> bool:
    return "TODO" in line or line.startswith((".long", ".word"))


def test_patched_use_programs_disassemble(fw2, use_dis):
    img = fwload.fill(fw2, RECIPE_LAYOUT, *FILL).images
    prog = {i: use_dis(img[i]) for i in (facts.TQ_USE_FILL, facts.TQ_USE_SEC, facts.TQ_USE_EOT,
                                          facts.TQ_USE_EOR)}
    # every instruction decodes, and each program ends on its last one
    assert {i: len(p) for i, p in prog.items()} == {
        facts.TQ_USE_FILL: 2, facts.TQ_USE_SEC: 2, facts.TQ_USE_EOT: 7, facts.TQ_USE_EOR: 3}
    for p in prog.values():
        assert not any(map(undecoded, p))
        assert ".end" in p[-1] and not any(".end" in ln for ln in p[1:-1])
    # the patched immediates, as the disassembler reads them
    assert prog[facts.TQ_USE_FILL][1].endswith("#0xFF336699")
    eot = prog[facts.TQ_USE_EOT]
    for r, v in enumerate(PARAMS[1:5]):
        assert eot[1 + r].endswith(f" r{r}, #0x{v:08X}")
    assert eot[6].endswith(f"#0x{PARAMS[5]:08X}")


def test_patched_pds_programs_disassemble(fw2, pds_dis, tmp_path):
    img = fwload.fill(fw2, RECIPE_LAYOUT, *FILL).images
    for pds in (facts.TQ_PDS_PRIM, facts.TQ_PDS_SEC):
        code = pds_dis(img[pds], 4, tmp_path)
        assert len(code) == 2 and not any(map(undecoded, code))
        assert code[0].startswith("movs doutu,") and code[1] == "halt"
    code = pds_dis(img[facts.TQ_PDS_PIXEVENT], 20, tmp_path)
    assert len(code) == 29 and not any(map(undecoded, code))
    # three USE tasks (PTOFF, EOT, EOR): each takes its U0 from the dword a DOUTU patch wrote,
    # and PTOFF and EOR their U1 from the next one
    tasks = [[o.strip() for o in ln.split(",")[1:3]] for ln in code
             if ln.startswith("movs doutu,")]
    assert [data_dword(t[0]) for t in tasks] == [0, 3, 4]
    assert [data_dword(t[1]) for t in (tasks[0], tasks[2])] == [1, 5]


def test_cli_fill(fw2, tmp_path):
    import json
    import subprocess
    doc = {"addr": {}, "heap_base": {str(h): hex(b) for h, b in
                                     RECIPE_LAYOUT.heap_base.items()},
           "tq_addr": {facts.TQ_NAMES[i]: hex(a) for i, a in RECIPE_LAYOUT.tq_addr.items()}}
    (tmp_path / "layout.json").write_text(json.dumps(doc))
    (tmp_path / "fw").write_bytes(F.pack(fw2))
    out = subprocess.run([sys.executable, str(HERE / "fwload.py"), str(tmp_path / "fw"),
                          str(tmp_path / "layout.json"), "--fill",
                          "0xf0200000,64,32,256,0xff336699", "-o", str(tmp_path / "img")],
                         capture_output=True, text=True, check=True).stdout
    assert "0x024 = 0xe4000040" in out
    got = (tmp_path / "img" / "tq0_USE_FILL.bin").read_bytes()
    assert got == fwload.fill(fw2, RECIPE_LAYOUT, *FILL).images[0]


# --- the real copy templates, in the copy recipe's layout ----------------------------------

# The copy recipe's layout: where it puts its seven programs. The copy's PDS
# primary and shader take the fill's slots, so only the copy's templates are placed.
COPY_RECIPE_LAYOUT = fwload.Layout(
    addr={}, heap_base={4: 0xF4000000, 6: 0xE4000000},
    tq_addr={facts.TQ_PDS_PRIM_1SRC: 0xE4000000, facts.TQ_PDS_SEC: 0xE4000040,
             facts.TQ_PDS_PIXEVENT: 0xE4000060, facts.TQ_USE_COPY: 0xF4000000,
             facts.TQ_USE_SEC: 0xF4000010, facts.TQ_USE_EOT: 0xF4000020,
             facts.TQ_USE_EOR: 0xF4000060})


def test_copy_templates_are_the_copy_layout():
    assert sorted(fwload.COPY_TEMPLATES) == sorted(COPY_RECIPE_LAYOUT.tq_addr)
    assert sorted(fwload.FILL_TEMPLATES) == sorted(RECIPE_LAYOUT.tq_addr)


COPY_SHA256 = {
    facts.TQ_USE_COPY: "9d0dfd83a18e929ed4da9bd5363bedd84c26e5d652515c8d646a545d5a78b297",
    facts.TQ_USE_SEC: FILL_SHA256[facts.TQ_USE_SEC],
    facts.TQ_USE_EOT: FILL_SHA256[facts.TQ_USE_EOT],
    facts.TQ_USE_EOR: FILL_SHA256[facts.TQ_USE_EOR],
    facts.TQ_PDS_PRIM_1SRC: "1b72b359092ce95661b3d4885e7b3a26503cd53ad42aa08f86850b8844657829",
    facts.TQ_PDS_SEC: FILL_SHA256[facts.TQ_PDS_SEC],
    facts.TQ_PDS_PIXEVENT: FILL_SHA256[facts.TQ_PDS_PIXEVENT],
}


def test_copy_recipe_words(fw2):
    tq = fwload.copy(fw2, COPY_RECIPE_LAYOUT, *COPY)
    img, tmpl = tq.images, fw2.tq_images
    assert sorted(img) == sorted(fwload.COPY_TEMPLATES)
    # step 3: the PDS primary's data segment (U0-U2, DOUTI, T2, T3, T0, T1) and the secondary
    pri = words(img[facts.TQ_PDS_PRIM_1SRC])
    assert pri[:12] == [doutu(0, 0), 0x02000004, 0, 0, 0x40012001, 0, COPY_PARAMS[8],
                        0xA0800000, COPY_PARAMS[6], COPY_PARAMS[7], 0, 0]
    only_patched(img[facts.TQ_PDS_PRIM_1SRC], tmpl[facts.TQ_PDS_PRIM_1SRC], set(range(12)))
    assert words(img[facts.TQ_PDS_SEC])[:3] == [doutu(0x10, 0), 4, 0]
    # step 4: the pixel-event program, as for the fill
    pix = words(img[facts.TQ_PDS_PIXEVENT])
    eot_u0 = doutu(0x20, 4)
    assert pix[:6] == [eot_u0, 0x00800000, 0, eot_u0, doutu(0x60, 1), 0x00C00000]
    assert pix[12] == 0x00800000
    only_patched(img[facts.TQ_PDS_PIXEVENT], tmpl[facts.TQ_PDS_PIXEVENT], {0, 1, 2, 3, 4, 5, 12})
    # step 5: the copy shader unpatched; the USE secondary the template
    assert img[facts.TQ_USE_COPY] == tmpl[facts.TQ_USE_COPY]
    assert img[facts.TQ_USE_SEC] == tmpl[facts.TQ_USE_SEC]
    # the EOT (the same destination as the fill) and the EOR
    fill = fwload.fill(fw2, RECIPE_LAYOUT, *FILL).images
    assert img[facts.TQ_USE_EOT] == fill[facts.TQ_USE_EOT]
    assert img[facts.TQ_USE_EOR] == fill[facts.TQ_USE_EOR]
    assert {i: sha(b) for i, b in img.items()} == COPY_SHA256
    # step 9: the fill's command words, with the pixel-event program moved
    want = dict(fwload.fill(fw2, RECIPE_LAYOUT, *FILL).cmd)
    want[0x024] = 0xE4000060
    assert dict(tq.cmd) == want and want[0x03C] == 0xE4000000


def test_copy_recipe_doutu_words(fw2):
    # step 2: U0 of the copy shader, USE secondary, EOT and EOR
    img = fwload.copy(fw2, COPY_RECIPE_LAYOUT, *COPY).images
    pri = words(img[facts.TQ_PDS_PRIM_1SRC])
    sec = words(img[facts.TQ_PDS_SEC])
    pix = words(img[facts.TQ_PDS_PIXEVENT])
    assert (pri[0], sec[0], pix[3], pix[4]) == (0, 0x20, 0x01000040, 0x010000C0)
    assert (pri[1], sec[1], pix[1], pix[5]) == (0x02000004, 4, 0x00800000, 0x00C00000)


def test_copy_meta(fw2):
    meta = {m.id: m for m in fw2.tq_meta}
    assert meta[facts.TQ_USE_COPY] == F.TQMeta(7, 4, 0, 0, 0x10, 8, 0, F.TQ_NO_STRADDLE)
    assert meta[facts.TQ_PDS_PRIM_1SRC] == F.TQMeta(8, 6, 0, 1, 0x40, 16, 0x30,
                                                    F.TQ_NO_STRADDLE)


def test_cut_copy_templates_disassemble(fw2, use_dis, pds_dis, tmp_path):
    code = use_dis(fw2.tq_images[facts.TQ_USE_COPY])
    assert len(code) == 2 and not any(map(undecoded, code)) and ".end" in code[1]
    assert words(fw2.tq_images[facts.TQ_PDS_PRIM_1SRC])[:12] == [0] * 12
    code = pds_dis(fw2.tq_images[facts.TQ_PDS_PRIM_1SRC], 12, tmp_path)
    assert [ln.split(" ", 2)[:2] for ln in code[:3]] == PRIM_1SRC_OPS and code[3] == "halt"


# The PDS primary's four instructions: a USE task, an iteration and a texture fetch, then halt.
PRIM_1SRC_OPS = [["movs", "doutu,"], ["movs", "douti,"], ["movs", "doutt,"]]


def data_dword(operand: str) -> int:
    """The data dword a PDS operand reads (format §9.4: rows of two per bank)."""
    bank, i = int(operand[2]), int(operand[4:-1])
    return 4 * (i // 2) + 2 * bank + i % 2


def test_patched_copy_programs_disassemble(fw2, use_dis, pds_dis, tmp_path):
    img = fwload.copy(fw2, COPY_RECIPE_LAYOUT, *COPY).images
    assert use_dis(img[facts.TQ_USE_COPY]) == use_dis(fw2.tq_images[facts.TQ_USE_COPY])
    pri = img[facts.TQ_PDS_PRIM_1SRC]
    code = pds_dis(pri, 12, tmp_path)
    assert len(code) == 4 and not any(map(undecoded, code))
    assert [ln.split(" ", 2)[:2] for ln in code[:3]] == PRIM_1SRC_OPS
    # every operand reads the dword its patch wrote: U0-U2, DOUTI 0-1, T0-T3 in order
    data = words(pri)
    ops = [[data[data_dword(o.strip())] for o in line.split(",")[1:]] for line in code[:3]]
    assert ops[0][:3] == [0, 0x02000004, 0]
    assert ops[1][:2] == [0x40012001, 0]
    assert ops[2] == [COPY_PARAMS[6], COPY_PARAMS[7], COPY_PARAMS[8], 0xA0800000]


def test_cli_copy(fw2, tmp_path):
    import json
    import subprocess
    doc = {"addr": {}, "heap_base": {str(h): hex(b) for h, b in
                                     COPY_RECIPE_LAYOUT.heap_base.items()},
           "tq_addr": {facts.TQ_NAMES[i]: hex(a) for i, a in
                       COPY_RECIPE_LAYOUT.tq_addr.items()}}
    (tmp_path / "layout.json").write_text(json.dumps(doc))
    (tmp_path / "fw").write_bytes(F.pack(fw2))
    out = subprocess.run([sys.executable, str(HERE / "fwload.py"), str(tmp_path / "fw"),
                          str(tmp_path / "layout.json"), "--copy",
                          "0xf0300000,0xf0200000,64,32,256,256", "-o", str(tmp_path / "img")],
                         capture_output=True, text=True, check=True).stdout
    assert "copy command words" in out and "0x024 = 0xe4000060" in out
    got = (tmp_path / "img" / "tq8_PDS_PRIM_1SRC.bin").read_bytes()
    assert got == fwload.copy(fw2, COPY_RECIPE_LAYOUT, *COPY).images[8]
    assert not (tmp_path / "img" / "tq0_USE_FILL.bin").exists()


# --- the command line's failures ---------------------------------------------------------

def run_cli(tmp_path, layout_doc, *args, fw_bytes=None):
    import json
    import subprocess
    (tmp_path / "fw").write_bytes(F.pack(tiny()) if fw_bytes is None else fw_bytes)
    (tmp_path / "layout.json").write_text(json.dumps(layout_doc))
    return subprocess.run([sys.executable, str(HERE / "fwload.py"), str(tmp_path / "fw"),
                           str(tmp_path / "layout.json"), *args],
                          capture_output=True, text=True)


def test_cli_missing_firmware_file(tmp_path):
    import json
    import subprocess
    (tmp_path / "layout.json").write_text(json.dumps({"addr": {}, "heap_base": {}}))
    r = subprocess.run([sys.executable, str(HERE / "fwload.py"), str(tmp_path / "fw"),
                        str(tmp_path / "layout.json")], capture_output=True, text=True)
    assert r.returncode == 1 and "Traceback" not in r.stderr and "fwload:" in r.stderr


def test_cli_missing_heap_base_is_a_layout_error(tmp_path):
    doc = {"addr": {str(i): hex(a) for i, a in TINY_LAYOUT.addr.items()}, "heap_base": {}}
    r = run_cli(tmp_path, doc)
    assert r.returncode == 1 and "Traceback" not in r.stderr and "heap" in r.stderr


def test_cli_with_nothing_to_build_fails(tmp_path):
    r = run_cli(tmp_path, {"addr": {}, "heap_base": {}})
    assert r.returncode == 1 and "nothing to do" in r.stderr
