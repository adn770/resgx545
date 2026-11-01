# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The clean-room checks of firmware tasks of our own (HACKING.md, "Firmware tasks of our own"),
on the real firmware file, which is private: set RESGX545_DATA_PRIVATE to the private data
repository. Without it these tests skip and say so: a skip is not a pass.

They print nothing of the closed data: a check compares sha256 digests and counts and says which
buffer or how many differ, never a word of the firmware. No assert has a closed value as an
operand, so a failure prints digests, offsets or counts only."""
import hashlib
import os
import pathlib
import re
import struct
import subprocess
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fwtask  # noqa: E402
import overlay_model as M  # noqa: E402
from test_host_verifier import host_build  # noqa: E402

FW = pathlib.Path(os.environ["RESGX545_DATA_PRIVATE"]) / "firmware/images/sgx545_ukernel.fw" \
    if os.environ.get("RESGX545_DATA_PRIVATE") else None
STATED = [6, 1434, 2766, 3594]      # the four start indices of PDS #13: E146 (and E003's records)
OWN = fwtask.OWN_INDEX


@pytest.fixture(scope="module")
def world():
    if FW is None or not FW.is_file():
        pytest.skip("SKIPPED, NOT PASSED: the real firmware file needs RESGX545_DATA_PRIVATE")
    sys.path.insert(0, str(M.ROOT / "tools" / "fwcutter"))
    import fwformat as F
    fw = F.unpack(FW.read_bytes())
    images, layout = M.build(fw)
    return fw, images


def test_there_are_15_buffers_and_four_start_slots_at_the_indices_E146_states(world):
    fw, images = world
    assert len(images) == 15
    assert [e.target for e in M.slots(fw)] == sorted(STATED)


def digests(images) -> dict[int, str]:
    """sha256 of each buffer: what these tests compare, so that a failure names buffers and counts
    and never prints a closed byte."""
    return {i: hashlib.sha256(b).hexdigest() for i, b in images.items()}


def differing(a: dict, b: dict) -> list[int]:
    return sorted(k for k in a.keys() | b.keys() if a.get(k) != b.get(k))


def test_unarmed_the_model_leaves_the_15_buffers_as_the_loader_built_them(world):
    """Of the model only (overlay_model.py): the kernel's side is the host build below."""
    fw, images = world
    after, changed = M.apply(fw, images, {}, OWN)
    assert not differing(digests(after), digests(images)) and not changed


@pytest.mark.parametrize("armed", [{0: 0}, {1: 0}, {2: 0}, {3: 0}, {0: 0, 3: 0}, {0: 0, 1: 0, 2: 0, 3: 0}])
@pytest.mark.parametrize("trc", [8, 9, 12])
def test_armed_exactly_the_start_dwords_of_the_armed_slots_differ(world, armed, trc):
    fw, images = world
    recs = M.slots(fw)
    after, changed = M.apply(fw, images, armed, OWN, trc)
    diff = {(i, o) for i in images for o in range(0, len(images[i]), 4)
            if images[i][o:o + 4] != after[i][o:o + 4]}
    want = {(M.PDS13, recs[r].offset) for r in armed}
    assert diff == want, f"{len(diff ^ want)} dwords differ from the expected set"
    for r in armed:
        o = recs[r].offset
        (new,) = struct.unpack_from("<I", after[M.PDS13], o)
        ok = new == (trc << 24) | 0xF | (OWN << 4)
        assert ok, f"slot {r}: the start dword is not the entry, CBASE 15 and TRC {trc}"


# ---- the kernel's code on the real firmware, through the host build (host/own_host.c) ---------
RES = 0x32140000


def run_kernel(fw_path, layout, tmp_path, armed=None, trc=8):
    """own_host over the real firmware: {buffer id: sha256}, and the status of the overlay."""
    lay = tmp_path / "layout.txt"
    lay.write_text("".join(f"addr {i} {a:#x}\n" for i, a in layout.addr.items()) +
                   "".join(f"heap {h} {b:#x}\n" for h, b in layout.heap_base.items()) +
                   f"pd_phys {layout.pd_phys:#x}\n")
    args = [str(host_build()), "fw", str(fw_path), str(lay)]
    if armed is not None:
        blob = tmp_path / "null.blob"
        blob.write_bytes(fwtask.blob_of("null"))
        mask = sum(1 << r for r in armed)
        args += [str(blob), f"{mask:x}", ",".join("0" for _ in armed), str(trc), f"{RES:x}"]
    r = subprocess.run(args, capture_output=True, text=True)
    assert r.returncode == 0, f"own_host failed ({r.returncode})"     # its output is digests only
    bufs, status = {}, None
    for line in r.stdout.splitlines():
        f = line.split()
        if f[0] == "buf":
            bufs[int(f[1])] = f[2]
        elif f[0] == "apply":
            status = int(f[1])
    return bufs, status


def test_kernel_loader_unarmed_builds_the_15_buffers_the_reference_loader_builds(world, tmp_path):
    fw, images = world
    layout = M.synthetic_layout(fw)
    got, _ = run_kernel(FW, layout, tmp_path)
    assert len(got) == 15
    assert not differing(got, digests(images)), "buffers of the kernel's loader differ from the reference loader's"


@pytest.mark.parametrize("armed", [{0: 0}, {2: 0}, {1: 0, 3: 0}, {0: 0, 1: 0, 2: 0, 3: 0}])
@pytest.mark.parametrize("trc", [8, 9])
def test_kernel_overlay_changes_only_buffer_4_and_as_the_model_says(world, tmp_path, armed, trc):
    """sgx_own_apply() on the real firmware: the 15 buffers' digests equal the model's, and only
    buffer 4 (PDS #13) differs from the unarmed build. Nothing of a buffer is printed."""
    fw, images = world
    layout = M.synthetic_layout(fw)
    after, _ = M.apply(fw, images, armed, OWN, trc)
    got, status = run_kernel(FW, layout, tmp_path, armed, trc)
    assert status == 0, f"sgx_own_apply returned {status}"
    assert not differing(got, digests(after)), "the kernel's buffers differ from the model's"
    assert differing(got, digests(images)) == [M.PDS13]


def test_kernel_refuses_a_slot_the_firmware_does_not_have_and_changes_nothing(world, tmp_path):
    fw, images = world
    layout = M.synthetic_layout(fw)
    got, status = run_kernel(FW, layout, tmp_path, {4: 0})
    assert status not in (0, None)
    assert not differing(got, digests(images))


def test_the_stock_start_words_name_only_the_indices_E146_states(world):
    fw, images = world
    uk = 0       # the synthetic layout puts the ukernel at the code base
    got = sorted((struct.unpack_from("<I", images[M.PDS13], e.offset)[0] >> 4) & 0x7ffff for e in M.slots(fw))
    assert got == sorted(STATED)


def test_no_constant_of_our_sources_is_a_word_of_the_closed_firmware(world):
    """Every constant of 17 bits or more in asm/fwtask/*.s: none is an aligned 32-bit word of
    any of the firmware's buffers. (A smaller constant is a word of any program.)"""
    fw, images = world
    words = {struct.unpack_from("<I", b, o)[0] for b in fw.images.values() for o in range(0, len(b) - 3, 4)}
    hits = []
    for s in fwtask.sources():
        for n, line in enumerate(s.read_text().splitlines(), 1):
            for m in re.finditer(r"#?(0x[0-9a-fA-F]+|\b\d+\b)", line.split(";")[0]):
                if int(m.group(1), 0) >= 0x10000 and int(m.group(1), 0) in words:
                    hits.append(f"{s.name}:{n}")
    assert not hits, f"{len(hits)} constants are words of the firmware: {hits[:5]}"
