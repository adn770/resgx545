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
- `E025` On the laptop the graphics device reports its stolen memory at 0x7f800000 and the table of
  GTT pages at 0x7ffc0000, so stolen memory is 7932 KiB (7936 KiB up to the GTT, less one page) and
  the GTT, if it runs to the end of that window, is 256 KiB; GMCH_CTRL reads 0x0030 and the host
  bridge's words at 0x50 and 0x52 read 0.
  *platform; HW, infer; data: `platform-memory-sizes`.*
- `E026` Of five registers the firmware never writes (0x0810, 0x0814, 0x0818, 0x0a78 and 0x0abc),
  the only one that changes a job is 0x0abc: a value with bits 4:1 all clear (0, 1, 0x20 or 0x21)
  hangs the next fill, copy or triangle, and no other value or single-bit flip of any of the five
  changes a pixel; the other four, and every other value of 0x0a78 and 0x0abc, change nothing.
  *platform; HW; data: `platform-untouched-registers`.*
- `E027` Bit 5 of the flags word of the kernel-built transfer command (word 42, byte offset 0xa8)
  makes a fill or a copy complete without writing anything, the target keeping its sentinel; the
  other 31 bits, singly, change nothing in either job; every transfer word userspace may set leaves
  the flags alone.
  *transfer; HW; data: `transfer-kernel-words`, `transfer-command-words`.*
- `E028` Over a source holding every value of every channel, a copy answers every flip of the
  transfer command's words in the same class as over the plain pattern (1429 of 1429 cases), and of
  the 256 values of bits 31:24 of word 14 exactly the 128 with bit 25 set change the image; the data
  does not show, for the few words whose changed pixel counts differ between the two sources (word 0
  bits 24 to 30, word 7 bit 1), that they apply no function of the value.
  *transfer; HW; data: `transfer-command-words`.*
- `E029` Bit 25 of the word that loads 0x0400 changes every pixel a fill, a copy or a triangle
  writes, the first pixel of each reading with bits 31:24 inverted (0xff336699 to 0x00336699,
  0xa5000000 to 0x5a000000, 0xff203040 to 0x00203040); no other bit of the word changes a pixel, and
  over the every-value source exactly the 128 values of bits 31:24 with bit 25 set change the image.
  *pbe; HW; data: `transfer-command-words`, `render-command-words`,
  `render-command-words-followup`.*
- `E030` The end-of-tile emit's sideband with bit 9 clear hangs the triangle job, in all four sizes
  tried and in both runs; with bit 9 set, bits 8:6 at each of 1 to 7 change no pixel of the ARGB8888
  image and none of the RGB565 image; pack mode 3 stores RGB565; bit 13 stores the same colours at
  1182 other places.
  *pbe; HW, infer; data: `pbe-sideband`, `pbe-sideband-followup`.*
- `E031` Of the 64 pack modes of the end-of-tile sideband, 41 store the shader's colour as ARGB8888
  (mode 0 and 40 others), mode 1 as ABGR8888, mode 2 as BGRA8888 and mode 3 as RGB565; modes 4, 5,
  6, 7, 8, 15, 18, 20, 24, 25, 27 and 28 store subsets in 16 or 8 bits, modes 9, 10, 12 and 13 store
  whole 32-bit colours into part of the target, mode 14 faults, and modes 22, 26 and 34 store other
  values; all but 22 and 34 repeat in two runs, and mode 14 faults in both.
  *pbe; HW, infer; data: `pbe-pack-modes`, `pbe-sideband`, `pbe-pack-modes-followup`.*
- `E032` Pack modes 22, 26 and 34 store one value per triangle pixel and none of the three is a pair
  of luma and chroma: mode 26 stores R >> 3 in bits 4:0, G >> 3 in bits 9:5 and 0x10 in bits 14:10;
  mode 22 stores 0x00000088 and mode 34 stores 0x60800000 in 727 of the triangle's 1062 pixels,
  neither explained; the backgrounds of 22 and 34 take scattered values that change from run to run;
  with o1 to o3 written, even mode 0 spills them into other pixels' places.
  *pbe; HW, infer; data: `pbe-pack-modes`, `pbe-pack-modes-followup`.*
- `E033` On a stride texture (T1 type 6) the sampler clamps to the edge for each address mode 1 to 7
  tried; on a twiddled 16x16 texture the modes 0 to 3 act as repeat, mirror (period twice the size),
  clamp to the edge and mirror once (the absolute coordinate, then clamped), at all seven positions
  tried, and the low three bits of the mode field do not act on the u coordinate; modes 4 to 7 read
  texels that none of 0 to 3 gives.
  *texture; HW; data: `texture-sampler`.*
- `E034` T3 bits 17:16 convert the fetched texel on the laptop (1 gives 10-bit fields, 2 half-float
  pairs, 3 one single float per channel) and, with conversion 3, T3 bit 15 divides the converted
  values by 255 (65535 for a 16-bit channel); the bit was not run with conversions 1 and 2.
  *texture; HW; data: `texture-sampler`.*
- `E035` With the state words T0 0x07fe0000, T1 0x0d00f00f (RGBA8888, a 16x16 power-of-two texture,
  TEXTYPE 0) and T3 0x00800800, every one of the 1062 triangle pixels samples the texel (tx, ty) =
  (((x + 32) / 2) mod 16, ((y + 32) / 2) mod 16), nearest and repeated; texel (tx, ty) is dword i of
  the texture with ty's bits in the even bits of i and tx's in the odd bits (so the texture is
  twiddled), and RGBA8888 holds R in byte 0.
  *texture; HW, infer; data: `texture-fetch`.*
- `E036` In the copy's texture word T2, bits 2 to 11 and 13 move the source address by 2^n bytes
  (the first pixel written is the source texel that far in), bit 12 reads other data, bit 14
  completes the job with nothing written, bits 15 to 31 and the values 0 and 0xffffffff fault; bits
  1:0 are not address bits (they give colours that are no source texel); over the every-value
  source, whose texels repeat every 1024 bytes, bits 10 and 11 change nothing.
  *texture; HW; data: `texture-state-words`.*
- `E037` A copy that reads its source as UYVY and loads colour-space set 0 with the limited-range
  BT.601 words writes, at every one of 2048 pixels and in both runs, sat_u8((cY * (Y - 16) + cU * (U
  - 128) + cV * (V - 128)) >> 7) in each channel, the arithmetic shift truncating; with the set
  loaded as zeros, or not loaded, the copy writes opaque black.
  *texture; HW; data: `texture-tpu-csc`, `texture-tpu-csc-followup`.*
- `E038` In a UYVY copy through colour-space set 0, bit 0 of the transfer word that loads 0x0848
  drops the luma offset and bit 2 reads U and V as signed bytes, the value 0xffffffff doing both;
  its other bits change nothing, and neither the words that load 0x0860 to 0x0868 nor any bit of
  colour-space set 1 changes a copy here; each model gives the target's hash.
  *texture; HW; data: `texture-tpu-csc`.*
- `E039` With T0 bit 31 set, a copy reads its texture as RGB, passes RGB through and takes alpha
  from the three words that load 0x0860 to 0x0868: alpha_above if a weighted sum of R, G and B plus
  an offset exceeds a threshold, else alpha_below; one model fits 74 of the 77 hand-run copies
  exactly, in both runs, and the 3 others, with bits 7:0 of the third word at 64, 128 and 255, fit
  none of its thresholds; T0 bit 31 is the only bit of T0, T1 and T3 whose effect depends on the
  three words repeatably, in both runs (six other cases differ between the tables, not repeatably).
  *texture; HW, infer; data: `texture-tpu-csc`, `texture-tpu-csc-followup`.*
- `E040` No bit of T0, T1 or T3 (103 cases) and no bit of the colour-space set 1 words or of 0x0848
  makes the UYVY copy follow the set 1 numbers (BT.709): every converting case keeps set 0;
  TEXFORMAT 28 (TEXTYPE 3) reads YUYV, Y0 U Y1 V, converted by set 0 at all 2048 pixels, and
  TEXFORMAT 26 with T0 bit 30 reads one byte per texel, rows of 64 bytes, written unconverted as
  grey with alpha 0xff at all 2048 pixels, in both runs; TEXFORMAT 26 without T0 bit 30 gives values
  that differ from run to run.
  *texture; HW; data: `texture-tpu-csc`, `texture-tpu-csc-followup`.*
- `E041` A twiddled 16x16 texture's mip levels follow level 0 back to back, largest first, each
  twiddled at its own size (levels 1 to 4 start 0x100, 0x140, 0x150 and 0x154 dwords after level 0);
  they are read when T0 bits 26:21 are 0x3f and bit 18 is clear and bits 20:17 are not all clear; T0
  bits 11:10 are the minification filter (1 and 2 linear, 0 and 3 nearest) and bit 9 picks the
  nearest level, a half rounding up (0), or blends the two levels around the LOD by its fraction
  (1).
  *texture; HW; data: `texture-mipmaps`.*
- `E042` smp.sinf returns no texel: its first register is 0 and its second the level, and with the
  mip filter linear the first holds the blend fraction between the two levels in bits 23:16 (0x41,
  0x82 and 0xc3 for a quarter, a half and three quarters: a six-bit fraction with its top two bits
  repeated below it) and the second the lower level; smp.rsd returns the same texel as the plain
  sample under point filtering, and under linear filtering at LOD 1.5, where the plain sample
  returns one blended word, eight registers: four texels of level 1 and four of level 2, the 2x2
  footprint of each level, without filtering.
  *texture; HW, infer; data: `texture-sampler`.*
- `E043` In the end-of-tile task's DOUTU1 word, bits 4 to 11 and bits 13 to 21 each change what the
  job writes when flipped alone, bits 3, 12 and 22 and the other bits below 23 and above bit 2
  change nothing, and bits 1, 23, 24, 25, the value 0 and 0xffffffff hang the job; fill, copy (two
  sources) and triangle agree, and a second run reproduces the cases.
  *pds; HW; data: `pds-data-words`, `pds-data-words-followup`.*
- `E044` Over every value of DOUTU1 bits 11:3 (x) and bits 21:12 (y) of the fill's end-of-tile task,
  x or y = 1 changes nothing, x or y = 2 or 3 leaves 1024 of the 2048 pixels unwritten, and every x
  or y from 4 up leaves the whole target unwritten.
  *pds; HW; data: `pds-end-of-tile`.*
- `E045` Writing every value 0 to 63 into register 0x0a78 before a triangle job changes nothing, and
  the same into 0x0abc hangs the job exactly for the values whose bits 4:1 are all zero (0, 1, 0x20,
  0x21); every other value of 0x0abc gives the baseline image, and every value read back as written.
  *pds; HW; data: `platform-untouched-registers`.*
- `E046` In a pixel task's DOUTU1, bit 25 set on a task with no fetch hangs the job and cleared on
  the copy's task changes 1410 to 1492 pixels, bit 23 flipped on a pixel task or on the end-of-tile
  task hangs it, bit 2 does nothing, and bit 22 does nothing on the end-of-tile task but its mask in
  the pixel-event program hangs when cleared; in the copy's DOUTI0, bits 4:0 pick the fetch
  coordinates (0 hangs, 2 to 31 give one image), bits 10:5 pick among five images (the baseline and
  four others), and bits 16:11 pick what the iterator writes (values 37 to 63 give the baseline);
  EMIT2's bits 15:8 write the same pixels at every value but 0x81.
  *pds; HW; data: `pds-data-words`, `pds-douti-fields`, `pbe-emit`, `pds-pixel-event`,
  `pds-data-words-followup`, `pds-douti-fields-followup`.*
- `E047` With DOUTI0 bit 18 set, the iterated x of the textured triangle is the plane (13/45) x +
  (8/45) y + 3/5 in clip coordinates (largest error 1e-7 over 1062 pixels), which takes 0.25, 0.75
  and 0.625 at the three vertices, so each vertex's x was reduced to its fractional part before
  iteration (an inference from the fit); with bit 27 set each pixel's value depends on its column
  alone and, for 906 of the 1062 pixels, is x in fixed point with 28 fractional bits, the other 156
  differing by 2^-8.
  *pds; HW, infer; data: `pds-iteration-sources`.*
- `E048` In the textured-triangle host with w = x + 2 at the vertices, DOUTI0 bit 24 makes every one
  of the 1062 pixels hold the perspective-correct iteration of the vertices' x (largest error
  1.2e-7, against 0.29 for the affine one), DOUTI word 1 bit 6 iterates flat, bits 26:25 pick vertex
  0, 1, 2 or the smooth iteration only with bit 21 set, and DOUTI0 bits 29 and 30 signal the last
  iteration and the last fetch that DOUTU1 bits 24 and 25 wait for: a wait with no matching signal
  hangs the job, and a signal with no wait leaves the attribute holding leftovers of earlier tasks
  (or hangs the job, with a fetch).
  *pds; HW; data: `pds-iteration-waits`, `pds-iteration-sources`, `pds-iteration-waits-followup`.*
- `E049` In the fill, the copy and the triangle alike, flipping bit 1 or bit 2 of the
  pixel-partition word of the kernel-built command, or setting it to 0xffffffff, hangs the job; the
  other 30 single-bit flips and the value 0 change nothing.
  *render; HW; data: `transfer-kernel-words`, `render-kernel-words`,
  `render-kernel-words-followup`.*
- `E050` Of the kernel-built render flags word of the triangle job (ta:7), bit 0 hangs the job, bits
  1 and 4 complete it with no pixel written, bits 5 and 9 and the value 0xffffffff fault, and the
  other bits and the value 0 change nothing; the two fresh runs agree on every bit.
  *render; HW; data: `render-kernel-words`, `render-kernel-words-followup`.*
- `E051` A TA kick without LAST_KICK leaves its render waiting (the job hangs and the context is
  lost); with one job per render, a cleared FIRST_KICK on the second render, FRAG_FLAGS.BIT2 or
  NO_DEALLOCATE on the first, or both, leave the second render's image its own triangle only, and a
  cleared BIT10 changes nothing; both runs agree.
  *render; HW; data: `render-scenes`.*
- `E052` A scene accumulates the geometry of several TA kicks that carry no end-of-scene: the first
  job that ends the scene renders all of them (2 kicks: 1730 triangle pixels, 625 of them from the
  first kick; 3 kicks: 1794, 695 more from the earlier two), and the next render is a scene of its
  own triangle only whatever BIT2, NO_DEALLOCATE or BIT10 the closing render carried; both rounds
  agree.
  *render; HW; data: `render-scenes`.*
- `E053` Rendering a scene empties it for the next kick: a third render whose triangle lies off the
  target and that appends to the closed scene (FIRST_KICK clear) stores only the 4096 background
  pixels, as the control does, whether the closing render carried BIT2, NO_DEALLOCATE or both and
  whether the third kick sets NO_DPM_CONTEXT_LOAD; all eight cases agree in both rounds.
  *render; HW; data: `render-scenes`.*
- `E054` Of the kernel-built words of the triangle job's TA and render-details commands, changing a
  layout word (ta:143, 144, 146, 147, rd:74, rd:75) faults the job for most bits, ta:5 hangs for
  bits 0 and 2, 0 and 0xffffffff, ta:154 at 0 removes the triangle, and the 12 register words that
  are zero in the job (ta:155, 156, 158 to 166, 168) change nothing at any value tried; ta:167
  faults for bit 8 and for 0xffffffff; two cases (ta:147 bit 20, ta:154 bit 1) differ between the
  two fresh runs.
  *ta; HW; data: `render-kernel-words`, `ta-zero-words`, `render-kernel-words-followup`.*
- `E055` The TA command's screen word (ta:145, CR_TE_SCREEN) holds the last tile's x from bit 0 and
  its y from bit 12 in tiles of 32x16 pixels: clearing bit 0 leaves the right tile column of the
  64x64 target unwritten (2048 pixels), clearing bit 12 the bottom row (1024), clearing bit 13 the
  bottom two rows (2048), and 0 leaves all but the top left tile (3584); no other bit changes
  anything; both fresh runs agree.
  *ta; HW; data: `render-kernel-words`, `render-kernel-words-followup`.*
- `E056` None of the TA words that are zero in the triangle job (ta:155, 156, 158 to 168) nor
  render-detail words rd:9 and rd:19, set to a scratch-buffer page in six numberings, is used as an
  address: no job writes the scratch buffer or changes a pixel, except ta:167 at 0x700, which
  faults.
  *ta; HW; data: `ta-zero-words`.*
- `E057` Bit 0 of the render details' ZLS control word (rd:11, CR_ISP_ZLSCTL), and the value
  0xffffffff, let the triangle job complete with no pixel written; the other 31 single-bit flips
  change nothing; the outcome is the same image as the render flags' bit 4 (E050), and both fresh
  runs agree.
  *zls; HW; data: `render-kernel-words`, `render-kernel-words-followup`.*
- `E058` With the render flags' depth-buffer bit set, the depth store (4096 floats, 4 pages) lands
  where 0x0488 points and never where 0x0484 points, the depth load reads from 0x0484 whatever
  0x0488 holds, and the stencil store (one page of bytes) lands where 0x0490 points only when its
  bit 31 is set and the stencil flag is on, never where 0x048c points; all repeated cases agree.
  *zls; HW; data: `zls-load-store`.*
- `E059` Setting either half of the terminate word to 0 leaves part of the 64x64 target unwritten:
  the high half 2048 pixels (x 32-63), the low half 1024 pixels (y 48-63); the other 28 values of
  the two halves change nothing, and all three repeats agree.
  *vdm; HW; data: `vdm-terminate`.*
- `E060` In the triangle's VDM stream, state word 1 bits 11:9 at 0 remove the triangle and 15:13 at
  0, 5 or 6 hang the job (sweep and probe agree); 11:9 at 7 hangs in the sweep but renders in a
  probe job that sets the same word, in both runs, so that value stays unsettled; all 16 values of
  the vertex task's bits 31:28 render the triangle alike.
  *vdm; HW; data: `vdm-state1`, `vdm-state1-followup`, `vdm-vertex-tasks`.*
- `E061` The state block's words vp0-vp3 are IEEE singles that scale and place the 64x64 triangle:
  each pair acts alike on the two axes, the offset words (vp0, vp2) leave 348 triangle pixels at 0
  and the scale words (vp1, vp3) leave none, and vp3 at -32.0 gives the triangle's mirror image;
  which pair is x and which is y rests on that one mirror, and vp4, vp5 change nothing in the flat
  triangle except that a NaN removes it.
  *mte; HW; data: `vdm-stream-words`, `vdm-stream-words-followup`.*
- `E062` Of the state block's MTECTL word (blk:15), bits 1:0 cull one winding (1 the triangle as
  drawn, 2 the mirrored one) or neither (0, 3), and bit 6 removes the triangle whatever the winding;
  bits 2-5 and 7 change nothing, in all 256 values of bits 7:0 on both windings.
  *mte; HW; data: `mte-mtectl`.*
- `E063` The two TA command floats at 0x0240 (ta:152) and 0x0244 (ta:153) act on no clipping scene:
  in 11 scenes (a vertex at w 0.1, 0, -0.05 and -0.5, all three at w 2, -1, 1.25, and 8x, 64x and
  1024x the triangle) each of 8 values of each float gives the scene's baseline image, 176 images
  equal to their baselines; the state block's w clamp word (blk:14) does change the w-scan scenes
  under the same tool.
  *mte; HW; data: `mte-clipping`.*
- `E064` Byte 0 of the render's cmd:16 word (0x88 in the job) moves the 64x64 triangle's edges: 10
  of the 256 values (0x79, 0x88, 0x89, 0x97, 0x98, 0x99, 0x9a, 0xa8, 0xa9, 0xaa) leave the image as
  it is, the others give 26 other images whose triangle covers 1074, 1086 or 1098 pixels (or 1062
  again, in a different image), and 8 is the centre of each nibble's stair; the data are pixel
  counts and hashes, so they do not say which nibble is x and which y.
  *isp; HW; data: `isp-sample-positions`.*
- `E065` ISP0 pass types 1, 2, 4, 5 and 6 draw the 64x64 triangle exactly as type 0 does and types 3
  and 7 remove it (types 2, 4 and 5 also at 32x32, 128x128 and 256x256); the nine ISP visibility
  registers (0x0494-0x04b4), among them the low half of 0x04b4, stayed at 0 in every job of these
  tables and in the 956 jobs of the four ISP constant-register scenes, pass type 4 included.
  *isp; HW; data: `isp-pass-counters`, `isp-constant-registers`.*
- `E066` Under four depth scenes of the 64x64 triangle (less written, translucent, punch-through,
  bit-exact equal) the only words of seven render words that change the image are cmd:11 bit 25 (and
  ~0) and cmd:13 bits 0 and 1 (and ~0, a hang); every flip, 0 and ~0 of cmd:17, cmd:21, cmd:22,
  rd:19 and rd:21 leaves it as it is, and the equal scene draws the triangle when vp4 and the
  background depth are both 0.3, which fits vp4 being the triangle's depth (no case varies vp4 under
  a depth test).
  *isp; HW, infer; data: `isp-constant-registers`, `vdm-stream-words`.*
- `E067` 0x0418, 0x04dc, 0x04e8, 0x0520 and 0x0800, held through a plain copy, the every-value copy,
  a UYVY copy through colour-space set 0 and a fill, change no pixel: 34 values of each (every
  implemented bit flipped, 0 and ~0) in each of the four jobs; on a textured 3D triangle 70 pokes of
  the same registers, every implemented bit and 0 and ~0, give the unpoked image (up to five of them
  may not have been applied).
  *isp; HW; data: `isp-render-only-registers`.*
- `E068` Among five scenes of five overlapping copies of the triangle (depth always, less,
  translucent less, translucent always, punch-through less) only 0x04dc bit 1 acts: with it set
  (values 2 and 7 tried) the punch-through scene hangs and the other four are unchanged; every other
  implemented bit of 0x0418, 0x04dc, 0x04e8, 0x0520 and 0x0800, and 0 and ~0 of each, gives its
  scene's baseline image in all five scenes (348 of 350 cases); why the punch-through scene hangs is
  not shown.
  *isp; HW; data: `isp-render-only-registers`, `isp-depth-test`.*
- `E069` No value of either byte of the copy's background object word bg:10 changes a one-layer
  copy: all 255 values of bits 7:0 and all 255 of bits 15:8 give the baseline image.
  *isp; HW; data: `isp-background-object`.*
- `E070` ISP word 1 (blk:2, 0x10f0 in the job) with bit 3 set makes the job count the triangle's
  1062 pixels (0x426) into a visibility counter: bits 2:0 = 0 count into 0x0498 and bits 2:0 = 7
  into 0x04b4, and with bit 3 clear nothing counts; the counters of 1, 2, 3 and 4 were not
  exercised, so that bits 2:0 name the counter is shown for two of its eight values.
  *isp; HW; data: `vdm-stream-words`, `isp-sample-positions`, `vdm-stream-words-followup`.*
- `E071` 0x041c (rd:5) is the polygon offset in units of one ulp of the stored depth, 0x0424 (rd:7)
  caps the offset at its value with 0 meaning no cap and a negative cap leaving a positive offset
  alone, and the offset needs ISP1 bit 23; 0x0420 (rd:6) at 4.0 adds nothing to the flat triangle.
  *isp; HW; data: `isp-depth-test`.*
- `E072` Against a loaded depth of 0.5 plus n ulp (n from 0 to 512, eleven steps), depth test less,
  the 64x64 triangle at depth 0.5 is removed at n = 0 and drawn from n = 1 up, with 0x0418 (rd:26)
  at 0 and at 1: the compare is exact to the ulp and 0x0418 is not a depth precision mode in this
  range.
  *isp; HW; data: `isp-depth-test`.*
- `E073` With 42 overlapping triangles per tile, opaque and with depth less, 0x0418, 0x04dc, 0x04e8,
  0x0520 and 0x0800 at the 18 values tried leave the covered-pixel count at 1275 of 4096 in every
  job; the check compares counts, not pixel positions.
  *isp; HW; data: `isp-render-only-registers`.*
- `E074` With the multisample positions set in cmd:16 and cmd:10, 0x042c (cmd:13) bits 1:0 = 1 and 2
  each change the 64x64 triangle's image (868 and 896 triangle pixels against 1086 with the
  positions alone), 3 hangs the job, TE anti-aliasing bits 31:30 change it again (1248 pixels), and
  bit 48 of an emit does nothing, while bit 31 of 0x042c clear removes the triangle only when bit 1
  is set; that the image holds each pixel's samples is not shown by these counts.
  *isp; HW, infer; data: `isp-msaa`.*
- `E075` Our own pixel programs measured on the hardware what USSE instructions do beyond their
  text, in 16 tables (169 probes, 2199 cases): of the 169 probes, the table's own model fits every
  case of 119, 2 do not fit (internal-register bank 7 and efo.gpiext on its own instance) and 48 are
  recorded explorations; the settled ones cover tests, 16-bit lanes, shifts, index registers,
  repeats, float rounding, dot products, internal registers, pack and unpack, colour operations,
  dual issue and efo.
  *usse; HW; data: `usse-branch`, `usse-colour-ops`, `usse-dot-products`, `usse-dual-issue`,
  `usse-efo`, `usse-flags`, `usse-fmad`, `usse-fmad16`, `usse-gradients`, `usse-indexing`,
  `usse-integer`, `usse-internal-registers`, `usse-moe`, `usse-pack`, `usse-predicates`,
  `usse-test-channels`.*
- `E076` The USEn_SERV_PIXEL and USEn_SERV_VERTEX registers (n = 0-3) read 0x00010000 after a
  firmware load or stop and count tasks in bits 15:0 with bit 16 set: pixel tasks on all four pipes
  (a 64x64 triangle 85, 86, 85, 85; the debugfs fill 130 and copy 120 and a client fill 40 on every
  pipe), vertex tasks on pipe 0 only (3 for a triangle).
  *usse; HW; data: `platform-register-snapshots`.*
- `E077` In a translucent pass (render block word 1 = 0x03d00200, pass type 1) a pixel shader's o0
  holds the pixel's current colour when it starts, for all 1062 pixels of the triangle; in the
  opaque pass it holds either the same background colour (714 and 800 pixels in two cases) or a
  leftover colour from elsewhere (348 and 262 pixels), different pixels in different cases.
  *usse; HW; data: `usse-output-registers`.*
- `E078` The USE filter block computes sat_u8((sum(tap * input) + bias) >> shift) on the byte it
  writes: eight signed taps at -3 to +4 from the centre in the first two words of a set's group
  (highest byte first), shift in bits 3:0 and a signed 16-bit bias in bits 19:4 of the third word;
  set 2 reads only three of its eight taps; sets 3 to 7 give 0 when the block is loaded; 0x0a9c bits
  1:0 choose the fixed banks and 3 selects the loaded block.
  *usse; HW; data: `usse-filter-taps`, `usse-filter-gain`, `usse-filter-control`,
  `usse-filter-sets`.*
- `E079` With 0x0a9c bits 1:0 at 0, 1 or 2 the fixed sets 2 to 5 are interpolation filters: bank 0
  gives the H.264 six-tap half-sample luma filter [1 -5 20 20 -5 1]/32 (set 2), [1 2 1]/4 (set 3),
  the MPEG-4 Part 2 eight-tap [-1 3 -6 20 20 -6 3 -1]/32 (set 4) and the six taps unscaled (set 5);
  bank 1 gives the VC-1 half-sample [-1 9 9 -1]/16 (sets 2, 3) and two roundings of about its
  quarter-sample [-4 53 18 -3]/64 (sets 4, 5); bank 2 gives [1 2 2 2 1]/8 (set 4) and [1 1 1 1]/4
  (set 5); taps that fall off the line fold by edge repeat, mirror about the edge sample or mirror
  with the edge sample doubled.
  *usse; HW, infer; data: `usse-filter-banks`, `usse-filter-control`.*
- `E080` Fixed bank 2's sets 2 and 3 give 0 on a pedestal of 0x80 and of 0x20 and, with one byte
  raised by 0x20, set 2 shows 4 at -1 and 16 at +1 (taps 1/8 and 4/8) and set 3 shows 32 at -2 and
  16 at the centre and at +1 (taps 1, 1/2, 1/2); the results clamp at 0, so negative taps are not
  seen, and the table has no lifted case, so [1 -4 4 -1]/8 for set 2 is consistent but not measured.
  *usse; HW; data: `usse-filter-banks`.*
- `E081` A pixel's o0 lands on its own pixel (all 1062 covered pixels, in all four tables); o1-o7
  write fewer pixels (508, 604, 400, 348, 348, 348, 312) and where they land is the instance's own
  pixel or one 16 or 32 rows and 0 or 32 columns away, a few at other offsets, for the plain table
  and for PDS_SIZE bits 17:16 = 0, 1, 2.
  *usse; HW, infer; data: `usse-output-registers`.*
- `E082` With the iteration marked done (U1 bit 24, iteration source set) the colour phase after a
  pt phase does not get the pt phase's writes or the iterated attributes: in the punch-through scene
  (render block word 1 = 0x08400200) none of the 4 + 3 cases writes a pixel in either of two runs,
  and in the depth-always scene (0x01d00200) they write 118 to 407 pixels of the colour 0xff00ff00,
  never the 0x12345678 the pt phase wrote, the count differing from run to run.
  *usse; HW; data: `isp-punch-through`, `isp-punch-through-followup`.*
- `E083` atst8 is an alpha test of src0's top byte against src2's top byte by the function in src2
  bits 15:13 (0 never, 1 less, 2 equal, 3 lequal, 4 greater, 5 notequal, 6 gequal, 7 always),
  writing src0 and setting the predicate on a pass and leaving both on a fail, in all 687 fill
  cases; in a fill the fb, nfb, optdwd and twosided modes, src1 and the other src2 bits change
  nothing, and depthf and pcoeff change nothing; in a punch-through pass a pixel is kept by atst8
  only with fb and a control word of 0xe001 or 0xffffffff in src1; ptoff is not measured.
  *usse; HW; data: `usse-alpha-test`, `isp-punch-through`, `isp-punch-through-followup`.*
- `E084` The EDM tick lasts HostCtl dword 6 cycles of a 399.0 MHz clock: with dword 6 at 200000,
  400000 and 800000 the tick runs at 1995.00, 997.48 and 498.76 Hz, 399.00 MHz to within 0.01 MHz
  each time, while TIMER counts 1/16 of that clock whatever dword 6 holds.
  *edm; HW; data: `edm-tick-rate`.*
- `E085` c0-c63 read the same fixed table in a fill shader, through a store's source and through a
  mov alike (c0-c2 zero, c3 1.0, c4-c13 powers of two 2 to 1024, c14-c27 0.5 down to 2^-14, c28-c39
  e, 1/e, sqrt 2, 1/sqrt 2, pi/4, pi/2, pi, 1/pi, 2/pi, 4/pi, 2 pi and 2^-16, c40-c44 small values
  from 1.55e-6 to 2.08e-2, c45-c47 two f16 1.0s, c48-c51 zero, c52-c55 1.0, c56-c59 all ones,
  c60-c63 0x7fff7fff); g0-g63 read small values only, most of them zero.
  *usse; HW, infer; data: `usse-constant-banks`, `usse-constant-banks-followup`.*
- `E086` In a 64x32 fill g23 is the pixel's x in its 32x16 tile, g24 its y, g25 its place in the 2x2
  quad, g17 the tile quarter (2 * x bit 4 + y bit 3), g18 a per-tile number (0x16, 0x14, 0x12, 0x10
  for the tiles (x bit 5, y bit 4) = (0,0), (1,0), (0,1), (1,1)) and g39 the quad's place in a 4x4
  block (4 * x bit 1 + 8 * y bit 1); g21 is constant over 4x4 blocks with 27 values from 4 to 0x1f,
  g22 constant over quads with 12 values from 0 to 0xb, and both differ between two runs (528 and
  544 pixels); g20 and g41-g43 are constants.
  *usse; HW, infer; data: `usse-constant-banks`, `usse-constant-banks-followup`.*
- `E087` smbo's first value offsets the destination register number of the instructions after it (+1
  writes r11, +2 r12, and a repeat moves every write), its third value offsets source 1 and its
  fourth source 2 (a store's source register included), the second value changes nothing the probes
  read; the offsets stay in force for the rest of the task; moest writes no register and no scratch
  dword in any case that completes (smbo's own offsets move the dump in one); and smoa with non-zero
  offsets does not fault by itself, but three cases fault the job in both runs (smoa #-1, #-2, #511,
  #-512 followed by the sixteen moest selectors, and smoa mirror on all four operands in two smr
  cases) and two in the first run only (smoa #1-#4 or smbo #1-#4 followed by the moest selectors).
  *usse; HW; data: `usse-moe`, `usse-moe-followup`.*
- `E088` .quadlead on an instruction runs it for the top-left instance of each 2x2 quad only (512
  quads: the 512 top-left pixels stored the incremented value and the other 1536 stored the
  unchanged one); lock #0 or #3 around a shared counter serialises quads, not instances (the counter
  ends at 0xd0000200, 512 updates for 2048 pixels, each value in exactly the four pixels of one
  quad); setm #0, #1, #2, #4, #8 and #15 change nothing of that.
  *usse; HW; data: `usse-quad-lock`, `usse-quad-lock-followup`.*
- `E089` A predicated br whose quad's instances disagree takes the whole quad where its top-left
  instance (instance 0) goes: p0 set on the even-x instances gives 4 in all 2048 pixels, p0 set on
  the odd-x instances or on instances 1-3 gives 7 in all 2048; when the quad agrees, each quad
  follows its predicate (1024 pixels 4, 1024 pixels 7); br.syncent and br.nosched give the same
  results as br, and br.synce and br.mon hang the job in the two predicates they were run on.
  *usse; HW; data: `usse-branch`.*
- `E090` ld/st with a post-increment access the base address and then advance it by the increment in
  dwords (two loads of [r20,#1++] read dwords 64 and 65 and leave r20 8 bytes on; [r20,#2++] reads
  dwords 64 and 66 and leaves it 16 bytes on; two stores of r1 and r2 land in dwords 64 and 65); ldr
  #7 and #8 read 0x01150000 and 0x0001000d; a value moved to pclink reads back unchanged (0x123).
  *usse; HW; data: `usse-memory`.*
- `E091` A recorded case for each of 16 groups of USSE forms that had no hardware readback (140
  cases): 136 complete and record their registers and pixel, the 4 smp repeat forms fail on the
  hardware, and ima16 with word bit 37 or 47 set (form 172) gives the same 0x0025001c as the plain
  form 27.
  *usse; HW; data: `usse-form-coverage`.*
- `E092` The test group's umul8, uadd8, usub8, uadd16 and umul16 work on each byte or 16-bit lane on
  its own, unsigned and wrapping; .sat clamps the unsigned byte results to 255 (the Rogue
  instruction set reference's UADD8, UMUL8, UADD16 and UMUL16 lane by lane); iadd8.sat writes the
  wrapped bytes, not a signed clamp; imul8, iadd16 and imul16 give the unsigned results.
  *usse; HW, infer; data: `usse-lane-integer`.*
- `E093` The three numbered modifiers act uniformly over all their values in 71 cases: .repeatN runs
  N times (1 to 16), mov and xor stepping every operand one register per iteration and touching no
  register past the Nth; ldad .fetchN loads N consecutive dwords into N registers (1 to 16),
  starting one element after the address with any fetch flag, by register offset too, and stepping
  the destination one register before any smlsi; imae .rsN shifts the sum right by N (0 to 7),
  arithmetically when signed; a fetch that would run past the task's temporaries (r29 or r30 with
  fetch4 over 32 temporaries) writes nothing.
  *usse; HW; data: `usse-numbered-modifiers`, `usse-numbered-modifiers-followup`.*
- `E094` The test group's unorm8 operations clamp per byte: fpadd8 is x + y up to 255, fpsub8 x - y
  down to 0, and fpmul8 round(x * y / 255) exactly rounded, in all 24 cases (96 byte pairs); the
  zero test sees each byte's unclamped result: an fpsub8 whose byte 0 clamps to 0 without being 0
  does not test as zero.
  *usse; HW; data: `usse-unorm8`.*
- `E095` fdpc's clip-plane result has no visible effect with the TA state our kernel sets by
  default: a vertex shader that runs fdpc against a plane every vertex is outside of (cp0 and cp5,
  the plane (0, 0, 0, -1)), inside of, or that splits the triangle by x still draws the control's
  image, 1062 triangle pixels and 3034 background.
  *usse; HW; data: `mte-user-clip-planes`.*
- `E096` With a user clip plane enabled by the output-select word, fdpc's cpN value becomes plane
  N's distance for the vertex, replacing the distance dword the vertex writes, and has no effect on
  a disabled plane; fddpc gives its first product (s0 * s1) to cpA and its second (s0 * s2) to cpB.
  *usse; HW; data: `mte-user-clip-planes`.*
- `E097` smlsi's swizzle mode makes iteration k of a repeat use the swizzle's k-th component as its
  register offset (source 1 under wzyx reads r4, r3, r2, r1, under xxxx r1 four times; a destination
  under wzyx writes r23 down to r20); smoa's offsets shift an operand's register number on every
  instruction (destination +1 writes r11, source 1 +1 or +2 shifts a repeat8 by that much), and with
  an smr range R and mode repeat the destination index wraps once, to index - R (smr 2, 4, 8 put r20
  at r18, r16, r12, and offset +2 moves each up two); moest writes no register and no scratch dword
  and setfc changes nothing a load or a repeat shows.
  *usse; HW; data: `usse-moe`.*
- `E098` eldd and eldq load the dword or the four dwords of element index + offset from the base
  when that element is below the limit (their last operand), and zeros otherwise; no cache mode
  (ldad's, stad's, eld's .bypassl1) makes a reload miss a store: in one instance all 21 combinations
  read the stored value on every pixel, and across instances the stored value is read except by 12
  or 64 pixels of tile (0, 0) in 10 of 21 combinations.
  *usse; HW; data: `usse-cache-control`, `usse-cache-control-followup`.*
- `E099` setm #0 to #15 masks nothing a fill or a single-sample triangle shows: in a fill every one
  of the 2048 pixels writes the marker in all 23 cases, with or without .skipinv on the mov and with
  a second mov, and the triangle's pixel shader after setm #0, #1 or #15 keeps exactly the 1062
  covered pixels, as without setm.
  *usse; HW; data: `usse-instance-masking`.*
- `E100` bexception between two marker writes, with or without .nosched, hangs a fill's pixel task
  (the job times out and the context is lost), and the baseline triangle run before and after each
  case is exact, so the kernel recovers the GPU; the same fill without bexception completes with
  both markers.
  *usse; HW; data: `usse-branch`.*
- `E101` phas's wait none lets a pixel shader's next phase run at once, with the temporaries the
  first phase wrote (1062 of 1062 pixels under parallel, 1060 under perinstance); perinstance does
  not run instances one at a time (the unlocked counter ends at 16 under parallel and 48 under
  perinstance, with 16 and 48 distinct values over 1062 pixels); a pixel shader hangs waiting on
  vcull in both modes, and waiting on pt it writes no counter or temporary value; the vertex shader
  draws alike waiting on vcull or none, in either mode, and hangs waiting on pt under parallel.
  *usse; HW, infer; data: `usse-phases`.*
- `E102` Bit 42 of the vertex emits (.twopart) is needed on emitvcbvtx and not on emitmtevtx:
  without it on emitvcbvtx alone the job hangs, without it on emitmtevtx alone the triangle is exact
  (1062 pixels), and without it on both the job completes with no triangle drawn.
  *usse; HW, infer; data: `usse-emits`.*
- `E103` setm #0 to #15 masks no sample of a 4x multisampled triangle, before an o0 write with or
  without .skipinv: all 34 cases draw the same 1248 samples; and no pixel of a single-sample
  triangle written without .skipinv is masked: all seven cases draw the 1062 covered pixels, 22 to
  36 more than the triangle covers.
  *usse; HW; data: `usse-instance-masking`.*
- `E104` In a triangle's pixel shader an instruction with .skipinv reaches exactly the 1062 covered
  pixels in all three repeats, and one without it also reaches 16 to 26 uncovered pixels of the
  quads the triangle covers, whole quads at a time (6 to 10 of the 42 partly covered quads);
  .skipinv skips the instances that cover no pixel.
  *usse; HW; data: `usse-instance-masking`.*
- `E105` smoa's address modes map an operand's first register once, and the iterations step on from
  it: with i the register plus the operand's smoa offset and M its smr range less one, none gives i,
  clamp min(i, M), mirror 2M - i and repeat i - (M + 1) when i is past M; this holds for the
  destination and for source 1 in all 70 cases (14 starting below r0), smr's field 0 goes with the
  destination and field 2 with source 1, and a first register below r0 drops writes and reads values
  from outside r0-r46.
  *usse; HW; data: `usse-moe`, `usse-moe-followup`.*
- `E106` .twopart (bit 42) on the state task's emitvcbst or emitmtest, alone or on both, changes
  nothing: the triangle is drawn exactly (1062 pixels) in all four cases.
  *usse; HW; data: `usse-emits`.*
- `E107` No load cache mode keeps an old dword when the host writes it while the job runs: with 1024
  reloads, in two runs, ldad, ldad.bpcache, ldad.fcfill, eldd, eldd.bpcache, eldd.fcfill and
  eldd.bypassl1 each show pixels that read the old value for at most 149 reloads and the host's
  value on every later one, and no pixel ends on the old value; every ready store (stad,
  stad.bpcache, stad.fcfill) reached memory, seen by the host 0 to 1935 microseconds after the
  submit.
  *usse; HW, infer; data: `usse-cache-control`, `usse-cache-control-followup`.*
- `E108` bexception branches like ba and br through the fields its form leaves out: with the target
  field n it jumps to instruction n, with bit 38 set it jumps by n from itself, and its predicate
  field (58:56) gates it; with the fields at 0, as the assembler writes it, it jumps to instruction
  0, which is how it hung a fill.
  *usse; HW, infer; data: `usse-branch`.*
- `E109` moest does not load the MOE state word its selector names from its register: after moest
  r17, #0 to #8 with r17 = 0x00000001, 0x00001001 or 0x01010101, a mov and a mov.repeat4 land and
  every dumped register reads as with no moest (28 of 28 cases identical); setfc #0-#1, #0-#1
  changes neither how a quad whose instances disagree branches (2048 of 2048 pixels give the
  control's value) nor what ldad.fetch4 loads (5 of 5 identical).
  *usse; HW, infer; data: `usse-moe`, `usse-moe-followup`.*
- `E110` In a triangle's two-phase pixel shader, parallel and perinstance give phase 1 the same view
  of what other instances did in phase 0: a counter incremented under lock #0 ends at 291 (0x123) in
  both and reads back with a similar spread (97 and 98 distinct values, smallest values 9 and 11
  under parallel, 9 and 10 under perinstance), and quads that skip a long spin read the marker the
  spinning quads store, in both modes.
  *usse; HW; data: `usse-phases`.*
- `E111` In a triangle's pixel shader every instance of every quad the triangle touches runs an
  instruction without .skipinv in four of five runs (291 quads, 4 instances each, 1164 distinct
  slots, for 1062 covered pixels; one run counted 1112 slots, 278 quads); what varies is whether an
  uncovered instance's o0 lands, and it lands for a whole quad or not at all: 32 to 36 of the 42
  partly covered quads here, 6 to 13 in the shorter shaders of E104 and E103.
  *usse; HW; data: `usse-helper-instances`.*
- `E112` phas's instance mode decides which instance a divergent quad's predicated branch follows:
  under parallel the quad's first covered instance (24 pixels, the right columns of the 12 quads
  whose left column is uncovered, branch as instance 1 does), under perinstance instance 0 even when
  it covers no pixel (all 1062 pixels branch as instance 0); .skipinv skips the uncovered instances
  under both modes.
  *usse; HW; data: `usse-phases`.*
- `E113` How many uncovered helper pixels' o0 lands is largest at 32 nops (71 of the triangle's 102
  in all three runs), against 26 to 43 for 0 to 16 nops and 53 to 59 from 64 nops on; quads whose
  instance 0 (top left) is covered land more often (17 of 18 at least once in nine runs from 32 nops
  on) than those whose instance 0 is a helper (16 of 24).
  *usse; HW, infer; data: `usse-helper-instances`.*
- `E114` The texture sampler keeps what it fetched in a cache that USSE stores do not update: after
  a pixel samples a texel, a store to it or to the texel beside it is not seen by the next sample,
  with idf + wdf and with every ci, cf and cfi level and flag between (17 cases); a texel the
  sampler has not fetched shows the store (the texel far away, and the cold cases); idf pixelbe and
  smp.syncs hang a fill.
  *texture; HW, infer; data: `texture-sampler-cache`.*
- `E115` phas's sample and selective rates change nothing a triangle shows at 1x or 4x: the pixel
  shader still runs once per pixel (all 324 pixels drawn at 4x hold one value over their four
  samples, one instance's g23, g24 and g25), every image is identical to the pixel rate's, and setm
  #1, #3, #5 and #15 mask nothing at any rate.
  *usse; HW; data: `usse-sample-rate`.*
- `E116` smp's .pcff16 takes its depth-compare reference as the f16 in the low half of the register
  after the coordinates, at full f16 precision and signed, where .pcf takes the whole register as an
  f32; the result is the same (1.0 for an f32 texture when the compare holds, else 0), over all
  eight cases.
  *texture; HW; data: `texture-sampler`.*
- `E117` Nothing tried turns on per-sample shading: with the pixel shader's phas at the sample rate
  on a 4x triangle, no unknown bit of the pixel task's U1 (bits 0, 1, 22, 23, 26 to 31), no bit of
  its U2 (all 32), no bit of the render command's te_aa (word 1) or aa_mode_3d (word 13), and no
  free bit of ISP words 0 and 1 makes a pixel's four samples differ; aa_mode_3d bit 1 cleared gives
  a 916-pixel image without the 4x layout, bit 0 hangs and bit 31 draws nothing, te_aa bit 29 draws
  nothing and bits 30 and 31 change the coverage (1312 and 832 pixels), and ISP word 0 bit 28 hangs
  a 4x render.
  *usse; HW; data: `usse-sample-rate`.*
- `E118` A fill's shader starts at its code base (pclink read after a call at instruction 5 gives 6
  in both runs); in a two-phase pixel program phase 1 closed by phas.end completes with every one of
  the 1062 pixels written, with or without a call or a pclink move; phas's register form, phas srcA,
  srcB, started no next phase from the next phase's absolute index, an offset or the doutu U0 layout
  against the immediate form's fields or its whole high dword: six cases hung, one faulted and the
  offset case completed with 166 pixels of neither phase's colour.
  *usse; HW, infer; data: `usse-phases`.*
- `E119` A phase boundary is a barrier under both instance modes: in a two-phase fill, the quads
  that skip phase 0's 4096-iteration spin all read the marker their 4x4 block's spinning quads store
  at the end of phase 0 (all 2048 pixels, in each of two runs, under parallel and under
  perinstance), while the same code in one phase leaves 112 of the 128 skipping quads (448 pixels)
  reading the slot's fill value.
  *usse; HW; data: `usse-phases`.*
- `E120` No bit of the render details' isp_sample_pos (word 19), reg_0800 (word 22),
  isp_line_sample_pos (word 26) or frag_flags (word 53), nor of the render command's word 10, runs a
  4x triangle's sample-rate pixel shader per sample; 22 bits of isp_multisamplectl (render details
  word 20, the same register as command word 16, with identical images bit for bit) move the samples
  and the coverage by a few samples (1240 to 1256 covered samples in 320 to 328 pixels against the
  control's 1248), the rest change nothing.
  *usse; HW, infer; data: `usse-sample-rate`.*
- `E121` phas's vcull wait makes the next phase of a vertex shader wait for the MTE's cull decision
  and skips it for a culled triangle: with MTE control's cull mode 1 culling the triangle, phase 1
  runs under none (one increment of its counter) but not under vcull, and the triangle is not drawn
  either way; with cull modes 0 and 2 the triangle (1062 pixels) is drawn and both phases run under
  both waits.
  *usse; HW; data: `usse-phases`.*
- `E122` Of the three registers the init script sets once, 0x0810 implements bit 0 only, 0x0814 bits
  16:0 and 0x0818 bits 10:0; a fill with any of them written to 0, to any single bit or with any one
  of bits 0 to 15 of its init value flipped completes exactly as with the init values.
  *platform; HW; data: `platform-init-registers`, `platform-init-register-jobs`.*
- `E123` Three models, one each for bilin, firv and firh, fit every video-filter case they were
  fitted to (bilin 636 of 636, firv 1068 of 1068 with a known latch, firh 2411 of 2411 with #s of -4
  or more), while the 563 firh cases with #s below -4 are recorded only and the dumped registers
  repeat in the follow-up run in 4835 of 4836 cases.
  *usse; HW; data: `usse-video-filters`, `usse-video-filters-followup`.*
- `E124` A fill whose shader runs a counted loop of 8 instructions takes a host-measured time linear
  in the iteration count taken modulo 65536 (3.03 µs an iteration over the 64x32 fill, 100 ms at
  zero, 0.95 ms rms), not in the count itself, although every run ends with the counter at 0.
  *usse; HW; data: `usse-loop-timing`.*
- `E125` From a fill's secondary PDS program, douta writes its first word to the secondary attribute
  named by bits 19:8 of its second word, and all sixteen words reached sa0 to sa15 with the
  background object's secondary attribute size at 4, 1 and 0 rows; attributes a job does not write
  read what earlier jobs left, and which earlier job differs between the first and the follow-up
  run; from the triangle's primary program the markers did not arrive, and markers A read the same
  sixteen values in both runs.
  *pds; HW; data: `pds-douta`, `pds-douta-followup`, `pds-alu`.*
- `E126` On a 128x128 triangle render of 64 tiles of 16x16, flipping bit 3 of the end-of-tile task's
  DOUTU1 or bit 12 gives one and the same whole picture, flipping bits 4 and 5 or bits 13 to 15
  writes every pixel but exchanges tiles, and flipping bits 6 to 11 or 16 to 21 writes no pixel.
  *pds; HW; data: `pds-pixel-event`, `pds-pixel-event-followup`.*
- `E127` In a fill's PDS secondary program, all six load and store cases (loads at 0, 0x40, 0x1000
  and 0x10000, a store then a load with and without a fence) fault the job, movs to mr, tim, ir0,
  slc, douts and a movsa on douta complete it and write nothing that the attributes read back show
  (the ir0 case reads the tile position), and movs to doutc faults it.
  *pds; HW; data: `pds-load-store`.*
- `E128` In a fill's PDS secondary program, bit 9 (.1) of a special source makes a mov16 read 0 (of
  ir0, pc and tim alike; ir1 reads 0 in any case) and a 16-bit 0 is all it writes, but in mov32 it
  reads the same register as .0; ir0 is the tile position, tile_y << 10 | tile_x, of the fill's
  16x16 tiles and pc.0 reads 3 ahead of the reading instruction's index with a few irregular places;
  a second run agrees.
  *pds; HW; data: `pds-moves`, `pds-alu`, `pds-load-store`, `pds-moves-followup`,
  `pds-alu-followup`.*
- `E129` With the render's pixel-event info word at 0, the douta writes of the replaced pixel-event
  program reach sa0 to sa15 of the plain USSE task it starts, all sixteen words in order; the data
  does not vary the info word, so the gate that bits 5:0 would make is not tested.
  *pds; HW; data: `pds-pixel-event`, `pds-pixel-event-followup`.*
- `E130` In the pixel-event program of triangle jobs, input word ir0 reads 0 on a one-tile render
  and tile_y << 10 | tile_x for the 16x16 tiles of larger renders (59 of the 60 tiles that stored
  anything on a 128x128 render, tile_y up to 255 on a 32x4096 one), ir1 reads 2 and, on the last
  tiles, 6; the vertex-index reading of ir0 is not in this data.
  *pds; HW; data: `pds-pixel-event`, `pds-pixel-event-followup`.*
- `E131` In the triangle host's primary pixel program, a douti started with no wait and no texture
  fetch delivers nothing to pa0 for any of the 64 sources (pa0 keeps 16 stale values), while with
  the fetch wait (DOUTU1 0x02000004) and the fetch's doutt it delivers source 0 (the pixel's x +
  0.5), source 1 (the coordinate set's x), sources 32 and 33 (0xff000000) and 0 for sources 2 to 31,
  34 and 35, and sources 36 to 63 leave the texel.
  *pds; HW; data: `pds-iteration-sources`, `pds-iteration-sources-followup`, `texture-fetch`.*
- `E132` With DOUTI0 bits 23:22 at 0, 1 and 2 the textured triangle's iteration writes x; x and y;
  x, y and 0 to pa0 onward and the texel in the next dword at every pixel, with 3 the first two
  components hold x and y on 1058 and 1031 of the 1062 pixels but pa3 is 1.0 on 1004 and the texel
  on 58, so the texel is not always in the dword after the components; bit 21 gives every pixel
  -0.75, which is vertex 0's x (tried with source 1 only), and bit 28 writes x as a half float in
  the low half of the dword at all 1062 pixels.
  *pds; HW; data: `pds-iteration-sources`, `pds-iteration-sources-followup`.*
- `E133` With state word 13 at 0x83800 and state word 16 at 5, iteration source 32 gives a vertex
  colour packed as ARGB8888, the colour of vertex 0, 1 or 2 for shade models 0, 1 and 2 on 753, 751
  and 723 of the 1062 triangle pixels and a varying colour for 3, while with word 13 left at the
  harness's default and word 16 at 4 it gives 0xff000000 under every shade model, and either word
  alone gives no colour (word 13 alone faults the job).
  *pds; HW; data: `pds-iteration-sources`, `pds-iteration-sources-followup`.*
- `E134` With register 0x0abc written to 0 (it holds 0xe) before the job, a fill, a geometry-only
  render and a whole render each hang and the context is lost, and each time the register is
  restored to 0xe a fill passes again; twelve values of 0x0abc from 0x02 to 0x3e, all with bits 4:1
  nonzero, leave the time of a 256x256 render within 1.2 percent.
  *pds; HW; data: `pds-task-limits`.*
- `E135` With DOUTI word 1 bit 6 set, the shade model of DOUTI0 (bits 26:25) 0, 1 and 2 gives every
  one of the 1062 pixels the x of vertex 0, 1 and 2 (-0.75, 0.75, -0.375), as DOUTI0 bit 21 does,
  but shade model 3 hangs the job where bit 21 iterates smoothly; word 1 at 0x60 and 0xc0 gives
  vertex 0's value as bit 6 alone does, and with word 1 at 0 all four shade models iterate smoothly.
  *pds; HW; data: `pds-iteration-sources`, `pds-iteration-sources-followup`.*
- `E136` Writing 0, 1, 2, 4, 8, 0x10, 0x20, 0x30 or 0x3f into bits 5:0 of register 0x0800 before a
  1024x1024 render whose 150-instruction pixel shader runs on 276192 pixels does not change the time
  the ISP is clocked (28646 to 28776 us in 50 jobs, against 1521 to 1848 us for the store alone) or
  any pixel.
  *pds; HW; data: `pds-task-limits`.*
- `E137` Clearing DOUTU1 bit 2 in the primary pixel program of the working punch-through scene (U1
  0x01000000 against 0x01000004) gives the same image in each of the three cases, in both runs: 2998
  background pixels, 1062 of 0x00000000 and 36 of 0x3d800000 in the always fb case and 4096
  background pixels in the other two.
  *pds; HW; data: `isp-punch-through`, `isp-punch-through-followup`.*
- `E138` DOUTU1 bit 2 changes no image in any of our runs, set or clear, on a pixel task, the
  end-of-tile task or the punch-through scene, so we read it as a scheduling hint of the task; this
  reading is an inference and no run measured a scheduling effect.
  *pds; infer; data: `pds-data-words`, `pds-data-words-followup`, `isp-punch-through`,
  `isp-punch-through-followup`.*
- `E139` PDS_SIZE bits 17:16 are not unused: at 0, 1 and 2 against 3 they change where the output
  registers o1 to o3 land, and o0 and the pixels it covers stay the same; we read the field as a
  size or count of the output register banks a pixel task is given, 3 being the plain value; this
  reading is an inference.
  *pds; infer; data: `usse-output-registers`.*
- `E140` With CR_PDS_REG_0ABC bits 4:1 at 0 a fill, a geometry-only render and a whole render each
  hang (the job times out and the context is lost), and a render of 256x256 triangles takes 67297 to
  68131 us at twelve values of the bits, 1 to 8, 10, 12 and 15; we read the field as one count of
  PDS task slots shared by every data master; this reading is an inference.
  *pds; infer, HW; data: `pds-task-limits`.*
- `E141` CR_PDS_REG_0A78 (6 bits, 0x2c as the firmware leaves it) changes no image at any of its 64
  values (E045); the render time of 256x256 triangles at seven of its values is 67288 to 67658 us at
  five of them, and 69038 and 70977 us at 0x20 and 0x01; we read it as a PDS tuning value with no
  effect on the image, and its effect on time is not settled; this reading is an inference.
  *pds; infer, HW; data: `pds-task-limits`, `platform-untouched-registers`.*
- `E142` In a PDS program with no load or store, rfence and rwfence leave the data-segment registers
  as they are: with no fence, with rfence and with rwfence the sixteen registers handed on through
  douta equal the inputs, and with both fences between three dependent mov32s each mov reads what
  the one before wrote; all four jobs complete.
  *pds; HW; data: `pds-memory`, `pds-memory-followup`.*
- `E143` With the scratch mapped in the first MiB, where the PDS reaches, a PDS load's dwords reach
  its registers only at the next rfence or rwfence (never by the end of the program, and not after
  four nops), a store takes the register's value at the time it runs, a load after a store reads the
  stored value, and stores of 8 dwords complete; rwfence after a store faults the job in 10 of 10
  programs of the table that have one, in both runs, 5 of them after a completed job or first in
  their table and 5 right after a faulted job.
  *pds; HW; data: `pds-memory`, `pds-memory-followup`.*
- `E144` A PDS program with stores and no rwfence faults when its stores total 2, 3 or 4 dwords,
  however they are split, after every dword has landed and the program has reached its end (20
  programs, in both runs), and completes when they total 5 to 9, 12, 16 or 18 (16 programs, in both
  runs) and in 12 of the 15 programs that total 1 or 10; the other three fault in one run only (two
  of total 1 in the follow-up run, one of 2 + 8 in the first); a job with rwfence run right after a
  faulted job faults whether or not it has a store (11 of 11, in both runs).
  *pds; HW; data: `pds-memory`, `pds-memory-followup`.*
- `E145` The kernel logs of the two runs of pds/memory hold 37 (first run) and 38 (follow-up run)
  BIF fault lines, one for each PDS case that faulted, in order; the status is 0xd2000 for the store
  faults (21 and 22) and 0x92000 for the 16 rwfence faults of each run; the 36 cases that faulted in
  both runs have the same status, address and SB in both, and the same CID in 32; the value
  (CR_BIF_FAULT) splits into the fields CID (3:0) and SB (8:4) as follows: SB is 2 or 3 in all 75,
  with 2 for rwfence after a store and 3 for rwfence with no store before it, and CID is 0 in all 16
  faults under one page directory in each run.
  *pds; HW, DDK; data: `pds-memory`, `pds-memory-followup`.*
- `E146` PDS #13 (40 instructions, 24 data dwords) tests one event word and starts one of four EDM
  tasks, three fast paths for exact event groups and a general task for everything else; PDS #14 (14
  instructions, 12 data dwords) tests one request word and starts one of three tasks by request-bit
  group, in priority order.
  *edm; RE, infer; data: `firmware-images`.*
- `E147` Run through the repository's decoder and simulator, the 29,137 vectors the probe runs gave
  (27,174 USSE, 1,963 PDS) show no mismatch: 6,028 scalar USSE vectors, 135 pixel vectors and 634
  PDS vectors pass, 19,217 + 26 + 235 stop as unsupported, and 166 USSE (165 scalar and 1 pixel) and
  18 PDS vectors are left out because one instance cannot reproduce their readback; 170 of the 219
  USSE forms and 24 of the 27 PDS forms have a passing vector.
  *usse; HW; data: `vectors-usse`, `vectors-usse-followup`, `vectors-pds`, `vectors-pds-followup`,
  `vectors-texture`, `vectors-isp`, `vectors-isp-followup`, `vectors-mte`, `vectors-pbe`,
  `vectors-pbe-followup`, `vectors-ta`, `vectors-vdm`, `vectors-vdm-followup`, `pds-alu`,
  `pds-alu-followup`, `pds-data-words`, `pds-data-words-followup`, `pds-douta`,
  `pds-douta-followup`, `pds-douti-fields`, `pds-douti-fields-followup`, `pds-end-of-tile`,
  `pds-iteration-sources`, `pds-iteration-sources-followup`, `pds-iteration-waits`,
  `pds-iteration-waits-followup`, `pds-load-store`, `pds-memory`, `pds-memory-followup`,
  `pds-moves`, `pds-moves-followup`, `pds-pixel-event`, `pds-pixel-event-followup`,
  `pds-task-limits`, `pds-timer`, `pds-timer-followup`, `pds-vertex-programs`,
  `texture-sampler-cache`, `usse-alpha-test`, `usse-branch`, `usse-cache-control`,
  `usse-cache-control-followup`, `usse-colour-ops`, `usse-constant-banks`,
  `usse-constant-banks-followup`, `usse-decoder-vectors`, `usse-dot-products`, `usse-dual-issue`,
  `usse-efo`, `usse-emits`, `usse-filter-banks`, `usse-filter-control`, `usse-filter-gain`,
  `usse-filter-sets`, `usse-filter-taps`, `usse-flags`, `usse-float-functions`, `usse-float-minmax`,
  `usse-float-misc`, `usse-fmad`, `usse-fmad16`, `usse-form-coverage`, `usse-gradients`,
  `usse-helper-instances`, `usse-indexing`, `usse-instance-masking`, `usse-integer`,
  `usse-integer-dot`, `usse-internal-registers`, `usse-lane-integer`, `usse-loop-timing`,
  `usse-memory`, `usse-moe`, `usse-moe-followup`, `usse-movc`, `usse-numbered-modifiers`,
  `usse-numbered-modifiers-followup`, `usse-output-registers`, `usse-pack`, `usse-phases`,
  `usse-predicates`, `usse-quad-lock`, `usse-quad-lock-followup`, `usse-repeat`, `usse-rlp`,
  `usse-sample-rate`, `usse-test-channels`, `usse-tests`, `usse-unorm8`, `usse-video-filters`,
  `usse-video-filters-followup`, `usse-video-ops`, `usse-write-masks`.*
- `E148` Render jobs from userspace draw every pixel exactly on 13 target sizes from 64x64 to
  256x256, up to sixteen tile rows and eight tile columns, with the library's render state (bit 8 of
  the render context's isp_ipfmisc word set) and no BIF fault; what clearing that bit does above
  64x64 and what the EDM's cleanups wait for are not shown by any run.
  *render; HW; data: `render-target-sizes`, `render-client-jobs`.*
- `E150` The kernel CCB command 9 (SET_HWPERF_STATUS) handler at 0x157 writes 0xffffffff to dword 2
  of the HWPerf buffer, stores command data dword 0 with bit 0 cleared as the HWPerf status word,
  and, only if bit 0 of the data was set, writes CR_HWPERF_CTRL = 0x1ff and pulses CR_HWPERF_PULSE;
  when the status is not zero it then writes HostCtl's group, shifted left 9 and masked with 0x1e00,
  to CR_HWPERF_CTRL.
  *platform; RE; data: `firmware-images`.*
- `E151` With a transfer context naming a client page directory that alone maps the fill's
  destination and an update target, the fill lands exactly and the update word holds its value,
  whether the EDM's own buffers are aliased in that directory read-write, read-only, or (for the
  fill alone) not at all; a fill aimed at a read-only alias of a kernel buffer writes nothing and
  leaves CR_BIF_FAULT naming that page and list 1.
  *bif; HW; data: `transfer-isolation`.*
- `E152` The EDM's only access to register 0x0e80 (CR_HWPERF_PULSE) is a write of 1 then a write of
  0 in the routine at 0x1ea, which also writes CR_HWPERF_CTRL; it is reached from the boot path at
  0x1c4 and from the SET_HWPERF_STATUS handler, never read, and no instruction that takes its
  register number from a register can name it.
  *edm; RE; data: `firmware-images`.*
- `E153` The routine at 0x15bc-0x1664 waits for a running TA or 3D to go quiet before a parameter
  buffer is swapped or a render is kicked: when told to settle the 3D it reads CR_SETTLE_POLL0 and
  CR_SETTLE_POLL1 (0x0308, 0x030c) together after the four ISP signature registers, then waits 1000
  loop counts and reads each set again, and loops until the xor of each set is the same on both
  reads; when told to settle the TA it does the same with CR_PPP_SIGNATURE and the two TE diagnostic
  registers instead and does not read 0x0308 or 0x030c; nothing in the firmware writes any of them.
  *edm; RE; data: `firmware-images`, `firmware-edm-dataflow`.*
- `E154` The request word TA3DCtl dword 31 has nine request bits in use, each posted by one pa1 bit
  of the event task or by a named routine and each handled by one of PDS #14's three tasks (0x1,
  0x2, 0x8 and 0x40000 by the task at 0xe74, 0x80 and 0x20000 by 0x5d4, 0x10, 0x20, 0x40 and 0x80000
  by 0xae8), and the EDM keeps the TA's state in sa8 and the 3D's in sa9 so that one TA job and one
  3D job are in flight at a time.
  *edm; RE; data: `firmware-images`.*
- `E155` In every handler of the EDM event tasks that acknowledges an event, the pa1 bit it tests
  and the CR_EVENT_HOST_CLEAR value it writes are related by acknowledged status bit = 22 minus the
  pa1 bit, for the seven pa1 bits 22, 21, 20, 10, 9, 7 and 4; pa1 bit 8 (the kernel CCB) writes no
  acknowledgement, and the timer tick arrives in pa0 bit 1; the reading that pa1 is CR_EVENT_STATUS
  bits 22-0 in reverse order fits all of these.
  *edm; RE, infer; data: `firmware-images`.*
- `E156` At TA_FINISHED (request 0x80, handler at 0x606) the EDM completes the TA command's sync and
  status words, raises SW_EVENT, and, when the kick carries LAST_KICK, flushes the tail pointer
  cache (unless render flag 0x8 is set) and queues the render details on the context's ready list
  and the 3D queue; a kick without LAST_KICK instead saves the tiling engine state and counts itself
  in the RT data set.
  *edm; RE; data: `firmware-images`.*
- `E157` The EDM's TA kernel-CCB handler (kick address 0x11d, instructions 0x11d-0x139) reads only
  the render context named in command data dword 1: it counts the kick in the context's
  submitted-commands word, queues the context on the TA queue if it was idle and had no pending
  render, and ends in the shared tail that posts the 3D and TA scheduler requests; the command's own
  address is never passed.
  *edm; RE; data: `firmware-images`.*
- `E158` The second half of the EDM's TA kick (0x9b7-0xacc) picks a DPM context slot for the RT
  data, clears (first kick, or flag 0x8) or reloads (slot held another RT data) its DPM state,
  control and OTPM, restores the tiling engine state, sets two TE_PSG bits, zeroes the RT status
  words on a first kick or flag 0x4, marks the TA running, copies the command into the render
  details, and starts the TA with a write of 1 to CR_VDM_START.
  *edm; RE, infer; data: `firmware-images`.*
- `E159` The first half of the EDM's TA kick (0x8e9-0x9b6) records the job in TA3DCtl, resets the TA
  on a FIRST_KICK, loads the context's parameter buffer unless it is already loaded (or applies a
  pending threshold update), writes the command's 28 TA register dwords, one str each in structure
  order, then the vertex partition count, maps the context's address space and invalidates caches as
  the TA flags ask.
  *edm; RE; data: `firmware-images`.*
- `E160` On a DPM out-of-memory (request 0x30, handler at 0xb50) the EDM waits for a render that can
  free memory, or grows the TA's global-list share once, or raises the ZLS page threshold, or aborts
  the macrotile; after an abort the TA stops (TA_TERMINATE, handler at 0xc23) and the EDM starts a
  partial render of what was tiled, using the render-details register block and the partial-region
  base, and its completion (request 0x80000, handler at 0xdbf) marks the macrotile's RT status word
  and restarts the TA.
  *edm; RE, infer; data: `firmware-images`.*
- `E161` The EDM's TA pick (0x6f5-0x7b0) takes a context's next TA command from its CCB only when
  the context has a counted kick and is not suspended, the command's READY bit is set, its
  transfer-queue sync is complete, its RT data is free when the kick is a first kick or has flag
  0x4, and (when another context is queued) its destination and source syncs are complete; it
  applies a PB threshold update on the way and starts the kick only when no TA is running.
  *edm; RE; data: `firmware-images`.*
- `E162` At each 3D kick the EDM writes dwords 0, 1 and 2 of the RT data's background object, in the
  3D's address space, from render details dwords 76 and 77 and from the word of the
  render-target-indexed list that render details dword 69 points at (list base plus 4 times the RT
  index); the TA kick has copied render details dwords 76 to 78 from command dwords 2 to 4.
  *edm; RE; data: `firmware-images`.*
- `E163` The EDM's 3D kick (0x112b-0x12db) records the job in TA3DCtl, picks a DPM slot for the RT
  data and loads its context unless it is resident, loads the 3D's parameter buffer unless it is
  loaded, sets the deallocation mode from render flag 0x8, writes the 52 dwords of the render
  details to 52 registers in structure order with no change except for the render-target index, flag
  0x10 and the depth and stencil flags, invalidates the caches, writes the background object (E162)
  and starts the render with a write of 1 to CR_ISP_START_RENDER; it does not write
  CR_PDS_EXEC_BASE.
  *edm; RE; data: `firmware-images`.*
- `E164` A render completes only when both the end of render (request 0x2, handler at 0xebb) and the
  3D deallocation (request 0x1, handler at 0xeb4) have arrived, in either order; the completion
  (0xfd1) then writes the RT index's destination sync, steps to the next render target or, on the
  last, completes the TA to 3D dependency, the 3D transfer-queue sync, the source syncs and the 3D
  status pairs, marks the RT data free and raises SW_EVENT; a partial render instead posts request
  0x80000.
  *edm; RE; data: `firmware-images`.*
- `E165` There is no 3D command: the kernel CCB's kick table (E012) has no render handler, the
  render details reach the 3D queue only through the render-queue routine (called from the
  TA-finished handler on a last kick, the abort path of the TA pick and two cleanup sites), and the
  3D schedule (request 0x40000, routine 0x1035) tries the transfer queue first and then the 3D
  queue, checks the ready render details' syncs before kicking, and returns to its caller after the
  first kick.
  *edm; RE; data: `firmware-images`.*
- `E166` In the firmware the render is queued at TA_FINISHED by a TA command with flag 0x2 (command
  dword 1, bit 1: the last kick), not by render flag 0x400, which the only code that tests it uses
  for a completion count; and a command that carries both the first-kick flag 0x1 and flag 0x2 runs
  the first-kick actions at its TA kick and the last-kick actions at its TA finished through the
  same code as two commands would.
  *edm; RE, infer; data: `firmware-images`.*
- `E167` The EDM tests bit 5 of a render context's flags word (dword 0) only in the render-context
  cleanup: with the bit set the cleanup clears the TA and 3D loaded-PB slots (TA3DCtl dwords 46 and
  47) that hold the context's own PB; with it clear it leaves them to the PB cleanup, which clears
  them whenever they hold that PB.
  *edm; RE; data: `firmware-images`.*
- `E169` Bit 4 of the render flags word the TA kick copies into the render details (render details
  dword 53) makes both of the firmware's code paths that start a render, the 3D kick and the
  partial-render restart, set bit 0 of CR_ISP_ZLSCTL; with the bit clear they skip that write.
  *render; HW, RE, infer; data: `firmware-images`, `firmware-edm-dataflow`.*
- `E172` The EDM tests dword 1 of the TA command with mask 0x5 at four places and mask 0x9 at three:
  at two of the 0x5 tests a non-zero result keeps the list-insertion stores that link the render
  details into the context, and a zero 0x9 result runs the cache, bank and DPM-context calls of the
  TA kick that a non-zero result skips.
  *ta; RE, infer; data: `firmware-images`.*
- `E174` The library's render contexts, sized for their target by its own rule, draw the first
  triangle exactly on 16 target sizes from 64x64 to 4096x4096 (two renders of each, 0 wrong pixels
  in every one), and a context sized for 256x256 draws a 64x64 target exactly; that the same buffers
  serve every smaller target is shown for that one pair.
  *ta; HW; data: `render-target-sizes`, `render-client-jobs`, `dpm-parameter-buffer`.*
- `E175` Between a 64x64 and a 256x256 triangle render the debugfs register file shows four tiling
  registers change as the target grows (0x020c, 0x0210, 0x0214 and 0x0248, whose values are the tile
  counts and pixel size minus one) and 0x0208 stay unchanged; the render is exact.
  *ta; HW; data: `platform-register-snapshots`.*
- `E182` With each of the TA command's twelve zero register words loaded with ~0, the culled
  triangle and the off-target triangle leave byte-for-byte the baseline's render memory (no object
  written), and the registers keep three words as aligned addresses (low 4, 4 and 2 bits clear) and
  four as full 32-bit values.
  *ta; HW, infer; data: `ta-zero-words`.*
- `E183` The TA command's twelve zero register words read best as state a TA saves and resumes when
  it is interrupted: the measurements fit it (every word zero in the job, three address-shaped, none
  a cull disable, none used as an address by a TA that runs to its end), but no run interrupts a TA,
  so the reading is untested.
  *ta; infer, HW; data: `ta-zero-words`.*
- `E184` After a one-render triangle job TA3DCtl dword 24 reads 0x32400000 and after a two-render
  job 0x324002c0, so it moves 0x2c0 for the second render; the DPM free-list status registers
  0x0700, 0x070c, 0x0710 and 0x071c change together on every render; VDM_CTRL_STREAM_BASE is not in
  the register file and is not shown.
  *vdm; HW; data: `platform-register-snapshots`.*
- `E185` With the triangle's VDM state word 1 bits 11:9 at 0 the TA writes no object and every
  region header is empty, byte for byte the render memory of the culled triangle; at 1, 6 and 7 the
  render memory is byte for byte the drawn triangle's, in both runs.
  *vdm; HW; data: `vdm-state1`, `vdm-state1-followup`, `ta-zero-words`.*
- `E186` After the jobs with VDM state word 1 bits 15:13 at 0, 5 or 6 hang, the saved render memory
  holds no object in either run, as does the three-index lines job; but a job hung in its pixel task
  leaves its object in the first run and none in the follow-up run, so a missing object does not
  show that the TA stopped before writing it.
  *vdm; HW; data: `vdm-state1`, `vdm-state1-followup`.*
- `E187` VDM_TASK0 bits 31:28 at 7, 1 and 0 and VDM_STATE1 bit 8 set leave the saved render memory
  (parameter buffer and TA data) byte for byte the same as the plain triangle's, in the runs that
  have them; neither field reaches what the TA writes for this triangle.
  *vdm; HW; data: `vdm-vertex-tasks`, `vdm-state1`, `vdm-state1-followup`.*
- `E189` VDM_TASK0 bits 31:28 set how many vertices one vertex task takes: with 126 vertices, values
  1, 2, 5 and 6 give tasks of 2, 3, 6 and 7 vertices in index order, each ending early when its last
  quad is short of vertices, values 3, 7 and 15 fill every quad of four, and 0 gives single-vertex
  tasks for 18 vertices and then hangs the job.
  *vdm; HW; data: `vdm-vertex-tasks`.*
- `E190` VDM_TASK0 bits 31:28 are the number of vertices per vertex task less one, a reading that
  fits the values 0, 1, 2, 5 and 6 and is not told apart from a cap on a task's quads at 3, 7 and
  15.
  *vdm; HW, infer; data: `vdm-vertex-tasks`.*
- `E191` In the triangle's VDM state word 1, setting bit 12 makes the TA write no object and leave
  all 64 regions empty, setting bit 18 hangs the job, and clearing bit 25 changes neither the TA's
  output (byte for byte) nor the image, in both runs of the sweep.
  *vdm; HW; data: `vdm-stream-words`, `vdm-stream-words-followup`, `vdm-state1`,
  `vdm-state1-followup`.*
- `E192` A coordinate set on the vertices needs three words changed together, which the probe tool's
  vertex-coordinates option does: OUTSEL's vertex size (blk:13 bits 19:16) 4 to 6 dwords, the
  coordsize word (blk:16) 0 to 2 and the vertex task's output size (vdm:7 bits 31:24) 1 to 2 rows;
  with the size alone at 5 or 6 the triangle keeps 490 of its 1062 pixels, and the output size alone
  at 0, 3, 5 or 9 removes it.
  *mte; HW; data: `pds-iteration-sources`, `vdm-stream-words`, `vdm-stream-words-followup`.*
- `E193` With the viewport's z offset at 0.75 and a vertex program that sets z to the clip x, the
  64x64 triangle draws 1026 of its 1062 pixels, those whose clip x is below 0.5 (the last at
  0.484375), so the depth is the z offset plus 0.5 times z against the background depth of 1.0, and
  vp5 (blk:11) is the viewport's z scale.
  *mte; HW, infer; data: `isp-depth-test`.*
- `E194` The triangle's size goes as 1/w (261 pixels at w 2, 3212 at w 0.5, the whole target from w
  1e-3 to 1e-5) and below w 1e-5 it shrinks away (395 pixels at 2e-6, 100 at 1e-6, 16 at 5e-7, 1 at
  1e-7, none at 0 or below); the state block's WCLAMP word (blk:14) holds 1e-5 in the job and, set
  to 1e-3, removes the triangle at w 1e-5 and below, set to 1e-7 or 0 keeps it whole down to 5e-7;
  the TA command's two 1e-6 floats change none of it.
  *mte; HW, infer; data: `mte-clipping`.*
- `E195` MTECTL (blk:15) bits 8:7 choose which vertex's values the clipper gives the vertices it
  makes (0 interpolated values, 1, 2, 3 vertex 0's, 1's, 2's) and the 2-bit fields from bit 10 say
  per attribute whether that choice is dropped for interpolation again; on a triangle that is not
  clipped no tried value changes the image, and bit 9 and bit 26 of the index list's third word
  change nothing clipped or not.
  *mte; HW; data: `mte-mtectl`.*
- `E196` With MTECTL bit 6 the MTE takes the vertex outputs x and y as window coordinates in pixels,
  as the shader wrote them, with no division by w and no viewport: the scaled triangle draws a
  3-pixel corner at scale 8 and a 66-pixel corner at scale 32 whatever w is (1 or 2), and the
  object's third group of three dwords holds w itself.
  *mte; HW, infer; data: `mte-mtectl`, `vdm-state1`, `vdm-state1-followup`.*
- `E198` OUTSEL bits 7:0 enable user clip planes: with bit 0 and a 5-dword vertex the triangle is
  drawn when the fifth dword (o4) is +1.0 and removed when it is -1.0, with bits 1:0 and a 6-dword
  vertex only when o4 and o5 are both positive, a plane crossing the triangle removes it whole
  instead of cutting it, and fdpc's value serves as the distance like fdp's; with a 4-dword vertex
  any of bits 7:0 set removes the triangle or faults the job.
  *mte; HW, infer; data: `mte-user-clip-planes`, `vdm-stream-words`, `vdm-stream-words-followup`.*
- `E199` The microkernel writes register 0x065c only with 1 and 0, four times, in the partial-render
  routine (0xc23-0xdbe) and its resume (0xdbf-0xe09), and register 0x0658 three times, 1 in the
  partial-render routine and 0 in the resume and in the 3D kick routine (0x112b-0x12db); it reads
  neither, and the writes of 1 are skipped under bits of one secondary attribute.
  *dpm; RE; data: `firmware-edm-dataflow`, `firmware-images`.*
- `E200` The EDM loads a parameter-buffer descriptor into the TA-side or the 3D-side DPM registers
  (0x0618-0x0668 and 0x0600-0x0664), stores the free-list status registers back into it, reloads the
  thresholds when the descriptor's flags have bit 1 set, and rebuilds the page table from the
  descriptor's block list when they have bit 0 set, one 32-bit entry per page holding the previous
  page in the high half and the next in the low half.
  *dpm; RE, HW; data: `firmware-edm-dataflow`, `firmware-images`, `dpm-parameter-buffer`.*
- `E201` The descriptor the host gives the EDM holds a flags dword, the initial and current
  free-list head/tail and previous-page words, a page-table base address, the local and global page
  counts, four thresholds (TA, ZLS, global, PDS), and a pointer to a list of blocks; with the host's
  values (0x422 pages) the DPM registers read back a free list from page 1 to the last page, a
  previous-page word one before it, thresholds of pages + 0x10, pages - 0x22, the same with bit 16
  set, and pages - 0x122, and the same fields at every smaller size.
  *dpm; RE, HW; data: `firmware-edm-dataflow`, `firmware-images`, `dpm-parameter-buffer`.*
- `E202` A scene larger than its parameter buffer is reported by the kernel as an overflow with the
  context kept, no fault or hang; at 4096x4096 it draws only part of the image from 0x100 pages
  down, at 1024x768 from 0x30 to 0x24 pages, while at 0x23 pages and 1024x768 the job still reports
  an overflow but the image is exact; the image is the same in both repeats of every size, and the
  amount missing does not follow the buffer size.
  *dpm; HW, infer; data: `dpm-parameter-buffer`.*
- `E204` Register 0x0658 reads 1 in jobs that overflow their parameter buffer and never in jobs that
  do not (40 timelines): one stretch per partial render, 1 to 10 of them as the buffer shrinks at
  4096x4096 and one at 1024x768, each stretch 26.8 to 28.9 ms long at 4096x4096 and 1.0 to 1.2 ms at
  1024x768; register 0x065c was never seen at 1.
  *dpm; HW, RE; data: `dpm-parameter-buffer`, `firmware-edm-dataflow`.*
- `E205` CR_DPM_PARTIAL_RENDER (0x0658) is 1 while a partial render runs and 0 otherwise; in our
  data the firmware sets and clears it, so it reads as a status the EDM keeps, and that it is also
  an enable is not shown.
  *dpm; HW, RE, infer; data: `dpm-parameter-buffer`, `firmware-edm-dataflow`.*
- `E206` The TA command word the EDM copies into CR_DPM_REG_074C (ta:167) faults the job when bit 8
  is set in every value tried (0x100, 0x700, 0xffffffff) and never when bit 8 is clear (31 other
  single bits, 0 and five address-like values), so the data fit an enable at bit 8 and do not fit an
  address field.
  *dpm; HW, infer; data: `render-kernel-words`, `render-kernel-words-followup`, `ta-zero-words`.*
- `E210` With the multisample positions in place, 0x042c bits 1:0 at 0, 1 and 2 give three different
  images of the 64x64 triangle (1086, 868 and 896 triangle pixels; 916, 1260 and 1248 with the TE
  anti-aliasing bits) and 3 hangs the job in both settings; which sample count each value selects is
  not shown, so reading 1 as two samples and 2 as four is an inference of ours.
  *isp; HW, infer; data: `isp-msaa`.*
- `E211` With 0x042c bits 1:0 at 2, bit 31 set draws the 64x64 triangle (896 pixels, 1248 with the
  TE bits and the macrotile words) and bit 31 clear draws none of it (4096 background pixels), in
  both settings; with the whole word at 0 the unpoked 1062-pixel image comes back; that bit 31 acts
  after tiling is not shown, because the render-memory dumps are not in the data.
  *isp; HW; data: `isp-msaa`.*
- `E213` With 0x04dc at 2 and at 3, every case of the first punch-through scene (a one-phase shader
  waiting for a fetchless iteration; four endings, nop.end among them) hangs the job, in two runs;
  at 0 the same four cases draw nothing, so whether bit 1 moves the depth test cannot be seen in
  this scene.
  *isp; HW; data: `isp-punch-through`, `isp-punch-through-followup`.*
- `E214` With ISP word 0 bit 28 set, 55 values of 0x0520 give 6 distinct images of the 64x64
  triangle, each reproduced pixel for pixel by one rule: a pixel is covered when the pixel centre,
  the pixel's top-left corner or any of four samples placed by the value's bytes (x in bits 3:0, y
  in bits 7:4 of each byte, sixteenths of a pixel) is inside the triangle; a second rule fits the
  same images, and no value removes a pixel.
  *isp; HW; data: `isp-sample-positions`.*
- `E215` With ISP word 0 bit 28 set, the single-sampled triangle's coverage depends on 0x04c8 as
  well as 0x0520 (1122, 1134 and 1098 pixels for 0x04c8 at 0x88, 0xffffffff and 0 with 0x0520 at
  0x0c0c0c0c, against 1098 with 0x0520 at 0), which the union of eight samples (0x04c8's four bytes
  and 0x0520's four) predicts in all four cases; a 4x render gives one image for three values of
  0x0520, bit 28 under 4x hangs the job, and mode 3 hangs in every setting tried.
  *isp; HW; data: `isp-sample-positions`.*
- `E216` The triangle's stencil test (ISP word 2 compare, reference in ISP word 0 bits 7:0) tests
  against a stencil value held in register 0x04bc bits 7:0: with the job's value equal-0 draws the
  triangle and equal-1 does not, with 0x301 it is the other way round, and bit 8 clear (0x201) stops
  the value being used; bit 9 clear (0x101, 0x1) leaves the target with old pixels; register 0x04e8
  at 0, 1 and 0x101 changes none of 9 runs' outcomes.
  *isp; HW; data: `isp-stencil`.*
- `E217` In the five-copy punch-through pass a pixel is kept only when the pt phase ends in atst8
  with fb, a passing alpha test and 0xe001 in src1 (~0 keeps it too, with the depth always winning):
  nfb, nop.end and ten other src1 words keep none, and a failing test shows the copy behind; the
  depth result (1062 pixels of the nearest copy, 36 of the next) is the same without pcoeff, without
  the source-34 iteration and without both, and moves between runs only when pcoeff runs with that
  iteration missing, or with a source register unset.
  *isp; HW; data: `isp-punch-through`, `isp-punch-through-followup`.*
- `E218` In the full punch-through shader the feedback's control word (src1 of atst8 with fb) keeps
  a pixel only with both bit 0 and bit 14 set: of the 32 single-bit flips of 0xe001 only those two
  lose the image, and flipping bit 2 or bit 3 makes the last copy win (1074 pixels of depth 1/4, 24
  of 1/8); 15 words with bits 15:13 and the low bits varied agree, and pcoeff's third source (12
  values) changes nothing, in two runs.
  *isp; HW; data: `isp-punch-through`, `isp-punch-through-followup`.*
- `E219` Reading 0x042c bit 31 as the enable of the multisampled ISP path is consistent with the
  data (bits 1:0 at 2: bit 31 clear draws nothing, in two multisample setups) but rests on one mode
  and two setups; that clear bit 31 still tiles the triangle is not shown.
  *isp; HW, infer; data: `isp-msaa`.*
- `E220` Naming 0x042c bits 1:0 the multisample mode (1 two samples, 2 four, 3 eight) agrees with
  three different images for 0, 1 and 2 and a hang at 3, but the sample counts are not measured.
  *isp; HW, infer; data: `isp-msaa`.*
- `E222` In the punch-through scene that draws (pcoeff and the source-34 iteration, 1062 pixels of
  the nearest copy and 36 of the next), 0x04dc at 0, 1 and 4 give the same image and 2 and 7 hang
  every case, atst8 with fb or nfb, depthf and nop.end alike, in two runs; whether bit 1 is the
  up-front depth test of other GPUs is not shown.
  *isp; HW, infer; data: `isp-punch-through`, `isp-punch-through-followup`.*
- `E224` 0x0520 is read as four sample positions by ISP word 0 bit 28 and is not the base of a table
  the ISP reads or writes: pointed at the scratch buffer it changes no scratch dword, no ISP word 0
  or word 1 bit tried changes a pixel with it except bit 28 (more pixels) and bit 18 (a fault that
  0x0520 at 0 gives too), and the 55 values of the bit-28 sweep are fitted by sample positions.
  *isp; HW, infer; data: `isp-sample-positions`.*
- `E225` Writing 0, 1, 2, 4, 8, 0x10, 0x20 or 0x3f into bits 5:0 of 0x0800 (which holds 0x30 = 48
  outside a render) does not change the time the ISP is clocked for a 1024x1024 render whose pixel
  shader runs 150 dependent fmads on 276192 pixels (28646 to 28776 us over 50 jobs), so a pixel-task
  maximum of 48 is not what the field holds; that it limits other work is a reading, not tested.
  *isp; HW, infer; data: `pds-task-limits`.*
- `E226` In the working punch-through scene atst8 ending in fb, optdwd, twosided with fb and
  twosided with optdwd all keep the same pixels (1062 of depth 0, 36 of 1/16, 2998 background, one
  identical image), in two runs; nfb keeps none (E217); what optdwd adds over fb, and what twosided
  does on front faces, is not shown.
  *isp; HW; data: `isp-punch-through`, `isp-punch-through-followup`.*
- `E227` In E226's scene atst8 in fb, optdwd, twosided fb and twosided optdwd keep the same pixels
  with ISP word 0 bit 20 set, on the scene mirrored in y to back faces, and with both (12 cases,
  1062 pixels of depth 0 and 36 of 1/16 each, the mirrored images being exact y-mirrors of the front
  one), in two runs; with later copies winning when the depth test is always (E218), a
  depth-write-off bit that the feedback obeyed would be expected to change the image, and it did
  not.
  *isp; HW, infer; data: `isp-punch-through`, `isp-punch-through-followup`.*
- `E228` ISP word 0 bit 11 turns on a two-sided stencil: with it set a back-facing triangle is drawn
  or not by the stencil word of presence bit 5 and needs the back ISP word 0 of presence bit 3,
  while a front-facing one keeps the front words; presence bit 4 is optional and the back word 0's
  own ISP-word-2-present bit is not needed; without bit 11 no back-face case draws; ISP word 0 bit
  18 hangs the render.
  *isp; HW; data: `isp-stencil`.*
- `E229` In the 64x64 punch-through scene turned to back faces with ISP word 0 bit 11 set and a
  second pair of state words added, the stencil words (front never and back always, or front always
  and back never) change nothing in atst8's fb and optdwd modes or in their twosided forms: all 8
  cases drew the copy at z 0 on 1062 pixels and the copy at z 1/16 on 36, in both runs.
  *isp; HW; data: `isp-punch-through`, `isp-punch-through-followup`.*
- `E230` With ISP word 2 at stencil compare never, no single bit of atst8's control word among bits
  1, 4-12 and 16-31 makes the punch-through pass obey the stencil: all 29 cases drew the copy at z 0
  on 1062 pixels and the copy at z 1/16 on 36, in both runs.
  *isp; HW; data: `isp-punch-through`, `isp-punch-through-followup`.*
- `E239` On a target of one tile (32x16) bit 9 clear still hangs the job, and an end-of-tile program
  that emits the tile twice stores the first emit's tile and leaves the next job's image wrong at
  1977, 2107, 2164 or 2165 of 4096 places according to the second sideband (the probe's colour, or
  RGB565 words when the second sideband has pack mode 3), in both runs; that the second emit is
  carried out during the next job, and that bit 9 is therefore not tile-relative addressing, are
  readings.
  *pbe; HW, infer; data: `pbe-sideband`, `pbe-sideband-followup`.*
- `E240` A public Rogue PBE state description names a one-bit field tilerelative, which suggests bit
  9 of our sideband word is tile-relative addressing; on a one-tile target our bit 9 clear still
  hangs the job, so we read bit 9 as marking an emit that counts against a PBE tile, which is a
  reading of E239's measurements and not a name.
  *pbe; infer, HW; data: `pbe-sideband`, `pbe-sideband-followup`.*
- `E242` T3 bits 26:23 do not change what a single fetch writes (pa0 in all 21 cases, and pa0 to pa3
  for f32 channels), and with two fetches in one primary program the second fetch's texel lands in
  the primary attribute numbered by the first fetch's field for the values 0, 1, 2, 3, 4 and 6,
  after the first fetch's own dwords (over them at 0).
  *texture; HW, infer; data: `texture-fetch`.*
- `E244` At the end of a punch-through pixel phase, depthf's src0 replaces the pixel's depth in the
  depth test, in ISP0 pass type 4 as in pass type 5: with 1.0 nothing is drawn, with 0, 0.5 or the
  copy's own depth the copy at z 0 keeps 1062 pixels and the copy at z 1/16 keeps 36, and with 0.5 -
  z the last copies win (1074 and 24 pixels); the same in both runs.
  *usse; HW, infer; data: `isp-punch-through`, `isp-punch-through-followup`.*
- `E245` The microkernel writes the TA command's context store and resume registers (0x0a04, 0x0aa0,
  0x02b0, 0x02b4, 0x02d0, 0x02d4, 0x0324, 0x0364, 0x0368, 0x0370, 0x0374) at one site each, in one
  run of straight-line code that fetches the values from memory and stores them without computing on
  them, reads none of them at a statically named site, and its 6637 instructions use none of the
  instructions moest, setfc, bexception, setm, smoa and smbo and no mon or synce modifier.
  *usse; RE; data: `firmware-images`.*

### 2026-11-02

- `E013` A forward dataflow over the whole EDM microkernel reaches all 6637 instructions in 70
  routines from 13 entry points and 21 further roots, and records every structure word (342) it
  reaches through a typed pointer, register (191) and secondary attribute (20) it touches; 248
  branches, 392 memory accesses, 14 register addresses and 113 sources it cannot resolve are
  counted, not guessed.
  *edm; RE, CAP; data: `firmware-edm-dataflow-3d`, `firmware-images`, `firmware-init-payload`.*
- `E149` The firmware's HWPerf routine (from instruction 0x1979) appends a 100-byte record to the
  HWPerf circular buffer, in which it stores the nine registers 0x0044-0x0064 (CR_HWPERF_COUNTER0 to
  8) and then the eight registers 0x0e84, 0x0e88, 0x0e8c, 0x0e90, 0x0eb8, 0x0eb4, 0x0ebc and 0x0ec0,
  once each per record, after a header that holds CR_TIMER; the reads do not depend on the record
  type, and each of its 33 callers first tests a bit of the HWPerf status word; read from a shader,
  in one run, 0x0044-0x0064 read 0 twice, 0x0e84, 0x0e88 and 0x0e8c were unchanged over the 24
  fmads, and 0x0e90, 0x0eb4, 0x0eb8, 0x0ebc and 0x0ec0 rose.
  *platform; RE, HW; data: `firmware-images`, `platform-hwperf`.*
- `E168` With render-context flag bit 5 set, the render-context cleanup unloads the context's own PB
  from the TA and 3D loaded-PB slots; with it clear the slots keep the PB until the PB cleanup; and
  with the flag set a context whose PB is not loaded leaves the slots alone.
  *edm; HW; data: `edm-context-flags`.*
- `E176` The TA's object, at the start of the parameter buffer, is three header words (read as the
  pixel program's words, which is not tested), one 1/w per vertex followed by that vertex's iterated
  outputs, the ISP words, the primitive list and line widths, a format word whose bytes count the
  stored and iterated dwords per vertex, four per-set masks, and the packed vertices; 13 probes give
  the format words and masks listed.
  *ta; HW, infer; data: `ta-objects`.*
- `E177` The TA writes for the triangle one region header per 32x16-pixel region of the target's
  macrotiles and, for the regions it bins the triangle into, a 128-byte-step control-stream block of
  a primitive word and an object word (a third dword with more than 6 vertices of the object)
  pointing at the object; 64x64 gives 7 streams, 128x128 19 against 17 regions with a pixel centre
  covered.
  *ta; HW, infer; data: `ta-regions`, `ta-objects`.*
- `E178` The TA's object carries ISP words 0 and 1 exactly as the job gives them (11 values tried),
  then the primitive list and the line width in both bytes of one dword; the region headers list
  every 32x16 region of the macrotiles, the ones outside the target included, with flags for
  outside, first of a macrotile, empty inside the target, last of a macrotile and last of the scene.
  *ta; HW; data: `ta-objects`, `ta-regions`.*
- `E180` The primitive word's bits 23:16 say which of a 32x16 region's two 16x16 tiles the triangle
  meets: 0x80 the left tile only, 0x98 the right only, 0x90 both; over 26 viewport offsets and 472
  streamed regions all three forms occur (74, 106 and 292 regions) and a bounding-box and edge test
  against the tiles reproduces every region's form.
  *ta; HW, infer; data: `ta-regions`.*
- `E181` The TA object holds a primitive list of 16-bit entries of three 5-bit vertex numbers
  counted from 16, two entries to a dword with the last repeated for an odd count, and the primitive
  word's bits 30:29 are 2 for triangles and lines and 3 for points; the object word's bits 31:26 fit
  twice the primitives less one in these dumps.
  *ta; HW, infer; data: `ta-objects`, `ta-regions`.*
- `E188` Setting the index list's word 4 to 0, 0x10000000 or 0x70000000 leaves the TA's output of
  five copies of the triangle byte for byte the same; word 5 at 0 does too, at 1 the TA writes no
  object, at 5 it writes five primitives over 10 vertices whose list entries fit the indices taken
  modulo 5 (a reading), and at 8 the job hangs.
  *vdm; HW, infer; data: `vdm-index-list`, `ta-regions`.*
- `E197` With 0x0240 (ta:152) at 0.3, 0.5 and 0.7 and 0x0244 (ta:153) at 0.25, the TA keeps a
  vertex's stored 1/w when it is above 0x0240 and stores 0.25 in its place otherwise: of the 1/w
  values 0.8, 0.364 and 0.615, none is replaced at 0.3, the 0.364 at 0.5, and the 0.364 and 0.615 at
  0.7.
  *mte; HW, infer; data: `mte-rhw`.*
- `E203` With bit 8 of ta:167 (the word loaded into CR_DPM_REG_074C) set, the job faults at the same
  BIF address, 0x20006011, whatever the other bits (0x1100, 0x10100, 0x100100, 0x1000100,
  0x10000100, 0x80000100 and 0x101: seven of the eight values), and at 0x20006013 once, with bit 8
  alone, which was also the first case of the run, so value and run order are not separated.
  *dpm; HW, infer; data: `dpm-reg-074c`.*
- `E209` In a two-layer background object the coordinate dwords are read vertex by vertex, layer A's
  (u, v) then layer B's, when the tag's size field is raised from 2 to 4: coordinate set 1 then
  copies the 8x4 source and set 2 mirrors it, for the format word at 0, 0x202 and 0x404, and set 2
  gives one image for eight format words (0 to 0xffff); with the dwords laid out layer by layer the
  two sets give other images; with the size field left at 2 both sets give one texel; the format
  word 0xffffffff breaks the copy.
  *isp; HW; data: `isp-background-layers`.*
- `E231` No render-level ISP word we can set makes a punch-through pass obey the ISP stencil: with
  the stencil compare at never and at always alike, every bit of render command words 12, 21 and 22
  and the kernel pokes of 0x04dc bits 0 and 2 and 0x04e8 bits 0 and 8 leave the punch-through image
  at 1062 and 36 pixels in all 202 probes, while command word 12 with any of bits 1 to 5 set, and
  with all bits set, removes a plain opaque triangle.
  *isp; HW; data: `isp-punch-through-stencil`.*
- `E232` Any of CR_ISP_CTL bits 5:0 set (the values 1 to 8, 16, 32 and 63) removes a triangle of
  ISP0 pass type 0 or 1 (opaque and translucent) and leaves pass types 2, 4, 5 and 6 drawn exactly,
  in all 72 cases of one run; the value 0 draws all six.
  *isp; HW, infer; data: `isp-valid-id`.*
- `E233` CR_ISP_CTL bits 5:0 act as a threshold that the opaque triangle's ISP word 1 bits 31:26 are
  compared with: over the 49 pairs of the thresholds 0, 1, 2, 3, 5, 32, 63 against the values 0, 1,
  2, 3, 5, 32, 63 (46 run as pairs, the other 3 by the free-bit probes of ISP1 bits 26, 27 and 31)
  the triangle is drawn exactly when the ISP1 value is at least the threshold; and with the
  threshold at 1, setting any one of ISP1 bits 26 to 31 draws it again, while none of the other free
  bits of the presence word, ISP word 0 or ISP word 1 tried does (the presence word's bit 27 hangs
  the job).
  *isp; HW, infer; data: `isp-valid-id`.*
- `E234` A punch-through pass writes no stencil: with a second, opaque object that draws only where
  the stencil equals 0x55, it draws nowhere after a punch-through object whose depth-pass stencil op
  is replace, under atst8 fb, optdwd and each with twosided, though it draws over the whole of an
  opaque object with that op; the punch-through object draws alike under all eight stencil compares,
  and atst8 right after pcoeff draws nothing while one nop between them lets it draw.
  *isp; HW, infer; data: `isp-punch-through-stencil`.*
- `E235` CR_ISP_CTL's threshold applies to the plain triangle of pass type 0 only among the pass
  types run here: with the object's ISP1 value at 0 or 63 and the threshold at 1 or 63, pass types
  2, 4, 5 and 6 draw in all 16 cases, while pass type 0 draws only with the value at 63.
  *isp; HW; data: `isp-valid-id`.*
- `E236` Under coordinate-set size words 1 to 5 a coordinate set iterated with four components
  reads, from the vertex's dwords x, y, 0.25 and 0.5, as x 0 0 1.0 (size 1), x y 0 1.0 (2), x y 0.25
  1.0 (3), x y 0 0.25 (4) and x y 0.25 0.5 (5), with 6 and 7 reading as 2; and read as two sets, the
  sizes 0x12, 0x19, 0x0b and 0x0a split the four dwords into x y | 0.25 0.5, x | y 0.25 0.5, x y
  0.25 | 0.5 and x y | 0.25, with 0x00 and 0x02 reading as 0x12; one run.
  *tsp; HW, infer; data: `tsp-coordinate-sets`.*
- `E237` On values a half float does not hold, bit i of the coordinate-format word makes coordinate
  set i arrive cut to 10 mantissa bits towards zero: 0.1, 1/3 and 0.7 arrive as 0x3dccc000,
  0x3eaaa000 and 0x3f332000 with bit i set, where with the word at 0 they arrive as 0x3dcccccc (or d
  or b), 0x3eaaaaa9 (or a) and 0x3f333331 (or 2); bit 0 acts on one set of four, bit 1 does nothing
  on it, and with two sets bit 0 cuts set 1 and bit 1 cuts set 2; one run.
  *tsp; HW, infer; data: `tsp-coordinate-sets`.*

## By unit

### bif

Records: E151.

### dpm

Records: E199, E200, E201, E202, E204, E205, E206, E203.

### edm

Records: E009, E014, E017, E084, E146, E152, E153, E154, E155, E156, E157, E158, E159, E160, E161,
E162, E163, E164, E165, E166, E167, E013, E168.

### firmware

Records: E001, E002, E003, E004, E005, E010, E011, E012.

### isp

Records: E064, E065, E066, E067, E068, E069, E070, E071, E072, E073, E074, E210, E211, E213, E214,
E215, E216, E217, E218, E219, E220, E222, E224, E225, E226, E227, E228, E229, E230, E209, E231,
E232, E233, E234, E235.

### mte

Records: E061, E062, E063, E192, E193, E194, E195, E196, E198, E197.

### pbe

Records: E029, E030, E031, E032, E239, E240.

### pds

Records: E043, E044, E045, E046, E047, E048, E125, E126, E127, E128, E129, E130, E131, E132, E133,
E134, E135, E136, E137, E138, E139, E140, E141, E142, E143, E144, E145.

### platform

Records: E006, E007, E008, E025, E026, E122, E150, E149.

### render

Records: E023, E049, E050, E051, E052, E053, E148, E169.

### ta

Records: E054, E055, E056, E172, E174, E175, E182, E183, E176, E177, E178, E180, E181.

### texture

Records: E033, E034, E035, E036, E037, E038, E039, E040, E041, E042, E114, E116, E242.

### transfer

Records: E015, E016, E018, E019, E020, E021, E022, E024, E027, E028.

### tsp

Records: E236, E237.

### usse

Records: E075, E076, E077, E078, E079, E080, E081, E082, E083, E085, E086, E087, E088, E089, E090,
E091, E092, E093, E094, E095, E096, E097, E098, E099, E100, E101, E102, E103, E104, E105, E106,
E107, E108, E109, E110, E111, E112, E113, E115, E117, E118, E119, E120, E121, E123, E124, E147,
E244, E245.

### vdm

Records: E059, E060, E184, E185, E186, E187, E189, E190, E191, E188.

### zls

Records: E057, E058.
