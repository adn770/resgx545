# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The first triangle's program headers: libsgxfive's (src/tri_progs_gen.h) and the kernel's
(sgx_tri_progs.h in the linux fork, checked when a checkout is present).

It must be what gen_tri_progs.py writes from asm/ today, and the programs
must keep the instructions the kernel's triangle test (sgx_tri.c, with the 3D
unit) patches where it patches them.
"""
from __future__ import annotations

import pathlib
import re
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import forkpin                # noqa: E402
import gen_tri_progs as G     # noqa: E402


def test_generated_header_is_fresh():
    pinned = forkpin.show(f"{forkpin.SGXFIVE}/sgx_tri_progs.h")
    if pinned is None:
        pytest.skip(f"SKIPPED, NOT PASSED: no fork commit {forkpin.pin()} in {forkpin.home()}")
    assert pinned == G.generate(), \
        f"stale: run tools/gen_tri_progs.py -o {G.OUTPUT} (the fork at {forkpin.pin()})"


def test_user_header_is_fresh():
    """libsgxfive's copy (src/tri_progs_gen.h): the same words, userspace types."""
    assert G.USER_OUTPUT.read_text() == G.generate(user=True), \
        "stale: run tools/gen_tri_progs.py --user -o userspace/libsgxfive/src/tri_progs_gen.h"


def test_headers_cite_no_document():
    """The generated text points at the sources, not at a specification."""
    for user in (False, True):
        head = G.generate(user).split("\n */")[0]
        assert "doc/" not in head and "design/" not in head
        assert "asm/tri/" in head


def test_user_header_matches_kernel_words():
    """Both headers carry the same words in the same order."""
    import re as _re
    words = _re.compile(r"\t(0x[0-9a-f]+)(?:ull)?,")
    assert words.findall(G.generate()) == words.findall(G.generate(user=True))


def text(name: str, isa: str) -> list[str]:
    return [t for _w, t in G.listing(name, isa)]


def test_patched_slots():
    """The instruction slots sgx_tri.c patches (by index)."""
    vtx = text("use_vtx.s", "usse")
    assert vtx[0] == "phas #7, #0, pixel, vcull, parallel"      # + the placement index
    assert vtx[7].startswith("phas #0, #0, pixel, end")
    assert vtx[8].startswith("emitmtevtx.end")
    assert text("use_fill.s", "usse")[1] == "mov.skipinv.end o0, #0x00000000"
    eot = text("use_eot.s", "usse")
    assert eot[1:5] == ["mov.skipinv r0, #0x00000000"] * 4      # r0..r3, PBE words 0-3
    assert eot[6].startswith("emitpix2.end.freep")                # + the sideband
    # The PDS programs' data segments: the dwords sgx_tri.c writes exist.
    for name, data in (("pds_vtx.s", 8), ("pds_mte.s", 8), ("pds_prim.s", 4),
                       ("pds_sec.s", 4), ("pds_pixevent.s", 20)):
        assert text(name, "pds")[:data] == ["data"] * data
        assert text(name, "pds")[data] != "data"


def test_every_program_is_in_the_header():
    hdr = G.generate()
    for name, _isa in G.PROGS:
        assert re.search(rf"static const u(32|64) sgx_tri_{pathlib.Path(name).stem}\[\]", hdr), name
