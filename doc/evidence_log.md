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
  bits 15:8 of the fill's pixel-event data dword 8, which this record first took for EMIT2 and which
  is the pixel-event program's end-of-render mask (E265), write the same pixels at every value but
  0x81.
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
  routines from 13 entry points and 21 further roots, and records every structure word (346) it
  reaches through a typed pointer, register (191) and secondary attribute (20) it touches; 249
  branches, 379 memory accesses, 14 register addresses and 109 sources it cannot resolve are
  counted, not guessed.
  *edm; RE, CAP; data: `firmware-edm-dataflow-11`, `firmware-edm-dataflow-3d`, `firmware-images`,
  `firmware-init-payload`.*
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
- `E246` Of the registers the glossary places at an offset, and the 13 the firmware or the init
  script touches with no row, 118 were written with all ones and zero through /dev/mem with the
  firmware live and idle and put back, in ten batches after each of which a fill and the triangle
  came out exact with no MMU fault, in two runs that agree in every implemented bit; the 109 others
  stay read-only for a reason the table gives; the method reproduces the bits earlier records
  measured for 0x0418, 0x04dc, 0x0520 and 0x0368; CR_HWPERF_CTRL takes bits 12:0, the nine HWPerf
  counters take no write, and 0x0b30 takes bits 8 and 0.
  *platform; HW; data: `platform-register-widths`.*
- `E247` Of the tiling-engine, VDM and TA registers, CR_TE_MTILE1 takes bits 31, 29:22, 19:12 and
  7:0, CR_TE_MTILE2 bits 30:22, 20:12 and 8:0, CR_TE_SCREEN bits 20:12 and 7:0,
  CR_TE_MACROTILE_STRIDE bits 17:0, CR_TE_PSG bits 26:18 and 6:0, the region and tail-pointer cache
  bases bits 31:6, CR_VDM_CTRL_STREAM_BASE bits 31:2 and CR_PPP_SCREEN bits 28:16 and 12:0;
  CR_TE_CONTEXT_STATE and 0x02b4 take no write; the other TA store registers take the bits E054
  found.
  *ta; HW, infer; data: `platform-register-widths`.*
- `E248` CR_MTE_MULTISAMPLECTL, CR_MTE_RHW_MIN and CR_MTE_RHW_CLAMP take all 32 bits,
  CR_MTE_OTPM_BASE bits 31:4 and CR_MTE_CTRL bits 14:0.
  *mte; HW; data: `platform-register-widths`.*
- `E249` Of the ISP registers, CR_ISP_RENDER takes bits 5:3 and 1:0, CR_ISP_CTL bits 24, 19:16, 8
  and 5:0, CR_ISP_MSAA bits 31 and 1:0, the render origin and end registers 0x040c and 0x0410 bits
  24:16 and 9:0, CR_ISP_BGOBJVALS bits 9:0, 0x04c4 bits 30:0 and the polygon-offset units bits 23:0;
  the visibility control and counters take no write, and 0x0444 and 0x0448 read the same values
  whatever is written.
  *isp; HW, infer; data: `platform-register-widths`.*
- `E250` CR_ISP_ZLSCTL takes bits 26:0, the depth load and store bases bits 30:4 and the stencil
  load and store bases bits 31:4.
  *zls; HW; data: `platform-register-widths`.*
- `E251` CR_REG_0400 takes bit 25 and bits 11:0.
  *pbe; HW; data: `platform-register-widths`.*
- `E252` CR_REG_0148 takes bit 0 only.
  *render; HW; data: `platform-register-widths`.*
- `E253` Of the DPM registers, the page-table, state and control bases take bits 31:4, the two free
  lists and the two page-count words all 32 bits, the TA, ZLS and PDS thresholds bits 15:0,
  CR_DPM_TA_GLOBAL_LIST bits 16:0, CR_DPM_STATE_CONTEXT_ID and CR_DPM_CONTEXT_PB_BASE bits 2:0,
  CR_DPM_3D_RT_INDEX and CR_DPM_REG_074C bits 8:0 and CR_DPM_SPM_SWITCH bit 0.
  *dpm; HW, infer; data: `platform-register-widths`.*
- `E254` Each colour-space and luma-key coefficient word takes two 10-bit fields, 25:16 and 9:0,
  except words 4 of each set (9:0 only), the luma-key B and offset word (23:16 and 9:0) and the
  luma-key alpha word (31:0); CR_TPU_YUV_CSC_INPUT takes bits 3:0.
  *texture; HW, infer; data: `platform-register-widths`.*
- `E255` The USSE filter coefficient sets 0 and 1 take all 32 bits of their two tap words and bits
  19:0 of their shift and bias words, set 2 only bits 31:24 and 7:0 of its first tap word, 15:8 of
  its second and 19:0 of its bias word; CR_USE_COEFFS_MODE takes bits 1:0.
  *usse; HW, infer; data: `platform-register-widths`.*
- `E256` While the TA runs, CR_DPM_TA_ALLOC_FREE_LIST_STATUS1 holds the parameter buffer's size in
  pages in its high half and the pages the TA has taken plus one in its low half, and STATUS2 the
  size less one; CR_DPM_PAGE_STATUS holds the pages taken in both halves; when the 3D starts the 3D
  pair copies the TA pair, and while it frees pages the high halves and STATUS2 change at every
  step, CR_DPM_PAGE_STATUS and CR_DPM_PAGE count down and 0x0730 reads 1; after the job the low half
  of STATUS1 keeps the TA's count plus one; 0x0740 reads 0 in every job, partial renders and two
  contexts included.
  *dpm; HW, infer; data: `platform-register-timelines`.*
- `E257` At eight target sizes from 64x64 to 4096x4096, 1366x768 among them, the triangle draws
  exact and the tiling registers 0x0208, 0x020c, 0x0210, 0x0214 and 0x0248 read after the TA exactly
  the values the library's macrotile rule gives, which the TA command loads: the hardware accepts
  the rule's encoding; 0x0208 changes with the size from 512x512 on, and its bit 31 is set from
  1024x768 on, where the rule chooses four macrotiles across.
  *ta; HW, infer; data: `platform-register-timelines`.*
- `E258` Around the fill, the copy, the triangle, two renders in one context, two render contexts, a
  partial render and the triangle at seven sizes, 137 of the 206 registers sampled never change; a
  fill moves 23, a copy 13, a triangle 31 to 51, a partial render 57, and `contexts -n 2` only 2 (it
  renders nothing); the USSE slot registers 0x0aa4, 0x0aa8, 0x0b80 and 0x0b84 hold 0xaaaaaaaa when
  idle and other 2-bit-per-slot patterns while tasks run.
  *platform; HW, infer; data: `platform-register-timelines`.*
- `E259` Of the 281 bits the 27 PDS forms left unmapped, the 136 of the 17 data-operation forms
  (movs, movsa, mov16, mov64, mov128, the ALU group, mul, both abs, both not, both tstz, both tstn,
  shl, shr) and the 28 of load, store and the fences were flipped one at a time: each left the
  readback as the unflipped word did, except abs ds1[n]'s bit 15, which changed the value read, and
  mov128's bit 15, which changed the four dwords it writes.
  *pds; HW; data: `pds-encoding-bits`, `pds-encoding-bits-memory`.*
- `E260` bra and call read bits 19-23 as target bits: each of the ten flips sent the fetch 4 << k
  bytes past the program, where the job faulted with the BIF fault address 0x2e000000 + (4 << k)
  (low bits aside); rtn's and halt's bits 23:0 and nop's bits 26:0 change nothing the readback
  shows, and with each nop bit flipped a later pc.0 read gives what the plain nop gives, within the
  fetch pc's run-to-run variation (E261).
  *pds; HW; data: `pds-encoding-bits-flow`.*
- `E261` pc.0 reads the reading instruction's index plus 3, or plus 2 or 1, never more nor less, in
  399 reads over 27 programs: back to back it reads less at instructions 26-27 in ten of twelve
  runs, whatever the nops before, and at 19-20 in two; abs's ds1[n] takes n from bits 15:10;
  mov128's source row reaches 31, rows 24-31 the temporaries, and with bit 15 set mov128 writes
  ds0[8], ds0[9] to both halves of its destination whatever its source row, and with swap at row 2;
  nop's bit 2 does not change the fetch pc.
  *pds; HW, infer; data: `pds-fetch-pc`, `pds-encoding-bits-followup`, `pds-encoding-bits-mov128`,
  `vectors-pds-knowledge`.*
- `E262` In the primary pixel program of a 64x64 and a 128x128 triangle, per pixel: if0 and if1
  never test true; ir0 is 0 only on tile (0, 0); the ALU's ir1, mov32's ir1.0, mr01 and mr23 read 0;
  tim and pc.0 are never 0; tstz of the source the decoder names ir1 tests true exactly where ir0 is
  0; bit by bit on the 64x64 triangle, ir0 is the 16x16 tile position tile_y << 10 | tile_x (bits 0,
  1, 10, 11 follow the tile, bits 2-9 and 12-15 are clear) and the ALU's ir1 has bits 0-11 clear.
  *pds; HW, infer; data: `pds-task-inputs`.*
- `E263` In the pixel-event program, on a one-tile render, the ALU, shl, abs, and mov32's ir1.0 and
  ir1.1 and mov16's ir1.0.l and .h all read 6, the event bits; per tile of a 128x128 render, on the
  slots whose slot word names the tile of their ir0, the ALU's ir1 and mov32's ir1.0 and ir1.1 read
  2 on every tile but (6, 7) and (7, 7), where 6; about a third of the slots carry a slot word that
  is not their own; if0 and if1 never test true, the last tiles included; mr01, mr23, ir2.l and the
  .h of ir0, ir1 and tim read 0 on every tile, ir2.h on the one tile; tstz of ir1 tests true on the
  one-tile render (ir0 0) and false on every other tile read.
  *pds; HW; data: `pds-task-inputs`.*
- `E264` In the primary pixel program of a 64x64 triangle, a movs to mr, slc, douts or ir0 before
  the iteration leaves every pixel as the control's and the render completes; mr01 reads 0 after the
  movs to mr, and ir0 still reads the tile position after the movs to ir0; a movs to doutc faults
  the job (BIF status 0xd0400, address 0x0401f030).
  *pds; HW, infer; data: `pds-task-inputs`.*
- `E265` The word E046's EMIT2 table varied is the pixel-event program's data dword 8, the
  end-of-render mask (0x100) of asm/transfer/pds_pixevent.s, and not an emit word: XOR 0x100 (0x81
  in that table's terms) sets it to 0 and the fill, the copy and the triangle then write no pixel,
  as at 0 and 0x2; at 0x4 the last 32x16 tile is left unwritten (512 pixels) in all three jobs;
  0x8000, 0x8100, 0x200, 0x4000 and 0x8 leave every image as built; both repeats of each case agree.
  *pbe; HW, infer; data: `pbe-emit-words`, `pbe-emit-words-followup`.*
- `E266` EMIT2 bits 15:8 count what the end-of-tile emit stores of a 32x16 tile in units of four
  pixels: at 0 the job writes no pixel, at each odd value it hangs, at an even value v up to 0x80
  (the value the library writes) it writes 4v pixels of every tile and leaves the rest unwritten,
  and above 0x80 it writes the whole tile with 40 to 2524 of 4096 pixels changed, other words and
  0x00000000 among them.
  *pbe; HW, infer; data: `pbe-emit-words`, `pbe-emit-words-followup`.*
- `E267` The end-of-tile emit stores only the pixels inside the rectangle EMIT0 (minimum x in bits
  12:0, y in 28:16) and EMIT1 (maximum x and y, inclusive) give; EMIT3 is a byte address whose bits
  1:0 are ignored; EMIT2 bits 27:16 give the row pitch as (value + 1) x 8 bytes; bits 15:13 and
  31:29 of EMIT0 and EMIT1 are ignored but EMIT1 bit 31, which hangs the job; EMIT2 bits 6:0 and
  31:28 change the image and bit 7 does not: bit 28 stores the image mirrored in x, bit 29 rotated
  by 180 degrees (or anti-transposed; this image does not tell them apart), bit 30 each 32x16 tile's
  2x2 box average into the tile's top-left 16x8 pixels, and bit 31 a triangle of another shape in
  the same two colours.
  *pbe; HW, infer; data: `pbe-emit-words`, `pbe-emit-words-followup`.*
- `E268` Bit 25 of the word that loads CR_REG_0400 inverts the stored alpha channel wherever the
  pack mode puts it: bits 31:24 in ARGB8888 (mode 0) and ABGR8888 (mode 1), bits 7:0 in BGRA8888
  (mode 2), and nothing in RGB565 (mode 3), which stores no alpha; bits 11:0 of the word (each
  flipped from 0x80), the word at 0 and the other bits change no pixel in any of the four modes.
  *pbe; HW; data: `pbe-reg-0400-modes`, `pbe-reg-0400-modes-followup`.*
- `E269` SIDEBAND bits 8:6 pick the channel a one-byte pack mode stores: in mode 8, 0 stores alpha,
  1 red, 2 green, and 3 to 7 the byte that is blue in both colours run (0x40, so blue is not told
  apart from another source of 0x40); at each of 0 to 7 they change no pixel under CR_ISP_MSAA modes
  1 and 2, on a 128x128 target, or in pack modes 4, 5, 9 and 26; sideband bit 10 dithers (one run):
  in pack modes 3, 4 and 5 it changes 650 to 1484 of the 4096 dwords, 650 to 2196 pixels, each one
  step of one or two channels off the plain value, the new value set by the plain value and the
  pixel's place in a 4x4 cell of x and y, and changes nothing in pack mode 0; bit 11 faults the job
  and bit 12 stores other values at every pixel.
  *pbe; HW, infer; data: `pbe-sideband-fields`, `pbe-sideband-dither`,
  `pbe-sideband-fields-followup`.*
- `E270` Pack modes 22 and 34 read o0 as an IEEE single: at 727 of the triangle's 1062 pixels (665
  or 730 in a few cases), mode 22 stores 0x00000088 for zero, negative and NaN values, 0xc0000088
  for every positive value from 1/128 to 2.0 and 0xfff00088 for values of 1e13 and up; mode 34
  stores 0x60800000 there, with bits 31:20 of the single in bits 11:0 for the values of 1e13 and up
  that are not NaN (0x7f807f80, a NaN, gives 0x7f9), and at 215 other pixels (149 at 2.0 and 1/128)
  bits 30:20 of the single in bits 21:11 for positive values from 1/128 to 2.0; read at the
  triangle's pixels, no stored bit of either mode copies a bit of o0 across the coded colours, while
  mode 26, the control, stores R >> 3, G >> 3 and B >> 2 at every pixel; the rest of each image
  changes with the job before it.
  *pbe; HW, infer; data: `pbe-pack-colours`, `pbe-pack-floats`, `pbe-pack-colours-followup`.*
- `E271` Bit 28 of the copy's T1 is the top bit of TEXFORMAT: set, the copy reads its source as YUYV
  (TEXFORMAT 28) and writes, at all 2048 pixels and over both sources, the colour-space set 0
  conversion of the source read as Y0 U Y1 V pairs at the source's stride; with set 0 at zeros that
  is opaque black; set 0 keeps its words from one job to the next; T1 bits 28 and 24 together
  (TEXFORMAT 29) read UYVY the same way.
  *texture; HW, infer; data: `texture-copy-words`.*
- `E272` With the copy's transfer word 0 (the background object tag) at 0 or with bit 24 or bit 30
  flipped, every pixel of the 64x32 copy is the source's last texel (63, 31), over both sources;
  with word 7 (the word that loads CR_ISP_MSAA) bit 1 flipped, mode 2, only the first 32x16 tile is
  written, pixel (x, y) holding texel (16 + x / 2, 8 + y / 2), and the other 1536 pixels keep the
  sentinel.
  *transfer; HW, infer; data: `texture-copy-words`.*
- `E273` The copy's T2 bits 12 and 14 read memory outside the source like every other address bit:
  flipping bit 12 reads the 4 KiB before the source (mostly zeros, 0x3f800000, 0x1000; the first
  pixel 0x04000004), so the source's address has bit 12 set; with the source 16 rows long bit 13
  reads the destination's sentinel and bit 14 faults, with it 32 rows long bit 14 reads the sentinel
  and completes, so bit 14's empty image is the destination's own sentinel read back; bit 13 as
  built leaves 448 and 256 sentinel pixels in the two rounds (plain source), 224 and 296
  (every-value source), as a read of a destination the copy is overwriting would.
  *texture; HW, infer; data: `texture-copy-words`.*
- `E274` In a copy, T3 bits 3:0 and 7:4 offset the texel read in y and in x by a signed 4-bit count
  (1, 2, 4 and -8 for each single bit), clamped at the source's edge; T3 bit 10 reads texel (0, 0)
  for every pixel; bits 18 and 19 scale the coordinates by 2 and 4; bits 27 and 28 read half-size
  and quarter-size images packed after the source; bit 14 reads (x + 32, y + x); bits 13 and 19
  fault; T0 bits 27 and 30 change every pixel to values of no texel; T0 bits 2:0, 16:14, 28 and 29
  and T3 bits 8, 9, 11, 12 and 20 to 22 change no pixel, over both sources; one run.
  *texture; HW, infer; data: `texture-sampler-bits`.*
- `E275` Bits 7:0 of the luma-key word that loads 0x0868 are the lower bound of a luma band: the
  copy writes alpha_below where low byte <= luma <= threshold and alpha_above elsewhere, at every
  pixel of 272 of 274 copies (all 256 values of the low byte at threshold 128, nine values at
  thresholds 0 and 255); in the other two (low byte 119 and 122) 8 pixels each, whose weighted sum
  is 4/1024 above the low cut, fall the other way; RGB is the source's in every copy.
  *texture; HW, infer; data: `texture-luma-cuts`.*
- `E276` On a twiddled mip chain T0 bits 20:17 are the highest level read (0 and 15 read level 0
  only, 1 to 14 cap the level at that value) and bits 26:21 shift the LOD by (value - 63) / 8 before
  the nearest level is taken: level = max(0, min(round_half_up(LOD + (b - 63) / 8), max)) fits every
  one of 192 reads, in both runs, a biased LOD below 0 reading level 0; bit 18 alone does not
  disable the chain.
  *texture; HW, infer; data: `texture-mip-fields`, `texture-mip-fields-followup`.*
- `E277` With two fetches in a primary program, T3 bits 26:23 of the first at 8 put the second texel
  in pa8 and at 15 in pa15, as the control at 1 puts it in pa1, image for image; with the first
  fetch as f32 channels and the field at 8 the second texel is again in pa8 and pa1 holds the first
  fetch's 0.0.
  *texture; HW, infer; data: `texture-fetch-size`, `texture-fetch-size-followup`.*
- `E278` With ISP word 0 bit 28 set a pixel is covered when any of eight samples is inside the
  triangle, the four bytes of CR_ISP_MULTISAMPLECTL and the four of CR_ISP_SAMPLE_POS, each byte x
  in bits 3:0 and y in bits 7:4 in sixteenths of a pixel from its top-left corner, under the
  top-left rule, which predicts all 56 bit-28 images of two runs; the reading with the pixel centre
  in place of 0x04c8's samples misses 12, 24 or 36 pixels in 10 of the 28 settings (20 of the 56
  images); with the bit clear only byte 0 of CR_ISP_MULTISAMPLECTL samples (one run).
  *isp; HW, infer; data: `isp-coverage-samples`, `isp-coverage-bytes`.*
- `E279` CR_ISP_LINE_SAMPLE_POS bit 0 moves the sample of a line's span test: a column x is covered
  when x + 1/2 (1) or x + 1 (0) lies in the line's span [start, end), and at both values its rows
  are those whose centre r + 1/2 lies within half the line's width of the line's y at x + 1/2, ties
  to the upper row; this fits all 32 cases of both runs, 6 of the 8 cases moved in x and y and all
  nine widths with no pixel missed [infer: one x-major line]; triangles never read the register;
  ISP1.LINE_WIDTH is the width in sixteenths of a pixel (0x10 one pixel, 48 pixels for the 48-column
  line, 0x08 24, 0x20 96; one run).
  *isp; HW, infer; data: `isp-line-sample`.*
- `E280` A user clip plane's state, set by fdpc on cpN, outlives the job that set it: after a job
  whose fdpc put every vertex outside plane N (-w), later jobs with that plane enabled and no fdpc
  are removed until an fdpc puts the vertices inside (+w) again, in planes 0, 1 and 2 and both runs;
  while the state is inside, the vertex's distance dwords o4 and o5 at -1 or +1 remove nothing with
  plane 0, plane 1 alone or planes 0 and 1 enabled (and o6 nothing under plane 1 alone with a
  7-dword vertex); no run varies a distance dword under plane 2 with its state inside, and plane 2
  alone was removed until its state was first set inside.
  *mte; HW, infer; data: `mte-clip-plane1`, `mte-clip-plane-state`, `mte-clip-plane-dist`.*
- `E281` CR_ISP_MSAA mode 1 stores two samples of each pixel side by side in x and mode 2 four in a
  2x2 block, samples 0 to 3 of CR_ISP_MULTISAMPLECTL in that order (mode 0 its byte 0 alone); under
  mode 2 the MTE's multisample word and CR_ISP_SAMPLE_POS do not place them, and mode 1's two from
  bytes 0 and 1 is read from mode 2 [infer: the mode 0 and 1 probes set both words alike]; the
  layout, position and TE probes ran once; with CR_ISP_MSAA bit 31 clear nothing of the triangle is
  stored while the parameter buffer and TA data are byte for byte those of bit 31 set; the TE
  anti-aliasing bits 31 or 30 without bit 29 remove the triangle.
  *isp; HW, infer; data: `isp-msaa-layout`, `isp-msaa-positions`, `isp-msaa-te`.*
- `E282` ISP word 0 bits 24:22 are the depth compare, 0 never, 1 less, 4 greater, 7 always, and 2
  equal, 3 less or equal, 5 not equal and 6 greater or equal by the order of the stencil compare
  [infer: no depth here equals another, so 2 draws as 0, 3 as 1, 5 as 7 and 6 as 4]; bit 20 set
  stops the object writing depth; bit 21 set stops it writing colour while it still writes depth
  (one run); bits 9, 10, 12 to 14, 19 and 29 to 31 change nothing over five overlapping copies (one
  run).
  *isp; HW, infer; data: `isp-depth-compare`, `isp-tag-write`.*
- `E283` In a translucent pass the stored pixel is exactly the shader's o0: a shader that writes a
  constant without reading o0 stores the constant, one that passes o0 on stores the background
  unchanged, and one that ORs 0xff into o0 stores the background with its low byte set; in the one
  ISP and PBE state run, nothing after the shader blends [infer: no blend-related word was varied].
  *isp; HW, infer; data: `isp-translucent-blend`.*
- `E284` ISP word 2 is the stencil word: bits 27:25 compare the masked reference with the masked
  stencil (0 never, 1 less, 2 equal, 3 less or equal, 4 greater, 5 not equal, 6 greater or equal, 7
  always), bits 15:8 mask both sides of the compare and bits 7:0 the bits written; bits 24:22, 21:19
  and 18:16 are the operations on stencil fail, depth fail and pass, 0 keep, 1 zero, 2 replace with
  the reference, 3 increment clamped, 4 decrement clamped, 5 invert, 6 increment wrapping, 7
  decrement wrapping; bits 31:28 change nothing; each probe ran once.
  *isp; HW; data: `isp-stencil-word`.*
- `E285` CR_ISP_REG_04E8 at the job's 0x100, at 0, 1 and 0x101 changes no outcome of the stencil
  test against the background stencil (equal 0 draws, equal 1 does not) and no pixel or visibility
  count of 42 overlapping copies, depth always or less, in two runs; it is not the background-object
  values.
  *isp; HW, infer; data: `isp-reg-04e8`.*
- `E286` OUTSEL bit 12 puts each vertex's 1/w into the TA's object: with it clear the object loses
  the three 1/w dwords, its format word drops bit 18 and one stored and one iterated dword per
  vertex (0x00040303 to 0x00000202), and the image of the triangle at w 1 is unchanged; bit 13 clear
  changes neither object nor image; of the presence word's bits 16-31 set one at a time, 17, 18 and
  22-25 remove the triangle, 27 hangs the job and the other nine change nothing (one run).
  *mte; HW, infer; data: `mte-outsel-bits`, `mte-presence-high`.*
- `E287` The MTE clips the triangle at clip z = -w and z = w: at w 1 a flat triangle at clip z from
  -1 to 1 draws whole and one at -1.01, 1.01 or beyond is removed, and a sloped one is cut where its
  z passes -1 or 1; the depth the viewport makes is not clipped: a z offset of -0.5 to 1.5 draws the
  whole triangle under depth always; against a clear depth a depth above 1 compares as itself (1.01
  and 1.5 pass greater than 1.0) while a negative one compares as 0 (-0.01 and -0.5 fail less than
  0.0 and pass less than 1.0); each probe ran once.
  *mte; HW, infer; data: `mte-depth-range`, `mte-depth-range2`.*
- `E288` In a scene over two and three TA kicks each kick writes its own object (kick 1's at 0x1000,
  kick 2's on a new page at 0x3000, kick 3's appended to kick 1's at 0x105c), a region's stream
  holds one primitive and object word pair per object in kick order, and the object word's low bits
  are the dword address of the object's ISP words (0x406, 0xc06, 0x41d); bits 31:26 of the object
  word are 1, 3 and 9 for objects of one, two and five triangles, twice the primitives less one; the
  scenes ran twice, the one-kick probes once.
  *ta; HW, infer; data: `render-kick-objects`.*
- `E289` With CR_ISP_CTL bit 8 clear the 3D skips every 32x16 region the TA left without a control
  stream, except the scene's last region, leaving its pixels unwritten: 1 region at 96x64, 12 at
  128x128, 33 at 256x128, none at 64x64; bits 24 and 19:16 flipped from 0x000f0100 change no pixel
  at any of the four sizes; one run.
  *isp; HW, infer; data: `isp-isp-ctl`.*
- `E290` CR_ISP_REG_04DC bit 1 neither hangs nor changes an opaque or a translucent pass of five
  overlapping copies with depth less and writes: the nearest copy keeps its 1062 pixels and the
  visibility counter counts 0x44a with the bit clear and set, in two runs.
  *isp; HW, infer; data: `isp-reg-04dc-depth`.*
- `E291` CR_ISP_LINE_SAMPLE_POS is the line sample position and not a depth-bias format: with a
  depth sloped across the triangle and the polygon offset on, the units (0x100000) and the factor
  (4.0) each move the depth test's boundary by the same four columns and a factor of 64.0 removes
  the triangle, identically with 0x0418 at 1 and at 0, in two runs; the factor acts on a sloped
  depth.
  *isp; HW, infer; data: `isp-line-bias`.*
- `E292` Given the coefficients its job loaded, every firh vector of the earlier probe rounds runs
  in the simulator with no mismatch: of 17,851, 16,753 match (15,053 of them with the latch bytes
  the task did not write taken as any value), 1,066 under fixed banks 1 and 2 agree with tap
  families fitted to those same vectors and count as fitted, not as matches, and 32 stop; the loaded
  sets read as E078 gives them, a job that loads nothing has mode 0 and zero groups, the centre
  field's values written #-16 to #-5 are centres 16 to 27, and positions from 19 read 0.
  *usse; HW, infer; data: `vectors-usse`, `vectors-usse-followup`, `vectors-usse-jobs`,
  `vectors-usse-knowledge`, `usse-filter-banks`, `usse-filter-bank2`, `usse-filter-edges`.*
- `E293` With 0x0a9c at 2, firh's fixed sets 2 and 3 are zero-sum difference filters: set 2 is [1 -4
  4 -1]/8 at -1 to +2 and set 3 is [1 -2 1/2 1/2] at -2 to +1, seen on a line lifted above 0 so that
  the negative taps show.
  *usse; HW; data: `usse-filter-bank2`.*
- `E294` After 11.7 the simulator matches 23,597 of the 25,245 scalar USSE vectors of the earlier
  probe rounds (6,028 before), 143 of the 161 pixel vectors (135 before), and stops on 582 (19,217
  before) and 18; 1,066 more agree with firh's fixed-bank families, which were fitted to them, and
  count as fitted, not as matches; none differs. The 15,262 near matches are 209 within a measured
  bound and 15,053 with a value taken as any value. atst8, pcoeff, depthf, setfc, moest and setm
  gain semantics; with the 11.7 runs' 1,038 vectors, 24,440 scalar vectors match, 1,112 are fitted,
  686 stop and none differs.
  *usse; HW; data: `vectors-usse`, `vectors-usse-followup`, `vectors-usse-jobs`,
  `vectors-usse-knowledge`, `usse-alpha-test`, `usse-moe`, `usse-moe-followup`,
  `usse-instance-masking`.*
- `E295` Of the 2,161 bits the 219 USSE forms leave neither identifying nor in a field, the 523 of
  61 data forms (the moves, the bitwise group, integer multiply-add, the single and dot-product
  float forms, the colour and integer dot products, rlp, movc, movmsk, the masked tests, the video
  operations, idiv, eleven dual-issue pairs and both ldr forms) were flipped one at a time: each
  left the readback as the unflipped word did, except idiv's enc[47], which changed every
  destination r10 to r17.
  *usse; HW; data: `usse-encoding-bits`, `usse-encoding-bits-dual`, `usse-encoding-bits-load`,
  `usse-encoding-bits-followup`.*
- `E296` Of the 238 unmapped bits of nop, setfc, moest, setm, imo, the immediate smoa, smr, smbo and
  smlsi, pcoeff, depthf and atst8, flipped one at a time in a fill, 235 change nothing and three
  hang the job: enc[51] on setfc, enc[51] on imo and enc[44] on depthf.
  *usse; HW, infer; data: `usse-encoding-bits-state`.*
- `E297` Of twelve words the decoder rejects, three each of classes 2, 22, 26 and 31, run in place
  of an instruction in a fill, none hangs or faults the job; eleven match no form's mask and one of
  class 22 is bilin's word with a reserved format value; the three of class 31 change nothing; the
  three of class 2, the bilin word and one of class 26 leave the program's sixteen stores unwritten,
  exactly the five with enc[50] set among classes 2, 22 and 26, and two of class 22 change some
  pixels.
  *usse; HW, infer; data: `usse-encoding-gaps`.*
- `E298` firh reads line position p (0 to 11) at centre p; at centres -4 to -1 rep reads byte 0, msc
  byte -p and mdc byte -1-p; at 12 to 18 rep reads byte 11, msc byte 22-p and mdc byte 23-p; from 19
  to 27 every mode reads 0. With a load, sets 6 and 7 give 0 at 0x0a9c = 0, and are not 0 at 1 and
  2: bank 1's two sets and bank 2's set 6 give values no loaded group gives.
  *usse; HW; data: `usse-filter-edges`.*
- `E299` VDM state word 1 with bits 11:9 = 7 hangs some jobs and completes others, on the library's
  triangle job and on the probe's: in this run, of six jobs with it, the three with every pixel read
  back hung and the three without completed, whatever the render dump or the pixel program; earlier
  runs went the other way (E060's sweep hung without the readback and its probe completed with it,
  two runs each), so the readback does not decide the hang from run to run [infer: two tables]; a
  library job that completes draws the job's own image and leaves render memory byte for byte that
  of bits 11:9 = 2; one run of each job.
  *vdm; HW, infer; data: `vdm-state1-split`, `ta-te-psg`.*
- `E300` The index list's first trailing word (VDM_INDEX2) changes the TA's object of the five-copy
  job: at 1 the object keeps five triangles and its last vertex's 1/w reads 100000.0, at 2 and 3
  four triangles (12 vertices), at 5 and 0x0f000000 three (9 vertices), but with 0x0f000000 bit 15
  is set in the primitive list's entries and the packed vertices differ, at 0xff none and no pixel
  of them; at 0, 0x80000000 and the job's own 0xf0000000 the object is the job's; in the first run
  the job's own value hung (every pixel read back, no TA data saved), and the eight other cases give
  the same bytes in both runs; every image with triangles is the job's image.
  *vdm; HW, infer; data: `vdm-index2`.*
- `E301` Render command word 23 is the background object's first PDS word, the one the kernel puts
  in TA command dword 2 (cmd_ta.pds_bgnd): flipping bit 27 there through the kernel poke (one run)
  gives one of the two images the same flip of word 23 gives; with bits 27, 28, 30 or 31 flipped the
  job faults after part of the first 32x16 tile is written, whole rows from row 0 or the whole tile,
  and every other pixel stays at the sentinel; under bits 27 and 28 the number of rows changes from
  run to run: over these two runs and the two of the earlier sweep, bit 27 kept 5, 5, 4 and 5 rows
  and bit 28 3, 4, 3 and 3, while bits 30 and 31 kept the whole tile in all four.
  *render; HW, infer; data: `render-bg-pds-word`, `render-command-words`,
  `render-command-words-followup`.*
- `E302` Render details dword 9, which the 3D kick loads into CR_REG_0148, changes no image at
  0xffffffff or with any one of its 32 bits set, in the triangle job and over five overlapping
  copies; after the job the register reads 1 when bit 0 was set and 0 otherwise; the transfer
  command's word for the register changes neither a fill nor a copy at any of 34 values; one run.
  *render; HW; data: `render-reg-0148`, `transfer-kernel-words`.*
- `E303` Read after a job's context is cleaned up, the TA/3D control block keeps the RT data in
  dword 20 (the first DPM slot's owner) when the render flags had bit 2 or bit 3, and in dword 25
  too with bit 3, and neither without them; with render flag bit 10 clear the render draws its image
  but the context's RT data set cleanup never completes, as after a scene of two kicks; dword 24
  reads the TA client CCB's base plus 0x2c0 per render less one, dword 32 the context's PB
  descriptor, the one the cleanup names (the only one tried; that it is the cleanup's is the RE
  dataflow's reading), and dword 49 one more per context; two runs.
  *render; HW, RE, infer; data: `render-frag-flags`.*
- `E304` Render details dword 54, not TA command dword 16, points at the RT data set the firmware
  counts a scene in: moved by 0xc it makes the kernel report a parameter buffer overflow, after one
  render and after a scene's geometry kick, so a count lands in the set's partial-render word; moved
  by 0x8 it turns one render's cleanup from completing to failing and a two-kick scene's from
  failing to completing; moving dword 16 by either changes nothing; unpoked, a scene of two kicks
  fails its RT data set cleanup and one render's completes; that the cleanup waits for the executed
  count to equal the kernel's pending count, which our kernel raises once per scene (DDK: linux
  fork, sgxfive_render.c), with a kick that is not the scene's last adding one (RE, E156) and a
  render with render flag bit 10 adding one (RE, E164), is the reading that fits these outcomes
  [infer]: no case read the counts; one run.
  *render; HW, DDK, RE, infer; data: `render-rtds-words`.*
- `E305` CR_TE_PSG reads 0x01400000 after every unpoked job (the kernel's 0x00400000 with bit 24,
  which the TA kick ORs in); with bit 21 set in the TA command's word the register keeps it and the
  TA sets bit 29 of word 0 of every target region's header, changing nothing else of its output and
  no pixel; bit 24 already set changes nothing; the word at 0 makes the job fault;
  CR_DPM_STATE_CONTEXT_ID reads 0 after one render, two renders and a scene of two kicks; one run.
  *ta; HW, infer; data: `ta-te-psg`.*
- `E306` The TA object's three header words are the state block's words 3, 4 and 5 (the pixel PDS
  secondary pointer, size word and primary pointer) copied as given: each of six values set in one
  of them appears unchanged in the object's matching dword, and no other dword of the parameter
  buffer or the TA data changes; the secondary pointer set to 0x08000004 faults the render yet its
  object holds the word, and the primary pointer set to 0x08000000 changes no pixel; one run.
  *ta; HW, infer; data: `ta-object-words`.*
- `E307` The region test fitted to 26 shifts of one triangle (E180: a bounding box half-open between
  a region's two 16x16 tiles, then each edge against the tiles' corners) predicts exactly the
  regions and the PRIM_TILES form of 24 fresh random triangles on 128x128, among them triangles
  reaching past the target's edges: 265 regions predicted, 265 streamed, none missing, none extra,
  none of another form; the triangles test the generic overlap, not the fitted boundary rules: no
  vertex or edge of theirs lands on a tile boundary, so a plain overlap test, closed or open, gives
  the same tiles in all 768 regions, and only the forms 0x80, 0x90 and 0x98 occur; one run.
  *ta; HW, infer; data: `ta-object-words`.*
- `E308` The 28 object dumps of probes/ta/objects.toml, from which 3d.md §10.1 was written, and the
  45 taken since (the 15 of probes/vdm/index2.toml with an object and 30 of the 31 of
  probes/ta/object-words.toml, the faulting case keeping no TA data to place it) decode with one
  layout placed by the stream's object word: three PDS words, each vertex's dwords (the object
  word's ISP address less three, over the vertices, gives 1, 2, 3 or 5 dwords a vertex), the two ISP
  words, the primitive list, the line widths, a format word whose bits 7:0 are those dwords a
  vertex, the four set masks, then the packed vertices; the set masks over the coordinate-size
  settings 1 to 5 of one set read as one bit in mask 2, none, mask 3, mask 4, masks 3 and 4; the 45
  new objects all have the format 0x00040101 (one dword a vertex) and differ only in their vertex
  counts, so they test the placement by the stream, the vertex count and bits 7:0 of that one
  format, while the other formats and the masks rest on the dumps the layout was read from; bit 15
  of a primitive list entry is set in 11 of the 24 random triangles, exactly those of one winding.
  *ta; HW, infer; data: `ta-objects`, `vdm-index2`, `ta-object-words`.*
- `E309` After a job CR_DPM_TA_ALLOC_FREE_LIST_STATUS1 and CR_DPM_3D_FREE_LIST_STATUS1 hold the free
  list's tail page in the high half and its head page in the low half, and the two STATUS2 registers
  the page before the tail in the low half, as the page table in memory chains them: the DPM
  rewrites the table in place, one 32-bit entry per page at the table base plus four times the page
  number, appending each freed page at the tail; one run of ten jobs, its registers repeated by
  E256's register timelines.
  *dpm; HW, infer; data: `dpm-free-list`.*
- `E310` CR_DPM_STATE_BASE0 and CR_DPM_CONTROL_BASE hold the RT data's DPM state and control pages;
  after a job with a partial render the state page holds seventeen two-dword page lists, one per
  macrotile numbered down then across and the global list last, each the page count and head page
  then the tail page, and every other job leaves the TA data's control, OTPM and state pages zero;
  TA3DCtl dwords 35 and 39 read the page count less 2 and the macrotile the DPM aborted; one run.
  *dpm; HW, infer; data: `dpm-free-list`, `dpm-partial-renders`.*
- `E311` Every triangle pixel of an overflowing scene is drawn by some render: with CR_ISP_CTL's
  PROCESS_EMPTY_TILES clear the partial-render jobs draw all of the triangle (207456 pixels at
  1024x768, 4422528 at 4096x4096) at every buffer size; with it set (the kernel's value) the pixels
  missing are whole 32x16 regions of the macrotiles that held geometry at a partial render, painted
  with the background by the final render, which has no stream for them.
  *dpm; HW, infer; data: `dpm-partial-renders`, `dpm-partial-timelines`.*
- `E312` Through a partial render CR_DPM_ABORT_STATUS_MTILE reads the aborted macrotile (5) as the
  TA stops, CR_DPM_STATE_CONTEXT_ID turns 2 and CR_DPM_STATE_BASE1 is set to the RT data's state
  page; the 3D then frees the pages of every macrotile, page status counting down to the global
  list's one page, and the TA resumes from the list's head; with 0x23 pages the first partial render
  starts at the first page; 0x0730 reads 1 while the 3D holds the global page, from a partial
  render's start (or the render's, without one) to the final render's last free, the TA's runs
  between partial renders included; 0x0738 reads 0 while a render runs, and 0x0748 0x1f idle, 0xf
  while the TA holds pages and through a partial render, 0x7 in some samples while the TA takes
  pages; 0x0740 stays 0.
  *dpm; HW, infer; data: `dpm-partial-timelines`.*
- `E313` With CR_DPM_REG_074C bit 8 set the 64x64 job faults at the context's address 0x20006010 or
  0x20006012 whether CR_DPM_STATE_BASE1 holds 0x20006000 or 0x20042000, so the address does not come
  from that register; on a context for up to 4096x4096, whose TA data covers 0x20006000, the same
  word renders the triangle exactly, with no fault and nothing written to the TA data's DPM pages.
  *dpm; HW, infer; data: `dpm-state-base`.*

### 2026-11-03

- `E314` Read while the context lives, the RT data set's executed count (word 1) and the kernel's
  pending count rise together by one at every kick, the geometry kicks included, and are equal after
  every job of scenes of one to four kicks; a render without render flag bit 10 adds to neither, so
  its cleanup completes; every cleanup of the table completes and no case resets the GPU, where
  one-count-per-scene cleanups of two kicks had failed; one run.
  *render; HW, DDK; data: `render-pending-counts`.*
- `E315` The RT data set's cleanup completes only when its executed count equals the word the set's
  word 0 points at: one render whose pending count is poked to 2 or to 0 (executed 1) fails its
  cleanup, and with the count at 2 but word 0 pointed at the executed count itself it completes;
  render details word 54 moved by 0x8 puts the count in the set's word 3, so one render leaves
  executed 0 against pending 1 and a scene of two kicks executed 1 against pending 2, and both
  cleanups fail; one run each.
  *render; HW; data: `render-pending-kw`, `render-pending-rd54`.*
- `E316` Read while the context lives, a render with render flag bit 2 leaves the TA/3D control
  block's dword 20 (the first DPM slot's RT data) set and dword 25 clear, one with bit 3 or both
  leaves both set; a later render on the context with the bits clear clears both; a new context at
  the same addresses starts with them set and its first render draws the control's image and clears
  them; the access word render details word 52 points at stays 0 in every case; with debugfs
  rtds_keep set the kernel leaves the RT data set's words as the previous job left them (an
  out-of-memory count poked to 5 stays 5) and nothing else of the set's words changes, the kept
  dwords cleared by the second render as without it; one run.
  *render; HW; data: `render-slot-words`.*
- `E317` With recovery held after a render faults reading its unmapped stream page, the EDM does not
  answer GETMISCINFO (the kernel's 500 ms wait ends the query, about 0.65 s from the shell), a fill
  on another context does not run, CR_BIF_INT_STAT reads 0x90008 and CR_BIF_FAULT 0x3e00000a the
  whole time, CR_EVENT_STATUS2 0x480, the interrupt counters do not move, the EDM tick count in
  CR_USE0_SERV_EVENT stays still between two reads 19 s apart, and the render memory holds no object
  and an all-zero TA data; the TA kick had taken the DPM slot and loaded the PB; a debugfs reset
  (halt, firmware buffers rebuilt, boot in place) recovers, the kernel log showing three more resets
  within 0.91 s: the fault watchdog's recovery of the faulted job, a failed render-context cleanup
  and the fault of a job left queued; one run.
  *edm; HW, DDK, infer; data: `render-hold-fault`.*
- `E318` Saved before the kernel recovers (recovery held), the job hung in its pixel task holds its
  object in the parameter buffer and the TA data a finished TA leaves (byte for byte the one-kick
  triangle's of E288), in both held runs; saved after the recovery, the same job holds the same
  object but an all-zero TA data; the job with VDM state word 1 bits 15:13 = 0 holds neither, held:
  the TA wrote nothing before it stopped; while either is held GETMISCINFO is not answered; one run
  of each, the pixel control held twice.
  *vdm; HW; data: `render-hold-hang`, `render-kick-objects`.*
- `E319` With the TA/3D control block mapped read-only in the render client's VM (debugfs
  alias_ta3d_ro) the first kick faults on the block's page, CR_BIF_INT_STAT 0x80400 and CR_BIF_FAULT
  0x32004005, before the PB load writes dword 46 and before the DPM slot is taken (dwords 46, 20 and
  25 stay 0), after the render-context count (dword 49) has moved; the job stalls, GETMISCINFO is
  not answered while recovery is held, and the job fails with a fault once recovered; one run.
  *edm; HW, infer; data: `render-ta3d-ro`.*
- `E320` On a lone render context the EDM starts a TA command whose one source sync is incomplete
  (read and write pending values 0x5a5a5a5a against a word that reads 0): the geometry kick
  completes, the render details take the sync (words 90 to 94), the closing render draws the
  control's image and the cleanup completes; the same kick with its transfer-queue sync set (word 25
  = 0x5a5a5a5a, word 26 that word) never starts and the EDM faults reading page 0 through its own
  directory list, 15 (bus status 0xd0400), the read of the sync's second pointer, word 28, left 0;
  one run.
  *edm; HW, RE, infer; data: `edm-ta-syncs`.*
- `E321` After each of three debugfs resets (about 0.27 s each from the shell) the EDM answers
  GETMISCINFO within 169 to 175 µs, on the first and the second query alike, and 168 µs after a
  render; while a faulted or hung job is held the query is not answered and the kernel's 500 ms wait
  ends it, about 0.65 s from the shell; one run.
  *edm; HW, DDK; data: `edm-miscinfo-reset`, `render-hold-fault`, `render-hold-hang`,
  `render-ta3d-ro`.*
- `E322` 11.6's scenes of one, two and three TA kicks run again on the kernel that counts each kick:
  every context cleanup completes and the table's kernel log holds no reset, where the 11.6 run had
  reset the GPU for the scenes of several kicks; the parameter buffers and TA data dumped after the
  closing renders are byte for byte those of the 11.6 runs, and the images the same (1062, 1730 and
  2026 triangle pixels); one run.
  *ta; HW; data: `render-kick-objects-again`, `render-kick-objects`.*
- `E323` The closed GLES1 and GLES2 stacks registers a 0x44-byte HW render context image whose dword
  2 it names as the page directory's physical address (the registration's offset 8, which the kernel
  patches); in every capture the context holds CONTEXT_FLAGS 0x21 (NEW and OWN_PB), priority 0, the
  client CCB and its control, no submitted command, its PB descriptor, in dword 7 the address of a
  0x40-byte parameter-heap object at the DPM page table's base plus 0x40000, empty render lists and
  queue links, and the process's PID; only the PID and, with the PB size, dword 7 change between
  runs, and our kernel's context differs only in OWN_PB, the page directory and the PID.
  *render; CAP, HW; data: `render-state-variations`, `render-draws-frames-pb`,
  `render-register-gaps`, `isp-registers`, `isp-line-width`, `texture-textures`, `texture-samplers`,
  `texture-formats`, `texture-streams`, `usse-inputs`, `usse-gles1-programs`, `usse-shaders`,
  `render-pending-counts`, `render-closed-compare`.*
- `E324` The closed GLES2 stack submits every frame as at least two TA kicks on one client CCB: a
  first kick (GEOM_FLAGS 0x71 on a context's first frame, 0x61 after; FRAG_FLAGS 0) whose control
  stream holds the frame's draws and is not the scene's last, then a closing kick (GEOM_FLAGS 0x62,
  FRAG_FLAGS.BIT10, CR_TE_PSG bit 22) whose stream is only the end-of-scene state blocks and the
  terminate; a glFlush adds a middle kick (0x60) holding the draws since the last kick; the stream
  base advances by each kick's stream length, the TA status update 0 carries that offset and update
  6 the kicks so far; with FlushBehaviour=2 the flush ends the scene itself (0x73 and
  FRAG_FLAGS.BIT10) and the next render of the frame carries FRAG_FLAGS bit 14 and frame number 1.
  *render; CAP; data: `render-draws-frames-pb`, `render-state-variations`, `render-register-gaps`,
  `isp-registers`, `isp-line-width`, `texture-textures`, `texture-samplers`, `texture-formats`,
  `texture-streams`, `usse-inputs`, `usse-gles1-programs`, `usse-shaders`, `ta-target-sizes`.*
- `E325` The closed GLES1 and GLES2 stacks' RT data set is a 0x88-byte KERNEL_DATA object: the
  0x18-byte header (the pending count's address, executed count 0, dword 2 = 8, no out-of-memory
  signal or partial render, dword 5 = 2) and two 0x38-byte RT data, which the client uses scene by
  scene in turn with two render details; each RT data holds the HW render context's address in dword
  0, render details 0, dwords 2 and 3 = 1 and 0xc0, the shared background object, a DPM state of its
  own, the shared DPM control and OTPM, the TE tail pointer cache and its size 0x100 in dwords 8 and
  9, one render target, a region-header stride of 0, a status word of its own and state 0x10; our
  kernel's set has the same header but dword 5 = 1 and one RT data whose words follow the same
  rules.
  *render; CAP, HW; data: `render-state-variations`, `render-draws-frames-pb`,
  `render-register-gaps`, `isp-registers`, `isp-line-width`, `texture-textures`, `texture-samplers`,
  `texture-formats`, `texture-streams`, `usse-inputs`, `usse-gles1-programs`, `usse-shaders`,
  `ta-target-sizes`, `render-pending-counts`, `render-closed-compare`.*
- `E326` The closed GLES2 stack's one-triangle frame and our tri job are built from the same objects
  (render context, client CCB and control, TA commands, render details with their 3D register block,
  an RT data set, PB descriptor and block, parameter buffer and 0x40000-byte page table, TA data:
  tail pointer cache, DPM control, OTPM, DPM state and region headers, background object and its
  primary-program word list, control stream, PDS and USSE programs, status and sync words); against
  the closed frame ours differs in using one kick for the scene, the background object for the
  clear, one RT data, no OWN_PB, CR_ISP_CTL bit 8 set and 0x04c4 bit 25 clear, and in words the
  firmware or the kernel fills; every other TA register and render-details word compared holds the
  closed driver's value.
  *render; CAP, HW; data: `render-state-variations`, `render-pending-counts`,
  `render-closed-compare`.*
- `E327` The closed GLES1 and GLES2 stacks' PB descriptor at the default size holds no flags, 0x422
  pages in dword 1, the free list (pages << 16 | 1) and the TA allocation word ((pages - 1) << 16)
  both initial and current, the page table's base, zero allocated, local and global counts,
  thresholds TA 0x432 (pages + 16), ZLS 0x400, global 0x400 and PDS 0x300, and its one PB block,
  which holds the page count, the free-list word, the descriptor's own address and no next block;
  PBSize=1048576 and 8388608 give 98 pages (TA threshold 114, ZLS and global 64, PDS 0), smaller
  PBSize values fail eglInitialize, MaxParamBufferSize changes nothing and ZLSThreshold=0 zeroes the
  ZLS threshold; our kernel's descriptor before its first render is the default one word for word
  but for the addresses.
  *dpm; CAP, HW; data: `render-state-variations`, `render-draws-frames-pb`, `render-register-gaps`,
  `isp-registers`, `isp-line-width`, `texture-textures`, `texture-samplers`, `texture-formats`,
  `texture-streams`, `usse-inputs`, `usse-gles1-programs`, `usse-shaders`, `render-pending-counts`,
  `render-closed-compare`.*
- `E328` In every TA command of the closed GLES1 and GLES2 stacks the size word is 0x2a8 plus 8 per
  3D patch rounded up to 64 bytes (0x2c0 for none or one, 0x300 for six) and the commands lie back
  to back in the client CCB; dwords 5 and 6 both hold 0x50000000, the four threshold words are 0,
  dword 16 holds the RT data set and dword 18 0; the shared block names seven TA and three 3D status
  updates and, on the closing kick only, the 3D transfer-queue sync; and of the TA register block's
  28 words the zero-word registers are 0 in every run, and the rest hold, for a single-sampled
  target, the values our tri job writes: CR_TE_AA 0x20000000, CR_MTE_CTRL 0xa2, the 1/w floats
  0x358637bd, CR_MTE_MULTISAMPLECTL 0x88, the tiling words by the size rule, CR_PPP_SCREEN (w - 1) |
  (h - 1) << 16, the region header base the render details also name and the TE tail pointer cache.
  *ta; CAP; data: `render-state-variations`, `render-draws-frames-pb`, `render-register-gaps`,
  `isp-registers`, `isp-line-width`, `texture-textures`, `texture-samplers`, `texture-formats`,
  `texture-streams`, `usse-inputs`, `usse-gles1-programs`, `usse-shaders`.*
- `E329` Across the closed GLES1 and GLES2 stacks' 3D captures (819 kicks of 12 capture tables, and
  the target sizes) the TA register block moves in eight registers and three address words only:
  CR_TE_SCREEN, CR_PPP_SCREEN, CR_TE_MTILE1, CR_TE_MTILE2 and CR_TE_MACROTILE_STRIDE with the
  target's size and with 4x multisampling, CR_TE_AA and CR_MTE_MULTISAMPLECTL with 4x multisampling,
  CR_TE_PSG with the scene's close and a depth or stencil buffer, and the three address words
  (control stream, region headers, tail pointer cache) with the kick and the scene; the 3D side
  moves as E330 lists; GEOM_FLAGS and FRAG_FLAGS move with the kick's place in the scene, a depth or
  stencil buffer and a render to a texture.
  *ta; CAP; data: `render-state-variations`, `render-draws-frames-pb`, `render-register-gaps`,
  `isp-registers`, `isp-line-width`, `texture-textures`, `texture-samplers`, `texture-formats`,
  `texture-streams`, `usse-inputs`, `usse-gles1-programs`, `usse-shaders`, `ta-target-sizes`.*
- `E330` Over every closing kick of the closed GLES2 stack's 3D captures the render details' 52-word
  3D register block holds the same value in 24 words whatever the state, size or program (among them
  CR_ISP_CTL 0xf0000, CR_REG_0400 0x80, CR_REG_0800 0x30, CR_ISP_BGOBJDEPTH 1.0 and CR_ISP_BGOBJVALS
  0x300 even with a clear depth of 0.5, CR_ISP_SAMPLE_POS 0 even under 4x multisampling, 0x04e8
  0x100, 0x04dc 0, 0x0148 0 and the second colour-space set and luma key 0), and the other 28 move
  only with an address, the scene's buffers, a depth or stencil buffer (the ZLS words, also by 3D
  patches), the polygon offset (its factor and units as given), 4x multisampling (CR_ISP_MSAA
  0x80000002, CR_ISP_MULTISAMPLECTL 0xeaa26e26), a YUV stream (the first colour-space set, or the
  USSE coefficients for NV12), a render to a texture (0x04c4 bit 8) or the parameter buffer's size
  (0x04c4 bits 19:12).
  *isp; CAP, HW; data: `render-state-variations`, `render-draws-frames-pb`, `render-register-gaps`,
  `isp-registers`, `isp-line-width`, `texture-textures`, `texture-samplers`, `texture-formats`,
  `texture-streams`, `usse-inputs`, `usse-gles1-programs`, `usse-shaders`, `ta-target-sizes`,
  `render-closed-compare`.*
- `E331` Over 222 render-target sizes from 1x1 to 4096x4096 the closed GLES2 stack's tiling words
  and size words all follow one rule: 32x16-pixel tiles; n = 4 macrotiles across and down from w x h
  >= 640 x 480 pixels (640x475 still 2, 640x480 and 4096x75 already 4), else 2; a macrotile spans
  the tiles over n rounded up to whole 4-tile blocks; CR_TE_SCREEN, CR_TE_MTILE1 (bit 31 for n = 4),
  CR_TE_MTILE2 and CR_TE_MACROTILE_STRIDE (16 per 4x4-tile block) as tiling3d.py gives them; and in
  the RT data set the tiles across all macrotiles (header dword 2), the blocks per macrotile (RT
  data dword 2), a macrotile's region headers (0xc0 per block, dword 3), the tail pointer cache (4
  bytes over the square of the power of two that covers the larger macrotile span, dword 9 and the
  cache object's size) and the region-header buffer (0xc0 per block per macrotile); widths or
  heights above 4096 fail eglCreatePbufferSurface.
  *ta; CAP; data: `ta-target-sizes`, `render-register-gaps`, `isp-registers`.*
- `E332` Under the harness the closed GLES2 driver writes ISP word 0's depth compare as the GL
  function's order (never 0, less 1, equal 2, less or equal 3, greater 4, not equal 5, greater or
  equal 6, always 7), sets bit 20 when depth is off or its writes masked and bit 21 with a colour
  mask of 0000, sets ISP word 2 (presence bit 2, ISP word 0 bit 8, the reference in bits 7:0) with
  GL's stencil function, masks and the three operations in the codes of ISP2's fields, and puts
  glColorMask in ISP word 1 bits 7:4 (red bit 7, green 6, blue 5, alpha 4); blending gives pass type
  1, and bit 9 is set in every clear object and triangle (the pass-type-3 objects have it clear).
  *isp; CAP; data: `render-state-variations`, `isp-registers`.*
- `E333` The closed driver's end-of-tile task hands the PBE EMIT0 = 0, EMIT1 = (height - 1) << 16 |
  (width - 1), EMIT2 = 0x80 << 8 with bits 27:16 the row pitch in pixels / 2 - 1 (the same field for
  RGB565 and ARGB8888, the pitch a whole number of 8 pixels: 104 for a width of 100), EMIT3 the
  surface address, and a sideband of pack mode 3 (RGB565) or 0 (ARGB8888) with bit 9, bit 10 while
  GL dithering is on (also in ARGB8888) and bit 13 only for a render to a texture; 4x multisampling
  leaves the words as they are.
  *pbe; CAP; data: `render-state-variations`, `render-register-gaps`, `isp-registers`.*
- `E334` In every render the closed driver submits, the background object's primary PDS program
  (cmd_ta.pds_bgnd word 2) holds in its data segment texture words describing the render target
  itself, in every run of the two tables captured: T1 a strided texture (TEXTYPE 6) of the target's
  format and size, T0 a clamped stride of the target's pitch in dwords minus one, T2 the target's
  address, T3 0x00800000 (that the program samples them is [infer]); the words are the same with a
  clear, without one and on a frame that does not clear, and CR_ISP_BGOBJVALS stays 0x300 and
  CR_ISP_BGOBJDEPTH 1.0 whatever the clear depth.
  *isp; CAP; data: `render-state-variations`, `render-draws-frames-pb`.*
- `E335` With depth or stencil on, the closed driver gives the window surface one GENERAL allocation
  of 0x5000 bytes, depth at its start (64 x 64 four-byte values) and stencil 0x4000 on, loaded and
  stored at the same addresses in every frame: the render flags carry 0x180 (DEPTH_BUFFER and
  STENCIL_BUFFER) whichever of the two GL uses, the first render of the surface names the buffer,
  and a later frame's render loads what the earlier stored; with ExternalZBufferMode=2 the buffer is
  set up with the context and loaded from the first render, and ExternalZBufferMode=1 and
  ZLSThreshold=0 change no word.
  *zls; CAP; data: `render-draws-frames-pb`, `render-register-gaps`.*
- `E336` The closed driver names a window surface's depth buffer through the TA command's 3D
  patches, not its render details: the surface's first render with the ZLS flags carries six
  {address, value} pairs, in this order CR_ISP_ZLSCTL (0x0017100c), CR_BIF_ZLS_REQ_BASE
  (0x08000000), CR_ISP_ZLOAD_BASE and CR_ISP_ZSTORE_BASE (both the depth offset),
  CR_ISP_STENCIL_LOAD_BASE and CR_ISP_STENCIL_STORE_BASE (both the stencil offset with bit 31), each
  address a render details register word; every later render of the surface carries one pair,
  CR_ISP_ZLSCTL 0x0017700e; renders without the flags carry none.
  *zls; CAP; data: `render-draws-frames-pb`, `render-register-gaps`, `isp-registers`.*
- `E337` The closed driver's CR_ISP_ZLSCTL values are 0x0017100c for a window surface's first render
  (bits 2, 3, 12, 16-18, 20), 0x0017700e for every later one (bits 1, 13 and 14 added), 0x0017300e
  set with the context under ExternalZBufferMode=2 (bits 1 and 13 added, 14 not), 0x0011700a written
  between frames (bits 2, 17 and 18 cleared from 0x0017700e) and 0x00140008 for a texture's depth
  attachment (bits 3, 18, 20; depth flag only); so bits 1, 13 and 14 are what a render that loads
  the kept buffer adds, and bits 2, 12, 16 and 17 are absent with the depth flag alone.
  *zls; CAP; data: `render-draws-frames-pb`, `render-register-gaps`, `isp-registers`.*
- `E338` With glPolygonOffset enabled the closed driver sets ISP word 1 bit 23 on the triangle (not
  on the clear object) and writes the render details' polygon offset registers:
  CR_ISP_POLY_OFFSET_FACTOR the GL factor as an IEEE single (1.0 0x3f800000, 2.0 0x40000000, -1.0
  0xbf800000, 0 at 0), CR_ISP_POLY_OFFSET_UNITS the GL units as a 32-bit integer (1, 4, -1 as
  0xffffffff), CR_ISP_POLY_OFFSET_CLAMP 0; the same with depth off and with depth less.
  *isp; CAP; data: `render-register-gaps`.*
- `E339` A multisampled texture render of the closed driver, asked for 2 or 4 samples, moves seven
  register words, and bit 48 of one instruction of the end-of-render program's second task, against
  the same render single-sampled: CR_ISP_MSAA mode 2 (0x80000002), CR_ISP_MULTISAMPLECTL and the
  TA's CR_MTE_MULTISAMPLECTL 0xeaa26e26 (samples at (6, 2), (14, 6), (2, 10), (10, 14) sixteenths),
  CR_TE_AA 0xe0000000 (bits 31:29), CR_TE_MTILE1 and CR_TE_MTILE2 0x00802002 (0x01004004
  single-sampled) and CR_TE_MACROTILE_STRIDE 4 (0x10); CR_ISP_SAMPLE_POS stays 0, and alpha to
  coverage and sample coverage move no word; a multisampled texture with a depth attachment is
  refused (incomplete) and renders single-sampled.
  *isp; CAP; data: `render-register-gaps`, `isp-registers`.*
- `E340` Over every captured run the closed driver uses four ISP pass types: 0 for opaque objects
  and the clear, 1 for every blended object and for the GLES1 alpha test, 4 for a GLSL shader that
  discards (with or without a depth test), and 3 for the two objects a scissor or a viewport smaller
  than the target adds (ISP word 0 0x07e00100, no ISP word 1, no pixel program); it writes
  glLineWidth x 16 into ISP word 1 bits 15:8 (1 0x10, 1.5 0x18, 2 0x20, 3 0x30, 4 0x40, 8 0x80, 15
  0xf0) for lines and points alike and 0x10 for triangles, 0 for the clear object, the object type
  in ISP word 0 bits 17:15 (triangle 0, line 1, point 3), and CR_ISP_LINE_SAMPLE_POS 1 in every
  render.
  *isp; CAP; data: `render-state-variations`, `render-register-gaps`, `render-draws-frames-pb`,
  `isp-registers`, `isp-line-width`, `texture-textures`, `texture-samplers`, `texture-formats`,
  `texture-streams`, `usse-inputs`, `usse-gles1-programs`, `usse-shaders`.*
- `E341` Streaming a YUV buffer through IMG_texture_stream2, the closed driver samples a packed UYVY
  or YUYV buffer (pixel formats 73 and 74) in one fetch, TEXTYPE 3 with TEXFORMAT 29 or 28, and
  loads colour-space set 0 in the render details as 0x00950095, 0x00000095, 0x010203ce, 0x039800cc
  and 0 with set 1, the input word and the USE coefficients at 0; it samples NV12 (format 64) as two
  fetches, the luma plane as TEXFORMAT 26 and the half-size chroma plane after it as TEXFORMAT 27,
  both with T0 bit 30, and loads the USE coefficient registers instead (CR_USE_COEFFS_MODE 3, three
  groups of taps and biases) with the colour-space sets at 0; the formats 69, 71, 195, 196, 199 and
  200 are refused at the bind and the draw samples a 1x1 RGBA8888 texture; one capture each.
  *texture; CAP; data: `texture-streams`.*
- `E342` The closed driver's texture words T0 and T1, one GL sampler or format change at a time:
  GL_LINEAR minification sets T0 bits 11:10 to 1 and magnification bits 13:12 to 1, a linear mip
  filter sets bit 9, any mipmapped minification sets bits 20:17 to 13 instead of 15, bits 26:21 stay
  0x3f; S wrap is bits 8:6 and T wrap bits 5:3 (0 repeat, 1 mirror, 2 clamp); T1 holds TEXTYPE
  (31:29: 0 power of two, 3 NPOT and streams, 6 depth), TEXFORMAT (28:24) and width and height less
  one (23:12, 11:0); RGBA4444 2, RGBA5551 4, RGB565 5, BGRA8888 12, RGB and RGBA8888 13, RGBA half
  float 17, float 18, PVRTC 2 bpp 23, PVRTC 4 bpp 24, ETC1 27, and with T0 bit 30 alpha 25,
  luminance 26, luminance-alpha 27 and luminance half float 30; a float RGBA texture is four
  one-channel fetches and a half-float one two; depth textures are TEXTYPE 6 float 18 with a
  32-dword stride; T3 is 0x00800800 in every texture but the luminance half-float one (0x01000800);
  one capture each.
  *texture; CAP; data: `texture-samplers`, `texture-formats`, `texture-textures`.*
- `E343` Every pixel PDS pointer the closed driver writes (an MTE state block's secondary and
  primary words, the TA command's special object words 0 and 2) holds the program's offset from
  PDS_EXEC_BASE in 16-byte units in bits 23:0 and its data size in 16-byte rows in bits 31:26, bits
  25:24 clear; each resolves into a PDSPIXEL_CODEDATA object holding the whole data, and the highest
  data dword the program's dout operands read lies in the last row the pointer counts in 4978 of the
  4990 programs (the other 12, all GLES1, also read registers above their data); of the size word
  between them, bits 17:16 are 3 in every block, bits 24:18 at least the secondary's constant dwords
  in rows of four (0 to 6), bits 6:0 1 except with three or more iterated sets (2 and 4), and bits
  31:25 0 on the clear's blocks and otherwise 12, or 11 when bits 24:18 are not 0, divided by bits
  6:0 and rounded down; the special object's size word is 0x00030001 in all 1263 kicks.
  *pds; CAP; data: `render-state-variations`, `render-register-gaps`, `render-draws-frames-pb`,
  `isp-registers`, `isp-line-width`, `texture-textures`, `texture-samplers`, `texture-formats`,
  `texture-streams`, `usse-inputs`, `usse-gles1-programs`, `usse-shaders`, `ta-target-sizes`.*
- `E344` In the closed driver's captured kicks every USSE code-address word a PDS program hands to
  doutu holds a code-base index in bits 3:0 and an instruction index in bits 23:4: the pixel-side
  programs (special object, MTE pixel programs, end of render) use base 0 and the vertex-side ones
  (VDM state-block programs, vertex tasks) base 10, and with base 0 at 0xf4000000 and base 10 at
  0xfc000000 all 15071 land on an instruction inside an object of the PIXELSHADER or the
  VERTEXSHADER heap, as the side says; a vertex task's PDS program fetches each attribute with one
  doutd whose second word gives the attribute's dwords less one in bits 3:0 and its offset in the
  vertex's attribute rows in bits 19:8, from a data word holding the stream address and one holding
  the stride in bytes, and starts its USSE program with a base-10 doutu.
  *pds; CAP; data: `render-state-variations`, `render-register-gaps`, `render-draws-frames-pb`,
  `isp-registers`, `isp-line-width`, `texture-textures`, `texture-samplers`, `texture-formats`,
  `texture-streams`, `usse-inputs`, `usse-gles1-programs`, `usse-shaders`, `ta-target-sizes`.*
- `E345` The secondary pixel program an MTE state block names is a lone doutu (no constants), one or
  two doutd of 10 to 18 constant dwords then a doutu, or in GLES1 a doutu then three or four douta,
  with DOUTU1 0 or 0x4; the primary is a doutu followed by one douti per iterated set and one doutt
  per texture fetch, each fetch after the douti of its coordinates, with DOUTU1 0x4 when it iterates
  nothing, 0x01000004 when it iterates without fetching (0x01000006 in three branching shaders),
  0x02000004 in most textured programs and 0x03000004 in every textured GLES1 program but
  GL_REPLACE's and in five GLES2 ones (texture times colour, two textures, a half-float luminance
  texture); the special object's programs are a lone doutu and a doutu, douti and doutt with
  0x02000004.
  *pds; CAP; data: `render-state-variations`, `render-register-gaps`, `render-draws-frames-pb`,
  `isp-registers`, `isp-line-width`, `texture-textures`, `texture-samplers`, `texture-formats`,
  `texture-streams`, `usse-inputs`, `usse-gles1-programs`, `usse-shaders`, `ta-target-sizes`.*
- `E346` Every one of the 1888 index lists in the closed driver's captured VDM streams is six words:
  a header with bits 31:30 = 2, the topology in 29:26 (0 triangles, 1 lines, 2 points, 3 strip, 4
  fan, a line strip arriving as lines), bits 25:24 clear, both trailing-word bits 23:22 set and the
  index count in 21:0; the index base in the GENERAL heap; the trailing words 0xf0000000 and
  0x003fffff (0xf4000000 once under GLES1 flat shading, 0xd0000000 once with eight vertex
  attributes); then the vertex task, whose word 0 holds VDM_TASK0.MAX_VERTICES (15 for most GLES2
  draws, 9 for GLES1's and a point-size shader's, 7 for the screen-space draws, 13 with eight
  attributes, 2 with nine output rows) and the vertex PDS program's address >> 4 in 27:0
  (PDSVERTEX_CODEDATA), and whose word 1 holds the output rows in 31:24 (1 to 4, and 9), 3 in 23:22
  (2 once, with nine output rows), one attribute row per vertex attribute in 14:7 and the PDS data
  rows in 6:0.
  *vdm; CAP; data: `render-state-variations`, `render-register-gaps`, `render-draws-frames-pb`,
  `isp-registers`, `isp-line-width`, `texture-textures`, `texture-samplers`, `texture-formats`,
  `texture-streams`, `usse-inputs`, `usse-gles1-programs`, `usse-shaders`, `ta-target-sizes`.*
- `E347` The closed driver's MTE state blocks take eight presence words, 0x2000 (2 dwords), 0xd485
  (9), 0xd4c3 (12), 0xd4c7 (13), 0xdf43 (18), 0xdf47 (19), 0xdfc3 (20) and 0xdfc7 (21), each block
  exactly the presence word plus the words its set bits add in bit order (isp0, isp1, isp2 one each,
  the pixel programs three, the region clip two, the viewport six, then one each for bits 9 to 15);
  the VDM state block's PDS program copies it with doutd, whose second word gives the dwords of a
  line less one in bits 3:0, the lines less one in 7:4, the destination dword offset in 19:8 and the
  line stride less one in 29:22, equal to the line length in every copy, a block over 16 dwords
  going as two or three lines (18 as 2 x 9, 20 as 2 x 10, 21 as 3 x 7) or as a 16-dword line and a
  second doutd of 3 dwords at offset 16; the end-of-scene block is written by douta instead; the VDM
  state word's bits 7:0 are at least the block's dwords in rows of four.
  *mte; CAP; data: `render-state-variations`, `render-register-gaps`, `render-draws-frames-pb`,
  `isp-registers`, `isp-line-width`, `texture-textures`, `texture-samplers`, `texture-formats`,
  `texture-streams`, `usse-inputs`, `usse-gles1-programs`, `usse-shaders`, `ta-target-sizes`.*
- `E348` In the closed driver's MTE state, the region clip word 0 holds an enable in bit 31 and the
  first and last 32-pixel tile columns in 30:16 and 15:0, word 1 the first and last 16-pixel tile
  rows in 31:16 and 15:0, counted from the bottom of the target in GL's window coordinates; a clear
  or mask fill's block always carries it, a draw's block only when its viewport does not cover the
  target; the viewport words are x + w/2, w/2, y + h/2, h/2 (y up, a positive scale), (n + f)/2 and
  (f - n)/2 of glViewport and glDepthRange; the end-of-scene term word holds the last 32-pixel
  column and row; MTECTL is 0x01555620 on every GLES2 draw (0x15555620 GLES1), plus 2 for cull back
  and 1 for cull front or cull back with clockwise front faces, 0x40 on the screen-space clear
  blocks, 0x3a0 on a flat-shaded GLES1 draw; GL_FRONT_AND_BACK drops the draw from the stream.
  *mte; CAP; data: `render-state-variations`, `render-register-gaps`, `render-draws-frames-pb`,
  `isp-registers`, `isp-line-width`, `texture-textures`, `texture-samplers`, `texture-formats`,
  `texture-streams`, `usse-inputs`, `usse-gles1-programs`, `usse-shaders`, `ta-target-sizes`.*
- `E349` The closed driver's 1263 captured VDM streams use three block types only, state (bits 31:30
  = 1), index list (2) and terminate (3), and no link (0), each stream one GENERAL object from
  CR_VDM_CTRL_STREAM_BASE to a lone terminate word 0xc0000000; every stream ends with a state block
  whose second word is 0x0400e100, the end-of-scene state block (first word bit 29 set, second word
  0x0e022401) and the terminate; a draw adds its MTE state block (second word 0x0e0224nn, bits 25
  and 17 set) and, before its index list, a block that loads the vertex program's constants
  (0x0800e1nn or 0x0c00e1nn, bit 8 set) when its state changed, and only an index list when nothing
  changed; state blocks' first words point into PDSVERTEX_CODEDATA, bit 28 is never set.
  *vdm; CAP; data: `render-state-variations`, `render-register-gaps`, `render-draws-frames-pb`,
  `isp-registers`, `isp-line-width`, `texture-textures`, `texture-samplers`, `texture-formats`,
  `texture-streams`, `usse-inputs`, `usse-gles1-programs`, `usse-shaders`, `ta-target-sizes`.*
- `E350` Of the 46 USSE forms still open (no passing simulator vector, or no semantics in the
  simulator), the closed GLES compilers and the closed driver's fixed programs use 14 across the 425
  distinct USSE programs of 595 captured runs: phas (form 8) in every program, emitpix1 in 223 and
  emitpix2 in 224 end-of-tile programs, the four vertex emits (emitmtest, emitmtevtx, emitvcbst,
  emitvcbvtx) in every vertex program, wdf in 93 programs, wop in 8, ptoff in one program every run
  holds, smlsi in 24 programs of the shader, input and GLES1 runs, atst8 and pcoeff only where a
  fragment is discarded or alpha-tested (atst8 also under the GLES1 alpha test), and the dual-issue
  form 64 only under GLES1 lighting; the other 32 open forms (among them smoa, smr, smbo, imo,
  setfc, moest, setm, depthf, ldr, str, idf, nop, emitpds, ba and the second phas forms) appear in
  no captured program.
  *usse; CAP; data: `render-state-variations`, `render-register-gaps`, `render-draws-frames-pb`,
  `isp-registers`, `isp-line-width`, `ta-target-sizes`, `texture-textures`, `texture-samplers`,
  `texture-formats`, `texture-streams`, `usse-shaders`, `usse-inputs`, `usse-gles1-programs`.*
- `E351` Every one of the 47 distinct vertex programs the closed GLES compilers emitted in the 595
  captured runs opens, past its leading phas and nop, with and.testtanz of two zero immediates into
  p0, then p0 ldad ... drc0 (a load that never runs), then wdf drc0; so do 27 of the 28 secondary
  programs and 11 of the 12 state-copy programs, and none of the 114 primary pixel programs or the
  225 end-of-render programs; the 93 programs with wdf are these 85 and 8 primary programs that wait
  after a texture sample, and the one vertex program with a second wdf (vs_texture) waits after its
  own texture sample.
  *usse; CAP; data: `render-state-variations`, `render-register-gaps`, `render-draws-frames-pb`,
  `isp-registers`, `isp-line-width`, `ta-target-sizes`, `texture-textures`, `texture-samplers`,
  `texture-formats`, `texture-streams`, `usse-shaders`, `usse-inputs`, `usse-gles1-programs`.*
- `E352` srvinit asks SGX_GETMISCINFO once, for the driver's revision (eRequest 2), before its init
  connection; whether the answer is left as srvinit passed the struct, all zeros, a plausible one
  (DDK 1.7.17, build 862890, build options 0x60218) or one with every build option flipped, srvinit
  makes the same 57 bridge calls in the same order with the same sizes, returns 0, and its init info
  (2068 bytes) and all 15 buffers are byte-identical.
  *firmware; CAP; data: `firmware-miscinfo-replies`.*
- `E353` The EDM itself clears InterruptFlags and InterruptClearFlags: its POWER handler clears bit
  1 of both, and the routine at instructions 0x1c4-0x599, which tests InterruptClearFlags bit 0,
  clears bit 0 of both after zeroing its TA/3D control words and setting the kernel CCB's read
  offset to the write offset; the same routine sets InterruptFlags bit 0 after counting a lockup and
  bit 1 when the active-power countdown reaches zero, each followed by a SW_EVENT write; no other
  resolved EDM access writes either word.
  *edm; RE; data: `firmware-edm-dataflow-11`.*
- `E354` With recovery held, a debugfs reset written while the hold is set recovers the held job
  with blame: a render faulting on its unmapped stream page fails once with -EIO and a pixel task
  hung on a fetch it never issued once with -ETIMEDOUT, after one reset each and with no second
  fault, hang or cleanup failure; while held the driver logs two lines (the detector's recovering
  line and the hold's warning) and nothing more until the reset, over 11.2 s and 3.1 s; one run.
  *render; HW, DDK; data: `render-held-reset`.*
- `E355` While a faulting render's recovery is held, another render context's cleanup that the
  stopped EDM does not answer fails (ret -110) and logs its warning, but no reset follows: the EDM
  still answers no GETMISCINFO, the bus fault stays in the status registers and seven kernel memory
  releases wait on the deferred list; the debugfs reset that ends the hold resets once, fails the
  held render with -EIO, empties the deferred list, and the faulted context's own cleanup then
  completes; one run.
  *render; HW, DDK; data: `render-held-reset`.*
- `E356` Render jobs queued on other contexts while a fault is held run again after the reset that
  ends the hold and end with the RT data set's executed count equal to the kernel's pending count: 0
  and 0 for a render without render flag bit 10, then 1, 2 and 3 for a three-kick scene whose first
  kick ran again; every cleanup completes and each round resets once; two rounds, and the same jobs
  without a hold as control.
  *render; HW, DDK; data: `render-replay-pending`.*
- `E357` CR_EVENT_STATUS2 bit 7 (TRIG_TA) sets 0.1 to 0.2 ms after the TA kick's PB load in a TA
  that hangs (VDM state word 1 bits 15:13 = 0) and in one that faults on its stream page, and bit 6
  (TRIG_3D) about 0.1 ms after the pixel units start in a fill whose pixel program loops 128 or more
  times over eight instructions, not with 16; neither sets in any render of one to three renders
  from 64x64 to 256x256, a 1024x768 partial render, a fill or a copy; once set each stays through
  later jobs until a reset; a fault raises no other bit of CR_EVENT_STATUS or CR_EVENT_STATUS2.
  *platform; HW, infer; data: `platform-event-timelines`, `platform-event-trigger`.*
- `E358` Sampled through one to three renders on a context at 64x64, 128x128 and 256x256 and a
  1024x768 render with partial renders, the high halves of CR_DPM_TA_ALLOC_FREE_LIST_STATUS2
  (0x0710) and CR_DPM_3D_FREE_LIST_STATUS2 (0x071c) read 0 in every job; CR_DPM_REG_0748 reads 0x1f
  idle, clears bit 4 while the TA takes pages, bit 0 briefly at a TA's PB load, bit 1 for about 10
  us before each page the 3D frees and bit 3 at the out-of-memory event; 0x072c reads 0x10001 from
  the TA's first page to the 3D's last free; TA/3D control block dword 36 reads 0 after the partial
  renders; two runs.
  *dpm; HW, infer; data: `platform-event-timelines`.*
- `E359` With the counter group set through SETHWPERFSTATUS, CR_HWPERF_COUNTER0 to 8 count by group
  (groups 7 and 9 to 15 count nothing in seven jobs; group 8 moves 0x0044, 0x0048 and 0x0050 in all
  seven, 0x4c889, 0x66e6 and 0x49e in the 64x64 triangle), and in group 0 COUNTER3 (0x0050) counts
  the pixels a job shades exactly (0x1000 at 64x64, 0x4000 at 128x128, 0x800 for a 64x32 fill);
  whatever the group, 0x0e84 counts renders, 0x0e88 jobs, 0x0e8c rises only with renders, 0x0e90
  with the pixels and the pixel program's length (eight times for eight times the loop) and 0x0eb8
  is the sum of 0x0e8c and 0x0e90; one run.
  *platform; HW, infer; data: `platform-hwperf-groups`.*
- `E360` TA/3D control block dword 49 is the bus interface directory list the EDM last gave a render
  context: the k-th context's first kick after a reset writes its page directory into
  CR_BIF_DIR_LIST_BASEk (k 1 to 14) or, at the 15th, CR_BIF_DIR_LIST_BASE0, and dword 49 reads k mod
  15; list 15 keeps the EDM's own directory; a 16th live context takes list 1 from the first, whose
  next kick takes list 2, and all 30 contexts of two runs (14 and 16 alive at once) render their
  second render exactly; one run.
  *render; HW, RE, infer; data: `render-context-lists`.*
- `E361` Render context dword 7 set to 0xdeadbeef or to the background object's address at the first
  kick changes nothing in a render, a scene of three kicks, a 1024x768 render that overflows its
  parameter buffer or the context's cleanup, and the word keeps the value through later kicks;
  render flag bit 0 hangs a render after its TA: held, the 3D has taken its render details, the PB
  descriptor holds the TA's two pages, the executed count is 0 against the kernel's pending 1, the
  RT data state reads 0x20; two runs and one.
  *render; HW, infer; data: `render-word-pokes`.*
- `E362` With the PB descriptor's flag bit 0 set at a render's first kick the EDM's write to the
  render context's page faults (CR_BIF_FAULT on page 0x32411000, the requester of its own writes)
  under the context's directory, where the kernel's memory is read-only, and the job fails; with
  CR_DPM_REG_074C bit 8 (0x100, and 0x1ff) on contexts for 4096x4096 and 1024x768 targets the render
  is exact and the TA data is the control's to the dword; two runs and one.
  *dpm; HW, infer; data: `render-word-pokes`.*
- `E363` The background object's first PDS word with bit 27 or 28 flipped faults at page 0x0001f000
  and with bit 30 or 31 at page 0x2e001000 (the pixel PDS heap's second page), on 64x32 and 128x128
  alike; on 64x32 bits 27 and 28 leave 11 to 14 whole rows and the rest of the first 16 rows at half
  width, bits 30 and 31 rows 0 to 15 whole and rows 16 to 31 at half width (32 of 64 pixels, 16 half
  rows), and on 128x128 no row; the second word's bits 27 and 31 and the third's bit 27 change
  nothing, its bit 31 faults at the same pixel-heap page with no row rendered; three runs and one.
  *render; HW, infer; data: `render-bg-pds-words`.*
- `E364` In the closed driver's 114 captured primary pixel programs with a texture fetch, DOUTU1 bit
  24 is set exactly when one of their douti iterates an attribute into the primary attribute
  registers (DOUTI0 source field 16:11 below 36: the vertex colour 32 or a coordinate set 1 to 3),
  21 of 21, and every USSE program those 21 start reads that iterated register; in the 93 without it
  every douti has source 36, which writes no attribute register, and their programs read only
  fetched texels.
  *pds; CAP, infer; data: `render-state-variations`, `render-register-gaps`,
  `render-draws-frames-pb`, `isp-registers`, `isp-line-width`, `texture-textures`,
  `texture-samplers`, `texture-formats`, `texture-streams`, `usse-inputs`, `usse-gles1-programs`,
  `usse-shaders`, `ta-target-sizes`.*
- `E365` With CR_CLKGATECTL2 as the boot leaves it, CR_CLKGATESTATUS reads 0x20 idle and 0x000ccfa0
  at every EDM tick, 0x000fffa7 and 0x000fffa4 while a fill runs a pixel loop of six fmads or of six
  integer multiply-adds alike, 0x00000078, 0x000ccff8, 0x000fffa7, 0x000fffff and, in one 256x256
  render of three, 0x000fffa4 through renders; bits 20 and above never read 1; one run of each loop
  twice.
  *platform; HW; data: `platform-event-timelines`, `platform-event-trigger`.*
- `E366` A mov to destination bank 6 with neither index bit set (numbers 0, 4, 8, 16, 64 and 124,
  printed i.) changes no temporary r0-r25, internal register i0-i2, index register or pixel o0 a
  fill reads back (one run of each number), and no primary attribute pa0-pa15 or secondary attribute
  sa0-sa31 (read for numbers 0, 4 and 64 only, three runs each); the marker appears in none of the
  stored o0-o7; numbers 1, 2 and 3 write i.l, i.h (from the low half) and both; no other number
  whose low two bits are 0 was run.
  *usse; HW; data: `usse-destination-bank6`, `usse-destination-bank6-moved`.*
- `E367` idiv's repeat count is enc[47:44] + 1 (1 to 16; enc[47], outside every field before, is its
  high bit): iteration k divides src1 + k by src2 + k, writes the quotient to dst + k and the
  remainder to dst + k + 1, which the next iteration's quotient overwrites, a divisor 0 giving
  0xffffffff for both; the 21 cases in which no iteration reads a register an earlier one writes
  match this exactly, and in the 9 in which one does every such read saw what an iteration ten or
  more before wrote and the old value where the writer ran nine or fewer iterations before.
  *usse; HW; data: `usse-idiv-enc47`, `usse-idiv-enc47-repeat`.*
- `E368` A word of class 2, 22 or 26 that no form decodes ends the program when its enc[50] is set:
  of the nine 11.7 words, each with enc[50] set (as run or flipped) lost the sixteen stores after it
  and the pixel's own final write, the pixel keeping what the job before left (nine of nine), and
  each with it clear kept them (six) or hung the job (three); flipping any other bit of enc[49:0] of
  a class 2 and a class 26 word keeps the end, and of a class 22 word with enc[50] clear, bits 32,
  33 and 51 remove the pixels it writes 0 (3 or 4 in the base) and bits 44, 45 and 46 raise them to
  7, 12 and 15, while the other bits give 2 to 6 (one run, so the 3-or-4 spread of the base is not
  told from the flips' by repeats).
  *usse; HW, infer; data: `usse-encoding-gaps-end`.*
- `E369` The MOE sequences that faulted fault through the probe template's own stores, not through
  moest: the three moest-state sequences completed in all 30 of ten interleaved runs, with mixed
  pixels; smbo #1, #0, #0, #0 before the moest selectors faulted one run of three, and smoa mirror
  on source 0 (or on all four operands) before a repeated mov faulted every run (6 of 6); each fault
  is a bus interface fault at an address outside the scratch; smoa #-1, #-2, #511, #-512 alone, each
  moest selector alone after it and each operand's offset alone complete.
  *usse; HW, infer; data: `usse-moe-faults`.*
- `E370` MOE state set in one job is not in force in the next: after a job whose program runs smbo
  #1, #0, #0, #0 (or smlsi with increments 2), the next job's mov r10, r1 (mov.repeat2 r10, r1)
  writes r10 (r10 and r11) as with no MOE instruction, in three runs of three; within its own job
  smbo's destination offset moves the final mov.end o0, r10 to o1, so the pixels keep the job
  before's o0.
  *usse; HW, infer; data: `usse-moe-state`.*
- `E371` A register written by mov, or, fmad, frcp or fexp reads as the result in the next
  instruction and at every distance up to 8 instructions, with or without .nosched on the writer:
  230 cases, every pixel the result.
  *usse; HW; data: `usse-hazards`.*
- `E372` g19 reads by the instruction that reads it, the same in every pixel of the fill: 0 through
  mov, 0x11 as source 1 or 2 of or and and, 0x1a as a store's source (each pixel storing to its own
  dword and loading it back), two runs each; g18 reads the same through mov, or and a store (0x10,
  0x12, 0x14 and 0x16, 512 pixels each), g23 through mov and a store (0 to 3, 64 pixels each), and
  g17 (0 to 3) and g20 (1) were read through a store only; g24 through mov only (0 to 3, 128 pixels
  each).
  *usse; HW, infer; data: `usse-g19`.*
- `E373` An output register a job does not write holds what the job before left in that instance's
  output buffer: a fill that never writes o0 reads 0xff203040 on 1432 pixels and 0xff00ff00 on 616,
  in the same pixel positions in ten runs, pieces of the baseline triangle's image (its 0xff00ff00
  triangle on its 0xff203040 background) laid out by tile; after a fill that writes 0x11223344 to o0
  the next fill's unwritten o0 and o1 read 0x11223344 in every pixel, three runs.
  *usse; HW, infer; data: `usse-leftover-o0`, `usse-destination-bank6`.*
- `E374` In the triangle's pixel program, on 64x64 and 128x128 targets, g16, g19 (through mov),
  g26-g31 and g40 read 0, g20 and g41 read 1, g42 0x3f800000 and g43 0xff000000 on every covered
  pixel, as in the 64x32 fill; g17, g18, g21-g25 and g39 vary from pixel to pixel in both (g39 takes
  0, 4, 8 and 12); two runs each.
  *usse; HW; data: `usse-globals`.*
- `E375` In a fill's pixel program, idf drc0 with mode pixelbe or the reserved modes 2 and 3
  followed by wdf drc0 hangs the job, with a plain or a .bypassl1 load after it, two runs of each
  (12 of 12); with bif every pixel loads back the dword it stored.
  *usse; HW; data: `usse-idf-modes`.*
- `E376` On the triangle's vertex program, incp 1, 2 or 3 on emitvcbvtx or on emitmtevtx draws the
  triangle as with 0 (1062 pixels, two runs each), and .cut on emitmtevtx hangs the job (two of
  two).
  *usse; HW; data: `usse-emit-flags`.*
- `E377` Below 65536 iterations a fill's loop time is linear in its count: 3.020 µs an iteration for
  8 instructions and 5.582 µs for 16 (1000 to 32000 iterations, 5 runs each, rms 0.4 and 1.2 ms), so
  0.3203 µs per instruction over the fill's 2048 instances, 127.8 cycles of the 399.0 MHz reference
  or 16.03 instances a cycle; at 60000 iterations (180 ms and more) our kernel declared 9 of 10 jobs
  hung.
  *usse; HW, infer; data: `usse-loop-short`.*
- `E378` With idiv's four-bit repeat count and bank 6's write to neither index register in the
  simulator, it matches 271 of the 340 scalar vectors of the 11.13 runs and stops on 69, none
  differing; over all the vectors 24,711 scalar vectors match (24,440 before), 1,112 are fitted, 755
  stop and none differs.
  *usse; HW; data: `vectors-usse-semantics`.*
- `E379` mov128 with bit 15 writes to both halves of its destination row the ds0 pair that the last
  mov32 or movs read from a data row (rows 0-23): row 4's pair in E261 is the one the template's
  last mov32 from a data row read (ds0[9]); with each of bits 23:16, 9, 7, 1 and 0 also set, bits
  23:16 and 1:0 together, source rows 0, 4 and 24 and destination ds[48] the same pair is written; a
  movs to mr or to douta from ds0[2] or ds0[6] names that pair instead, as does a mov32 from ds0[2],
  while a movs from the temporary pair ds0[50], ds0[51], a not of a temporary (ds0[48-55] or
  ds1[48-55]), a mov32 from ds1[9] and a mov64 from mr01 leave it; three runs of every case, and the
  same with another set of markers.
  *pds; HW; data: `pds-mov128-bit15`.*
- `E380` A store (stad) from pa0-pa7 or sa0-sa7 stores what a mov of the same register reads, in
  every one of 30 jobs: in a fill a mov to sa_n changes what pa_n and sa_n both read, a mov to pa_n
  changes neither, and an unwritten pa_n or sa_n reads the job's pixel colour (0x0da7a000,
  0x11110000, 0x33330000, 0x55550000 as the case's colour was), which E366's r1 marker was; the r
  and o stores store their registers; so a store takes pa and sa as its data source and E366's r1
  was the register's content, not a substitution.
  *usse; HW, infer; data: `usse-store-sources`.*
- `E381` In the triangle's primary pixel program, sixteen douta writes reached the USE task's sa
  registers in one job of thirteen: markers C to attributes 16-31 arrived in sa16-sa31 in their
  third run, with sa0-sa15 holding markers B of a job three jobs earlier; in the other twelve jobs
  sa0-sa31 held one of two sets of values that other jobs had left (one the sa of the fill probe run
  just before, with sa0 = 0x00000002 in place of its first value), and pa0-pa15 held values that
  differ from job to job.
  *pds; HW, infer; data: `pds-douta-primary`.*
- `E382` With a shader that names each pixel, EMIT2 bits 29:28 rotate the stored image by 90, 180
  and 270 degrees at 1, 2 and 3 (the pixel stored at (X, Y) of the 64x64 target is the one from (Y,
  63 - X), (63 - X, 63 - Y) and (63 - Y, X)), every one of the 1062 pixels in both runs, so E267's
  bit 28 is a rotation by 90 degrees, not a mirror; bit 31 scales by two (the pixel at (X, Y) is the
  one from (X/2, Y/2), after the rotation of bits 29:28 for 0x9-0xb, all 1728 named pixels); bits 30
  and 31:30 together store no named pixel; EMIT2 bits 6:0 are fit by an offset into the order in
  which a tile's pixels are read [infer], an offset of 1 reading the next pixel of the order x0, y0,
  x1, x2, x3, y1, y2 of each 16x8 block [infer] (1, 2, 4, 8 and 16 fit 928-1053 of about 1050
  pixels, 3 fits 1035; carries out of the block do not); counts above 0x80 (0x82-0xfe) store the
  image with 39 to 2742 pixels changed, mostly at the first places of each tile's order.
  *pbe; HW, infer; data: `pbe-emit-transforms`.*
- `E383` SIDEBAND bits 8:6 select the channel only in pack modes 8 and 7: in mode 8 (one byte a
  pixel) 0 stores alpha, 1 red, 2 green and 3 to 7 blue; in mode 7 (two bytes) 0 stores alpha and
  red and 1 to 7 green and blue; modes 15, 18 and 28 store green and blue and modes 24 and 25 blue
  whatever the field; two colours whose bytes all differ, every pixel; sideband bit 12 stores words
  of no colour in modes 0-6 (the same in both runs) and zeros in modes 7 and 8, and bit 11 faults
  the job in each of modes 0-8.
  *pbe; HW; data: `pbe-sideband-channels`.*
- `E384` pc.0 read sixteen times back to back after 0, 1, 2, 3, 4 and 8 leading words of 0 ((p0)
  movs mr, ds0[0], ...) is the reading instruction's index plus 3, the leading words counted as
  instructions, or 1 below at a pair of reads, in all 480 reads of 30 jobs (five runs each): with 1
  to 4 leading words one pair sits at instructions 24-25 (dwords 60-61) in 14 of 20 runs and one
  among the first four reads in 19; with none at 26-27 (two runs), 19-20 (two) or nowhere (one);
  with 8 at 35-36 in all five.
  *pds; HW; data: `pds-fetch-pc-pad`.*
- `E385` The low byte of the word that loads CR_REG_0400 is the threshold of the one-bit alpha of
  pack mode 4 (ARGB1555): with an alpha that varies over x, the stored alpha bit is set where the
  alpha is above the low byte and clear where it is below (low byte 0: set from 2 up; 0x40: clear to
  62, set from 66; 0x80: clear to 120, set from 132; 0xc0: clear to 188, set from 196; 0xff: clear
  everywhere), every triangle pixel in both runs; bits 8-11 change nothing in modes 0 and 4 and bits
  7:0 nothing in mode 0; bit 25 inverts the alpha in modes 4 and 5 (all 2048 dwords) and changes
  nothing in mode 8.
  *pbe; HW; data: `pbe-reg-0400-alpha`.*
- `E386` Two end-of-tile emits per tile hang the job on a 64x64 target (eight tiles) whatever
  SIDEBAND bit 9 on either emit, in both runs of each of three variants (6 hangs); on a one-tile
  target a double emit with bit 9 on both or on the first only completes and leaves every later job
  storing the tile of the job before it (the later single-emit and blank jobs of a sequence store a
  tile or none by turns, a blank job (EMIT2 count 0) included) until a hang's recovery reset; the
  campaign's check after the one-tile table found 2164 of 4096 pixels different from the one before
  it; with bit 9 on the second emit only, a job one or two later hangs (one in run 1, two in run 2).
  *pbe; HW, infer; data: `pbe-emit-twice`.*
- `E387` Pack mode 34 stores bits 30:20 of an IEEE single in bits 21:11, for the words found where
  2.0, 1.0, 0.5, 0.25 and 0.3 land, and for 0.5 + y/128 at 689 of the 704 pixels holding such a word
  in run 1 and 695 of 709 in run 2 (the others hold another row's word); mode 22 stores 3 in bits
  31:30 for 1.0 and 0x3ff in bits 19:10 for 2.0; but every pixel of a shader that writes o0-o3
  shows, in mode 0 as in 22 and 34, the value of o0 at some pixels and of another output register at
  others (mode 0: o0 at 981, o1 at 512 of the triangle's place), and outside the triangle's pixels
  the words differ from run to run, so which register each field of a pixel reads is not settled.
  *pbe; HW; data: `pbe-pack-floats-channels`, `pbe-pack-floats-ramps`.*
- `E388` Bits 17, 18 and 19 of the pixel-event program's data dword 2 add stray writes of 0x00000002
  (or 0x00000006) at the first pixel of 16x4 blocks: on the copy bit 17 changes 2-3 pixels in all 10
  runs, bit 19 1-2 in 7 of 10, bit 18 2 in 1 of 10 (none in 9); on the fill bit 18 changes 3-5
  pixels in 5 of 5; on the triangle bit 18 6-8 in 5 of 5 and bit 17 1-4 in 4 of 5 (the fifth
  faulted); bit 16 faults every triangle job and leaves the copy unchanged in 10 of 10.
  *pds; HW; data: `pds-pixel-event-word2`.*
- `E389` In the primary pixel program neither if0 nor if1 tests true on any pixel of a 64x64 render
  with the triangle drawn twice or five times over itself: every pixel of both flag cases equals the
  source-1 control (x + 0.5 where a flag held would be the source-0 control's), three runs each.
  *pds; HW; data: `pds-input-flags-overlap`.*
- `E390` A douta from the triangle's vertex PDS program does not reach the vertex task's sa
  registers: with each of twelve special reads passed by douta to sa[4 + ir0], the vertex shader
  stored sa4-sa6 = 0.75, -0.375, 1.0 (vertex data) and sa0-sa3 = 0x32400000, 0x00400000, 0,
  0x7e570000 in 34 of 36 jobs, whatever the read, as the earlier vertex-programs douta probe's
  single run did; two jobs (one mov32 ir0.1, one mov64 mr01 high) stored other values (0x2, 0x73,
  0x1000, 0x32411200, 1); so the specials of a vertex program were not read this way.
  *pds; HW; data: `pds-vertex-specials`.*
- `E391` A fill's secondary douta reaches sa0-sa31 at their own index and never sa32-sa63, whatever
  the secondary attribute size in the background object's dword 1 (bits 24:18 at 0, 1, 2, 4 and 8
  rows): sixteen markers to attributes 0-15 and to 16-31 arrive in all 20 jobs, to 32-47 and 48-63
  in none, and nowhere else, two runs.
  *pds; HW; data: `pds-attribute-room`.*
- `E392` The vertex-colour iteration cases of E133 (state words 13 = 0x83800, 16 = 5; shade models
  0, 1, 2) give their vertex colour at all 1062 triangle pixels in every one of 18 jobs, in the
  order 0, 1, 2, 2, 1, 0 three times: the group of about 300 pixels keeping the previous case's
  colour (E133) does not occur.
  *pds; HW; data: `pds-shade-order`.*
- `E393` With a douti that has no completion bit and no wait, pa0 never holds the iterated value at
  any of the 1062 pixels, whether the shader reads it at once or after 4, 16 or 64 nops, in 20 jobs;
  it holds 0 (888-973 pixels), 2 (72-139), 6 (8-25) and a few other values, while the same iteration
  with bit 29 and the wait gives the iterated x at every pixel (two runs).
  *pds; HW; data: `pds-no-wait`.*
- `E394` E130's grid16 probe (a 128x128 render, each 16x16 tile's end-of-tile task storing a slot)
  run five times: 57-61 of the 64 slots hold data each run (ir1 2 or 6 in their third dword, E130's
  rule), slots 0 and 1 are empty in all five, 1 to 5 others differ from run to run (13, 20, 22, 25,
  33, 46, 51, 52), and slots 64 and 768 hold only colour words in four of the runs, slot 768 holding
  data (ir0 0x1407, ir1 2) in the first.
  *pds; HW; data: `pds-tile-slots`.*
- `E395` PDS stores with no rwfence totalling 11, 13, 14, 15 and 17 dwords complete the job (total
  11 faulted in one of three runs, the others in none), totals of 1 dword (from ds1, and followed by
  nine nops) and of 10 (2 then 8) complete in all five runs each, and a total of 2 faults in every
  run, also with an rfence between the two stores; the kernel logged BIF status 0xd2000 at 0x10020
  for the faults of total 2 and 0x1002e for the total-11 one.
  *pds; HW; data: `pds-store-totals`.*
- `E396` CR_PDS_REG_0A78 at 0x00, 0x01, 0x08, 0x20, 0x2c and 0x3f does not change the time of a
  256x256 triangle render: the median of five runs, each the mean of the last five of six renders,
  lies between 67274 and 67469 us for every value (0.3 percent), in a shuffled order; one 0x01 run
  had two slow renders (73110, 74396 us), the only outlier.
  *pds; HW; data: `pds-reg-0a78-timing`.*
- `E397` T3 bits 7:0 offset the copy's texel read by two signed 4-bit counts, bits 3:0 in y and 7:4
  in x, clamped at the source's edge: at each of the 256 values every one of the 2048 pixels is the
  as-built image's texel at the offset place, and the 16 values run twice agree.
  *texture; HW; data: `texture-copy-followup`.*
- `E398` The copy draws its source only with the background tag's layer count (transfer word 0 bits
  30:25) at 1, as the library builds it: at 0, 2, 3, 31 and 63 every pixel is one colour (0xff6648dc
  over the every-value source), two runs; a 128x64 copy was rejected by the kernel (Invalid
  argument) and wrote no pixel, with or without word 7 bit 1 (CR_ISP_MSAA mode 2), so mode 2 on it
  was not measured.
  *transfer; HW; data: `texture-copy-followup`.*
- `E399` The colour-space words set 0 holds survive the driver's GPU reset (debugfs reset) and a 5 s
  idle: a YUYV copy that does not load set 0 gives, after the reset and after the idle, the same
  image as one that loads it, every pixel, two runs.
  *texture; HW; data: `texture-copy-followup`.*
- `E400` With mov128's bit 15 (lastpair) writing the ds0 pair the last mov32 or movs read from a
  data row, after the instructions E379 measured, the simulator matches 116 of the 169 vectors of
  the 11.14 PDS fill runs and stops on 52 (25 on the leading (p0) movs mr words of the fetch-pc
  probe, whose p0 it does not know, 27 on a movs to mr, an open port in a fill), one skipped (a
  store fault in one run of three), none differing; over all the vectors 1305 PDS vectors match and
  98 stop, where the coverage report before 11.14 had 1144 and 91 over the vectors then: the 116 new
  ones and the 45 mov128 bit 15 stops of E261's runs, now matching, and the USSE and pixel counts
  are unchanged (24711 matching, 1112 fitted, 755 stopping; 143 pixel vectors), none differing.
  *pds; HW; data: `vectors-pds-semantics`.*

### 2026-11-07

- `E401` None of the 161 sgx*defs.h headers of the openpvrsgx archive defines a register from 0x0780
  to 0x0880 (the nearest defined are EUR_CR_TIMER at 0x0144 and EUR_CR_USE_CODE_BASE_0 at 0x0a0c),
  so no public SGX header names 0x0810, 0x0814 or 0x0818; Linux's Rogue driver defines
  ROGUE_CR_MIPS_WRAPPER_CONFIG at 0x0810 and ROGUE_CR_MIPS_ADDR_REMAP1_CONFIG1 at 0x0818, each with
  a 64-bit mask (0x000001030F01FFFF and 0x00000000FFFFF001) on an 8-byte stride, where E122 found
  0x0810, 0x0814 and 0x0818 to implement bit 0, bits 16:0 and bits 10:0 as separate 4-byte
  registers.
  *platform; DDK; data: none.*
- `E402` With the kernel asking GETMISCINFO at the end of every boot of the firmware and clearing
  the answer when the firmware stops, DEV_QUERY reports the firmware's core 545, revision 0x1000d
  and DDK 1.7.17 build 862890 after the load and after a reset, in a build with the debug option and
  in one without it, and nothing before the load; during a debugfs reset GPU_INFO has SW_VALID clear
  from 1 ms after the reset is written until it returns (3619 of 3717 reads in the window); the EDM
  answers in 0.18 to 3.9 ms at the load and in 0.18 to 1.8 ms after a reset; one run of each.
  *edm; HW, DDK; data: none.*
- `E403` With 0x0810, 0x0814 and 0x0818 each narrowed (down to 0), no job's median time falls
  outside 0.81 to 1.21 of the init values' (inside the spread of the init runs), from a 64x32 fill
  to a 2048x2048 triangle, eight back-to-back renders and pixel loops of 9.6 to 62 ms, and no job
  faults or hangs (64 chained transfers all report ok; the tool prints no time for them); every
  output holds but a triangle with 0x0818 = 0x3ff (E404); one reset restored all three to their init
  values.
  *platform; HW; data: `platform-register-limits`, `platform-init-register-copy`,
  `platform-init-register-tri`.*
- `E404` With 0x0818 holding bit 8 and not bit 10 (0x100, 0x1ff, 0x3ff), a triangle render draws
  wrong pixels when the render before it ran under the same value with a target of another size,
  deterministically, the job reporting ok; with the init value 0x7ff, with any other of 32 values
  tried, with the register written between the two jobs, with one job after the write and with two
  of the same size, it draws exactly.
  *platform; HW; data: `platform-register-limits`, `platform-register-limits-scan`,
  `platform-register-limits-pairs`, `platform-register-limits-values`.*
- `E405` Of 24 values of 0x0818 (bits 10:8 in every combination, a low byte of 0x00, 0x7f or 0xff),
  exactly the six with bit 8 set and bit 10 clear (bit 9 either) make the second of two triangles of
  different sizes draw wrong, with the same count of wrong pixels in all three repeats (2439 of
  16384 for 96 then 128, 2155 of 9216 for 128 then 96); the other 18 draw exactly.
  *platform; HW; data: `platform-register-limits-combos`.*
- `E406` With ISP word 0 bit 26 or 27 (0x05d00200 or 0x09d00200), CR_REG_0148 (render details dword
  9) bit 0 and the state block's word 4 at 0x00030001 (PDS_SIZE 3, one data row), a shader writing
  o0 to o7 with a tag in each leaves o0 on its own pixel and o4 on other pixels (tags 1 and 5) and
  o1 to o3 (tags 2 to 4) on no pixel at all, in 27 of 27 jobs, where the plain job shows o1 to o3 on
  447 to 600 other pixels; with the data rows at 2 to 4 the pattern is tags 1, 3, 5 and 7 and at 5
  to 7 the job hangs; no single flip of 1797 jobs over PDS_SIZE, the VDM stream, the state block and
  20 render details words gives the setup's pattern, three give the tags 1, 3, 5, 7 pattern.
  *usse; HW; data: `usse-output-room`, `usse-output-room-vdm`, `usse-output-room-blk`,
  `usse-output-room-rd`, `usse-output-room-bit15`, `usse-output-room-isp0`,
  `usse-output-room-combos`, `usse-output-room-four`, `usse-output-room-seq`,
  `usse-output-room-rows`, `pbe-pack-floats-room`.*
- `E407` CR_TE_MTILE1 (0x0208) and CR_TE_MTILE2 (0x020c) take the TA command's te_mtile1 (ta:143)
  and te_mtile2 (ta:144) as poked (but for te_mtile1 bits 8 and 20 at 256x256 and bits 8 to 10 at
  1024x768, which do not take), and the render changes with them in three of three runs: at 256x256
  flipping te_mtile1 bit 12, 15 or 16 leaves 6144 to 16384 pixels wrong and bit 13 or 31 faults the
  job, while te_mtile1 bit 24 and te_mtile2 bit 0 draw the target exactly with a register value that
  is not the rule's; at 1024x768 te_mtile1 bits 0, 1, 2 and 5 and te_mtile2 bits 0 and 1 leave
  pixels wrong and te_mtile2 bits 2 and 8 fault the job.
  *ta; HW; data: `ta-te-words`, `ta-te-words-repeat`.*
- `E408` With CR_ISP_CTL (render details dword 3, rd:3) at the closed driver's 0xf0000 (bit 8 clear)
  our triangle job leaves 36352 of 65536 pixels at 256x256 and 542720 of 786432 at 1024x768 as the
  tool's sentinel, three runs each with the same count, and none at 64x64; 0x04c4 (rd:18) at the
  closed driver's 0x2046400 changes neither the image nor the time at any of the three sizes; the
  job time rises with the number of pokes, not with the value.
  *render; HW; data: `ta-te-words`.*
- `E409` CR_DPM_STATE_CONTEXT_ID (0x0630) reads 0 at every one of 2.96 million samples taken in 15
  runs of one to three 1024x768 renders, so it cannot show the 3D's DPM slot; CR_TE_PSG (0x0218)
  drops from 0x01400000 to 0x00400000 for 8 to 25 microseconds at each render's kick, and with the
  command's bit 21 set it reads 0x01600000 before the first dip and shows one dip across two
  renders.
  *ta; HW; data: `ta-te-words`.*
- `E410` On the one-triangle job, the render details dwords 76 and 77 (the background object's
  second and third words) at every single-bit flip, 0 and 0xffffffff change nothing (68 of 68 runs,
  the image of the control); dword 69 (its first word, 0x32411214) with 11 of its 32 bits flipped
  draws the same wrong image (2860 of 4096 pixels), with the other 21 fails the job (19 faults and 2
  hangs), and with 0 or 0xffffffff faults it.
  *isp; HW; data: `isp-bg-words`.*
- `E411` In a render with depth and stencil stored (CR_ISP_ZLSCTL 0x17100c), clearing bit 2 stores
  nothing, clearing bit 17 stops the stencil store, clearing bit 18 stops the depth store, setting
  bit 19 stores the depth as -1.0, bit 24 as 0x00ffffff and bit 25 as 0xffffffff on two pages, with
  the same stored pages in both of two runs for all 32 flips; with bit 1 set, bit 13 drops the
  stencil store and bit 14 stores the loaded depth, and neither does anything without bit 1, in two
  runs each.
  *zls; HW; data: `zls-control-bits`.*
- `E412` CR_REG_0148 (render details dword 9) at 0 and at 1 gives the same image, the same stored
  pages and a time within the spread in a render with depth and stencil stored, in 4x multisampled
  renders in modes 1 and 2, in a 1024x768 render and in a 1024x768 render that overflows the
  parameter buffer at 0x24 and 0x30 pages (the same wrong-pixel count each), three runs each.
  *render; HW; data: `render-reg-0148-jobs`, `render-reg-0148-partial`.*
- `E413` Jobs of the one-triangle library job with VDM state word 1 bits 11:9 = 7 hang exactly when
  the previous such job completed and complete when it hung: 55 of 55 consecutive such jobs
  alternate, with or without the pixel readback, with the unpoked control between them, in series of
  ten and in mixed series; the control itself never hangs (0 of 35), bits 11:9 = 3 and 5 hang 3 of
  20 and 5 of 20 jobs.
  *vdm; HW; data: `vdm-state1-hang`, `vdm-state1-hang-seq`.*
- `E414` With the index list's first trailing word at 0xf0000000 | k on the five-copy job (15
  indices), the TA's object keeps floor((16 - k) / 3) of the five triangles, the leading ones, for k
  = 0 to 6 and none for k = 16, 256 and 4096, in two runs each; bit 24 alone or with 0xf0000000
  keeps three and sets bit 15 in the first two primitive-list entries; bits 25 to 27 alone or with
  0xf0000000, and bits 31:28 at 0xf, 0xd and 0x7 with a vertex task of 16 and of 14 vertices, change
  nothing; topology 1 (line) hangs the job and 2 (point) writes no object.
  *vdm; HW; data: `vdm-index-trailing`.*
- `E415` Under CR_ISP_MSAA modes 1 and 2 a 10-pixel triangle placed in each of the nine 16x16 tiles
  of a 64x64 target is drawn only in the first and third tile columns with the TE anti-aliasing bits
  clear and only in the middle column with them set (nine of nine cases each, three triangle phases
  and three rows), each drawn tile with the TE bits clear landing 4 pixels right of its place (x)
  and at its place (mode 1) or 4 pixels below (mode 2); with them set the middle triangle is wider
  and lies left of its tile.
  *isp; HW; data: `isp-msaa-tiles`.*
- `E416` ISP word 0 bit 28 hangs a render in CR_ISP_MSAA mode 1 and mode 2 in 8 of 8 jobs whatever
  0x0520 holds (0 or 0xeaa26e26), and single-sampled it widens a horizontal-edge right triangle only
  at k = 6 (45 to 64 pixels, not at k = 0 and 12) with the same counts at 0x0520 = 0 and 0x88;
  CR_ISP_REG_04DC with bit 1 set hangs the punch-through pass in 24 of 24 jobs, whether the shader
  only discards, always fails, or uses pcoeff alone, and bit 1 clear completes all of them (12 of
  12); the punch-through pass with pcoeff and the source-34 iteration draws the same five times, and
  without that iteration its kept pixels differ from run to run (4 to 5 outcomes in 5 runs, with and
  without pcoeff).
  *isp; HW; data: `isp-bit28-modes`, `isp-punch-through-repeat`.*
- `E417` In the triangle's opaque pass a shader that stores o0 unchanged gives the previous job's
  colour on 390 to 450 of the triangle's 1062 pixels at 64x64 after a job of one constant colour and
  on 0 to 336 of 2403 at 96x96 and 0 to 183 of 4284 at 128x128, the rest the background, and the
  counts repeat (426 in four of seven pass-through jobs at 64x64); at 64x64 a pass-through job after
  a pass-through job keeps the colour, at 96x96 and 128x128 it shows it on 0 to 183 pixels (none in
  three of six).
  *isp; HW; data: `isp-o0-start`.*
- `E418` Plane 0's held clip result survives a job that hangs and the reset after it: with fdpc
  having put every vertex outside (a job drew nothing) the next jobs without fdpc were removed
  before the hang and after it (2 of 2 runs), and with fdpc having put them inside the next jobs
  drew before and after the hang, with the distance dwords at -1 and +1 changing nothing (2 of 2
  runs each); fdpc with the vertices inside cleared the held outside result (2 of 2).
  *mte; HW; data: `mte-plane-reset`.*
- `E419` With the vertex shader of the perspective probes (two coordinate sets, w = x + 2) and a
  texture-and-iterate pixel program, OUTSEL 0x63000 and 0x61000 give one object (three dwords a
  vertex with the 1/w, format 0x00040303) and 0x62000 and 0x60000 another (two dwords a vertex,
  0x00000202), and all four give the same image, whose iterated value fits an affine interpolation
  of the vertex values on all 1062 pixels (maximum error 1.7e-16) and not a perspective-correct one,
  in two of two runs.
  *mte; HW; data: `mte-outsel-persp`.*
- `E420` With DOUTI0 bits 23:22 = 3 the pixel shader reads pa3 = 1.0 on 1038 to 1062 of the
  triangle's 1062 pixels and a texel-valued dword (0xd0......) in pa4 on all 1062, in ten of ten
  runs; the exceptions in pa3 (up to 24 pixels with other values) came in the first runs after a
  baseline job.
  *pds; HW; data: `pds-douti-four`.*
- `E421` A movs to doutc in the triangle's primary pixel program faults the job in 8 of 8 jobs with
  BIF status 0xd0400 at 0x1f031 (once 0x1f034) whichever of its four words holds the scratch
  buffer's placeholder 0x5CAF0000, while the control completes.
  *pds; HW; data: `pds-doutc-address`.*
- `E422` In seven hung pixel-task jobs (five with recovery held, two without) the render memory dump
  holds the object in the parameter buffer every time, and the TA data holds 71 non-zero dwords in
  the five held dumps and none in the two unheld ones; the three held VDM state hangs have no object
  at the start of the buffer; the object E186 found missing is not reproduced.
  *render; HW; data: `render-hold-hang-repeat`.*
- `E423` The simulator is unchanged by 11.15 and still matches every vector it models: over all the
  vectors 24711 scalar vectors match, 1112 are fitted, 755 stop and none differs, 143 pixel vectors
  match with 18 stopping and none differing, and the PDS vectors match, as after 11.14 (E400).
  *usse; HW; data: none.*
- `E424` Flipping bit 8 of the RT data's state word (kernel poke rtds:19, dword 13 of the RT data)
  before the first kick makes CR_TE_PSG read 0x01600000 after the kick, and the TA data holds the
  same bytes as with the TA command's te_psg at 0x01600000 (hash equal in 3 of 3 runs at 64x64 and
  at 1024x768; 8 and 1536 bytes differ from the control): one region header marked each; the images
  are the controls' in all 48 jobs and CR_DPM_STATE_CONTEXT_ID read 0 throughout.
  *ta; HW, DDK, infer; data: `ta-psg-state`.*
- `E425` With the copy's tool printing its addresses and a counting page before the source
  (0xB0000000 | dword), the source of the 64x32 copy lies at 0x3e002000 (the page before it at
  0x3e001000), its destination at 0x3e005000 (0x3e006000 with the source moved 4 rows down,
  0x3e004000 at 64x16), and T2 flipped by 0x2000, 0x3000 and 0x4000 reads 0x3e000000 (first dword
  0x04000004, then zeros and a few other dwords), the counting page and the destination's second
  page: 28 of the 30 cases identical pixel for pixel in 3 of 3 runs and the other 2 (64x16, T2
  flipped by 0x4000) faulting in 3 of 3.
  *texture; HW; data: `texture-copy-addresses`.*
- `E426` With a source row whose weighted sum S sits at cut x 1024 + k for every even k from -16 to
  16 (102 cases, twice), the band of the luma key starts at least 16 below the low cut for the cuts
  119, 120 and 122 (all of the 8 sums below the cut inside the band, 2 of 2 runs, three cuts), and
  at the high cut five pixels with S 1000 to 1016 above cut x 1024 are outside the band where others
  up to 1016 are inside, so the comparison is not on S alone.
  *texture; HW, infer; data: `texture-luma-ramp`.*
- `E427` In a stream of two objects, each with its own state task, flipping the fields of the second
  state word (VDM word 9) while the first block stays as built gives the same completions and hangs
  as flipping the first block's (word 1) for bits 15:13 (0, 5, 6 and 7 hang in 16 of 16 jobs, 2, 3
  and 4 complete in 12 of 12) and for bits 11:9 at 3 and 4 (8 of 8 complete); bits 11:9 at 0 in the
  second block draws the first object only (2 of 2), at 1 hangs in the second block and completes in
  the first; bit 8 changes nothing in either.
  *vdm; HW, infer; data: `vdm-state2-fields`.*
- `E428` A DOUTU word with only bit 21 set (the offset's bits 20:19 in word bits 21:20, CBASE 0)
  starts a USE program placed 1 MiB above the code heap's base, and one with CBASE 8 starts a
  program placed 4 MiB above it, in 3 of 3 runs each, while the bit-21 form at 4 MiB (all zero)
  starts the program at the base: the 18 program-counter bits reach bit 21 of the word and CBASE
  adds the offset's bits 22:19.
  *pds; HW, infer; data: `pds-doutu-place`.*
- `E429` In the room setup of E406, pack mode 34 stores bits 30:20 of o3's single in bits 21:11 on
  537 pixels for each of 0.75, 1.0, 1.5, 2.0 and 4.0 (3 of 3 runs: 0x001fa304, 0x001fc304,
  0x001fe304, 0x00200304, 0x00204304), and mode 22 sets the field of bits 19:10 to 0x3ff
  (0x088ffc00) on 851 pixels at o3 of 1.0, 2.0 and 4.0 (549 to 567 at 0.75 and in two ramps); o2
  alone reaches a few pixels only (8 in mode 34, 12 in mode 22).
  *pbe; HW, infer; data: `pbe-pack-floats-o23`.*
- `E430` After a douti with no wait, none of pa0 to pa15 holds the waited iteration's pa0 at its
  pixel beyond chance (0 to 25 of 1062 pixels per register, three runs), pa4, pa8 and pa12 hold the
  target's pre-fill 0xdeadbeef on 258 to 288 pixels in all 9 runs, and the other registers hold 0,
  2, 6, 0x40000000, 0x3f800000 and other floats that differ between runs on 7 to 54 percent of the
  pixels, depending on the register and the pair of runs.
  *pds; HW, infer; data: `pds-no-wait-where`.*
- `E431` After a reset CR_EVENT_STATUS2 bit 6 (0x40) is set by a fill whose pixel program loops 55
  or 56 iterations (eight instructions each) in 3 of 3 runs, 54 in 2 of 3, and never by 53 or fewer
  (3 of 3 runs each, 16 to 53 iterations tried), and always by 56 to 136 iterations in steps of 8.
  *edm; HW, infer; data: `platform-event-steps`, `platform-event-fine`.*
- `E432` The 24 cases of the three sampler-cache probes (a store to a sampled texel, with each fence
  and cache operation between) give the same results with the texture and its buffer in the texture
  heap (0xf0000000) as in the general heap, in 3 of 3 runs each (72 of 72 jobs).
  *texture; HW; data: `texture-sampler-cache-texheap`.*
- `E433` With the TA command's word 23 (the background object's first PDS word) bit 27 or 28
  flipped, mapping the page 0x1f000 it fetches from (filled with 0xd1d1d1d1, 0 or 0xffffffff) turns
  the fault into a hang with 512 pixels changed where the unmapped job faults with 1024 to 1184 (3
  of 3 runs, each fill); with bit 30 or 31 flipped, mapping the pixel PDS heap's second page changes
  nothing (fault, 512 pixels at 64x32, 3 of 3 runs, each fill).
  *render; HW, infer; data: `render-bg-pds-map`.*
- `E434` Under HWPerf group 0 register 0x0060 counts 3, 15, 45 and 126 for the triangle probe with
  1, 5, 15 and 42 triangles (three vertices each) and group 1's 0x0050 counts the same, group 0's
  0x004c counts 7 a triangle for 1 to 15 triangles and 304 for 42, and 0x0e84 (renders) is 1 for
  each triangle job in all 16 groups; the same in 3 of 3 runs of the table (48 group-runs), with the
  fills of 128x32 and 256x16 and the 128x32 copy run at strides equal to their widths.
  *platform; HW, infer; data: `platform-hwperf-vary`.*
- `E435` With render flag bit 0 and debugfs hold_recovery set, the job holds in its hang with
  CR_EVENT_STATUS (0x012c) gaining bit 11 and 0x0748 ending at 0x1d in 3 of 3 runs; with five
  registers sampled instead of 118 (five runs) 0x0218 dips in 2 of 5 held jobs and in 4 of 5 unpoked
  ones, so the TA kick is not absent from the held job.
  *render; HW; data: `render-flag-bit0-timeline`, `render-flag-bit0-dense`.*
- `E436` In a textured primary whose program iterates an attribute (a coordinate set) into the
  primary attributes (DOUTI0 0x20000800: source 1, completion bit 29) and then fetches a texture,
  pa0 (the attribute) and pa1 (the texel) are the same image at every pixel in all three runs with
  DOUTU1 bits 24 and 25 set and with bit 25 alone (the fetch wait), and with bit 24 alone or neither
  bit pa0 and pa1 change from run to run in all three runs; bit 24 with a douti that lacks the
  completion bit hangs the job (24 of 24 jobs, bit 25 also set or not), while bit 25 alone gives the
  same pa0 and pa1 images with or without the completion bit.
  *pds; HW, infer; data: `pds-iter-wait-textured`.*
- `E437` A douti with DOUTI0 0x20400000 (source 0, components bits 23:22 at 1, completion bit 29)
  under DOUTU1 bit 24 writes the pixel's x + 0.5 to pa0 and its y + 0.5 to pa1 at all 1062 triangle
  pixels of the 64x64 job in three runs of each, and pa2 holds none of them (0 of 1062).
  *pds; HW; data: `dpm-partial-reload-pos`.*
- `E438` In 66 jobs of the triangle and copies of it (3 to 1500 vertices) on a 4096x4096 and a
  1024x768 target with parameter buffers of 0x422 to 0x23 pages, the high halves of
  CR_DPM_TA_ALLOC_FREE_LIST_STATUS2 (0x0710) and CR_DPM_3D_FREE_LIST_STATUS2 (0x071c) read 0 after
  all 42 jobs that completed or overflowed (their low halves 1 to 0x241), TA3DCtl dword 36 reads 2
  and 3 after the 4096x4096 jobs of 900 and 1500 vertices in 0x422 pages (global list of 4 and 5
  pages, three runs each) and 1 after the 1024x768 job of 1500 vertices in 0x23 pages (one page),
  and 0 after the other overflows, and all 24 jobs of 300 or more vertices at 4096x4096 in 0x40 or
  0x23 pages or 900 or more in 0x100 pages hang.
  *dpm; HW, infer; data: `dpm-partial-wide`.*
- `E439` A 4x render of our stack (CR_ISP_MSAA mode 2, the closed driver's TE words) through our
  end-of-tile task with the PBE words and sidebands the closed driver hands it (a 64x64 rectangle,
  pitch 64, sideband 0x200 or 0x2200) writes all 4096 pixels of the 64x64 target with 1248 triangle
  and 2848 background pixels and no other colour, the same in three runs of each of the 12 probes
  (36 jobs), with bit 48 of either emit set giving the same image; sideband 0x2200 (bit 13)
  rearranges the pixels of the single-sampled and the 4x image without changing their counts; a
  64x64 rectangle on a 128x128 target writes 4096 pixels and leaves 12288 unwritten.
  *isp; HW, infer; data: `isp-msaa-pbe`.*
- `E440` In a two-object stream whose second state block's primary pixel PDS program writes a
  constant (0xff00ff00, douta to sa0) for a shader that writes sa0 as the colour, the constant
  reaches 24 to 270 of the 978 non-background pixels in the 3 control runs (138, 270 and 24; the
  others read 2, 6 and other leftovers) and 24 to 270 pixels with every field of either state word
  flipped (bit 8, bits 11:9 at 1, 3 and 4, bits 15:13 at 2, 3 and 4: 42 jobs of which 37 complete),
  so no field changes the load beyond that spread; bits 11:9 at 0 in the second block remove the
  second object (3 of 3 runs, the first object's 1098 pixels showing), in the first block they leave
  398 green pixels (3 of 3); bits 11:9 at 1 hang in the second block (3 of 3) and at 4 hang in one
  of three runs of each block.
  *vdm; HW, infer; data: `vdm-state2-consts`.*
- `E441` On a 128x128 twiddled chain of eight levels read at whole LODs 1 to 9, T0 bits 20:17 at 1
  to 14 give level = min(round_half_up(LOD), maximum, 7) in 84 of 84 reads (the 14 reads of a
  maximum of 8 to 14 at LOD 8 and 9 all read level 7, the 1x1 level), and 0 and 15 read level 0 at
  every LOD (6 of 6 each); bits 26:21 at all 64 values and LOD 5 and 7 give level = max(0,
  min(round_half_up(LOD + (value - 63) / 8), 7)) in 128 of 128 reads; with T0 bit 9 (MIPFILTER) set
  the result is the channel-wise linear blend of the texels read at levels floor(LOD + bias) and the
  next, by the fraction of LOD + bias, byte for byte in 15 of 15 cases (bias values 0x3f, 0x3b and
  0x37, LOD 1.25 to 7.5), the same in three runs.
  *texture; HW, infer; data: `texture-mip8-fields`.*
- `E442` A background object whose pixel shader fetches the render target itself at the pixel's
  position (the target as a strided ARGB8888 texture, the position from a douti of source 0 with two
  components) gives all of the triangle's pixels, 4422528 of 4422528 as a count, of the 4096x4096
  job that overflows a 0x100-page parameter buffer, in three of three runs, where the library's
  background gives 987008 of them (three of three); at 1024x768 in 0x23 pages the image is exact
  with either background (207456 triangle pixels, three runs each); where nothing was stored the
  reload shows the target's 0xdeadbeef pre-fill (578976 and 12354688 pixels), also in jobs that do
  not overflow.
  *dpm; HW, infer; data: `dpm-partial-reload`, `dpm-partial-reload-pos`.*
- `E443` In timelines of the DPM registers 0x0700 to 0x0750 through 12 renders of the triangle and
  copies of it at 4096x4096 (3, 900 and 1500 vertices in 0x422 pages, 300 in 0x100, three runs
  each), the high halves of 0x0710 and 0x071c are 0 in every sample of all 12 runs, 0x072c reaches
  0x10001 with 3 vertices, 0x40004 with 900 (three runs) and 0x50005 with 1500 (three runs) and
  0x20002 with 300 in 0x100 pages (three runs), and 0x0748 reads 0xb, with bit 2 clear, in 4 of the
  12 runs (the three runs of 300 vertices in 0x100 pages and one of 900 in 0x422 pages) and never in
  the other 8.
  *dpm; HW, infer; data: `dpm-partial-wide-timelines`.*
- `E444` With a bus-interface fault held and the host event enables written through debugfs kregnow,
  the host interrupts that come with no SW_EVENT are those of CR_EVENT_STATUS bit 29 and
  CR_EVENT_STATUS2 bit 10, which an idle GPU has set too, of bit 7 after a TA fault (status2 0x480),
  and of bit 6 after a background program's fetch fault (0x440); the EDM's write to a read-only page
  leaves status2 at the idle 0x400 and sets no further bit; the fault itself raises no host
  interrupt while only the EDM's event is enabled (14 held faults: five of the TA read and of the
  PDS fetch, four of the EDM write; and an idle control).
  *edm; HW, infer; data: `edm-host-events`.*
- `E445` With CR_CLKGATECTL2 written through debugfs kregnow, each of seven of its two-bit fields
  (bits 13:12 and 21:20, the MADD0 and MADD1 fields of the GPL kernel's header, and bits 15:14,
  17:16, 19:18, 23:22 and 1:0) at 0, 1 and 3 in turn with the others as the boot leaves them (2),
  CR_CLKGATESTATUS reads the same five values 0x20, 0x000ccfa0, 0x000fffa4, 0x000fffa7 and
  0x000fffff under a floating-point loop, an integer loop, a texture copy and a fill as it does
  unwritten, the loops take 43.99 to 44.49 ms in all 22 settings written while idle, and the copy
  and the fill finish with the right pixels; with both MADD fields written at 0, 1 and 3 while a
  loop ten times as long ran, all six runs hung (job hung, context lost) and the GPU was reset, and
  the same long loops run with no write at all hung in 6 of 7 runs (floating-point 3 of 3, integer 2
  of 3, a plain run 1 of 1; linux fork 01cff214d7d2), so the hang is the long loop's and not the
  write's.
  *platform; HW, infer; data: `usse-clockgate2`, `usse-clockgate2-noload-control`.*
- `E446` With the render context's page mapped writable in the client directory (debugfs
  alias_ctx_rw) and render flag bit 0 of the PB descriptor set at the first kick, a 64x64 render
  comes out exact in 3 of 3 runs on the kernel's own page table (the table after the job equal to
  that of the job without the flag, byte for byte) and in 3 of 3 runs with the descriptor's
  page-table base aimed at 16 zeroed scratch pages, where 1058 dwords (0x422 pages) of the table at
  the base change, 1023 in the first scratch page from dword 1 on and 35 in the second from dword 0,
  and moving the base by 0x1000 or 0x2000 moves them by as much (a control with the base at scratch
  and flag bit 0 clear, 6 of 6 runs, faults the render and changes 0 to 2 scratch dwords, so the
  1058 stores need the flag [HW]; that the EDM's builder makes them is [infer]); with no
  alias_ctx_rw the same pokes fault as in E362 (once each).
  *dpm; HW, infer; data: `dpm-ctx-page-writable`, `dpm-ctx-page-writable-control`.*
- `E447` With the TA data page at 0x6000 of a 4096x4096 render context filled before the job with a
  ramp (0xa5000000 plus the word's index) or a constant (0x5a5a5a5a), a 64x64 triangle with
  CR_DPM_REG_074C written through the TA command (word 167) as 0x0ff, as 0x100, 0x101, 0x102, 0x104,
  0x108, 0x110, 0x120, 0x140, 0x180, 0x1ff, 0x155 and 0x1aa (bit 8 with bits 7:0 of 0x00, 0x01,
  0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0xff, 0x55 and 0xaa) and unpoked draws the exact image
  in all 17 runs, no fault, and the page reads back as written in 1024 of 1024 words in every run,
  the TA data's other nonzero page (page 67, 71 words) the same in all.
  *dpm; HW, infer; data: `dpm-ta-data-pattern`.*
- `E448` A second render context in the VM, on a parameter buffer of its own or on the first
  context's (the PB descriptor and block of the first), renders the triangle exactly in 69 of 69
  renders at 64x64 and 256x256, with the two contexts' jobs run one after the other or the second's
  job submitted before the first's was waited for (the overlap in the firmware was not timed), and
  with render context dword 7 poked to 0xdeadbeef or 0xffffffff in the first context, the second or
  both (20 renders per context in 10 cases, and 2 per context in a last one, 69 per context in all:
  32 + 20 + 2 + 15): no fault, no recovery, the first context's 69 renders exact too, and the second
  context's dword 7 reading 0x10c63000 before the first render and 0xdeadbeef after the first and
  after the second render.
  *render; HW, infer; data: `render-two-contexts-one-pb`.*

### 2026-11-08

- `E449` On two render contexts sharing one parameter buffer, the sharing context's cleanup sends
  the RT data and context steps and no PB step and leaves the loaded-PB slots (TA3DCtl dwords 46 and
  47) at the donor's descriptor, and the donor's cleanup, whose PB step clears them, runs after the
  sharing context has been released whichever of the two is closed first, in 8 of 8 closes of the
  sharing context and 8 of 8 of the donor; all 24 renders exact.
  *render; HW, infer; data: `render-cleanup-two-contexts`.*
- `E450` With two render contexts in a VM, a TA command with an incomplete transfer-queue sync
  (dword 25 set, dwords 26 and 28 naming a zero word) or an incomplete source sync does not complete
  (job hung, context lost after 4 s) in 3 of 3 runs of every case, whichever context holds it, while
  the other context's job completes in the cases where only one is held; the second context's
  command with such a sync is held also when the first context's job has finished (3 of 3 runs
  each); the destination sync was not tried.
  *edm; HW, infer; data: `edm-ta-sync-two-contexts`, `edm-ta-sync-second-first`.*
- `E451` After a first-context render that keeps the DPM owner with render flag bit 2 (TA3DCtl dword
  20 = its RT data set + 0x18, dword 25 clear), a second context's render with the bits clear leaves
  dword 20 as it was in 2 of 2 runs; with bit 3 or bits 3 and 2 kept the words read 0 after the pair
  in 2 of 2 runs each; the second context's own kept words take dword 20 and 25 when only it keeps
  (2 of 2) and replace the first's when both keep with 0xc (2 of 2), or dword 21 when both keep with
  0x4 (2 of 2); all 56 renders exact.
  *render; HW, infer; data: `render-kept-owner-two-contexts`.*
- `E452` A write of the MADD fields of CR_CLKGATECTL2 alone (bits 13:12 and 21:20, both at 0, 1 or
  3, or each at 0 alone), issued 17 to 27 ms into a loop that finishes and returning after it (loops
  of 2500000 iterations) or inside it (5000000), leaves 18 of 18 loops of 2500000 iterations
  (floating-point and integer) and 12 of 12 single-field writes finishing in 87.1 to 88.1 ms, as the
  6 of 6 loops with no write do (87.2 to 87.7 ms), and the register reads the value written; the
  floating-point loop of 5000000 iterations hung in 2 of 9 writes and in 2 of 3 controls.
  *usse; HW, infer; data: `usse-madd-length`, `usse-madd-write`.*
- `E453` With the PB descriptor's page-table base at 16 scratch pages that the host filled with the
  table the kernel builds before a job and its flag bit 0 clear, a 64x64 render comes out exact in 6
  of 6 runs and changes 4 scratch dwords, not 1058, and with flag bit 0 set over that table it comes
  out exact in 6 of 6 runs and changes the same 4; a table of the values a finished job leaves
  faults the render in 3 of 3 runs, and a zero table faults it in 4 of 4 unflagged runs; the plain
  health triangle after the last faulted run faulted too.
  *dpm; HW, infer; data: `dpm-ctx-table-host-filled`, `dpm-ctx-table-flag-order`.*
- `E454` In a textured primary whose program iterates the vertex colour (source 32) alone, the
  colour then a two-component coordinate set, or a three-component coordinate set before the fetch,
  pa0 to pa3 and the image are the same (the coordinate registers reading 0 in every pixel
  throughout) in every run that completed (29 of 29 with bits 24 and 25, 30 of 30 with bit 25 alone,
  30 of 30 with bit 25 alone and no completion bit) with the fetch wait (DOUTU1 bit 25) set, whether
  DOUTU1 bit 24 is set or clear, and change from run to run without bit 25 (in 9 of 10 probes with
  bit 24 alone, in 10 of 10 with neither bit); 1 of 30 jobs with bits 24 and 25 hung (0 of 30 with
  bit 25 alone).
  *pds; HW, infer; data: `pds-iter-wait-colour`.*
- `E455` On a new transfer context, poking word 0 of its HW context to 0x2 makes a fill complete
  without writing (2 of 2 runs), 0x10 or 0x12 or a priority word of 1 or 2 hang the job (12 of 12
  jobs, the driver recovered each), a priority word of 3 faults it (2 of 2), and the controls
  complete (4 of 4).
  *transfer; HW, infer; data: `transfer-ctx-flags`.*
- `E456` A write to register 0x0740 through kregnow (values 0x1ff, 0x200, 0x400, 0x1000, 0x3fe00,
  0x3ffff) reads back 0 right after each of 156 writes (26 before the first kick, 10 between kicks,
  120 beside 300 renders) and every one of 64 samples after a job; the 76 renders of 64x64 on one or
  two contexts are exact.
  *dpm; HW, infer; data: `dpm-task-fields-0740`.*
- `E457` With any one of the firmware buffers 6, 7, 8, 10 or 11 left out of a render VM's alias in
  the client directory, 2 renders are exact in 10 of 10 runs, as in the 2 controls; leaving out
  buffer 9 (TA3DCtl) alone, buffers 6 to 11 or all sixteen faults the first job in 6 of 6 runs, as
  TA3DCtl read-only does (2 of 2).
  *bif; HW, infer; data: `bif-render-directories`.*
- `E458` With the first context closed after a render that keeps the DPM owner with render flag bit
  2 alone, a render on a second context at another RT data address is exact and the kept dword 20
  stays (4 of 4 runs); with bit 3 (NO_DEALLOCATE) kept, the second context's render faulted at page
  0x20003000 in 6 of 6 runs, and with the first context open it was exact and cleared the words in 4
  of 4; that the slot step is what stores the kept word is [infer].
  *render; HW, infer; data: `render-kept-owner-gone-context`.*
- `E459` In a textured primary under the fetch wait, a douti of source 1 reads varying non-zero
  values in pa0 and pa1 when the vertex has dwords for the set (a set of two or three dwords, the
  colour dwords then a set, and with the colour select word's vertex size matching 6, 7 or 8
  coordinate dwords); with the select word left at size 8 over a vertex of 10 or 11 dwords and the
  default coordinate-size word pa0 and pa1 read 0 in every triangle pixel (16 of 16 jobs, 856
  pixels), and a coordinate-size word of 2 or 0x12 on 6 coordinate dwords or 3 on 7 faults every job
  (24 of 24 with the vertex size matching, 36 of 36 with it left at 8).
  *pds; HW, infer; data: `pds-iter-coords-arrive`, `pds-iter-coords-colour`,
  `pds-iter-coords-sized`.*
- `E460` With coordinate registers that deliver (E459), DOUTU1 bit 24 set or clear under the fetch
  wait gives the same image and registers in 33 of 33 completed jobs with both bits against 36 of 36
  with bit 25 alone (12 probes of three shapes, three runs each), and 3 of 36 jobs with both bits
  hung, one in each probe that reads the last iterated register; 0 of 60 further jobs with both bits
  hung; bit 24 alone or neither bit differ from the stable image in 36 of 36 jobs each.
  *pds; HW, infer; data: `pds-iter-coords-bit24`.*
- `E461` With a depth buffer (ZLS stored, the triangle at z 0.5) a job writes a window of 64512
  dwords at 1024x768 (326656 at 4096x4096) whatever the parameter buffer; when the job overflows,
  the window's first 15104 dwords (80640) read 0.0 and, at 0x28 pages and below at 1024x768, the
  rest hold the depth with its sign bit set (-1.0, -0.5), in 2 of 2 runs of every 1024x768 case, and
  the job draws fewer triangle pixels than without the depth buffer (0, 27408, 31629 and 31629
  against 51408, 162544, 205061 and 207456 at 0x30, 0x28, 0x24 and 0x23 pages).
  *dpm; HW, infer; data: `dpm-depth-partial`, `dpm-depth-load`.*
- `E462` After a first render that keeps the DPM owner with render flag bit 3 (0x8 or 0xc) the DPM
  status registers read 0x0700 and 0x070c = 0x04220003, 0x0710 and 0x071c = 0x421, 0x0724 =
  0x00020002 and 0x0728 = 2 (6 of 6 runs), and 0x00020003, 1, 0 and 0 with bit 2 alone or no flag (6
  of 6); closing the first context changes none of the 85 registers 0x0600 to 0x0750 (4 of 4 runs
  with bit 3, and in the 4 runs with the control and bit 2 alone) and the second context's render
  then faults (9 of 9 runs) with none of the 85 changing before the recovery (3 of 3 timeline runs
  that sampled all of them), where with the first context open the second render takes them back to
  0x00020003, 1, 2 and 0 (5 of 5).
  *render; HW, infer; data: `render-kept-owner-regs`, `render-kept-owner-timeline`.*
- `E463` After a fault of the base alone over a zeroed table (kernel poke pb:4 only), exactly the
  next two jobs fault whatever they are (the flagged build over zeros 20 of 20, the plain triangle 8
  of 8, the base over the kernel's table 4 of 4) and the third completes (8 of 8), with a debugfs
  GPU reset before each job or none (16 of 16 sequences, the same outcomes); a fault from an
  unmapped scene stream leaves nothing (16 of 16 followed by an exact job).
  *dpm; HW, infer; data: `dpm-ctx-table-fault-order`, `dpm-ctx-table-fault-chain`.*
- `E464` After the partial renders of a 1024x768 scene in 0x28 pages the TA data's state page holds
  18 non-zero dwords (the ten printed read like page numbers) and its control and OTPM pages hold
  none, in 2 of 2 runs; a second job's dump holds 18 with other page numbers and flipping the second
  render's flag 0x8 changes nothing; a state page filled with a ramp keeps 990 of 1024 dwords, 34
  leaving the ramp, and the image is unchanged; 0x0740 reads 0 after all 20 jobs and after writes of
  0x200 and 0x3fe00 (2 of 2 each).
  *dpm; HW, infer; data: `dpm-partial-state-page`.*

## By unit

### bif

Records: E151, E457.

### dpm

Records: E199, E200, E201, E202, E204, E205, E206, E203, E253, E256, E309, E310, E311, E312, E313,
E327, E358, E362, E438, E442, E443, E446, E447, E453, E456, E461, E463, E464.

### edm

Records: E009, E014, E017, E084, E146, E152, E153, E154, E155, E156, E157, E158, E159, E160, E161,
E162, E163, E164, E165, E166, E167, E013, E168, E317, E319, E320, E321, E353, E402, E431, E444,
E450.

### firmware

Records: E001, E002, E003, E004, E005, E010, E011, E012, E352.

### isp

Records: E064, E065, E066, E067, E068, E069, E070, E071, E072, E073, E074, E210, E211, E213, E214,
E215, E216, E217, E218, E219, E220, E222, E224, E225, E226, E227, E228, E229, E230, E209, E231,
E232, E233, E234, E235, E249, E278, E279, E281, E282, E283, E284, E285, E289, E290, E291, E330,
E332, E334, E338, E339, E340, E410, E415, E416, E417, E439.

### mte

Records: E061, E062, E063, E192, E193, E194, E195, E196, E198, E197, E248, E280, E286, E287, E347,
E348, E418, E419.

### pbe

Records: E029, E030, E031, E032, E239, E240, E251, E265, E266, E267, E268, E269, E270, E333, E382,
E383, E385, E386, E387, E429.

### pds

Records: E043, E044, E045, E046, E047, E048, E125, E126, E127, E128, E129, E130, E131, E132, E133,
E134, E135, E136, E137, E138, E139, E140, E141, E142, E143, E144, E145, E259, E260, E261, E262,
E263, E264, E343, E344, E345, E364, E379, E381, E384, E388, E389, E390, E391, E392, E393, E394,
E395, E396, E400, E420, E421, E428, E430, E436, E437, E454, E459, E460.

### platform

Records: E006, E007, E008, E025, E026, E122, E150, E149, E246, E258, E357, E359, E365, E401, E403,
E404, E405, E434, E445.

### render

Records: E023, E049, E050, E051, E052, E053, E148, E169, E252, E301, E302, E303, E304, E314, E315,
E316, E323, E324, E325, E326, E354, E355, E356, E360, E361, E363, E408, E412, E422, E433, E435,
E448, E449, E451, E458, E462.

### ta

Records: E054, E055, E056, E172, E174, E175, E182, E183, E176, E177, E178, E180, E181, E247, E257,
E288, E305, E306, E307, E308, E322, E328, E329, E331, E407, E409, E424.

### texture

Records: E033, E034, E035, E036, E037, E038, E039, E040, E041, E042, E114, E116, E242, E254, E271,
E273, E274, E275, E276, E277, E341, E342, E397, E399, E425, E426, E432, E441.

### transfer

Records: E015, E016, E018, E019, E020, E021, E022, E024, E027, E028, E272, E398, E455.

### tsp

Records: E236, E237.

### usse

Records: E075, E076, E077, E078, E079, E080, E081, E082, E083, E085, E086, E087, E088, E089, E090,
E091, E092, E093, E094, E095, E096, E097, E098, E099, E100, E101, E102, E103, E104, E105, E106,
E107, E108, E109, E110, E111, E112, E113, E115, E117, E118, E119, E120, E121, E123, E124, E147,
E244, E245, E255, E292, E293, E294, E295, E296, E297, E298, E350, E351, E366, E367, E368, E369,
E370, E371, E372, E373, E374, E375, E376, E377, E378, E380, E406, E423, E452.

### vdm

Records: E059, E060, E184, E185, E186, E187, E189, E190, E191, E188, E299, E300, E318, E346, E349,
E413, E414, E427, E440.

### zls

Records: E057, E058, E250, E335, E336, E337, E411.
