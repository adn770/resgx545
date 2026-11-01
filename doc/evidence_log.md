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

### 2026-10-31

- `E012` The boot payload's kick-address table names an EDM handler for eight of the eleven kernel
  CCB commands (TA, TRANSFER, POWER, CONTEXTSUSPEND, CLEANUP, GETMISCINFO, PROCESS_QUEUES,
  SETHWPERFSTATUS) and none for 2D, DATABREAKPOINT and FLUSHPDCACHE; the same at both captured
  layouts.
  *firmware; CAP, DDK; data: `firmware-init-payload`.*
- `E013` A forward dataflow over the whole EDM microkernel reaches all 6637 instructions in 70
  routines from 13 entry points and 21 further roots, and records every structure word (170) it
  reaches through a typed pointer, register (191) and secondary attribute (20) it touches; 299
  branches, 554 memory accesses, 14 register addresses and 204 sources it cannot resolve are
  counted, not guessed.
  *edm; RE, CAP; data: `firmware-edm-dataflow`, `firmware-images`, `firmware-init-payload`.*
- `E014` The EDM writes HostCtl dword 14 (assert_fail) only with constants: 0xad002600 at
  instruction 1, on the instruction-0 path that no normal boot takes, and 0xad001a07 at instruction
  0x55c of the event routine, taken when the kernel CCB's write and read offsets differ; it never
  reads the word.
  *edm; RE, HW; data: `firmware-edm-dataflow`, `platform-boot`.*
- `E015` The EDM's TRANSFER handler only counts and queues the context; a later routine picks a
  ready context from the queue heads, skips suspended ones (flag bit 4), takes the dummy path for
  context flag bit 1 or command flag 0x20, applies updates through the context's directory, loads
  the command's 17 register words into fixed registers (the three coefficient groups only when their
  load words are set) and starts the render by writing 1 to 0x0428; completion reads the size word,
  writes the status values and raises SW_EVENT.
  *transfer; RE, HW; data: `firmware-edm-dataflow`, `transfer-dummy`, `transfer-fill`,
  `transfer-isolation`.*
- `E016` In 67 transfers of the closed stack under the harness every command is 0x1c0 bytes with
  flags 0x8, no update and one status entry whose value is the command's fence word plus one, the
  fence word counting the context's commands from 0; the commands lie back to back from offset 0 of
  a 0x104c8-byte client CCB in KERNEL_DATA, and the context is a 0xb4-byte KERNEL_DATA object.
  *transfer; CAP, DDK; data: `firmware-transfer`.*
- `E017` Through the kernel CCB the EDM on the laptop answers GETMISCINFO with the core and DDK
  identity and the thirteen structure sizes srvinit's payload records, idles and powers off on the
  POWER command within about 0.2 ms with its clocks gated, and boots again after a power-off.
  *edm; HW, DDK; data: `edm-ccb`.*
- `E018` Dummy transfers complete on the laptop: eleven in a row each apply their update, write
  their status word, advance the client CCB's read offset by the command size, leave the context's
  count at 0 and raise one SW_EVENT; a dummy behind a destination sync one write short stays queued
  for the 50 ms the kernel waits and, once the host completes the sync and sends PROCESS_QUEUES,
  then runs and sets the write counter to pending + 1.
  *transfer; HW, DDK; data: `transfer-dummy`.*
- `E019` Solid fills built from the firmware file's templates render exactly on the laptop: a whole
  64x32 surface, a 32x16 rectangle on a 320-byte stride, a 33x16 rectangle across tiles and one
  pixel, each with every other dword of three pages untouched, the command equal to the file's 12
  TQ_CMD words, no BIF fault, interleaved with dummies.
  *transfer; HW; data: `transfer-fill`.*
- `E020` Copies built from the firmware file's templates render exactly on the laptop: a whole 64x32
  surface, a 32x16 rectangle from (5,3) of a 320-byte-stride source to (8,4) of a 288-byte-stride
  destination, and a 33x16 rectangle across tiles, from a texture-heap source whose dwords all
  differ, with every other destination dword untouched.
  *transfer; HW; data: `transfer-copy`.*
- `E021` A transfer renders and applies its updates through the page directory its context names: a
  fill and an update into addresses only a client directory maps land, with the EDM's buffers
  aliased read-write or read-only in that directory, and the fill alone without them; a fill aimed
  at a read-only alias of a kernel buffer writes nothing, faults at that page, never completes, and
  leaves the EDM unable to power off until a reload and boot.
  *transfer; HW; data: `transfer-isolation`.*

### 2026-11-01

- `E022` Transfer jobs submitted from userspace through the render node complete exactly on the
  laptop: a chain of eight dummies, fills of a whole 64x32 surface, an inset rectangle, a 300x70
  rectangle across tiles and one pixel, and copies of three rectangles, three times each, with every
  pixel as the CPU computes it and no dword of the buffer outside the rectangle changed; on a fresh
  boot the first job starts the firmware.
  *transfer; HW; data: `render-client-jobs`.*
- `E023` A render job submitted from userspace draws the first triangle exactly on the laptop: ten
  renders, at 64x64, at 128x96, at 64x64 on a context sized for 256x256 targets and at 64x64 after a
  faulting render, each with every pixel as the CPU reference computes it; one sgxfive-test loop
  iteration takes about 5 to 6 ms at 64x64, and in one run 32 render contexts took about 4.6 MiB of
  low memory each.
  *render; HW; data: `render-client-jobs`.*
- `E024` A job that faults on the laptop is detected through the BIF fault; the kernel stops and
  resets the core and boots the firmware again in place, the EDM answering the kick within 152 to
  684 µs; the faulting job's wait fails 111 ms after its submit, its context is lost, a job queued
  on another context runs again, later jobs run exactly, and the third fault from a file within a
  minute bans the file.
  *transfer; HW; data: `render-client-jobs`.*

## By unit

### edm

Records: E009, E013, E014, E017.

### firmware

Records: E001, E002, E003, E004, E005, E010, E011, E012.

### platform

Records: E006, E007, E008.

### render

Records: E023.

### transfer

Records: E015, E016, E018, E019, E020, E021, E022, E024.
