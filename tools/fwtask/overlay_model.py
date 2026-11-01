# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""What the kernel's debug overlay (sgxfive_own_apply, phase 11.29) does to the firmware buffers,
as a model over the reference loader's output, so that a reviewer can check the claim of
HACKING.md ("firmware tasks of our own") on the real firmware file: with no slot armed the
15 buffers are the loader's, byte for byte; with slots armed, exactly the start dword of each
armed slot of PDS #13 differs, and nothing else does.

The start dword of a slot is a FACT record of kind CODE_WORD (doc/specs/fw_format.md section 4,
E003): `addend | (index << 4)`, the addend 0x0800000f (CBASE 15, TRC 8). The overlay re-evaluates
the record of one slot with another index (ours: the code page, OWN_INDEX plus the entry) and
another TRC; the closed code is only ever named by the `target` the record states (E146).
"""
import pathlib
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "fwcutter"))
import facts  # noqa: E402
import fwformat as F  # noqa: E402
import fwload  # noqa: E402

PDS13 = 4                       # the buffer that holds PDS #13's data (E003)
INDEX_BITS = 0x7ffff << 4       # the pc field of the word (bits 22:4)


def synthetic_layout(fw) -> "fwload.Layout":
    """A layout with every buffer in its heap, in id order, and the ukernel at the code base."""
    bases = {h: 0x10000000 * (h + 1) for h in range(8)}
    nxt = dict(bases)
    addr = {}
    for b in sorted(fw.buffers, key=lambda x: x.id):
        a = (nxt[b.heap] + max(b.align, 0x1000) - 1) & ~(max(b.align, 0x1000) - 1)
        addr[b.id] = a
        nxt[b.heap] = a + ((b.size + 0xFFF) & ~0xFFF)
    return fwload.Layout(addr=addr, heap_base=bases, pd_phys=0x3000)


def slots(fw) -> list[F.Expr]:
    """The CODE_WORD records of PDS #13's buffer, one per start slot, by increasing target."""
    return sorted((e for e in fw.patches if e.kind == F.K_CODE_WORD and e.buffer == PDS13),
                  key=lambda e: e.target)


def apply(fw, images: dict[int, bytes], armed: dict[int, int], own_index: int, trc: int = 8):
    """The buffers after the overlay: `armed` maps a slot's rank to the entry (instruction
    index inside our blob) it starts. Returns (images, {offset: (old, new)} of PDS #13's
    buffer)."""
    out = {i: bytearray(b) for i, b in images.items()}
    recs = slots(fw)
    changed = {}
    for rank, entry in armed.items():
        e = recs[rank]
        (old,) = struct.unpack_from("<I", out[PDS13], e.offset)
        addend = (old & ~INDEX_BITS & 0x00FFFFFF) | trc << 24
        new = (addend | ((own_index + entry) << 4)) & 0xFFFFFFFF
        struct.pack_into("<I", out[PDS13], e.offset, new)
        changed[e.offset] = (old, new)
    return {i: bytes(b) for i, b in out.items()}, changed


def build(fw, layout=None):
    layout = layout or synthetic_layout(fw)
    return fwload.load(fw, layout).images, layout
