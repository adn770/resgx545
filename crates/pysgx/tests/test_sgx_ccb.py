# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Kernel CCB commands to the closed microkernel in the simulator, after the boot of
test_sgx_boot.py: the host's submit (harness/ukernel-extract/ccb.py, our driver's
sgx_ccb_submit), then EVENT_KICK, which runs the event program PDS #13 with the host-kick bit
in ir1 and so edm.event.general and the CCB fetch.

Two inputs the hardware gives are not modelled: the event program's ir0 and the counter tim
it passes on. The tests run each command with both at their extremes and require the same
outcome. And the event program passes ir1.l and tim.l on with movs, which the simulator reads
as the ALU reads ir1 and tim only when asked (pds::Pds::alu_specials_in_movs): measured to
agree in a fill's secondary program; here the firmware's own fast paths need ir1.l to, and the
tim.l it passes on is never read.

Every test here needs the boot to finish, and the simulator refuses init_done's `mov pa2, r0`
(a pa2 write no record measured, Q098), so all of them are xfail(strict) with that reason, by
test_sgx_boot.unmeasured, and fail as XPASS, to be unmarked, when the form is measured."""
import pathlib
import struct
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent.parent.parent / "harness" / "ukernel-extract"))
import ccb  # noqa: E402
import test_sgx_boot as tb  # noqa: E402
from test_sgx_boot import facts, fwformat, load  # noqa: E402

pytestmark = [*tb.pytestmark, tb.unmeasured]
EVENT_KICK, EVENT_TIMER = 0xAC8 // 4, 0xACC // 4
USE0_SERV_EVENT = 0xB14 // 4
POWER_STATUS = 0x04
MISCINFO_READY, MISCINFO_GET_STRUCT_SIZES = 0x1, 0x2
INPUTS = [(0, 0x01020000), (0xFFFFFFFF, 0x01FFFFFF)]      # (ir0, tim) at their extremes


def booted_sgx(ir0: int, tim: int, assume: bool = True):
    s, lay, boot = tb.boot(load.pysgx())
    # as the hardware reads it: the served-event count, bit 16 always set (hw_spec 12.2)
    s.seed(USE0_SERV_EVENT, 0x00010003)
    s.event_ir0, s.event_tim, s.alu_specials_in_movs = ir0, tim, assume
    return s, lay, boot


def submit(s, lay, boot, cmd: str, data: list[int]) -> list:
    """The host's writes for one command (ccb.submit), then the kick; the log it adds."""
    offset = s.load32(lay.addr[facts.CCB_CTL])
    kicker = s.load32(lay.addr[facts.KICKER])
    for target, off, value in ccb.submit(boot.kick, cmd, data, offset, kicker):
        if target == "ccb":
            for i, w in enumerate(struct.unpack("<8I", value)):
                s.store32(lay.addr[facts.CCB] + off + 4 * i, w)
        elif target == "ccb_ctl.write_offset":
            s.store32(lay.addr[facts.CCB_CTL], value)
        elif target == "event_kicker":
            s.store32(lay.addr[facts.KICKER], value)
        else:
            n = len(s.log())
            s.write_reg(off // 4, value)
    s.run(200_000)
    return s.log()[n:]


def get_misc_info(s, lay, boot) -> list[int]:
    misc = lay.addr[facts.MISC]
    s.store32(misc, MISCINFO_GET_STRUCT_SIZES)
    for i in range(1, 21):
        s.store32(misc + 4 * i, 0)
    submit(s, lay, boot, "GETMISCINFO", ccb.get_misc_info(misc))
    return [s.load32(misc + 4 * i) for i in range(21)]


@pytest.mark.parametrize("ir0,tim", INPUTS)
def test_getmiscinfo_reports_what_the_hardware_reported(ir0, tim):
    s, lay, boot = booted_sgx(ir0, tim)
    mi = get_misc_info(s, lay, boot)
    assert mi[0] & MISCINFO_READY
    # CORE_REVISION, CORE_ID, the DDK version word (1.7.17), the DDK build, 545, the ukernel's
    # revision, the build options: the identity our driver checks (hw_spec 5.1, 9.6). The build
    # number and the options are read from the firmware file, not pinned here.
    fw = fwformat.unpack(tb.FW.read_bytes())
    assert mi[1:8] == [0x1000D, 0x01150000, 1 << 16 | 7 << 8 | 17, fw.ddk[2], 545, 0x1000D,
                       fw.build_options]
    assert mi[8:21] == list(boot.struct_sizes.values())
    assert s.load32(lay.addr[facts.CCB_CTL] + 4) == 1           # ReadOffset moved past it


@pytest.mark.parametrize("ir0,tim", INPUTS)
def test_power_idle_stops_the_tick(ir0, tim):
    s, lay, boot = booted_sgx(ir0, tim)
    get_misc_info(s, lay, boot)
    host = lay.addr[facts.HOST_CTL]
    log = submit(s, lay, boot, "POWER", ccb.power(ccb.POWERCMD_IDLE))
    # on the hardware: HostCtl dword 1 (power status) becomes 4 and EVENT_TIMER reads 0
    assert s.load32(host + POWER_STATUS) == 4
    fw_writes = [(e[2], e[3]) for e in log if e[0] == "write" and not e[1]]
    assert fw_writes == [(EVENT_TIMER, 0)]


def test_the_kick_needs_the_movs_assumption():
    s, lay, boot = booted_sgx(0, 0x01020000, assume=False)
    with pytest.raises(Exception, match="ir1.l as a movs source is open"):
        get_misc_info(s, lay, boot)


def test_the_timer_tick_counts_the_wraps_and_nothing_else():
    """The tick: EVENT_STATUS.TIMER (sgx545defs.h, GPL) reaches the event program as ir0 bit 1
    (the microkernel's handler tests pa0 bit 1), nothing in ir1. On the hardware HostCtl dword
    12 (ui32TimeWraps) advances once a tick and nothing else
    changes (hw_spec 12.2); so here, for three ticks."""
    s, lay, boot = booted_sgx(2, 0x01061A7F)
    host = lay.addr[facts.HOST_CTL]
    before = [s.load32(host + 4 * i) for i in range(17)]
    n = len(s.log())
    for k in range(1, 4):
        s.event(0)
        s.run(200_000)
        assert s.load32(host + 48) == before[12] + k
    after = [s.load32(host + 4 * i) for i in range(17)]
    assert [a for i, a in enumerate(after) if i != 12] == [b for i, b in enumerate(before) if i != 12]
    assert not [e for e in s.log()[n:] if e[0] == "write"]
