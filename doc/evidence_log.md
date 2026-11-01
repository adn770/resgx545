<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
# SGX545 evidence log

*Generated from `evidence/` by `tools/records/evidence_log.py`; do not edit.*

Every evidence record, by the day it was made and again by unit: its claim, the unit it belongs to,
its provenance tiers (HW our hardware, CAP captures of the closed stack, RE our reading of the
firmware, DDK the GPL kernel sources, infer an inference) and the datasets or files it rests on. The
record itself, in `evidence/<unit>/`, gives the method and what it does and does not show.

## Chronology

### 2026-10-30

- `E001` srvinit passes the kernel 13 MKIF structure sizes, among them CMDTA 0x2b0, TRANSFERCMD
  0x4c8, HWRENDERDETAILS 0x1ec, HWTRANSFERCONTEXT 0xb4 and HOST_CTL 0x44.
  *firmware; CAP; data: `firmware-layout`.*
- `E002` The EDM reads sa0-sa2 as base pointers into TA3DCtl, HostCtl and the kernel CCB control,
  filled by PDS #11; 9 patched immediates.
  *firmware; CAP, RE; data: `firmware-layout`, `firmware-images`.*
- `E003` The firmware file's PATCHES table (our format) holds 81 expression records for 1.7.862890:
  9 ukernel immediates, 24 PDS data words, 8 TA3DCtl words and 40 signature-buffer words.
  *firmware; RE, CAP; data: `firmware-images`.*
- `E004` Captures of 52 fills and 15 copies of the closed stack reproduce the transfer-queue
  templates of the format's v2 and v3: every piece's bytes sit in libsrv_um where the piece table
  cuts them, every varying field is a TQ_PATCHES record with its encoding and value, and the tables
  rebuild all 441 captured ARGB8888 programs byte for byte.
  *firmware; CAP; data: `firmware-transfer`.*
- `E005` HostCtl is 17 dwords; before the first kick the host writes only PowerStatus,
  HWRecoverySampleRate = 10, uKernelTimerClock = 400000, ActivePowManSampleRate = 0, HostClock and
  InitStatus = 0, and on the laptop dword 12 then advances once per EDM tick.
  *firmware; DDK, CAP, HW; data: `firmware-init-payload`, `platform-boot`, `platform-edm-tick`.*
- `E006` The init scripts srvinit hands the kernel write 2 registers before the reset and 38 after
  it, in a fixed order ending with EVENT_PDS_ENABLE = 0x2204b00f, and the deinit script clears 9; on
  the laptop the registers they leave read back as written.
  *platform; CAP, HW, infer; data: `firmware-init-payload`, `platform-boot-registers`.*
- `E007` The laptop's GPU is PCI 8086:0be1 rev 09 with its registers in a 1 MB BAR0 at 0x80000000
  and no BAR2; the host bridge is 8086:0bf1 rev 03; the core reads CORE_ID 0x01150000 and
  CORE_REVISION 0x0001000d.
  *platform; HW, DDK, infer; data: `platform-identity`, `platform-boot-registers`.*
- `E008` The phase-3 kernel boots the firmware on the laptop at the DDK's REV1 heap bases in 20 of
  20 load, boot and stop cycles: InitStatus bit 0 within about 0.2 ms in most cycles, no BIF fault,
  no AssertFail, the EDM translating through directory list 15, and a clean stop.
  *platform; HW, DDK, infer; data: `platform-boot`, `platform-boot-registers`.*
- `E009` Left alone, the running firmware moves exactly four values: TIMER, EVENT_TIMER,
  USE0_SERV_EVENT and HostCtl dword 12; the last two advance at 997.46 Hz, and TIMER at 1/16 of the
  same 399.0 MHz.
  *edm; HW, infer; data: `platform-edm-tick`.*
- `E010` The microkernel's register loads and stores name 191 distinct registers, with 183 read
  sites and 421 write sites; it writes EVENT_HOST_CLEAR at 34 sites, EVENT_HOST_CLEAR2 at 4,
  BIF_CTRL at 4, and no BIF directory-list base.
  *firmware; RE; data: `firmware-boot-path`, `firmware-images`.*
- `E011` srvinit's boot payload names build options 0x60218, no 2D kick, the EDM task registers
  USE0/USE1_SERV_EVENT, clock gating 0xa6aa / 0xaaaaaa with idle mask 0xffffffdf, cache control 0x2,
  and allocates the control blocks and the six kernel-code buffers in a fixed order and size; only
  TA3DCtl dword 23 follows the page directory.
  *firmware; CAP; data: `firmware-init-payload`, `firmware-layout`.*

## By unit

### edm

Records: E009.

### firmware

Records: E001, E002, E003, E004, E005, E010, E011.

### platform

Records: E006, E007, E008.
