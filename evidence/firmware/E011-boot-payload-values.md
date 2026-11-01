+++
id = "E011"
claim = "srvinit's boot payload names build options 0x60218, no 2D kick, the EDM task registers USE0/USE1_SERV_EVENT, clock gating 0xa6aa / 0xaaaaaa with idle mask 0xffffffdf, cache control 0x2, and allocates the control blocks and the six kernel-code buffers in a fixed order and size; only TA3DCtl dword 23 follows the page directory"
unit = "firmware"
method = "srvinit run to completion under the extraction harness at the DDK's REV1 heap bases and, separately, at the default bases with only the page-directory address changed; the 2068-byte boot payload decoded with initinfo.py; the allocations compared byte for byte with the phase-1 base capture"
tiers = ["CAP"]
date = "2026-10-30"
data = ["firmware-init-payload", "firmware-layout"]
terms = ["host_ctl", "ta3d_ctl", "CR_USE0_SERV_EVENT", "CR_USE1_SERV_EVENT", "CR_CLKGATECTL", "CR_CLKGATECTL2", "CR_CLKGATESTATUS"]
+++

**Values (REV1 run).** Client build options `0x60218`. The kick-address table has no 2D entry.
EDM task registers: `USE0_SERV_EVENT` and `USE1_SERV_EVENT`. Clock gating: `CLKGATECTL`
`0xa6aa`, `CLKGATECTL2` `0xaaaaaa`, idle polled on register `0x8` (`CLKGATESTATUS`) with the
mask `0xffffffdf`. Cache control `0x2`. `asInitDevData[8..13]` = `0x2, 0, 0x300, 0x940,
0x2e000000, 0x37000000` (the last two the PDS and pixel-shader heap bases); the other entries
are 0.

**Allocations, in order.** Kernel data heap: the kernel CCB (`0x2000`), its control (`0x8`), the
event kicker (`0x4`), TA3DCtl (`0xec`), HostCtl (`0x44`), misc (`0x54`), the HWPerf circular
buffer (`0x640c`), the TA signature buffer (`0x620`) and the 3D signature buffer (`0x2088`).
Kernel code heap: the microkernel (`0xcf68`), then PDS #10-#14 (`0x18`, `0x38`, `0x18`, `0x100`,
`0x68`). At REV1 the harness places the microkernel at `0x30001000` and PDS #10-#14 at
`0x3000e000`-`0x30012000`.

**Only the page directory moved.** The run at the default bases with the page-directory
address changed differs from the phase-1 base capture (firmware-layout) in three bytes of
TA3DCtl, bytes `0x5d`-`0x5f`, inside dword 23, and nowhere else: not in any other allocation
and not in the boot payload.

This shows what srvinit computes for this build, not what the hardware does with it (E006,
E008), nor whether any value depends on the core revision or DDK version the harness reports.
