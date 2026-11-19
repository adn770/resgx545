# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The closed microkernel boots in the simulator (pysgx.Sgx): the firmware file built by
tools/fwcutter (firmware/images/sgx545_ukernel.fw of the private data repository, found as
$RESGX545_FW, or beside $RESGX545_UKERNEL, or in $RESGX545_DATA_PRIVATE or
../resgx545-data-private; skipped without it), placed as our driver places it, the host's boot
writes of doc/specs/boot_sequence.md, then the kick.
The chain is doc/specs/hw_spec.md 11.1: PDS #10 -> edm.task.boot -> PDS #11 and #12 ->
edm.task.pds11 and edm.task.init_done, which installs PDS #13, programs the timer and sets
HostCtl.InitStatus, the bit the host polls (on the laptop it is set within about 0.2 ms, hw_spec 11.1)."""
import os
import pathlib
import shutil
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import load  # noqa: E402

REPO = load.REPO
sys.path.insert(0, str(REPO / "tools" / "fwcutter"))
import facts  # noqa: E402
import fwformat  # noqa: E402
import fwload  # noqa: E402



def find_fw() -> pathlib.Path | None:
    """The cut firmware file in the private data repository, None when it is absent."""
    env = os.environ
    cands = []
    if env.get("RESGX545_FW"):
        cands.append(pathlib.Path(env["RESGX545_FW"]))
    if env.get("RESGX545_UKERNEL"):     # <repo>/firmware/images/images/00_ukernel.bin
        cands.append(pathlib.Path(env["RESGX545_UKERNEL"]).parent.parent / "sgx545_ukernel.fw")
    private = pathlib.Path(env.get("RESGX545_DATA_PRIVATE") or REPO.parent / "resgx545-data-private")
    cands.append(private / "firmware" / "images" / "sgx545_ukernel.fw")
    return next((c for c in cands if c.is_file()), None)


FW = find_fw()
pytestmark = [
    pytest.mark.skipif(shutil.which("cargo") is None, reason="needs cargo"),
    pytest.mark.skipif(FW is None, reason="no sgx545_ukernel.fw in the private data repository"),
]

# The driver's heaps (REV1) and allocation order, page-aligned bump placement from the heap
# base (kernel/gma500/sgxfive/sgxfive.c: sgx_heap_base, sgx_alloc_order, sgx_fw_place).
HEAPS = {2: 0x30000000, 3: 0x32000000, 4: 0x37000000, 5: 0x3C000000, 6: 0x2E000000}
ORDER = [6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 1, 2, 3, 4, 5]
PAGE = 0x1000

# Registers (dword index = offset / 4) and HostCtl dwords the boot touches.
CORE_ID, CORE_REVISION = 0x1C // 4, 0x20 // 4
EVENT_OTHER_PDS_EXEC, EVENT_OTHER_PDS_DATA = 0xA68 // 4, 0xA6C // 4
EVENT_TIMER, EVENT_KICK2 = 0xACC // 4, 0xAE8 // 4
INIT_STATUS, HW_RECOVERY_SAMPLE_RATE, UKERNEL_TIMER_CLOCK, HOST_CLOCK = 0x00, 0x14, 0x18, 0x34


def layout() -> fwload.Layout:
    nxt, addr = dict(HEAPS), {}
    by_id = {b.id: b for b in facts.BUFFERS}
    for i in ORDER:
        b = by_id[i]
        align = max(b.align, PAGE)
        a = (nxt[b.heap] + align - 1) & ~(align - 1)
        addr[i] = a
        nxt[b.heap] = a + ((b.size + PAGE - 1) & ~(PAGE - 1))
    return fwload.Layout(addr=addr, heap_base=dict(HEAPS), pd_phys=0x01234000)


def prepare(pysgx) -> tuple:
    """A SGX with the firmware placed and the host's boot writes done, the kick not yet given."""
    lay = layout()
    boot = fwload.load(fwformat.unpack(FW.read_bytes()), lay)
    s = pysgx.Sgx()
    # the boot's emitted programs read ir0 as the emitpds's s2 (E146 [infer]; E488: not in a client fill)
    s.emit_s2_is_ir0 = True
    for i, image in boot.images.items():
        s.map(lay.addr[i], image)
    host = lay.addr[facts.HOST_CTL]
    # HostCtl as the host leaves it before the kick (boot_sequence.md B3, B4)
    s.store32(host + HW_RECOVERY_SAMPLE_RATE, 10)
    s.store32(host + UKERNEL_TIMER_CLOCK, 400000)
    for off, value in boot.scripts["part2"]:
        s.write_reg(off // 4, value)
    # the core's identity as the hardware reads it (hw_spec 5.1)
    s.seed(CORE_ID, 0x01150000)
    s.seed(CORE_REVISION, 0x0001000D)
    # C9-C12: HostClock, InitStatus = 0, then EVENT_KICK2
    s.store32(host + HOST_CLOCK, 1000)
    s.store32(host + INIT_STATUS, 0)
    s.write_reg(EVENT_KICK2, 1)
    return s, lay, boot


def boot(pysgx) -> tuple:
    """A booted SGX, its layout and the firmware's boot data (fwload.Boot). The boot runs past
    init_done's `mov pa2, r0`, an EDM task's write to pa2 that E820 measured."""
    s, lay, boot_data = prepare(pysgx)
    s.run(100_000)
    return s, lay, boot_data


@pytest.fixture(scope="module")
def booted():
    return boot(load.pysgx())


def test_the_boot_runs_past_init_done_s_pa2_write(booted):
    """The boot runs PDS #10 to #12 and the tasks boot, pds11 and init_done to their end,
    init_done's `mov pa2, r0` included (an EDM task writes pa2 to pa4: E820)."""
    s, lay, _ = booted
    assert any(e[0] == "task" and e[2] == 0x1C4 for e in s.log())


def test_the_boot_sets_init_status(booted):
    s, lay, _ = booted
    assert s.load32(lay.addr[facts.HOST_CTL] + INIT_STATUS) & 1 == 1


def test_the_boot_chain_runs_in_order(booted):
    s, lay, _ = booted
    pds = {lay.addr[i]: i for i in (facts.PDS10, facts.PDS11, facts.PDS12)}
    started = [(pds[e[1]], e[3]) if e[0] == "pds" else ("task", e[2])
               for e in s.log() if e[0] in ("pds", "task")]
    # entries: edm.task.boot 0x1ac, edm.task.pds11 0x1be, edm.task.init_done 0x1c4, the code
    # words of PDS #10-#12 with the ukernel at the code base (hw_spec 11.2, 11.3; facts.py)
    assert started == [(facts.PDS10, None), ("task", 0x1AC), (facts.PDS11, 0), (facts.PDS12, 0),
                       ("task", 0x1BE), ("task", 0x1C4)]


def test_init_done_installs_the_event_program_and_the_timer(booted):
    s, lay, _ = booted
    assert s.reg(EVENT_OTHER_PDS_EXEC) == lay.addr[facts.PDS13]
    assert s.reg(EVENT_OTHER_PDS_DATA) == 6
    # from HostCtl.ui32uKernelTimerClock, with bit 24 set (hw_spec 11.1)
    assert s.reg(EVENT_TIMER) == 400000 | 1 << 24


def test_pds11_loads_ta3dctl_into_the_secondaries(booted):
    s, lay, _ = booted
    ta3d = lay.addr[facts.TA3D_CTL]
    # sa0 TA3DCtl, sa1 HostCtl, sa2 the CCB control, sa22 the CCB, sa23 the PD (hw_spec 11.1)
    assert [s.sa(n) for n in (0, 1, 2, 22, 23)] == [
        ta3d, lay.addr[facts.HOST_CTL], lay.addr[facts.CCB_CTL], lay.addr[facts.CCB], 0x01234000]
    assert [s.sa(n) for n in range(64)] == [s.load32(ta3d + 4 * n) for n in range(64)]
