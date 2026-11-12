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
  *zls; HW, infer; data: `zls-control-bits`.*
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
- `E465` The ZLS store writes the 32 x 16 pixel tile (tx, ty) at dword 512 * (ty * (G + 1) + tx) of
  the depth buffer, G being CR_ISP_ZLSCTL bits 11:3, with the dword index inside the tile made of
  the bits y0 x0 y1 x1 y2 x2 y3 x3 x4 from the lowest; in 18 cases on 13 target sizes (one run each)
  every stored dword is at the rule's address in 16, and in the two overflowed 4096 x 4096 jobs
  80640 and 48000 stored dwords are not (the zeros of E468 [infer]), and with a pitch smaller than
  the tiles of a row the tiles overlap, so the window is (th - 1) * (G + 1) + tw tiles (64512 dwords
  at 1024 x 768 and 326656 at 4096 x 4096 for the control 0x0017100c, G = 1).
  *zls; HW, infer; data: `zls-store-layout`.*
- `E466` Bits 26:24 of CR_ISP_ZLSCTL select the format of the stored depth: 0 the 32-bit float (512
  dwords a 32 x 16 tile), 1 the 24-bit unsigned integer round(z * 0xffffff) (512 dwords a tile,
  786432 of 786432 pixels exact), 2 a 16-bit integer, round(z * 0xffffff) >> 8, with the rows y even
  and odd of a column in the low and high half of a dword (256 dwords a tile, 786432 of 786432
  exact); 4 and 7 store no depth without a stencil buffer, and 3, 5 and 6 store other layouts; bit
  19 stores the depth negated (shown by the three most frequent stored dwords only); bits 2 and 18
  enable the depth store and bit 17 the stencil store (bit 17 from E411; here clearing it changes
  nothing without a stencil buffer).
  *zls; HW, infer; data: `zls-store-format`.*
- `E467` A render loads depth only with CR_ISP_ZLSCTL bits 1 and 14 and stencil only with bits 1 and
  13 (neither without bit 1; load-only controls without the store enables store nothing), the loaded
  dword read at the address the store uses (32768 of 32768 depth dwords and 8191 of 8191 stencil
  dwords copied to the same index of a second buffer; stencil dword 0 cannot be told from the clear
  value 0), the loaded depth takes part in the depth test (16384 of 32768 pixels drawn when half the
  loaded depth is 0.25f and half 0.75f against the triangle at 0.5, less), and the sign bit of a
  loaded depth is cleared (0xdeadbeef stored as 0x5eadbeef, 0xffffffff as 0x7fffffff, 0x80000000 as
  0).
  *zls; HW, infer; data: `zls-load-copy`.*
- `E468` In a 1024 x 768 job that overflows the parameter buffer (0x28, 0x23 and 0x30 pages) with
  the ZLS store of the control 0x0017110c (no two tiles at one address), the 336 tiles of tile rows
  0 to 11 hold zeros (48 more are half zeros, at tile columns 6, 14, 23 and 31), the other 1152
  tiles hold the depth with the sign bit set at the address of E465 (602112 of 602112 dwords), and
  11264 more stored dwords (their value was not tabulated) lie in the 2 slots each tile row has
  beyond its 32 tiles; the aliased job of the control 0x0017100c equals those tiles written in
  raster order with the first 8 x 12 tile macrotile last, except 512 dwords (0x28, 0x23) and 1536
  (0x30).
  *dpm; HW, infer; data: `zls-store-layout`.*
- `E469` ima32.u and ima32.s compute the low 32 bits of a * b + c on full 32-bit operands, and every
  route to its three sources agrees: 826 of 826 cases fit, among them the 343 combinations of the
  corner values 0, 1, 0xffff, 0x10000, 0x7fffffff, 0x80000000 and 0xffffffff as a, b and c (.u), 147
  of them signed (.s gives the same bits as .u, with no saturation), 22 sums that land just below,
  on and just above 2^16 and 2^32, the add lowering ima32.u d, a, #1, c (49 cases, a + c mod 2^32)
  and immediates 0, 2, 3 and 127 in source 2 (56), immediates 0, 1, 2 and 127 in source 3 (45) and
  in both (21), c0 as source 3, the mul lowering (49, the low 32 bits of a * b), and the constants
  c3, c13, c45, c56 and c60 as source 3 (40) and c0, c3, c13 and c60 as source 2 (40) read as the
  integers of E085.
  *usse; HW; data: `usse-ima32-full`.*
- `E470` A 32-bit subtract is one ima32: ima32.u d, b, c56, a computes a - b mod 2^32 because
  c56-c59 read as 0xffffffff through the integer multiplier (80 of 80 cases through c56, 6 of 6
  through each of c57 .u, c58 .u, c59 .u and c59 .s, and 8 of 8 with an all-ones register); a .neg
  on source 2 (enc[40]) or source 3 (enc[39]) of ima32, negates that source in two's complement, -(a
  * b) + c and a * b - c (90 of 90 cases in nine spellings: registers in .u and .s, and in .u an
  immediate and a constant; of the three other readings, complement fits 0 or 1 of 10 and ignored 0
  to 4 in every probe, and swapped 1 or 2 of 10 in the eight probes with one negated source, 80 of
  the 90 cases, where it is told apart: the probe with both sources negated cannot tell it); a chain
  of four dependent ima32 is exact with no gap between them (10 of 10); and the carry-in of ima32,
  cie, iN, adds bit 0 of iN only (10 of 10; adding all of iN fits 4 of 10, adding its low 16 bits
  4).
  *usse; HW, infer; data: `usse-ima32-neg`.*
- `E471` imae.u d, a.low, b.low, c, u32 with coe, iN writes the carry out of the 32-bit sum a16 *
  b16 + c into iN, overwriting it with 0 or 1 whether or not the sum carried (14 of 14 cases with iN
  preset 0x55; writing only on a carry fits 7, ORing it in 0); cie, iN adds bit 0 of iN only to that
  sum (10 of 10; iN = 2 adds nothing, iN = 0xffff and 0xffffffff add 1); coe and cie together on one
  iN assemble and write the carry of the whole sum including the added bit (14 of 14, the sum a16 *
  b16 + c + bit 0 of iN); two imae chained through i0, a coe then a cie, are an exact 64-bit
  accumulate of a16 * b16 products (10 of 10); and imae.s multiplies the 16-bit halves as signed
  values and adds c as an unsigned 32-bit number, the carry being that add's (6 of 6 cases, no model
  beforehand).
  *usse; HW, infer; data: `usse-imae-neg`.*
- `E472` A class 9 test of a 32-bit register through source 2 tests all 32 bits (iadd32.testnat,
  testpat, testtaz and testtanz.chan0 !c0, p0, #0, rN: bit 31 set, bit 31 clear, all zero, any set,
  8 of 8 corner values each; iaddu32.testtanz 8 of 8; iaddu32.testnat never true, 8 of 8), but with
  a source 1 the sum is not the wrapped 32-bit sum, for the tests run: n and p of iadd32 read the
  sign of the true sum sext16(r1) + r2 (r2 signed), so r1 = 0x7fff with r2 = 0x7fffffff leaves n
  clear and p set (12 pairs, of which 5 overflow the signed 32-bit sum and separate the readings:
  the true sum fits 12 of 12, the wrapped one 7 of 12), and the nonzero test of iaddu32 sees the
  carry out of bit 31, so r1 = 1 with r2 = 0xffffffff is nonzero (8 of 8, the wrapped sum fits 5 or
  7; the one pair (1, 0xffffffff) decides it for a zero- and a sign-extended r1 alike, the two
  others whose wrapped sum is zero only if r1 is zero-extended); z of iadd32 and testpat, testtaz of
  iaddu32 were not separated; the exact unsigned and signed compares of two 32-bit registers cost
  six instructions each with the borrow formula over t = ima32.u r11, r2, c56, r1 (64 of 64 pairs
  each, and 16 of 16 for the unsigned compare only with three nops after the ima32), and ima32
  itself has no test field.
  *usse; HW, infer; data: `usse-compare32`, `usse-compare32x`.*
- `E473` Class 9 tests with a seven-bit immediate in source 2 act on the full 32-bit result:
  shr.testtanz.chan0 !c0, p0, r1, #n sets p0 when r1 >> n is nonzero, for n in 0, 1, 3, 7, 15, 16,
  31, 32, 33 and 127, with n of 32 and over giving a result of zero (80 of 80 cases over eight
  values of r1; reading n mod 32 fits 64), xor.testtaz.chan0 !c0, p0, r1, #n sets p0 when all 32
  bits of r1 ^ n are zero (18 of 18 cases for n of 0, 7 and 127 including r1 = 0x10000 and
  0x80000000; looking at the low 16 bits only fits 11), and and, or, xor and rol with testtanz and
  asr and shl with testnat test their 32-bit result (48 of 48); the assembler refuses ~ in the three
  test forms tried (and.testtanz with ~#7 and with ~r2, xor.testtaz with ~#7), while and r10, r1,
  ~#7 assembles; or, rol and xor with ~r2 in a test were not tried, and no raw word was run.
  *usse; HW, infer; data: `usse-compare32`.*
- `E474` The immediate of the bitwise group is its 16-bit field rotated left by the five-bit
  rotation field enc[42:38], whatever the rotation: raw words with the field 0xffff, 0x8001 and
  0x1234 under each of the 32 rotation values build rotl(field, r) in 96 of 96 cases (rotating right
  fits 6, ignoring the rotation 3, using its low four bits 48), the 18 values the assembler encodes
  (0x80000001, 0xffff0000, 0x7fff8000, 0xff0000ff, 0x12340000 ...) arrive unchanged (18 of 18), ~#X
  complements the whole 32-bit operand after the rotation (19 of 19 on and, or and xor), and shl,
  shr, asr and rol by a rotated immediate use the whole 32-bit value as the amount (36 of 36: shl
  and shr give 0 and asr the sign for 32 and over, rol takes it mod 32).
  *usse; HW, infer; data: `usse-rot-imm`.*
- `E475` pclink holds 18 bits and a call stores the index of the instruction after it: mov pclink,
  rN keeps bits 17:0 of rN (19 of 19 cases, 0x40000 reads back 0, 0x7fffffff 0x3ffff, 0x80000000 0,
  0xa5a5a5a5 0x1a5a5; the whole 32 bits come back for no value above 0x3ffff), ba.savelink and
  br.savelink store the index of the next instruction (calls with the next instruction at index 20,
  40, 64, 127 and 128, and a predicated call taken: 9 of 9) as an absolute index counted from the
  program start of a fill (the code base of a placed program: E476), a predicated ba.savelink whose
  predicate is false still writes pclink (one case, p0 ba.savelink with p0 clear: the preset 0x77
  read back 0x15, the index after the call, with the call not taken; br.savelink, other predicates
  and !pN were not run), and a lapc after mov pclink, rN uses the new value with no instruction
  between them (19 of 19 cases with 0 to 3 instructions between, with and without .nosched on the
  move and on the lapc: the stale link of the call never used); pclink is not reset between jobs: a
  reader job reads the value a writer job left in 94 to 98 percent of its 2048 pixels (the ten
  reader jobs of usse-pclink-pixels, after five writers) and 0xeb3 or 0x98 in the others, which are
  aligned 2 x 2 quads of pixels (every deviant pixel has its x^1, y^1 and diagonal neighbours
  deviant too).
  *usse; HW, infer; data: `usse-link`, `usse-pclink`.*
- `E476` lapc lands exactly on the index in pclink for each of the indices run (listed in What it
  shows; no index outside them is known to fail, and no other index was run): a jump through the
  link of a ba.savelink call returns to the instruction after it (4 of 4 cases, including a new link
  moved into pclink after the call with 0 to 2 instructions between), nested calls whose routine
  saves and restores pclink in r14 return twice with br.savelink and ba.savelink (2 of 2), lapc
  lands on targets 1 to 100 instructions ahead with the target a constant (8 of 8, landing at the
  indices 30, 31, 32, 34, 37, 45, 69 and 129) or computed by an ima32 add (8 of 8, the same indices)
  and 0, 1, 2, 5, 20 and 100 instructions back over three passes (6 of 6), pclink bits above bit 17
  set in the register moved into it are ignored and the jump lands on bits 17:0 (4 of 4: bit 18, bit
  19, bit 31 and bits 31:18), and in programs placed in the code heap the indices count from a code
  base that is the placement rounded down to 512 KiB (this rests on one placement that is neither
  0x10000 nor a multiple of 0x100000, 0x1ff000: the step of 0x80000 is the only one the five links
  allow, but a second such placement was not run): a lapc to index 8192 + 129, 8192 + 200 and 8192 +
  250 lands (3 targets, each run 3 times at the one offset 0x10000: 9 of 9 jobs) and so does a lapc
  computed from the link of a br.savelink read at run time, forward 8 instructions, in programs
  placed at offsets 0x10000, 0x100000, 0x1ff000, 0x200000 and 0x400000, whose links read 0x2002, 2,
  0xfe02, 2 and 2 (5 placements, each run twice: 10 of 10 jobs); a jump to index T in a placed
  program that counts T from the program start instead faults the job (BIF fault at 0x37001014 to
  0x37001031) or hangs it, and the GPU recovers (no job after the faults failed to run; 7 jobs
  failed in all: 3 lapc faults in place, 2 `ba #T` faults and 2 hangs in place-ctl2).
  *usse; HW, infer; data: `usse-risky`, `usse-place`, `usse-place-ctl`, `usse-place-ctl2`,
  `usse-place2`, `usse-place-link`.*
- `E477` p0-p3 are state no branch changes: of 28 cases (patterns 1010, 0101, 1111 and 0000 through
  ba, br #2, a br.savelink call with a lapc return, a routine that rewrites the predicates, and a
  predicated ba, !p1 ba and p2 br taken and not) the predicates read back after the flow are those
  set before it, or the routine's own rewrite when it made one (28 of 28), and the same through
  ba.savelink calls, lapc returns, a p1 lapc that returns or falls through, and a p0 ba.savelink (16
  of 16); across jobs the predicates are left over for most pixels but not all: a reader job that
  reads p0-p3 before setting them reads the previous setter's pattern in 98.4 to 99.2 percent of its
  2048 pixels (2016 to 2032 pixels in each of the ten readers after a setter of the dataset: 1111
  after a setter of 1 in five of five readers, 0000 after a setter of 0 in five of five) and another
  pattern in the other 16 to 32 pixels (0xd, 0x5, 0x1, 0xf or 0 of the packed bits p0..p3); the
  first reader, after the baseline triangle, has 1992 pixels at 0000 and 56 at others.
  *usse; HW, infer; data: `usse-pflow`, `usse-risky`.*
- `E478` One wdf drc0 waits for every load outstanding on drc0, ldad, ldad.fetchN and ldr alike, and
  no limit on how many are outstanding was seen: 1, 2, 4, 8 and 16 independent ldad (5 of 5 cases),
  five mixes of ldad, ldad.fetchN of 2, 4, 8 and 16 dwords and ldr #7 and #8 (5 of 5), and, in the
  growth table, 24, 32, 48, 64, 80 and 100 distinct ldad on drc0 (6 cases), 32, 64 and 100 on drc1
  (3), 128, 160 and 200 ldad that issue the same eight loads again over eight registers, which
  cannot show a lost reload (3) and 2, 4, 8, 12 and 16 ldad.fetch16, up to 256 dwords (5) (17 of 17
  cases) all return their data after the one wdf, so what the data show is up to 100 distinct ldad
  on one counter (drc0 and drc1) and 16 ldad.fetch16, while a single ldad read by a stad after 0, 1,
  2, 4, 8, 16 or 32 nops and four ldad after 0 or 16 nops still hold the register's marker (9 of 9
  cases), in a client pixel task: the register still holds its marker 32 instruction slots after a
  single ldad (16 after four) with no wdf, and the wdf gives the data.
  *usse; HW; data: `usse-fence-batching`, `usse-fence-growth`.*
- `E479` A wdf drcN does not wait for loads counted on other counters that were issued after the
  loads it waits for: in a client pixel task, eight cases run ten times each, of which the data hold
  one run: in that run two ldr on drc2 followed by four ldad on drc1 and a wdf drc2 only leave all
  four ldad registers at their markers (case 7) and four ldad on drc1 followed by four on drc0 and a
  wdf drc1 only leave the drc0 registers at their markers (case 3), and the other six cases return
  all their data; nine more runs of the table, kept in the scratch tree and not in the data, were
  recounted by the reviewer together with the dataset's: markers in case 7 in 10 of 10 runs, in case
  3 in 2 of 10 runs (the dataset's run and one of the nine), and none in the other six cases in 10
  of 10 runs each (60 of 60 case readings), counts a reader of the data cannot recompute.
  *usse; HW, infer; data: `usse-fence-batching`.*
- `E480` A wdf, or an idf drcN, bif, with nothing outstanding returns at once and does not hang the
  job: as the first instruction after phas on each of drc0, drc1, drc2 and drc3, twice in a row, on
  all four in a row, with an idf drc0 or drc1, bif, and as the second and third wdf after one load
  or a wdf on a counter nothing was issued on (11 of 11 cases, the pixel reads the sentinel), and in
  seven short programs the dword or dwords the host reads after the job hold the stored value
  whether or not a fence precedes the end of the program (7 of 7 cases; every one of the 2048
  instances of the fill stores the same value to the same dword, so this shows the final value of
  that dword, not that any one instance's unfenced store reaches the host): one stad followed by no
  fence, by idf drc0, bif only, by wdf drc0 only, by the usual idf and wdf, or by one nop (5 cases),
  and sixteen stad followed by no fence or by idf drc0, bif only (2 cases).
  *usse; HW; data: `usse-fence-batching`.*
- `E481` A stad is seen by a later load of the same dword without an idf in between, by instances
  that all store the same value to the same dword (a single instance's store is not isolated, since
  each of the 2048 instances of the fill stores to that dword and a load may return another
  instance's identical store): in 17 cases the load returns the stored value in the 16 that load the
  stored dword (ten with no idf, among them ldad, ldad.bypassl1, ldad.fcfill, eldd, ldad.bpcache and
  ldad on drc1, two stad of one dword where the later wins, and sixteen stad then a load of the last
  and of the first dword, each returning its own store; four with an idf and its wait; two with an
  idf not waited) and the buffer's fill in the control, a load of the next, untouched dword, so an
  idf is not needed for this order.
  *usse; HW, infer; data: `usse-fence-batching`.*
- `E482` stad.fetchN stores N consecutive registers to N consecutive dwords in one instruction, so
  that ldad.fetch16 followed by one stad.fetch16 copies 16 dwords with two instructions and one wdf:
  the stores land one dword on from the base, dwords b + k + 1 to b + k + N for [rb,+#k]
  (stad.fetch2, 4 and 16 with k 1 and fetch4 with k 0: 4 of 4) and dwords b + 1 to b + N for
  [rb,#1++], which moves rb by N (fetch2, 4 and 16: 3 of 3), the layout of a load fetch, and the
  16-dword copy from r2-r17 of the dwords a load fetch read matches in order (1 of 1); a plain stad
  [rb,#1++] repeated sixteen times, the control, stores b to b + 15 and moves rb by 16 (1 of 1).
  *usse; HW; data: `usse-store-repeat`.*
- `E483` stad.repeatN and ldad.repeatN step the pointer register along with the data register:
  iteration i uses r(b + i) as its address and r(s + i) (r(d + i) for a load) as its data, the
  address read for every iteration i for N up to 16, and the pointer registers r40 to r43 move by
  the increment of the form (k after its own access for [rb,#k++], before it for [rb,++#k], not at
  all for [rb,+#k]), in 26 of 26 stad cases of the follow-up with 16 valid pointers (five plain,
  five post-increment, three pre-increment, twelve after an smlsi and one 16-dword copy) and in 7 of
  7 ldad.repeat cases, in a client pixel task; the pointer movement was read for r40 to r43 only
  (the probe stores its marker through those four pointers, whatever N, so min(N, 4) markers: 2, 3
  and 4 at N = 2, 3 and 4 and 4 above), so that whether r44 to r55 move, and whether the pointers a
  repeat does not use stay, was not read; after smlsi #a, #b, #c, #d the second increment sets the
  step of the pointer register and the fourth the step of the data register, the first and third
  doing nothing to a store (12 of 12; they were varied only together, in (1, 0, 1, 1) and (1, 1, 1,
  1)), so that smlsi #0, #0, #0, #1 and stad.repeat16 [r40,#1++], r2 store r2 to r17 at the 16
  consecutive dwords from r40 and move r40 by 16 (2 of 2: the smlsi probe's case 2 and the 16-dword
  copy after an ldad.fetch16); with only r40 a valid pointer, 27 of the 43 cases of the first run
  faulted the job.
  *usse; HW, infer; data: `usse-store-repeat`, `usse-store-repeat-regs`, `usse-store-repeat-regs2`.*
- `E484` In a fill pair, a job reads what the job before it left in the temporaries, internal
  registers, predicates and sa, with different reach: r40 and r47 written by one job are read by the
  next in 7 of 7 reader jobs (2048 of 2048 pixels each) and still by a reader two jobs later, after
  a job that wrote no temporary, in 2 of 2; i0, i1 and i2 in 9 of 9; p0 and p1 in 96.3 to 100
  percent of the pixels of 10 of 10 reader jobs; sa1, sa5 and sa7 written by one job are read by the
  next in 9 of 9 reader jobs (2048 of 2048), but after a job that wrote no sa the reader reads that
  job's pixel output instead of the sa it wrote two jobs earlier (3 of 3), as it does for an sa
  nobody wrote (2 of 2), so sa is kept for one job only; and 12 pixels (4 of each of the three
  values) of every one of the 18 jobs that wrote sa1, sa5 and sa7 show the sa value as their output
  instead of the colour.
  *usse; HW, infer; data: `usse-task-state`.*
- `E485` In a client pixel task (a fill, not a firmware task) started with up to 128 temporaries
  every register sampled up to r123 is real, separate storage: with the runner's --temps 52 and 64
  the registers r2, r4 ... and the top one (26 and 32 registers, 4 of 4 cases, ascending and
  descending) and with --temps 80, 96, 112, 124 and 128 the registers r2, r6 ... and the top one
  (21, 25, 29, 32 and 32 registers, 10 of 10 cases) read back their own markers (14 of 14 cases), so
  the file does not wrap at 32, 48 or 64, and r123 reads back at --temps 124 and 128 (8 of 8 cases);
  the registers between the sampled ones (r3, r5, r7 and so on) were not read; r124-r127 are not
  named by an ALU instruction (usse-asm refuses r124 and up as an ALU operand [infer]: no raw word
  was run) but are destinations of a load, and after ldad.fetch4 r124 in a job started with 128
  temporaries i0, i1 and i2 keep their markers (1 case, 3 of 3 registers) and i3 reads the marker of
  i0 (the reading of E075).
  *usse; HW, infer; data: `usse-temps-max`, `usse-temps-sparse`.*
- `E486` In a client pixel task (a proxy: not a firmware task), a register past the allocation reads
  back as the register whose index is the register's modulo the allocation in most pixels, and a
  write to it was not seen to reach that register: with --temps 8, 16, 32 and 64, r(n) for n of the
  allocation T and above reads the marker written to r(n mod T) in 88 to 99.6 percent of the 2048
  pixels in 15 of 15 cases that write nothing to r(n) (T = 8: r10, r11, r18, r29; T = 16: r18, r19,
  r34, r53; T = 32: r34, r35, r66, r101; T = 64: r66, r67, r123), reads the scratch pointer held in
  r1 for r(T + 1) in 2040 and 1968 pixels of two cases (r9 with T = 8, r33 with T = 32), and in 4 of
  4 cases at T = 8 and 32 (none at 16 and 64) that also write a marker to r(n) (r12 and r108 with T
  = 8, r36 and r48 with T = 32) the pixels and r(n mod T) read the value written to r(n mod T), not
  the one written to r(n), the rest of the pixels reading other values; the 5 further cases with n a
  multiple of T (r8, r24, r48 with T = 8; r32, r96 with T = 32) read varying leftovers of earlier
  jobs.
  *usse; HW, infer; data: `usse-temps-past`, `usse-temps-wrap`.*
- `E487` The temporaries a phase uses are the ones its phas asks for, up to 192: a fill started with
  8, 32, 64 or 128 temporaries whose phas asks for 8, 16, 32, 64, 96, 124, 128, 132, 136, 144, 160
  or 192 for phase 1 (the 12 values run, all started with 8; 192 also started with 32, 64 and 128)
  reads back the marker it wrote to its highest register (r123 from 124 up) in all 15 jobs, and a
  request of 196, 200, 204, 208, 212, 216, 220, 224, 252, 256, 508 or 1020 hangs the job in all 15
  jobs (196 also when started with 32, 64 and 128), each recovered with no reload, in a client pixel
  task (196 is the lowest request that hung and 192 the highest that ran, among the values run:
  every request run was a multiple of four, as the field counts in fours, and 100 to 120, 148 to
  156, 164 to 188, 228 to 248, 260 to 504 and 512 to 1016 were not run; the 12 and 12 values are not
  an interval), whatever the task was started with (8, 32, 64 or 128 for 192 and 196); every request
  from 124 up wrote r123 only, r124 and up cannot be named by usse-asm, so a request above 124
  exercised r123 and not the registers past it; the 15 jobs that ran took 420 to 583 microseconds,
  single samples, with no trend seen in the request.
  *usse; HW, infer; data: `usse-temps-past`, `usse-temps-bound`, `usse-temps-bound2`,
  `usse-temps-bound3`.*
- `E488` An emitpds in a client fill shader starts the PDS program it names, and then the job
  faults: with the fill's PDS secondary named by s1 (its offset in the pixel PDS heap shifted right
  by four, 4 for the copy's secondary at heap base + 0x40) and s0 = 2 data rows, addend 0x100, the
  emitted run of the program stores an input word to scratch in 18 of 19 ir0.0 probes (the ir0.1 and
  ir1 probes are not counted; the program's ir0.0 reads 3 in 16 and 2 in 2, against 0x400 to 0x403
  for the fill's own run), s2 not reaching ir0.0 or ir1.0 (s2 0, 1, 0xFFFFFFFF and 0xE17D0001 give
  ir0.0 3, 3, 2, 3, and ir1.0 is 0 for s2 0, 0xFFFFFFFF and 0xE17D0001), and the flags .tasks,
  .taske, both, neither, .freep and .nosched, #incp 1 to 3, the sideband 0x1, 0x200 and 0x2000 and
  2, 1 or 4 rows changing nothing seen of that, while with the addend 0x1000 the dword held the
  no-emit value 0x403 (1 probe, and once more in a probe.py repeat outside the data, both in jobs
  that faulted: one observation of no 2 or 3 seen, the late 0x400 value moving from run to run in 5
  of 20 probes); every job with an emit ended with a BIF fault at 0xd2000 (22 of 24, 0x92000 once
  with sideband 0x1) or a hang (two emitpds in a row), 24 of 24, each recovered with no reload, and
  the two controls without an emit completed.
  *usse; HW, infer; data: `usse-emitpds`.*
- `E489` The address rule of E465 recomputed from stored depth dumps of a rerun of the 11.22
  store-layout run, by a script written separately from the run's script: of 3415552 dwords stored
  in the 18 cases (13 target sizes, G 0 to 511), 3279132 decode to a pixel whose rule address is the
  dword's own, 7780 are the background depth 1.0 of pixels past the target, and 128640 (48000 and
  80640 in the two overflowed 4096 x 4096 jobs) are zero in both ramp dumps, none is at another
  address (0), the pixel to address direction holds for all 1098340 pixels of the four cases whose
  tiles do not overlap, and every one of the 18 lines of the run (changed, slots, not at the
  predicted address, background) equals the 11.22 run's, so the zeros of E465 are measured zeros,
  not an inference about the decoding.
  *zls; HW, infer; data: `zls-store-layout-dumps`.*
- `E490` The depth formats of E466 recomputed from stored dumps of a rerun of the 11.22 store-format
  run, by a separate script: at 1024 x 768 with G = 33, format 0 holds the float z of the ramp at
  786432 of 786432 pixels (within 1e-5 of the geometry's), format 1 holds round(z * 0xffffff) at
  786432 of 786432 (z is the float format 0 stores at that pixel; floor, 333955), format 2 packs two
  rows in one dword in 256 dwords a tile with the dword index lx0 ly1 lx1 ly2 lx2 ly3 lx3 lx4 and
  the half ly0, derived from the dumps alone (786432 halves, 512 of 512 slots the same in every
  tile), formats 4 and 7 store nothing without a stencil buffer (0 dwords), formats 3, 5 and 6 store
  965120, 96580 and 86084 dwords in 1885, 1508 and 1536 slots in the x ramp (the y ramp stores
  965120, 84480 and 73760; format 3 reaches the last dword of the buffer, so its count is a lower
  bound), and bit 19 stores the float depth negated at 786432 of 786432 pixels and changes no dword
  of formats 1 and 2 (the dumps are byte-identical to the dumps without it, same sha256), where E466
  had shown it by three frequent dwords.
  *zls; HW; data: `zls-store-format-dumps`.*
- `E491` A call that is not taken still writes pclink: with the predicate false, ba.savelink and
  br.savelink left pclink at the index of the instruction after the call in all 16 not-taken calls
  of the fill table (p0, p1, p2 and p3 false for each form, !p0 and !p1 with the predicate false, p0
  with pclink preset 0 and 0x3ffff and with the next instruction at index 48 and 84), in all 3
  not-taken calls of a chain of two calls, and in all 10 jobs of five placed programs (5 programs, 2
  jobs each, at heap offsets 0x10000 and 0x1ff000); the reading that a call not taken leaves pclink
  as it was fits none of them (0 of 16, 0 of 3, 0 of 10), and the taken calls write the same link (2
  of 2 in the fill table, 4 of 4 placed jobs).
  *usse; HW, infer; data: `usse-callfalse2`, `usse-callfalse`, `usse-place-more`.*
- `E492` The code base of a placed program moves in steps of 0x80000 bytes (65536 instructions) at
  five more placements: a br.savelink in a program placed at 0x2ff000 reads its link as 0xfe02, at
  0x1a0000 as 0x4002, at 0x3a8000 as 0x5002, at 0x4ff000 as 0xfe02 and at 0x300008 as 0x3 (the
  offset inside the step divided by 8, plus 2), and a lapc to the link plus 8 computed at run time
  lands in each (5 offsets, a read and a jump program at each, 2 jobs of each program: 20 of 20
  jobs, o0 = the link, never 0xFA11); with E476's five placements, 0x80000 is the only power of two
  from 0x1000 to 0x1000000 that fits all ten links (0x40000 fits 7, 0x20000 and 0x100000 fit 5, the
  others 4 or fewer), and seven of the ten placements are not multiples of it (0x10000, 0x1ff000 and
  the five of this table).
  *usse; HW, infer; data: `usse-place-more`.*
- `E493` The extra i operand of ima32, ima32.u d, iK, a, b, c (enc[38] set, iK in enc[37:36]),
  writes the high 32 bits of a * b + c to iK for the operands run: d = the low 32 bits and iK = bits
  63:32 in 15 of 15 cases (K = 0, 1 and 2 over the five triples of unsigned `.u` register operands
  (3, 7, 100), (0xffffffff, 1, 1), (0xffffffff, 0xffffffff, 0xffffffff), (0x10000, 0x10000, 0) and
  (0x80000000, 2, 0xffffffff), the other two of i0, i1 and i2 keeping their presets 0x55, 0x66 and
  0x77); the reading 'iK = the carry out of the 32-bit add' fits 6 of 15 and 'iK unchanged' 0 of 15;
  and eight raw ima32.u words that differ from the plain word 0xD000000001404103 outside what the
  assembler writes (enc[38] set with enc[37:36] = 3, enc[38] clear with enc[37:36] = 1, 2 and 3, and
  one of the bits 46, 45, 44 and 35 set), each over three triples (24 jobs), gave the plain result
  in r10 and left i0, i1 and i2 at their presets in 24 of 24, and in the 21 jobs of the words
  without bit 46 no other dumped register changed, but with bit 46 set r14 read 0x2255 instead of
  its preset 0xb0b1b2b3 in 3 of 3 jobs.
  *usse; HW, infer; data: `usse-ima32-forms`, `usse-raw25`.*
- `E494` The carry in of ima32 and imae adds bit 0 of iN for every iN and value that ran: ima32.u d,
  a, b, c, cie, iK adds bit 0 of iK for K = 0, 1 and 2 and the eight values 0x10000, 0x80000000,
  0xfffffffe, 0x10001, 0x80000001, 2, 0x55555554 and 0xaaaaaaab (24 of 24 cases, 3 * 7 + 100 with
  the other two i registers holding 1; adding all of iK fits 0 of 24 and its low 16 bits 12 of 24),
  imae.u cie, iK for K = 0 and 1 and the values 0x10000, 0x80000000, 0x10001 and 1 does the same (8
  of 8), and imae coe, iK writes the carry of the sum to the iK named and leaves the other i
  registers at their presets 0x55, 0x66 and 0x77 (8 of 8: for K = 0 and 1 and the four triples (2,
  3, 0xfffffffe), (2, 3, 0xfffffff0), (0xffff, 0xffff, 2) and (1, 1, 1), of which only the first
  carries, so 1 carry and 3 sums without for each K).
  *usse; HW, infer; data: `usse-ima32-forms`.*
- `E495` ima32 takes the seven-bit immediates 4, 5, 6, 7, 8, 15, 16, 17, 31, 32, 33, 63, 64, 65,
  100, 125 and 126 (17 values; with E469's 0, 1, 2, 3 and 127, 22 of the 128 values have run in
  source 2 and 21 in source 3, where 3 was not run) in source 2 and in source 3, giving a * imm + c
  and a * b + imm (68 of 68 cases, two triples for each value and source), `.neg` negates in two's
  complement on the ten forms run, `.s` with #1.neg and #5.neg in source 2, #1.neg and #127.neg in
  source 3, c56.neg and c3.neg in source 2 and c56.neg in source 3, and `.u` with #5.neg and
  #127.neg in source 2 and #127.neg in source 3 (80 of 80 cases, eight triples each; leaving the
  `.neg` out fits 12 of the 80), and a dependent reader of an ima32 result sees it with and without
  `.nosched` on the writer after 0, 1, 2, 3, 4, 5, 6 and 8 nops, for an ima32, a mov and an xor
  reader (48 of 48 cases, one case per writer, distance and reader).
  *usse; HW; data: `usse-ima32-forms`.*
- `E496` ima32.u writes the six r-bank destinations run, r9, r18, r28, r30, r31 and r0 (the other
  dumped registers untouched: 18 of 18 cases) and sa0, o0, i1 and i2 (read back in the same job: 12
  of 12), but not pa0: in the jobs of pa-dest, `ima32.u pa0, ...` twice and `mov pa0, r1` once (3 of
  3 jobs) left pa0 at the value it read before (0xff00ff00 in 1536 pixels and 0xff203040 in 512),
  the pa0 destination jobs of the dest probe read 0x02dadf6f in all three (two of the three jobs
  separate it from the result, 0x79 and 0 expected), and the persistence of an sa0 written by
  ima32.u from one job to the next is not separated from the colour rule of E484 (job 8 reads 0x79
  in sa0, 2048 of 2048 pixels, which is also the colour that job 7, the writer, output; job 9 reads
  0x79 in pa0, also the colour job 8 output); ima32.u accepts the operands pa0, pa1, pa4, sa0, sa1,
  sa4, o0, o1, o3, i0, i1 and i2 in source 1 and pa0, pa1, pa4, sa0, sa1, sa4, o0, o1, g0, g1, g7,
  i0, i1 and i2 in sources 2 and 3 and reads 0 where mov reads 0 and the preset in i0 to i2 (40 of
  40 cases: 31 of them read 0 by both routes, so a bank field that the instruction ignored would
  pass there, and only the 9 cases of i0 to i2 show a nonzero value).
  *usse; HW, infer; data: `usse-ima32-forms`, `usse-pa-dest`.*
- `E497` The six-instruction signed 32-bit compare of E472 needs no gap after the ima32: with one,
  three and six nops between ima32.u r11, r2, c56, r1 and the instruction that reads r11, a < b
  signed over the 16 pairs (0, 1), (1, 0), (0, 0), (0xffffffff, 0), (0, 0xffffffff), (0x80000000,
  1), (1, 0x80000000), (0x7fffffff, 0x80000000), (0x80000000, 0x7fffffff), (0xffff, 0x10000),
  (0x10000, 0xffff), (0xffffffff, 0xffffffff), (0x80000001, 0x80000000), (0x7fffffff, 0xffffffff),
  (0xffffffff, 0x7fffffff) and (5, 5) is right in 48 of 48 cases (16 each: the pixel r10, a - b in
  r11, the word a xor t in r13 and r15 all as computed), where E472 ran the signed compare unpadded
  (64 of 64) and the unsigned compare with three nops (16 of 16).
  *usse; HW; data: `usse-compare32-pad`.*
- `E498` On the 16 pairs (r1, r2) = (0x8000, 0x8000), (0xffff, 1), (0x8000, 0xffff8000), (0x8001,
  0xffff7fff), (0xffff, 0xffffffff), (0x9000, 0xffff7000), (1, 0xffffffff), (0x7fff, 0xffff8001),
  (0, 0), (0, 0xffffffff), (0x8000, 0), (0xffff, 0), (0x8000, 0x7fff0000), (0xffff, 0x80000000), (5,
  0xfffffffb) and (0x8000, 0x7fff8000), the class 9 tests of a sum read it as follows: iadd32
  testnat and testpat read the sign of the true signed sum sext16(r1) + r2 (16 of 16; the wrapped
  32-bit sum fits 15, the one pair (0xffff, 0x80000000) separating the two readings), iadd32 testtaz
  and testtanz read the zero of that sum with r1 sign-extended from 16 bits (16 of 16: the pairs
  (0x8000, 0x8000) and (0xffff, 1) read zero, which a zero-extended r1 does not give, 11 of 16; the
  true and the wrapped sum give the same zero test on every pair, 16 of 16), iaddu32 testpat is true
  and testnat false for all 16 pairs, and iaddu32 testtaz is true for (0, 0) only (1 of 16) and
  testtanz for the other 15, the five pairs whose sign-extended sum wraps to zero and the six whose
  zero-extended sum wraps to zero (besides (0, 0)) included: the sum with its carry out of bit 31
  fits 16 of 16 under either extension and the wrapped 32-bit sum under neither, and no pair
  separates a zero-extended from a sign-extended source 1 for iaddu32.
  *usse; HW, infer; data: `usse-iaddu32-pairs`.*
- `E499` Bit 43 of a class 9 test word is the pat bit of the test field enc[43:40] (taz 1, tanz 2,
  nat 4, pat 8), not an invert: the sixteen test words the assembler writes (and, or, xor and rol,
  with r2 or #7, testtaz and testtanz), run as raw words, give the test of op(r1, source 2) (96 of
  96), the same words with bit 43 set give the plain condition ANDed with pat (96 of 96: taz with
  pat is taz, tanz with pat is nonzero and positive; the invert of source 2 fits 53 of 96, the
  condition ORed with pat 48 and no effect 79); all 15 values 1 to 15 of the field on `and` r1, r2
  over six input pairs (90 of 90 cases) give, with enc[39] = 1 (join `a`) and chan0 in all 732 raw
  test words run, the AND of a zero part (tanz if bit 41, else taz if bit 40) and a sign part (pat
  if bit 43, else nat if bit 42), a rule read out of those 90 cases (so a fit to them: the plain AND
  of the set conditions fits 69 of 90 and the OR 57), and the same rule, written down before the
  next table, predicted all 450 cases of a table run afterwards on other forms (all 15 values over
  six input pairs for `or`, `xor` and `rol` with registers and for `and` and `xor` with #7: 5 forms,
  90 cases each, join `a` and chan0 only: 450 of 450; the `o` join with a two-part field was not
  run).
  *usse; HW, infer; data: `usse-raw25`, `usse-rawcond`, `usse-rawcond2`.*
- `E500` In three more runs of the 15 jobs of E475's usse-pclink-pixels (a, b and c: 30 reader jobs,
  40 with E475's own run), the pixels that read another value than the writer's are 0xeb3 in 48 to
  80 pixels of a job (exactly 64, 16 aligned 2 x 2 quads, in 29 of the 40 reader jobs: 6, 8, 7 and 8
  in the four runs) and 0x98 in 16 to 64 pixels of 12 of the 40 jobs (2, 3, 2 and 5 in the four
  runs), no other value in any job, and their positions repeat in part and not whole: the minority
  pixels of one reader job in two of the four runs share 4 to 52 pixels over the six pairs of runs
  (1 to 13 quads, 3 to 13 in the runs a and b, where two random sets of 16 of the 512 quads would
  share about 0.5), and all four runs share 0 to 16 pixels of a job; two different reader jobs of
  the same run also share quads, 1 to 12, 1 to 12, 2 to 13 and 1 to 16 over the 45 pairs of each of
  the four runs.
  *usse; HW, infer; data: `usse-pclink-repeat`, `usse-pclink`.*
- `E501` The high word of the subtract form gives the borrow, and an exact unsigned compare is two
  instructions on the pairs run: ima32.u r10, iK, r2, c56, r1 leaves a - b mod 2^32 in r10 and b -
  [a < b] in iK (75 of 75 cases: K = 0 over the 49 pairs of the seven values 0, 1, 0xffff, 0x10000,
  0x7fffffff, 0x80000000 and 0xffffffff, K = 1 and K = 2 over the same 13 pairs, the other two i
  registers keeping their presets 0x55, 0x66 and 0x77; as E493's high word predicts, b * 0xffffffff
  + a = (b - 1) * 2^32 + (2^32 - b + a) for a < b), so ima32.u r11, i0, r2, c56, r1 followed by
  xor.testtanz.chan0 !c0, p0, r2, i0 sets p0 to a < b unsigned in 64 of 64 pairs (unsigned only, not
  padded, with r11 as the destination and the sources r1 and r2 as a and b: all pairs of the eight
  values 0, 1, 0xffff, 0x10000, 0x7fffffff, 0x80000000, 0x80000001 and 0xffffffff, 28 of them with a
  < b, the equal pairs and the pairs across the sign boundary included), where E472's formula takes
  six instructions and was run on the 64 pairs of those eight values; the high word was run for b *
  0xffffffff + a only (its source 2 is c56 = 0xffffffff in all 75 cases).
  *usse; HW, infer; data: `usse-ima32hi`, `usse-ucmp2`.*
- `E502` Under multisampling the pixel program's iterated position is the pixel's x + 0.375 and y +
  0.125, the same as in mode 0 and for the five CR_TE_AA values tried (0, 0x20000000, 0x60000000,
  0xa0000000, 0xe0000000; mode 0 only with 0x20000000), not the pixel centre: in 48 identity-map
  runs (40 configurations of modes 0, 1, 2 and CR_TE_AA 0 to 0xe0000000 at five target sizes from 64
  x 64 to 128 x 128, four of them run three times; 96 jobs, an x job and a y job a run) 401977 of
  the 402432 stored pixels of the x jobs decode to a pixel with those offsets, the other 455 hold
  the background colour, none holds any other value, a CR_TE_AA of 0 and of 0x20000000 give
  byte-identical outputs in 10 of 10 pairs of configurations (20 of 20 jobs) and the 8 repeat runs
  are byte-identical to their first runs (16 of 16 jobs).
  *isp; HW, infer; data: `isp-msaa-ident`.*
- `E503` A multisampled render stores in each 32 x 16 tile of the target the pixels of a half window
  of the tile's own area, every sample slot written: tile (tx, ty) holds the source pixels from x =
  32 tx + 16 b31 and y = 16 ty + 8 b30 (b30 acts in mode 2 only; stated for modes 1 and 2, the modes
  run with the bits: mode 0 ran only with CR_TE_AA 0x20000000, where b31 = b30 = 0), 16 columns by
  16 rows in mode 1 and by 8 in mode 2, each stored twice in x (modes 1, 2) and in y (mode 2), where
  b31 and b30 are CR_TE_AA bits 31 and 30; the rule was read post hoc from the 64 x 64 runs (88
  tiles of 11 configurations, 88 of 88) after the declared test decoded nothing (E502), and agrees
  with all 634 tiles of the 29 configurations at the four sizes declared held out (634 of 634: an
  agreement found after the rule was written, not a prediction) and with the 64 tiles of the 8
  repeat runs, 786 of 786 tiles of the 48 runs of E502, of which 773 are written in all 512 pixels;
  the declared H30a (a tile of its own pixels, only its 16 x 16 corner written) failed as a test (0
  of 48 runs decodable) and post hoc holds in its origin only, not in its corner.
  *isp; HW, infer; data: `isp-msaa-ident`.*
- `E504` CR_TE_AA reaches the register as poked in 21 of 21 jobs and acts in the TA's output, not
  only after tiling: against the CR_TE_AA 0x20000000 job of the same size and mode, a value of 0
  gives 0 differing dwords of the 1150976-dword parameter buffer and of the 6144-dword TA data (3 of
  3 pairs), 0x60000000 and 0xa0000000 each differ in 76 and 132 dwords (mode 0 and mode 2, 64 x 64),
  0xe0000000 in 204 and 279 (64 x 64, mode 2, twice) and 805 and 367 (128 x 128), and 0x40000000,
  0x80000000 and 0xc0000000 remove the triangle (3969 of 4096 pixels differ, 6 of 6).
  *isp; HW, infer; data: `isp-msaa-te-dumps`.*
- `E505` At sizes whose macrotile rule has two macrotiles in a row (n = 2) the first and third
  boundary fields of the macrotile words are free: at 256 x 256, 28 of 28 poked words (B1 of each
  word 0 to 3 and 0 to 7, B3 5 to 8 and 9 to 12, four partitions of each word) draw exactly, and at
  the held-out 512 x 384, 8 of 8 (B1 zero and one less, B3 one and four more, on each word) draw
  exactly, 3 of 3 control runs a size exact.
  *ta; HW, infer; data: `ta-mtile-fields`.*
- `E506` At sizes with four macrotiles in a row (n = 4: 640 x 480, 768 x 640, 1280 x 720) the first
  and third boundary fields are not free and the declared PB and PC fail: of the 39 fit cases at 640
  x 480 only 2 draw exactly (CR_TE_MTILE1 B3 25 and 28, both beyond the 20 tile columns) with 34
  faults and 3 wrong images, and of the 16 held-out cases at 768 x 640 and 1280 x 720 2 draw exactly
  (768 x 640, CR_TE_MTILE1 B3 one and four more) while PB and PC predicted all 16; B1 zero or one
  less faults the job in 8 of 8 of them; PA, expected to fail, is right in 16 of 16 of them and in
  34 of 39 at 640 x 480; the controls draw exactly 3 of 3 a size.
  *ta; HW, infer; data: `ta-mtile-fields`.*
- `E507` Our stack's 4x multisampled render (mode 2, CR_TE_AA 0xe0000000, the closed driver's sample
  words) with the unpoked rule words completes at 64 x 64, 128 x 64, 128 x 128, 256 x 128, 96 x 48
  and 192 x 96 and faults the job (BIF fault at pages 0x20006, 0x20008 and 0x2000a) at 320 x 160,
  384 x 192, 448 x 224, 512 x 256, 512 x 384 and 640 x 480, 6 of 6 held-out sizes; the poked family
  U2 (words 0x802002, 0x802002, stride 4) draws the same image as the rule at 64 x 64.
  *ta; HW, infer; data: `ta-mtile-msaa`.*
- `E508` On our stack the 64 x 64 render under the closed driver's 4x settings (mode 2, CR_TE_AA
  0xe0000000) stores 4096 pixels that hold 1024 distinct source pixels, the 16 x 8 window of each
  tile written twice in x and in y: the 4096 stored pixels are not a 64 x 64 image of the pixels;
  the identity maps of E502 cannot show an average, since every sample slot of a pixel holds the
  same iterated value and an average equals it.
  *isp; HW, infer; data: `isp-msaa-ident`.*
- `E509` At 256 x 256 (two macrotile columns) the second boundary B2 alone decides: of 56 poked
  words that change only B1 or B3 over 0 to 12, 16 and 20 (below and above B2, so also non-monotone)
  all 56 draw exactly, and of 28 that change only B2 none does (16 fault, 12 wrong); the stride is
  not the rule's in 12 of 12 (256 x 256: 0 to 31 draw wrong, 33 to 128 fault), bit 31 set faults,
  and at the held-out sizes B2 one and four more is not exact in 12 of 12 (512 x 384: 4 wrong; 768 x
  640 and 1280 x 720: 8 faults); with four macrotile columns (640 x 480) B1, B3 and B2 are all read
  and a B2 at or past B3 (24 and above) of CR_TE_MTILE2 draws exactly.
  *ta; HW, infer; data: `ta-mtile-fields-risky`, `ta-mtile-fields`.*
- `E510` No single flip of the 32 sideband bits of the end-of-tile emit, from 0x200 and from 0x2200,
  resolves or blends a 4x render: of 64 jobs 50 write the plain triangle and background of 1248 and
  2848 pixels, bits 0 and 1 change the byte order of the colour (0xff403020 and 0x403020ff for
  0xff203040, no new colour), bit 2 packs two ARGB1555 pixels a dword (0x90c8, 0x83e0, 2048 dwords
  left at the fill), bit 3 writes 1024 pixels of 0xffffffff, bit 9 cleared from 0x2200 (0x2000)
  writes 128 background pixels, bit 12 set on 0x200 writes 14 values (four of them 0x0066 and 0x0000
  pairs, none a mix or a copy of the two colours), and 4 jobs fail (bit 9 cleared from 0x200 hangs,
  bit 11 faults from both, bit 12 set on 0x2200 hangs); no pixel holds an average of the two colours
  (the control image has 24 aligned 2 x 2 blocks that mix them).
  *isp; HW, infer; data: `isp-msaa-resolve`.*
- `E511` On our stack's 4x render the closed driver's 64 x 64 macrotile words (0x802002 and
  0x802002, stride 4) draw exactly at 96 x 48 and 128 x 64 and fault the job (BIF fault at
  0x10000012 to 0x10000016) at 128 x 128, 192 x 96 and 256 x 128; a macrotile of two tiles with only
  CR_TE_MTILE1 poked draws exactly at 128 x 128; the tile signature of every job that completes
  equals the unpoked rule's (3 of 3 U2 jobs here, 4 of 4 with E507's U2 job at 64 x 64; the 6 R jobs
  of E507 are the rule itself), and the 20 held-out and larger cases of the 26 declared were not
  run.
  *ta; HW, infer; data: `ta-mtile-msaa-risky`.*
- `E512` An instance sees its own unfenced stad: with every one of the 2048 instances of the 64 x 32
  fill storing a value of its own (0x5107E000 + n, n = y * 64 + x from pa0) to a dword of its own
  and loading it back, the load returns that instance's own value in 2048 of 2048 pixels in each of
  nine cases (ldad, ldad.bypassl1, ldad.fcfill, ldad on drc1 and ldad after a wdf drc0 with no idf,
  two stad of V1 then V2 where the load returns V2, with an idf drc0, bif and its wait between, and
  with the idf at the end), and a load of another region that was never stored returns the fill
  value in 2048 of 2048 in the tenth, and 2048 dwords of the region changed in all ten cases (32
  values read, 2016 counted), among them the seven with no idf at all and no fence at the end.
  *usse; HW, infer; data: `usse-store-own2`, `usse-store-own`.*
- `E513` A branch over code that a test of pa0 selects is taken by a whole 2x2 quad, from the test
  of its top-left lane: with `xor.testtaz.chan0 !c0, p0, r7, #0` and `!p0 br` over the code, the
  four lanes (the pixels 0, 1, 64 and 65) ran it for pa0 == 0 and the four lanes 2, 3, 66 and 67 for
  pa0 == 2, and no lane for pa0 == 1, 3 and 64 (a value no instance has); in the quads that ran the
  code each lane saw its own stad, unfenced in 2 of the 3 cases that load (8 of 8 lanes; the third
  has an idf and its wait between: 4 of 4 lanes) and the four stores of a quad reached the host in
  each of the 5 jobs that stored (cases 0, 2, 3, 4 and 6 of the table, three of them, 0, 4 and 6,
  with no fence at all).
  *usse; HW, infer; data: `usse-store-own2`, `usse-store-own`.*
- `E514` An unfenced stad is seen by a load of another instance that ran earlier and in part by one
  that ran later, [infer] as a rule of timing (raster and tile order, not a fence): in the pairs
  with the x and y neighbours in the same 2x2 quad (n ^ 1 and n ^ 64; the diagonal n ^ 65 was not
  run) every one of 2048 loads returned the partner's value in each of four cases (with and without
  an idf and its wait), with the instances of other quads (n ^ 2: the next quad in x, n ^ 128: two
  rows on, n ^ 32: 32 columns on) 1088, 1088 and 1024 of 2048 (all 1024 of the loads whose partner
  has the lower number, and 64, 64 and 0 of those whose partner has the higher), after 64 and 192
  nop 1816 and 2008 of 2048 for n ^ 2 (1024 lower, 792 and 984 higher) and 1024 for n ^ 32 after 192
  nop (no higher), and for the partners n ^ 1023, which lie in the other column of 32 (the left half
  is partner of the right half), 1024 of 2048 in the three cases (no idf, an idf and its wait, 192
  nop): exactly the pixels with x from 32 to 63.
  *usse; HW, infer; data: `usse-store-own2`, `usse-store-own3`, `usse-store-own`.*
- `E515` stad.repeatN and ldad.repeatN move the pointer registers r40 to r55 (r56 to r71 for a load)
  by the form's increment when they are used and leave the unused ones, for N = 5 to 16: iteration i
  uses r(b + i) in 10 of 10 plain stad.repeatN [r40,+#0] cases (N = 5, 6, 7 and 9 to 15), and with
  all sixteen pointers read through a marker, the post-increment form [r40,#K++] moved r(40 + i) by
  K dwords for i < N and no other pointer in 15 of 15 cases (K = 1: N = 5 to 16; K = 2: N = 8, 12,
  16), the pre-increment form [r40,++#K] likewise in 4 of 4 (N = 8, 12, 16 with K = 1; N = 8 with K
  = 2), and ldad.repeatN r10, [r56,#K++] and [r56,+#0] iteration i loads from r(56 + i) into r(10 +
  i) in 11 of 11 plain cases (N = 5 to 7, 9 to 16, the destinations not reached holding their
  markers) and moved r(56 + i) for i < N in 10 of 10 post-increment cases (K = 1: N = 5 to 9, 12,
  15, 16; K = 2: N = 8, 12), in a client pixel task.
  *usse; HW; data: `usse-repeat-ptrs`.*
- `E516` stad.fetchN [rb,+#k] stores at the dwords b + k + 1 to b + k + N for k = 2, 3, 4, 7, 8 and
  15 (fetch4), 3 (fetch8) and 2 (fetch16) (8 of 8 cases), [rb,#k++] stores at b + k to b + k + N - 1
  and moves rb by N for k = 1 to 4 (4 of 4: fetch4 with k = 2 and 3, fetch8 with k = 2, fetch2 with
  k = 4; k = 1 from E482), and [rb,++#k] stores at b + k + 1 to b + k + N and moves rb by N for k =
  1 and 2 (3 of 3: fetch4 with k = 1 and 2, fetch16 with k = 1), in a client pixel task; the plain
  rule was predicted (8 of 8), the post and pre rules are fits to their 4 and 3 readbacks, read
  after the run, whose predictions failed.
  *usse; HW; data: `usse-repeat-ptrs`.*
- `E517` An ALU instruction reads the old value of a load's destination until a wdf: `ima32.u r11,
  r10, #1, r12` after `ldad r10` with 0, 1, 4, 16, 32 and 48 `nop` between read the marker (6 of 6
  cases, r11 = marker + 7 and r10 still the marker when stored), so the ALU reader has no interlock
  either; a load not waited for had landed when a stad read r10 after 40, 100 and 128 `nop` and not
  after 48 and 64 (3 of 5 cases landed), so it can land with no wdf, not as a function of the slot
  count; and a `mov r10, #X` after an `ldad r10` and before its `wdf` is overwritten by the load in
  4 of 4 cases (0, 4, 16 and 32 `nop` between), while a mov after the wdf wins (1 of 1).
  *usse; HW, infer; data: `usse-load-readers`.*
- `E518` No limit on outstanding loads was seen up to 192 ldad on one counter: 104, 112, 128, 160
  and 192 `ldad` on drc0, and 128 and 192 on drc1, each with the first 100 into r4 to r103 and the
  others reloading r4 onward with a different line, then one wdf, left every one of the 8 sampled
  registers holding the line of its last load in 7 of 7 jobs (the 4 or 5 reloaded registers read per
  job, 4 of 4 up to 5 of 92, the new line, the others the first line), no reload seen lost, and no
  job hung or faulted, in a client pixel task.
  *usse; HW; data: `usse-reload-growth`.*
- `E519` The phas request that runs is not an interval: it counts modulo 256, so that a request T
  runs when T mod 256 is 4 to 192 and hangs the job when it is 0 or 196 to 252, in every request
  run: 100 to 120 and 148 to 156, 164 to 188 and 260 to 448 (all multiples of four there) ran (6 +
  10 + 45 + 3 = 64 requests, o0 = the marker written to the last register of the request, or r123),
  228 to 248 and 452 to 504 hung (6 + 14 = 20), and the 15 requests 512 to 1016 chosen by the rule
  (8 predicted to run, 7 to hang) all did as predicted (15 of 15, 8 ran, 7 hung).
  *usse; HW, infer; data: `usse-phas-low`, `usse-phas-low2`, `usse-phas-high-a`, `usse-phas-high-b`,
  `usse-phas-high-c`, `usse-phas-high-d`, `usse-phas-high-e`, `usse-phas-mod`.*
- `E520` The addend of an emitpds control word matters: with the addends 0xFFF, 0x1000, 0x1001,
  0x1010, 0x1100 and 0x2000 the dwords that the started PDS program stores (dword 8 and dwords 16 to
  31) read 0x403, the value the fill's own run leaves, in 12 of 12 probes (6 in the first table,
  which ran them consecutively, 6 in the interleaved second table); of the other 27 probes, 24 read
  3 or 2 (the base addend 0x100 in 11 of 11, the addends 0, 0x10, 0xF0, 0xFF, 0x101, 0x110, 0x200,
  0x400, 0x4000, 0x8000 and 0x10000 once each in the first table, and 0x200 and 0x4000 in the
  second), 0x800 read 0x401 in the first table and 0x400 in the second (2 of 2), and 0x10 read 0x400
  in the second table; every emitting job faulted (37 of 39) or hung (2 of 39, the addend 0x2000 in
  each table), in a client pixel task.
  *usse; HW, infer; data: `usse-emit-addend`, `usse-emit-addend2`.*
- `E521` iaddu32 writes the low 16 bits of source 1, zero-extended, plus source 2, mod 2^32: its
  source 1 is zero-extended in the value it writes, in 16 distinct pairs of two datasets run before
  11.28, seven of which a sign extension would write otherwise (bit 15 of the low half of r1 set):
  (r1, r2) = (0x8000, 0x8000) writes 0x10000 (a sign extension writes 0), (0xffff, 1) 0x10000,
  (0xffffffff, 1) 0x10000, (0x7fffffff, 1) 0x10000, (0xffffffff, 2) 0x10001, (0x7c23a2bd,
  0x47b003f0) 0x47b0a6ad and (0xb99ede85, 0x87261f80) 0x8726fe05, and the nine others agree with
  both; the zero extension fits 16 of 16 and the sign extension the nine with bit 15 of the low half
  clear.
  *usse; HW; data: `usse-decoder-vectors`, `usse-integer`.*
- `E522` The simulator of 11.28 matches 5406 of the 5750 USSE vectors of the usse runs of 11.23 to
  11.27, stops on 135, skips 9, leaves 156 out of the replay and differs on none (the model of 11.27
  matched 3148, differed on 218 and stopped on 2100), and over all 34510 USSE vectors 30260 match,
  1112 are fitted, 908 stop and none differs.
  *usse; HW; data: `vectors-usse-nokernel`.*
- `E525` ima32.u r10, iK, r1, r2, r3 writes bits 63:32 of the exact 64-bit a * b + c to iK and bits
  31:0 to r10 on generic 32-bit register operands: 282 of 282 jobs (42 corner triples and 200 random
  triples with K = 0, then K = 1 and K = 2 over 20 of the random triples each), the other two i
  registers keeping their presets 0x55, 0x66 and 0x77 in 282 of 282; the reading 'iK = the high word
  of a * b alone' (no carry from c) fits 141 of 282 and 'iK = the carry out of the 32-bit sum (a * b
  mod 2^32) + c' fits 10 of 282.
  *usse; HW; data: `usse-ima32hi-generic`.*
- `E526` ima32.s r10, iK, r1, r2, r3 (the assembler accepts the .s form with the extra operand, word
  0xD000024001404103 for K = 0) writes bits 63:32 of the signed 64-bit sext(a) * sext(b) + sext(c)
  to iK and bits 31:0 to r10: 282 of 282 jobs over the 282 triples of E525 (K = 0, 1, 2 as there);
  the readings 'c zero-extended' fits 142 of 282 and 'the unsigned high word' 32 of 282 (the same
  triples); the other two i registers kept their presets in 282 of 282.
  *usse; HW; data: `usse-ima32hi-signed`.*
- `E527` The two-instruction unsigned compare of E501, ima32.u r11, i0, r2, c56, r1 then
  xor.testtanz.chan0 !c0, p0, r2, i0, sets p0 to a < b unsigned in 252 of 252 seeded pairs (200
  random, 20 equal, 12 differing in one bit at the positions 0, 8, 15, 16, 24 and 31 in both orders,
  10 with equal low half and 10 with equal high half; 127 with a < b), and with 0, 1 and 3 nops
  between the two instructions over 48 of those pairs each (24 random, 8 equal, 8 with equal low
  half, 8 with equal high half; 21 with a < b): 48 of 48 for each of the three paddings.
  *usse; HW; data: `usse-ucmp2-random`, `usse-ucmp2-pad`.*
- `E528` A signed compare built from the high word of ima32.s exists and is exact on the pairs run:
  ima32.s r11, i0, r2, c56, r1 (c56 = 0xffffffff, signed -1: the signed 64-bit a - b, whose high
  word is 0xffffffff for a < b and 0 otherwise) then xor.testtanz.chan0 !c0, p0, i0, #0 (true when
  i0 is nonzero) sets p0 to a < b signed in 164 of 164 pairs (the 64 pairs of the eight values 0, 1,
  0xffff, 0x10000, 0x7fffffff, 0x80000000, 0x80000001, 0xffffffff, the equal pairs and the pairs
  across the sign boundary included, and 100 seeded random pairs; 78 with a < b signed).
  *usse; HW, infer; data: `usse-scmp`.*
- `E529` With enc[39] = 0 (the o join, chan0) the two parts of the class 9 test field are ORed and a
  part that is absent from the field counts as true: the rule (zero part: tanz if bit 41, else taz
  if bit 40, else true; sign part: pat if bit 43, else nat if bit 42, else true; p0 = zero part OR
  sign part) fits the 90 cases of and r1, r2 over the 15 field values 1 to 15 and six input pairs
  (90 of 90, a rule read from those 90 readbacks, so a fit to them: the first prediction, the parts
  ORed with an absent part false, fitted 75 of 90, the parts ANDed 48 and the OR of the set
  conditions 75, and the runner's verdict was NONE) and predicted, written before the run, all 270
  cases of a fresh run on or and xor with registers and and with #7 (three probes, 15 values over
  six other input pairs each: 90 of 90, 90 of 90, 90 of 90); in particular every one-part field (1,
  2, 4, 8) and the fields 3 and 0xc read true for every input of the 90 cases, which is the 'a
  one-part test is always true under the o join' reading.
  *usse; HW, infer; data: `usse-rawjoin-o`, `usse-rawjoin-o2-or`, `usse-rawjoin-o2-xor`,
  `usse-rawjoin-o2-and7`.*
- `E530` The chan field enc[38:36] of an and test word with the a join changes what the test reads:
  the prediction written before the runs (the chan field does not change a test of a 32-bit result,
  p0 as for chan0) failed for each of the seven values 1 to 7 (the readings fit 26, 26, 26, 32, 30,
  32, 30 of the 36 cases of the six fields 1, 2, 4, 8, 9, 0xa over six input pairs); chan 1, 2 and 3
  read the same constant for every input pair (taz 0, tanz 1, nat 0, pat 1, taz with pat 0, tanz
  with pat 1: 36 of 36 equal across the six pairs and the three values), chan 4 and chan 6 read tanz
  and pat as the result's (true when the result is nonzero, true when it is not negative) and taz
  and nat as false in all six pairs (the same readings in the two tables), and chan 5 and chan 7
  read taz and nat as the result's and tanz and pat as true in all six pairs (the same readings in
  the two tables).
  *usse; HW, infer; data: `usse-rawchan-1`, `usse-rawchan-2`, `usse-rawchan-3`, `usse-rawchan-4`,
  `usse-rawchan-5`, `usse-rawchan-6`, `usse-rawchan-7`.*
- `E531` A firmware (EDM) task of our own runs: with the start dword of PDS #13's general slot
  (instruction index 6, E146) retargeted at load to a page of our code at the kernel code heap +
  0x20000 (index 0x4000), a 3-instruction wrapper that only jumps to the closed task the slot used
  to start (mov pclink, limm; lapc, the index taken from the replaced CODE_WORD record) left the EDM
  as it was in the one run that finished its evaluation (p1129-s2b-null: ticks at 998.0 Hz, miscinfo
  answered, a 64x32 fill exact, 0 of 2048 pixels differing, a 64x64 triangle exact, 0 of 4096, no
  BIF fault, EVENT_STATUS2 0x400) and in the gate of the earlier attempt (p1129-s2-null: the same
  fill and triangle exact, 994.2 Hz).
  *edm; HW; data: `firmware-tasks-null-wrapper`.*
- `E532` A stad from a firmware task of our own lands, and the tick event hands the task pa0 = 0x2,
  pa1 = 0x02000000 and pa2 = 0x01061a70 in 2 of 2 runs: a wrapper that reads a command dword of its
  results page (ldad.bypassl1, wdf) and stores pa0, pa1, pa2 and a marker, then idf drc0,bif, wdf
  drc0 and the state flag, finished within the tool's 100 ms of the command with all four dwords
  stored in 2 of 2 runs; the prediction declared before the runs, that a tick has pa1 = 0, was
  falsified (pa1 has bit 25 set).
  *edm; HW, RE, infer; data: `firmware-tasks-memory-only`.*
- `E533` ldr in a firmware task of our own reads the registers as the host does (CORE_ID 0x01150000
  and CORE_REVISION 0x0001000d in 2 of 2 runs, and CR_TIMER a count that is not the initial fill
  value 0xdeadc0de: 0xc782bb2b and 0xd5cd8747), and, after a general-slot task of ours that wrote
  sa64, sa100, sa127, sa20, sa24, r20, r21, i0, i1, p0 to p3 and pclink and ended with nop.end,
  without jumping to the closed task, the EDM's tick stopped: in the one run of item 12 (stage 8,
  stopped on its own trigger) HostCtl dword 12 stayed at 1190 and USE0_SERV_EVENT at 1195 over three
  reads 20 ms apart, the command the task had armed for the next event never ran (the task both
  skipped the closed task and wrote many registers in that one run, so which of them stopped the
  tick is not separated), and one debugfs reset rebuilt the stock firmware, which ticked at 967.1 Hz
  after the reset and passed the stock gate (0 of 2048 and 0 of 4096 pixels differing, 971.6 Hz).
  *edm; HW, infer; data: `firmware-tasks-ldr-and-persistence`.*
- `E534` In a firmware (EDM) task of our own, a str to CR_REG_0814 (0x0814, 17 bits) or
  CR_PDS_REG_0A78 (0x0a78, 6 bits) is seen by the next ldr of the same register and lands in the
  register the host reads, with nothing between them and at every distance run: in 318 of 318 runs
  the predicted (L, H) came out; 228 of the 306 matrix runs could tell a str that landed from one
  that did not (the value finally stored differs from the one the register held), 138 on 0x0814 and
  90 on 0x0a78, and those 228 are the ones that show it. Per case: str then ldr with 0, 1, 2, 4 and
  16 nops between, with a wdf, with an idf and a wdf, with an idf alone, or with a second str read B
  (or C) and left the host reading B (or C); an ldr of the other register read that register's own
  value, which kept it (X8); an ldr before a str is not changed by it (X6, 30 of 30 that could
  tell); a stad of the result, then a load of the run id, a wdf and two more stores, then the state
  flag with no idf, landed in 18 of 18 (X9).
  *usse; HW, infer; data: `firmware-tasks-str-then-ldr`, `vectors-usse-fwtask-9b`.*
- `E535` With a different marker in every job, E519's two-phase fill (started with 8 temporaries,
  phas #T, r123 written with the job's own marker and read back as o0) read the job's own marker in
  2048 of 2048 pixels for the 6 requests T = 260, 264, 300, 316, 376 and 448 in both runs (12 of 12
  jobs) and for the 6 controls that write inside the request (T = 124, 128 and 192 with r123, T = 8,
  32 and 64 with r3, r31 and r63: 12 of 12 jobs), and did not read it in any pixel the report lists,
  for the 6 requests T = 4, 8, 16, 32, 64 and 100 that write r123 (0 of 12 jobs: run a lists all
  2048 pixels of each of its six jobs, run b only its top four values, 1656 to 2040 of 2048 pixels
  per job), where the pixels read other values (0x403, 0, 0xa4a5a6a7, E519's marker 0x7e57007b,
  0x7e570003 and, in the run in reverse order, the markers of earlier jobs of that run: 17 of the 24
  values its report lists for those six cases); so a write to r123 is not seen by the read of r123
  in the same job when the request is 100 or less, the read-back of r123 at 260 to 448 in E519 was a
  write that landed, and [infer] five of those requests (260, 264, 300, 316 and 376, which the
  modulo-256 rule makes 4, 8, 44, 60 and 120 registers) allocated at least 124.
  *usse; HW, infer; data: `usse-q147-a`, `usse-q147-b`, `vectors-usse-q147`.*
- `E536` A firmware task of ours (state2.s, cmd 1) that wrote sa64, sa100, sa127, sa20, sa24, r20,
  r21, i0 and i1 (a random value each, none equal to anything the controls read) and set p0 to p3 to
  0, 0, 1, 1, armed a reader for the next event and then tail-called the closed general task, left
  the EDM running (tick rate 910.8 to 1005.4 Hz after each of the 9 steps, 3 writers, 3 readers
  after 1200 ms and 3 readers after a client fill, the 3 fills diff 0 of 2048; no stop trigger, no
  log line, no reset), and the reader the writer armed ran at the next event (the writer's flag
  0.42, 0.47 and 0.70 ms after the command, the reader done 1.50, 1.53 and 1.74 ms after it) and
  read the values written for sa100, sa127, sa20 and sa24 (12 of 12 values in 3 of 3 rounds), r20
  and r21 (6 of 6), i0 and i1 (6 of 6), p1 = 0 (3 of 3, against 1 in all 8 other readings) and
  pclink = 6 (3 of 3, against 0x98 in the 8 readings of the controls, the 1200 ms readers and the
  fill readers; [infer] 6 is the value the writer's own tail triple wrote, a write every pass of the
  wrapper makes), p2 and p3 = 1, 1 (as written, but also 1, 1 after 1200 ms, 0, 0 in the controls
  and 0, 1 after a fill: they move between readings with no writer in between, so they show
  nothing), but sa64 = 2 (3 of 3, as in both controls) and p0 = 1 (written 0); 1200 ms (1200 ticks
  of the closed task) later sa (12 of 12), r (6 of 6) and i (6 of 6) were still there, and a client
  fill between left sa (12 of 12) and i (6 of 6) and replaced r20 and r21 (r20 = 0 and r21 = 0x1000,
  0x2000, 0x3000: 0 of 6 values ours).
  *edm; HW, infer; data: `firmware-tasks-tail-pair`, `vectors-usse-fwtask-p1130`.*
- `E537` A firmware task of ours (state3.s, cmd 4) that wrote sa64, sa100, sa127, sa20, sa24, sa65,
  sa63, r20, r21, i0 and i1 and set no predicate, stored its done flag with the reader armed (cmd =
  9) and tail-called the closed general task was not followed by the reader it had armed for the
  next event within 100 ms (1 of 1 run of this writer); HostCtl dword 12 advanced 6 in that 100.3 ms
  window (ticks_during = 6) and then did not move: it read 0x9db and USE0_SERV_EVENT 0x9e0 in both
  dumps taken seconds later (the status dump and the register dump, so no event ran between them);
  EVENT_STATUS2 0x400, BIF_INT_STAT 0x00080000, BIF_FAULT 0, no log line, and one debugfs reset
  restored the stock firmware (ticks 999 Hz, GETMISCINFO answered, fill and triangle diff 0 of 2048
  and 0 of 4096); the writer of E536 (state2.s cmd 1, with p0 to p3 set to 0, 0, 1, 1 and without
  sa63 and sa65) did not stop the tick in 3 of 3 rounds.
  *edm; HW, infer; data: `firmware-tasks-writer-variants`.*
- `E538` With pa1 bit 25 masked in the test of four entry stubs (one per PDS #13 slot, each logging
  pa0, pa1 and pa2 when pa1 & 0xfdffffff is non-zero and then taking its own tail call), one
  GETMISCINFO kick with no job reached the general slot only (slot 0: hits flag 1; the other three
  slots' 12 log dwords 0) with pa0 = 2, pa1 = 0x03000000 and pa2 = 0x01061a70 in 3 of 3 runs, and a
  window of 50 ms of ticks before the kick logged nothing in any slot (3 of 3 windows, about 150
  ticks in all); the frozen prediction pa1 & 0xfdffffff = 0x100 (E155's reversed status bit 14)
  failed (it is 0x01000000) and so did its falsifier 0x4000 (E146's reading).
  *edm; HW, infer; data: `firmware-tasks-kick-event-words`, `vectors-usse-fwtask-p1130`.*
- `E539` A firmware task of ours that sets its state flag to busy, spins n iterations of a
  three-instruction loop (ima32, a test, a branch) and sets the flag to done, with every wrapper
  pass that finds the flag busy storing an overlap flag, ran 10 times (n = 10000 four times, 30000
  and 100000 three times each) with the overlap flag 0 in 10 of 10 runs, taking 0.73 to 0.97 ms (n =
  10000), 2.07 to 2.43 ms (30000) and 6.21 to 6.92 ms (100000) from command to done as the host saw
  it, and HostCtl dword 12 counted 38 to 42 ticks in the 38.2 to 44.3 ms windows: within 2.2 of the
  0.997 ticks per ms expected in all 10 runs (none more than 3 behind, the run's limit), +1.7 to
  -0.7 in the seven runs of n = 10000 and 30000 and 1.9 to 2.2 behind in the three of 100000.
  *edm; HW, infer; data: `firmware-tasks-slow-task`, `vectors-usse-fwtask-p1130`.*
- `E540` In a firmware task of ours started with TRC T = 8, 9, 12, 16, 24 and 31 (32 to 124
  temporaries) a marker written to r(4T - 1) (r31, r35, r47, r63, r95 and r123) read back as written
  in 6 of 6 runs, with the closed task called after it (the tail call), the tick advancing and the
  status registers healthy after each (arming rates 965.8 to 999.4 Hz), and the marker written to
  the register past the allocation (r32, r36, r48, r64 and r96 for T = 8, 9, 12, 16 and 24; none for
  T = 31, whose next register r124 cannot be named) was not read back in any of the 5 runs (0 of 5;
  one job and one read per T, so "never" is not shown): it read 0 (T = 8 and 9), 0xb8b9babb (T =
  12), 0xd0000e00 (T = 16) and 0xd00009c0 (T = 24); r0 read 0 in all 6; TRC 32 and above have no
  result: the arm of T = 32 failed (its saved error is cut off and kernel.log holds no refusal line;
  [infer] the fork's arm gate refuses a TRC above its free maximum unless trc_hazard=1 is given,
  which the tool as it ran gave only from 49), and arming with the hazard word was not made.
  *edm; HW, infer; data: `firmware-tasks-trc-ladder`, `firmware-tasks-final-stock-check`,
  `vectors-usse-fwtask-p1130`.*
- `E541` The TA's object holds a vertex as 1 + N dwords less, for each coordinate set whose format
  bit is set, the components its size code names minus half of them rounded up (1, 2, 3, 3 and 4
  components for codes 1 to 5): that rule gives the stored dwords of 12 of 12 held-out jobs, the
  format word's bits 15:8 are 1 + N and the four set masks follow the size and format words in 56 of
  56 completed jobs; in the `alt` pattern 3 of 7 jobs did not complete (N = 2 faulted, N = 3 and 8
  hung), and a set described past the outputs the vertex program writes does not decide it.
  *ta; HW, infer; data: `ta-object-format`.*
- `E542` The region test of triangles holds at every tile boundary tried: over 35 jobs (27 with a
  vertex on a 16-pixel line at 64, 128 and 256 pixels, copy 2's exactly on it in 24 five-copy jobs,
  the first triangle's in the 3 single-triangle fit jobs, and 8 with an edge exactly through a tile
  corner), 14656 (primitive, tile) pairs, a 16 x 16 tile is met iff the bounding box meets it (high
  sides open, low sides closed) and no edge has the four corners strictly outside: 0 mismatches,
  where the landed fit (half-open only between a region's tiles) is wrong in 11 of 23 held-out jobs
  and in 4 of 4 fit jobs, by listing tiles the TA does not list (27 pairs, none the other way).
  *ta; HW, infer; data: `ta-tri-region`.*
- `E543` Lines run through the TA with ISP word 0 + 0x8000 and index list topology 1 (26 of 26 jobs
  complete: the 20 one-line jobs write one object of 2 vertices, the 6 multi-line jobs one or two
  objects of 2, 4 or 6 vertices): a one-line object's regions are those a thickened segment meets,
  not those the exact segment meets (right in 4 of 23 held-out jobs), the reach being 0.5 pixel at
  ISP word 1 width 0x10 (near-vertical: listed at 0.4375, not at 0.5), and at the widths 0x20 to
  0xf0 (28 near-vertical jobs) between 0 and 1.0 pixel at 0x20, 1.497 and 2.0 at 0x40, 3.493 and 4.0
  at 0x80, 6.487 and 8.0 at 0xf0 (listed up to the first, not at the second; w / 32 fits, as does
  any reach inside those brackets), but not by one distance at width 0x10 (near-vertical and
  near-horizontal lines differ by about 0.12 pixel); the multi-line objects are not predicted.
  *ta; HW, infer; data: `ta-line-point`.*
- `E544` A point's size is the first coordinate output of its own vertex, read when OUTSEL bit 8 is
  set, in pixels: the point covers the pixels whose centre is in [v - S/2, v + S/2) in x and y, in
  40 of 42 sized jobs (sizes 0.5 to 256, pixel-centre, corner and fractional vertices) and in 4 of 4
  jobs with a different size a vertex; without bit 8 a point draws no pixel (16 of 16 jobs with the
  pixels read), and its tile list is that of a footprint of at most one pixel.
  *ta; HW, infer; data: `ta-points`, `ta-line-point`.*
- `E545` In a two-object stream, of the fields of one block's VDM_STATE1 flipped (bit 8, bits 11:9,
  bits 15:13, bit 17, bit 25 and the closed driver's two word forms; the grid set bits 11:9 and
  7:0), each moves all that block's marks (viewport x, ISP word 1 in the object, own pixel shader)
  together or none: of 86 completed jobs 77 show all the control's marks, 8 the marked block's
  object absent (bits 11:9 = 0) and 1 neither (sg-v6-r0, the other block's object absent); bit 8,
  bit 25 and bits 15:13 = 2, 3, 4 change nothing (20 of 20), and the one word 0x0a022205 hung in 2
  of 2 runs and completed in 1 of 1, so the marks of a block move together under every field flipped
  and a hang is not a function of the word.
  *vdm; HW, infer; data: `vdm-state-units`.*
- `E546` With 126 vertices and a vertex program of R output rows, a vertex task of V = MAX_VERTICES
  + 1 vertices keeps every vertex in the TA's objects when R * V <= 32 (31 of 31 jobs, regular
  objects of 15 vertices) and breaks the regular objects when R * V >= 36 (21 of 21 jobs, no fault,
  no hang; vertices lost or repeated [infer]), at 33 depending on the program (5 regular, 4
  irregular; at the same R = 3 and V = 11, N = 6 splits and N = 5 and 8 do not, so R * V is not a
  sufficient statistic); the splitting is the same on every repeat (13 of 13) and the task's
  attribute rows (VDM_TASK1 bits 14:7) enter it: at R * V = 33 rows 8 splits objects that rows 2 and
  4 keep regular (4 of 12 jobs differ from the default rows); the top nibble of the index list's
  first trailing word changes no object in 9 of 9 jobs.
  *vdm; HW, infer; data: `vdm-vtask-capacity`.*
- `E547` In ordinary jobs CR_EVENT_STATUS shows PIXELBE_END_RENDER, DPM_3D_MEM_FREE and
  MADD_CACHE_INVALCOMPLETE in triangle jobs, TA_FINISHED, TPC_FLUSH and the DPM state and control
  bits only in the 256-pixel and partial jobs, a fill only PIXELBE_END_RENDER and a copy neither,
  and SW_EVENT with MASTER_INTERRUPT in 41 of 41 jobs in which one appears, and CR_EVENT_STATUS2
  shows OTPM_MEM_CLEARED in 5 of 20 depth-store and partial jobs and DPM_TA_FREE_LOAD in 1 of 10
  256-pixel jobs; the short pulses of PIXELBE_END_RENDER, DPM_3D_MEM_FREE and TA_FINISHED are 4.2 to
  6.0 microseconds at an average sampling interval of 1.06 to 3.68 and 5.7 to 6.1 at 2.36 to 5.58,
  at most a few samples wide, and what holds them that long is the firmware's acknowledgement
  [infer].
  *platform; HW, infer; data: `platform-event-bits`.*
- `E548` Armed one at a time through the host event enables, 7 of 41 bits raised a host interrupt of
  their own in a 64 x 64 triangle (CR_EVENT_STATUS bits 0 DPM_3D_MEM_FREE, 6 DPM_STATE_CLEAR, 9
  DPM_CONTROL_CLEAR, 18 PIXELBE_END_RENDER, 20 OTPM_INV, 26 MADD_CACHE_INVALCOMPLETE and
  CR_EVENT_STATUS2 bit 1 DPM_3D_FREE_LOAD) and 1 of 41 in a fill (bit 26); with TA_FINISHED and
  TA_TERMINATE the host saw none; three repeats give the first run's answer in 51 of 54 case-runs
  (21 of 24 for the 8 cases with an interrupt, 30 of 30 for the 10 without; the three misses are bit
  9 and STATUS2 bit 1 of the triangle and bit 26 of the fill), and the 24 unarmed controls raise
  none; that the armed bit is what raised the interrupt is inferred, the handler having read only
  TIMER and MASTER_INTERRUPT in all 82 armed jobs [infer].
  *platform; HW, infer; data: `platform-event-bits`.*

### 2026-11-09

- `E549` On the module built from the reworked phase 11.29 series (tip 3d9b8bdefe94: the code page
  read-only for the EDM, the stricter verifier, 6 of 6 series checks PASS, KUnit 106 debug off and
  172 on), the firmware tasks of E531 to E534 behave as before: the null wrapper, which only
  tail-calls the closed task from a page the EDM can now only read, is fetched and runs (ticks 994
  Hz, fill and triangle exact, no fault), so the EDM fetches code from a read-only page; the
  memory-only wrapper stores its marker (the tick's event words as in E532), ldr reads CORE_ID,
  CORE_REVISION and CR_TIMER (the first two equal the host's), the same-value str (X0, X1) lands as
  before, and one repeat of the 9b matrix on 0x0814 and on 0x0a78 (17 cases each, the discriminating
  value pair) reads the same (L, H) per case as E534, 34 of 34 as predicted.
  *usse; HW, infer; data: `firmware-tasks-recheck`.*
- `E550` In a firmware task of ours armed with TRC T = 32, 36, 40, 44 and 48 and trc_hazard=1 on the
  fixed module (srcversion 5AD04F33F6BCDA7B880E238) the arm and the job ran at each T (10 jobs: one
  per T, then one more per T), and a marker of the job's own (a random 32-bit value with bit 31 set,
  written by the host to parameter dword 8, never the same in two jobs) written to r123 read back as
  written in 10 of 10 jobs, r0 read 0 in all 10, every job was done within 100 ms, the tick advanced
  (arming rates 967.6 to 1016.9 Hz), EVENT_STATUS2 was 0x400, no BIF fault and no kernel log line of
  fault or hang, and the fill and the triangle were exact after the reset to stock after each of the
  10 (0 of 2048 and 0 of 4096 pixels differ); r123 is the top register of the T = 31 allocation that
  E540 already read back, so this shows that these arms run and a marker is read back through r123,
  and nothing above r123 and no allocation size at T = 32 to 48 was observed (r124 and up cannot be
  named); TRC 49 and above was not armed.
  *edm; HW, infer; data: `firmware-tasks-p1133-trc-first`, `firmware-tasks-p1133-trc-repeat`.*
- `E560` In a --coords --pixels fill of 2048 pixels (pa0 = (y << 16) | x, each pixel building its
  own coordinates and doing one smp) the four gate controls read the declared image under their
  hypotheses in 4 of 4 jobs (g1-tw16 a 16x16 twiddled identity map, g2-st64x32 a 64x32 strided one,
  g3-tw16-lod2 LOD 2 of a chain, g4-tw16-u-mirror a mirror), 4 of 4 again in the second run of the
  gate that run-all-1132.sh made (the dumps of the first run kept apart), the health triangle exact
  after each; this is the first smp of ours that ran in a --coords fill.
  *texture; HW; data: `texture-p1132-gate-first`, `texture-p1132-tx-gate`, `texture-p1132-run`.*
- `E561` In 28 windows of 64 by 32 texels over twiddled level-0 textures of 32-bit texels, 16x16,
  32x32, 64x32, 64x16, 64x64, 128x16, 128x32, 32x128, 128x128, 16x64 and 8x128, the index of texel
  (X, Y) is the plain interleave (Y in bit 0, X in bit 1, and so on) only up to 16 on each side:
  32x32, 64x32, 64x64, 128x32, 32x128 and 128x128 do not read plain Morton (D1: 512 of 1024 texels
  plain at 32x32, 512 of 2048 at 64x32, 512 of 4096 at 64x64, 512 of 4096 at 128x32, 2048 of 4096 at
  32x128, 1024 of 16384 at 128x128) while 16x16, 16x64, 64x16, 128x16 and 8x128 do (all texels); one
  law fits every size, fit on all 28 windows after the run: tiles of up to 16x16 texels interleaved
  as before (the whole texture when it is smaller) and the tiles in raster order with x first
  (32x32: i8 = x4, i9 = y4; 64x32: i8 = x4, i9 = x5, i10 = y4; 128x128: i8 to i10 = x4 to x6, i11 to
  i13 = y4 to y6), exact on 28 of 28 jobs (the 16384 texels of 128x128 included), and it gives the
  dwords of E441's levels 0 to 2 (the texel (28, 84) at 128 wide, (14, 42) at 64 and (7, 21) at 32
  read 0x29b0, 0x8ec and 0x23b, the plain indices of E441's decoded pairs (20, 108), (10, 46) and
  (5, 23), 3 of 3; E441's data were not used in the fit); the declared prediction (plain Morton at
  every size) held for the 16x16 control, 1 of 3 fit sizes (64x16; 32x32 and 64x32 failed) and 8 of
  24 held-out jobs, and the 32x32 control of the shapes group (shp-32x32-l0) failed under all three
  declared hypotheses for the same reason.
  *texture; HW, infer; data: `texture-p1132-tx-twiddle`, `texture-p1132-tx-shapes`,
  `texture-p1132-recomp`, `vectors-texture-p1132`.*
- `E562` On non-square twiddled textures (32x16, 128x16, 16x32, 64x4, 8x64; 32x32 as the square) the
  level read at a whole LOD is level l of a chain whose sides halve to 1 each (levels of max(1, w >>
  l) by max(1, h >> l) texels back to back, the last level 1x1, LOD above it clamping there),
  hypothesis chain=A: 8 of 8 fit jobs and 49 of 49 held-out jobs exact (7 control jobs: 6 exact
  under all three, the 32x32 window failed for E561's reason) (chain=B, the chain stopping at the
  short side's 1: 5 of 8 and 26 of 49; chain=D, square-padded levels: 1 of 8 and 6 of 49); the T0
  fields on 32x16 and 128x16 (maximum 8 values, bias 7, MIPFILTER 7 fractions, 44 jobs) read it
  under chain=A as they read a square chain, 22 of 22 fit and 22 of 22 held-out exact (B 18 and 14,
  D 5 and 3); the 32x32 control failed under all three because of the tile law of E561.
  *texture; HW; data: `texture-p1132-tx-shapes`, `texture-p1132-tx-fields`.*
- `E563` In 45 gradient and quad-derivative jobs of 64x64 chains read at a LOD between levels, the
  LOD read per pixel is a logarithm of a footprint (pwl_max4 and pwl_euc, exponent plus linear
  mantissa: 0 of 14 fit and 0 of 7 held-out gradient jobs exact, against 2016 to 2048 of 2048 pixels
  for max4 (a logarithm) on the diagonal cases at k = 2 to 5), but the footprint is neither declared
  rule on every case: with the gradients given as dudx, dvdx, dudy, dvdy, on these cases max4
  (largest component) is exact on 2016 to 2048 of 2048 pixels where only dudx and dvdx are set
  (gr-vx-k2 2016, gr-vx-k4 2048; euc 8 and 0), euc (the larger of the two vectors' lengths) is exact
  where all four are set (gr-all-k2 2024, gr-all-k4 2048, gr-neg-k2 2024; max4 8, 0 and 8) and for
  the quad's own derivatives with a v component (au-vx 2048, au-vy 2048, au-vx4 2048; max4 0, 0 and
  128), and no declared rule is exact on the two-u-term, two-v-term and u-with-dudy jobs (gr-uu-k2,
  gr-vv-k2 at most 8 of 2048, gr-uvy-k2 52); this partition was read from the vectors after the run
  and was not declared or held out (held-out exacts: euc 1 of 7); the declared hypotheses scored:
  gradients fit euc 2 of 14, max4 2 of 14, min 1 of 14, pwl 0 of 14, held out 1 of 7 for euc, max4
  and min, 0 of 7 for pwl; automatic LOD fit euc 5 of 7, max4, min, pwl_max4 and pwl_euc 4 of 7,
  held out euc 13 of 17, max4 11 of 17, pwl 11 of 17, min 4 of 17; on the diagonal ladder the
  fraction of the logarithm in 1/64 is truncated everywhere the columns tell (gr-diag-k2 2036, k3
  2016, k4 2032 and k5 2048 of 2048 exact under truncation, against 1524, 1520, 1856 and 2048 when
  rounding to nearest), the one exception being the column x = 5 of k2, k3 and k4 (12, 32 and 16
  pixels differ from truncation), where the footprint is 4.3125, 8.625 and 17.25 texels, the
  fraction 6.946/64 and the hardware reads 7/64.
  *texture; HW, infer; data: `texture-p1132-tx-lod`.*
- `E564` With bilinear filters and explicit gradients of five ratios (an-r1 to an-r5, ratios 2 to
  32) none of the 2048-pixel images is exactly any declared single-level bilinear formula (lodf =
  euc, max4 and min: 0 of 5 jobs each; pixels equal to max4 and euc 1279, 1540, 1528, 1580 and 1792,
  to min 391, 0, 0, 0 and 0); the declared control an-ctl (ratio 8) did not match either (1528 of
  2048 pixels under max4 and euc, 0 under min; the script printed MISMATCH against the declared hash
  b80690ea...), so the baseline, one bilinear tap at the level the footprint picks, is not
  established and the five ratios and the flips have no reference to be compared with; of the 15 bit
  flips at ratio 8 eleven give the control's image exactly (T0 bits 14, 15, 16, 28, 29 and T3 bits
  8, 9, 15, 20, 21, 22), so those 11 bits do not change this image, and four change every pixel
  (2048 of 2048 pixels differ from the control, 0 of 2048 equal any declared formula): T3 bit 11
  (cleared from the control's 0x00800800) reads 2048 distinct names from the start of level 0
  (0xd0000000, 0xd0000002, 0xd0000008, ...), T3 bit 12 (set) reads the constant 0xd0001554, and T0
  bits 27 and 30 read values that are no name of the buffer (935 and 90 distinct values, the first
  0x1fae245d and 0x7f9c0000); no anisotropic filtering was identified, and none could be told from
  the failed baseline, so nothing is claimed about whether the core has it.
  *texture; HW, infer; data: `texture-p1132-tx-lod`.*
- `E565` On a 16x16 twiddled texture with u swept over 64 positions (-1.5 + (x + 1/2) / 16, a pitch
  of one texel) or v swept over 32 positions (-1.5 + (y + 1/2) / 8, a pitch of two texels) the modes
  0 to 3 reproduce E033 in 12 of 12 control jobs (every declared mode47 hypothesis agrees on them);
  for modes 4 to 7 on the v axis (u inside) mode 6 and mode 7 read exactly the clamp image (bd-v6,
  bd-v7: 2048 of 2048 pixels each) and mode 4 and mode 5 read the repeat image, the same as mode 0
  (bd-v4, bd-v5: 576 of 2048 pixels equal the clamp model, and D5's row and column decode are those
  of bd-v0), while on the u axis (v inside) and on both modes 4 to 7 read other texels, some of them
  indices past the 256 of the texture (+324 to +366 in the row of y = 8 in every one of modes 4 to
  7; in modes 5 to 7 the first columns read texels inside the texture), no u-sweep job exact under
  clamp or border (0 of 4 each) and under nomask at most 4 of 2048 pixels, and the held-out jobs on
  another base address and a 32x8 texture read no hypothesis exactly (the 8 jobs: at most 4 of 2048
  pixels under any; the 5 of 13 held-out jobs exact under each hypothesis are the strided texture's,
  where modes 4 to 7 read the clamp image of mode 0: bd-st-u0, u4, u5, u6, u7, 2048 of 2048 pixels
  equal for every hypothesis); the declared hypotheses mode47=clamp, nomask and border were
  falsified for the u axis.
  *texture; HW; data: `texture-p1132-tx-border`.*
- `E566` In smp on a strided 64x32 texture T3 bits 0 to 3 offset the row (+1, +2, +4, -8) and bits 4
  to 7 the column (+1, +2, +4, -8) at every value tried (single bits, 22 flip jobs and the control,
  30 single-nibble values and 16 combinations: 46 of 46 fit values exact under both declared t3off
  hypotheses, pre and post), T3 bits 8, 9, 11, 12, 20, 21 and 22 change nothing on that texture
  (2048 of 2048 pixels equal the control in each; on the twiddled 64x64 chain texture of E564 bits
  11 and 12 change every pixel), and bits 10, 14, 18, 27 and 28 give images in which the decoded
  column and row offsets are not one constant but change with the pixel position (D6: bit 10 column
  0, -1, -2 ... every 32 pixels and row 0, -1, -2 ...; bit 14 +32 and -32 over 1024 pixels each; bit
  18 column 0, 1, 2 ... and row 1, 2, 3 ...; bit 27 column -1, -2, -3 and row 31, 30, 29 ...; bit 28
  column -3, -6, -9 and row 37, 34, 31 ...); the rows of bits 27 and 28 follow the source's height
  (t3rows=after) at 64x16 (2048 of 2048 pixels each under pre/after and post/after, 0 under
  pre/fixed) and at 64x32 (all three agree), but at 32x32 strided bits 27 and 28 are exact under
  none of the three (0 of 2048); on a twiddled 32x32 bit 10 and bit 27 read as the control (2048 of
  2048), bit 28 under none (0), bit 18 on 4 pixels, bits 0 and 4 offset it (1024 of 1024 under pre,
  992 under post); held out, t3bits 8 of 15 (pre/after and post/after) and 6 of 15 (pre/fixed),
  t3vals 6 of 24 under pre and 1 of 24 under post; the declared t3off=pre and t3off=post,
  t3rows=after and fixed were falsified as complete models; T3 bit 13 faulted the job (r-b13: job
  faulted, context lost, 1 of 5 risky jobs) and so did bit 14 on a twiddled 32x32 (tw32-t3b14), the
  health triangle drew exactly after each.
  *texture; HW; data: `texture-p1132-tx-t3`, `texture-p1132-tx-t3-risky`.*
- `E567` smp3d (the form without a LOD operand) on a 16x16 twiddled texture at third coordinates
  -0.5, 0, 0.5, 1, 1.5 and 4 (ty0-3d-w-5, w0, w5, w10, w15, w40, the names read w times 10) and on a
  strided one (TEXTYPE 6) at 0 and 1 (ty6-3d-w0, w10) gives the 2D image in 8 of 8 jobs (0 of 2048
  pixels differ from the 2D control in each; w3d=ignore exact 2048 of 2048 in all eight), the third
  coordinate swept 0 to 2 down the rows changes nothing on types 0, 3 and 6 (wsw-ty0, wsw-ty3,
  wsw-ty6: the 32 rows of each are identical, 3 sweeps); TEXTYPE 7 reads exactly the twiddled image
  (the pixel sha256 of the gate's g1) under smp2d and smp3d at 0.5 and 1.5 in 3 of 3 jobs (rt7-2d,
  rt7-3d-w5, rt7-3d-w15), TEXTYPE 3 reads the same 256-valued image as TEXTYPE 1 (pixel sha256
  6551611e... in ty3-2d, ty3-3d-w0, ty3-3d-w10 and rt1-2d, rt1-3d-w5, rt1-3d-w15: 6 of 6 jobs, 32
  and 8 of 2048 pixels equal the twiddled and the raster-of-4-byte-texels models), TEXTYPE 4 and 5
  give one image each under all three of smp2d and smp3d at 0.5 and 1.5 (rt4: 8a36df6c..., 256
  distinct values, 8 pixels of the twiddled model; rt5: 354d06c9..., 2 distinct values), and TEXTYPE
  2 gives three different images under smp2d (dc945d2f..., 9 distinct values), smp3d at 1.5
  (480213ab..., 25 distinct) and smp3d at 0.5 (79970597..., 12 distinct): the third coordinate acts
  on TEXTYPE 2, the only type of the eight run (0 to 7) on which it does; flipping T3 bits 10, 18,
  27, 28 and T0 bits 27, 30 at w 0.625 on type 0 changed the image against the control (ind-t0b27
  and ind-t0b30 on all 2048 pixels, ind-t3b10 and ind-t3b18 on 2040, ind-t3b27 and ind-t3b28 on
  2048), T3 bit 14 faulted the job (ind-t3b14); no cube or volume reading was identified, no job
  hung, and the health triangle drew exactly after every job of the group (97 health checks of the
  whole batch, none failed).
  *texture; HW; data: `texture-p1132-tx-types`, `texture-p1132-tx-types-risky`.*
- `E568` YUV formats 28 and 29 on 64x32 type 3 textures read 0xff000000 at all 2048 pixels in all 8
  jobs (two patterns, with and without xfer:17^=1 and xfer:18 to 22 poked in the fill's transfer
  command; the E037 conversion model exact on 0 of 4 csc jobs and on 4 of 4 black ones), so the poke
  did not reach a loaded colour-space set in a fill (or the set stays unloaded) and the formats
  cannot be told apart from black here; the names maps of formats 23 to 27 (16x16) read 164, 186,
  77, 117 and 28 distinct values; in the block jobs formats 23 and 24 read cells that are constant
  over 4x4, 8x4 and 4x8 regions under constant data but a data bit changes 7 to 13 pixels (in 0 of
  16 blocks does a data bit change exactly one pixel), and format 27 reads its 16 blocks in an order
  for which, of the three tried, only Morton with y in the low bit is consistent (morton-y0: 16 of
  16 blocks; raster 0 of 16, morton-x0 4 of 16; the test fixes the order only up to the permutations
  that fit the pattern's block map, so other orders are not excluded) with every bit of the low and
  the high data dword changing exactly one pixel, 16 of 16 blocks each, in the map bit i to (x, y) =
  (i div 4, i mod 4).
  *texture; HW, infer; data: `texture-p1132-tx-formats`, `vectors-texture-p1132`.*
- `E569` The 28 triangle jobs of the Q021 probes (a vertex shader writing a set of four outputs o4,
  o5 = x, y, o6 = 0.25, o7 = x + y, two temporaries more than E420's; the pixel shader storing pa2,
  pa3, pa4 or pa5; five runs of 0x40c00801 and two controls of 0x40800801 per register, 7 jobs each)
  all failed with 'job hung, context lost (Connection timed out)' (28 of 28; the kernel log names 28
  hung jobs and 'recovering'), no pixel was read, and the health triangle drew exactly after each of
  the 28 (a reset between, the 28 jobs took about 8 s each); the question whether pa3 is a fourth
  component or 1.0 (Q021) has no result from this batch, and the two controls of 0x40800801 hung
  too, so the hang is not tied to the fourth component's source word.
  *texture; HW; data: `texture-p1132-tx-douti4`.*
- `E570` In the triangle's pixel task, with the eight-register tagged shader at 13 target
  configurations of 7 shapes (64x64 to 256x128; 10 shapes with the 8 configurations of the third
  table) and PDS_SIZE bits 17:16 at 0 to 3, the destination pixels that carry o1's tag, 6995 pairs
  read from the x and y runs at the same place in the tile, hold the value written from the tile one
  position later: in the raster order of the target's 32x16 tiles (tile index ty * ceil(W / 32) +
  tx) in 6362 of 6995 pairs (91 percent) and in the order of the TA data's region headers (regions
  with a stream) in 6110 (87 percent); the raster rule fails at 64x128 (300 of 402 pairs) and
  256x128 (184 of 362), the header order is the better of the two only at 256x128 (262 of 362) and
  192x96 size 0 (54 against 52 of 84); the header order was built on 12 configurations (5551 of 6329
  pairs there) and gives 559 of 688 on the 8 it was not built on; o2 and o3 land one, two or three
  tiles back (o2: 743 one, 318 two, 91 three of 2094; o3: 268, 150, 24 of 532) with no setting tried
  fixing the offset; the same table twice at 128x128 size 3 gives 705 and 463 pairs of tag 2.
  *usse; HW, infer; data: `usse-output-room-tiles`.*
- `E571` In the vertex task of the triangle job (126 vertices at 4, 6 and 8 vertices a task, 12
  jobs), 125 of the 126 vertices of each job read in full (vertex 67 is cut by the 4 KiB boundary at
  0x2000: its first nine dwords read 0 in all 12 jobs): g16, g19, g26-g31 and g40 read 0 and g20 1
  on 125 of 125, g42 reads 0x3f800000, and g41 0xf and g43 0xdf000000 (where the pixel task has 1
  and 0xff000000) on every vertex of a task of 4 or more, a last task of 2 vertices reading 0x3 and
  0x20000000; g17, g22, g24, g25 and g39 follow the vertex's task and lane (g25 = lane mod 4, g22 =
  lane div 4 mod 2, g39 = 4 * g22, g24 = 8 * (task mod 2), g17 = task mod 4) in 125 of 125 vertices
  in each of the 12 jobs (24 of 24 job-register scores, 12 of them held out at 4 and 6 vertices a
  task), and g23 = 0x10 * (task div 2 mod 2) in 125 of 125 in each of the 4 jobs that read it, a
  rule read from the data after all 12 jobs were in.
  *usse; HW, infer; data: `usse-globals-vertex-eot`, `vectors-usse-globals-vertex`.*
- `E572` In the end-of-tile task of the triangle job a stad of a global register to the scratch
  lands the register's value in 44 of 44 jobs that stored (37 of q053-eot2, the 4 of the second form
  of q053-eot, 3 of q053-eotst) and the job then faults: BIF fault 0xd0400 at 0x340042 in 39 of the
  44, at 0x340043 in 1 and at 0x740012 in 4 (the cases g23 at 64x64 and 128x128, g18 and g25 at
  32x16: no pattern with the register or the size), the health triangle drew exactly after every
  recovery (no health failure line in any of the 5 scripts); the 4 jobs of the first form (a store
  through r8) faulted at 0x42; 5 programs of 7 to 10 instructions without a store complete 5 of 5;
  and the registers read as in a pixel task (g16, g26-g31, g40 = 0, g20 and g41 = 1, g42 =
  0x3f800000, g43 = 0xff000000; 12 of the 13 declared constants), with g19 reading 0x1a through a
  store, as in E372; g17 reads 0, g18 0x16 at 32x16, 64x64 and 128x128, g21 0x12, 0x16, 0x15 and g23
  0, 0x10, 0x10 by target size.
  *usse; HW, infer; data: `usse-globals-vertex-eot`.*
- `E573` With the read-only alias of the EDM's buffer left out of the client directory one buffer at
  a time, the renders are exact for each of the buffers 1, 2, 3, 4, 5, 12, 13 and 14 (2 of 2 runs
  each, 2 renders a run), for the mask bit 15, which names no buffer of the debugfs layout (ids 0 to
  14), and for the pairs 6+7, 8+10, 10+11 and the five 6, 7, 8, 10, 11 together (2 of 2 each); with
  buffer 0 (0x30000000) left out the first job faults (2 of 2: BIF fault status 0x91000 at
  0x3000b022) and the context is lost; the directory the faulting kick used is list 2 (BASE2 equals
  the page directory of the fault line, BASE1 holds the health triangle's), and the debugfs layout's
  pd_phys, 0x28b0c000, equals CR_BIF_DIR_LIST_BASE15 (the EDM's own directory) and differs from
  BASE1 in 30 of 30 runs.
  *bif; HW, infer; data: `bif-alias-skip`.*
- `E574` Through 36 jobs of triangles of 3 to 900 vertices at 4096x4096 in 0x100 to 0x422
  parameter-buffer pages (3 runs of 12 cells; 6 completed and 30 overflowed into partial renders,
  none hung or faulted), the high halves of STATUS2 (0x0710, 0x071c) and the register 0x0740 read 0
  in every timeline line of all 36 jobs (30 to 1066 lines a job, the readings about 29 microseconds
  apart); 0x0748 bit 2 cleared in 5 of the 36 jobs, in 6 lines of one reading each (300 vertices in
  0x100 pages 1 of 3, 150 in 0x100 1 of 3, 450 in 0x100 1 of 3, 600 in 0x100 2 of 3, none of the
  other cells; 5 of 15 jobs at 0x100 pages, 0 of 21 elsewhere), against 3 of 3 for 300 in 0x100 in
  E443: across the two batches the clearing is not a function of the scene's vertices and pages
  alone, and 29 of this batch's 36 jobs ran after a reset (a reset follows each failed job), which
  E443's record does not say of its own; 450 and 600 vertices in 0x100 pages overflowed without a
  hang (6 of 6).
  *dpm; HW, infer; data: `dpm-bit2-grid`.*
- `E590` In a 64x64 render of one triangle on a coloured background (ISP_BGOBJVALS 0x300), a kernel
  poke of any one of the words 3 to 16 of the render's background object (17 dwords, at 0x463000 of
  debugfs render_param's dump: six zero words, then the vertex words) leaves the image the control's
  in 140 of 140 jobs (ten values a word: bits 0, 3, 7, 8, 15, 16, 24 and 31 flipped, 0, 0xffffffff;
  131 of the 140 change the word, 9 set a zero word to 0) and the poked value reads back in the
  object after the job in 140 of 140; setting the words 3 to 16 together to 0xffffffff, to 0 and to
  0xa5000000 + N leaves it the control's in 6 of 6; a poke of one of the words 0 to 2 is not in the
  object after the job (the EDM's value) in 18 of 18 and changes nothing in 18 of 18; all 169 jobs
  completed, none faulted or hung.
  *isp; HW, infer; data: `isp-bg-object-pokes`.*
- `E591` With the first context's mappings, slot and memory kept at its close (kernel debugfs
  render_keep), the second context's render after the close of a first context that kept the DPM
  owner (render flags 0xc) is exact in 13 of 13 jobs (7 of keep-closed, 6 of keep-pages) and leaves
  TA3DCtl dwords 20 and 25 cleared as with the first context open (13 of 13), where without keep it
  faults at 0x200030c1 (BIF status 0x90004) in 2 of 2; afterwards the kept first context's TA data
  holds words in its control page (page 1: 16 of the ramp's dwords replaced, word 0 0x00200047),
  OTPM page (page 2: 20 dwords replaced, word 0 0x04000417) and state page (page 3: 34 dwords
  replaced, words 0 and 1 0x00020001 and 2) in the 9 of 9 flags-0xc jobs that put a ramp 0xa5000000
  + i in one of the pages, and in none of the 6 of 6 jobs with flag bit 2 alone or no flag, and the
  ramps do not change the render (exact in 9 of 9); a kept first context that rendered a 1024x768
  scene in partial renders, with no second context rendered, holds 18 non-zero dwords in its state
  page (page 6), 4 of 4, as E464 found without keep.
  *dpm; HW, infer; data: `dpm-kept-state-page`, `dpm-kept-state-page-amended`.*
- `E592` The page directory word of a render context's HW context (debugfs render_words ctx:2,
  newest context) equals the list register the kick wrote in 15 of 15 jobs: CR_BIF_DIR_LIST_BASE1
  after the first kick following a reset (3 of 3 jobs) and never CR_BIF_DIR_LIST_BASE15 (the EDM's
  own directory, 15 of 15 jobs); the k-th process's context (a new VM each) has it in BASEk for k =
  1 to 4 (4 of 4, the lists before unchanged); a second context of the same VM, rendered, adds no
  list (BASE2 stays 0, 2 of 2); and a partial render (1024x768 on 0x28 pages) under alias_skip masks
  0, 0xc0 and 0xdc0 has it in BASE1 (6 of 6).
  *bif; HW, infer; data: `bif-client-directories`.*
- `E593` With a marker of its own in every job (a half of its own in the upper 16 bits, the register
  number in the lower 16) and a GPU reset and 3 seconds before each job, the 25 jobs of E485's two
  tables (temps-max 15, temps-sparse 10), run in the table's order and in the reverse order, read
  back in every register read (the pixel, which is the top register r123, and the first 32 dwords
  the tool shows) the job's own marker: 742 of 742 values of each run in the 25 jobs of each order,
  with no failed job, no marker of another job and no wrapped register number among them; for the 10
  jobs of temps-max with T >= 80 (T = 80, 96, 112, 124 and 128, both sweeps) the registers past the
  32 shown (8, 16, 24, 30 and 30 more) were counted as changed, as predicted, and not read; so
  E485's finding stands without its fixed marker, for the registers read: a register a job wrote
  reads back what that job wrote, up to r123, and the i0-i3 job still reads i3 as i0; in the one job
  of each order that reads r123 without writing it (the i0-i3 job) the pixel holds markers of
  earlier jobs of the run, one job's marker in 2048 pixels in one order and those of two earlier
  jobs in 1536 and 512 pixels in the other, after a reset in front of the job [HW]; the temporaries
  are not cleared between jobs by the debugfs reset [infer].
  *usse; HW, infer; data: `usse-temps-fresh-a`, `usse-temps-fresh-b`, `vectors-usse-temps-fresh`.*
- `E594` With a marker of its own in each job, E487's jobs T = 132 to 192 read their marker back: T
  = 132, 136, 144 and 160 started with 8 temporaries and T = 192 started with 8, 32, 64 and 128 (8
  of 8 jobs, the same pixel in 2048 of 2048 pixels, the same value in the one scratch dword), each
  with a marker no other job writes (0x7nnnnnnn from seed 1137), so in these 8 jobs a write of the
  job's own marker lands and is read back (a clean rerun cannot show what E487's read-back was; that
  it was a write and not a leftover is [infer]); none hung, as E519's rule predicts (T mod 256 is 4
  to 192).
  *usse; HW, infer; data: `usse-temps-fresh-c`, `vectors-usse-temps-fresh`.*
- `E595` In client pixel tasks (fills), with a GPU reset and 3 seconds before each job, the
  two-instruction 64-bit compares `ima32.u t, i0, b, c56, a` then `xor.testtanz.chan0 !c0, p0, b,
  i0` and `ima32.s t, i0, b, c56, a` then `xor.testtanz.chan0 !c0, p0, i0, #0` gave a < b (unsigned
  and signed) in 256 of 256 jobs: 192 of 192 on the registers r5/r6/r7, r26/r27/r28, r31/r30/r25,
  r64/r65/r66 (started with 80 temporaries), r123/r122/r121 (124 temporaries) and with the result
  register equal to a source (r1/r2/r1), 16 pairs each, p0 set to the opposite first, and 64 of 64
  right after another compare that left i0 holding its own high word, so the test read the fresh
  high word and never the one before (32 of 32 unsigned, 32 of 32 signed, 49 of the 64 cases would
  read the opposite from a stale i0); no job failed [HW]; the measurement is a client pixel task:
  whether a firmware (EDM) task does the same is not measured, the firmware-task verifier refuses
  `ima32` with the extra operand i0.
  *usse; HW, infer; data: `usse-fw37-compare`, `vectors-usse-fw37`.*
- `E596` In client pixel tasks (fills), with a GPU reset and 3 seconds before each job, the
  predicated register moves `p0 mov r, r` and `!p0 mov r, r` and the predicated limm moves `p0 mov
  r, #n` and `!p0 mov r, #n` followed p0 in 64 of 64 jobs (8 gaps between the test that sets p0 and
  the move: none, 1, 4, 16 and 64 `mov` limm, and 1, 4 and 16 `ldad` with one `wdf`; p0 set to 0 and
  to 1 for each, a marker of its own per job), and a predicated `ba` whose predicate is false (`p0
  ba` with p0 = 0, `!p0 ba` with p0 = 1, five gaps each) fell through to the next instruction in 10
  of 10 jobs, so p0 survived every gap and no form ignored it [HW]; a client pixel task: the
  verifier of the firmware tasks refuses `p0 mov r, r`, `!p0 mov r, r` and every predicated `ba`, so
  these forms were not run in a firmware task, and the taken `ba` was not run.
  *usse; HW, infer; data: `usse-fw37-pred`, `vectors-usse-fw37`.*
- `E597` In client pixel tasks (fills), with a GPU reset and 3 seconds before each job, `ima32.u d,
  i0, a, b, c` and `ima32.s d, i0, a, b, c` with the four operands in every one of the 15 partitions
  into registers (d, a, b and c each its own register, any two or three alike, all four the same
  one; `mov d, #0; ima32 d, i0, a, b, d; mov d, i0` of the request is the partition with c in d's
  group) read their sources before the write: r10 held the low word and i0 the high word of the
  64-bit a*b+c (c sign-extended for .s) in 300 of 300 jobs (30 probes of 10, i0 preset to a marker
  of its own each so that an unwritten i0 shows), with the markers never read back from i0 [HW]; a
  client pixel task: the firmware-task verifier refuses `ima32` with the extra operand i0, so the
  form was not run in a firmware task.
  *usse; HW, infer; data: `usse-fw37-ima32hi-repeat`, `vectors-usse-fw37`.*
- `E598` In client pixel tasks (fills), with a GPU reset and 3 seconds before each job, `ldab` and
  `ldaw` with an immediate offset read the byte at base + n and the halfword at base + 2n,
  zero-extended (the offset counts elements of the access size, not dwords and not bytes for the
  halfword): 16 of 16 jobs (8 offsets each, from the dwords 0x9c8db6a7 and 0x7e6d5c4b, every byte of
  the first with bit 7 set, so a sign extension would show: ldab #0 to #3 read 0xa7, 0xb6, 0x8d and
  0x9c), and `ldaw` and `ldad` at an address that is not a multiple of their size read the bytes at
  that address, across the dword boundary too (`ldaw` at base + 1, + 2 and + 3 read 0x8db6, 0x9c8d
  and 0x4b9c, `ldad` at base + 1, + 2 and + 3 read 0x4b9c8db6, 0x5c4b9c8d and 0x6d5c4b9c): 6 of 6
  jobs; no job faulted or hung [HW]; client pixel jobs: the firmware-task verifier refuses `ldab`
  and `ldaw` (unknown form), so a narrow load was not run in a firmware task.
  *usse; HW, infer; data: `usse-fw37-narrow`, `vectors-usse-fw37`.*
- `E599` In client pixel tasks (fills), with a GPU reset and 3 seconds before each job, `stab
  [r28,+#n], r5` changed only the byte at base + n to the low byte of r5 (0xdd) and `staw [r28,+#n],
  r5` only the two bytes at base + 2n to its low halfword (0xccdd), nothing else changed, in 23 of
  23 jobs (`stab` 16: bases at +0, +1, +2 and +3 bytes and n = 0 to 3, so also at odd addresses;
  `staw` 7: bases at +0 and +2 and n up to 3, aligned), and a plain `stad` control landed at an
  aligned address and nowhere at an unaligned one in 3 of 3 jobs (as usse_isa 7.10 has it): 26 of 26
  jobs; no job faulted or hung [HW]; client pixel jobs: a narrow store was not run in a firmware
  task (the verifier refuses `stab` and `staw`), and a `staw` at an odd address and a narrow store
  with a register offset, a negative offset or an increment form were not run.
  *usse; HW, infer; data: `usse-fw37-narrow`, `vectors-usse-fw37`.*
- `E600` In a firmware (EDM) task of ours (stage f10, p1137_imm and p1137_wide, one arm each with
  slots=0x1 entry=0, the landed verifier unchanged), `xor.testtanz.chan0 !c0, p0, rV, #n` encodes
  every n from 0 to 127 exactly and zero-extended, and a value of 128 and up reaches the test
  exactly through `mov rK, #W` (limm) and `xor.testtanz.chan0 !c0, p0, rV, rK`: 7 of 7 jobs with 128
  and 64 tests each, every p0 as predicted; with V = n all 128 p0 false, with V = n xor one bit (two
  jobs, the bit 1 << (n mod 32) and 1 << ((n + 16) mod 32)) all 128 true, and with V = n or
  0xffffff80 all 128 true (the 7-bit field is not sign-extended: n = 64 to 127 would read false if
  it were), and for 64 wide values W from 128 to 0xffffffff, the limm field boundaries 20/21 and
  25/26 and the powers of two included, V = W gives p0 false 64 of 64 and V = W with one bit flipped
  gives p0 true 64 of 64 in two jobs [HW]; every job was done within 0.78 ms, the tick advanced
  after each arm (991.2 and 998.0 Hz) and the gate was exact after each reset.
  *edm; HW, infer; data: `firmware-tasks-p1137-f10`, `vectors-firmware-tasks-p1137`.*
- `E601` In a firmware (EDM) task of ours (stage f8, p1137_pred, slots=0x1 entry=0, the landed
  verifier unchanged), with p0 set by `and.testtanz` from the job's P before a gap (none; 1, 4, 16
  or 64 `mov` limm; 1, 4, 16 or 32 `ldad.bypassl1` and one `wdf`; a mix of mov, ldad and a `mov`
  from a loaded register; `wdf`, `idf`, `wdf`; a taken `br` hop), `p0 mov r20, #A` wrote iff P was
  not 0 (else r20 kept the job's marker), `!p0 mov r21, #B` wrote iff P was 0, `p0 br` was taken iff
  P was not 0 and `!p0 br` iff P was 0: 72 of 72 jobs (12 gaps, P = 0 and 1, 3 repeats, shuffled, a
  pair of markers of its own per job), so p0 survived every gap and the four forms the verifier
  accepts follow it [HW]; the verifier refuses `p0 mov r, r`, `!p0 mov r, r` (unknown form) and `p0
  ba`, `!p0 ba` (form not allowed), so those were not run in a firmware task.
  *edm; HW, infer; data: `firmware-tasks-p1137-f8`, `vectors-firmware-tasks-p1137`.*
- `E602` In a firmware (EDM) task of ours armed with trc=31 (stage f12, p1137_wdf, the landed
  verifier unchanged), one `wdf drc0` after N `ldad.bypassl1` (N = 2, 4, 8, 16, 32, 64 and 100, from
  two page bases, offsets in a permutation of 0 to 127, every 11th load repeating the address of
  load 0) left every destination holding its own load: 21 of 21 jobs (7 N x 3 repeats, every
  destination equal to the dword the host stored there for that job), which shows that loads, one
  `wdf` and then the stores is sufficient for these sequences and not that the `wdf` waits or is
  needed; and the control prediction failed: 32 `ldad.bypassl1` followed by 32 `stad` of their
  destinations with NO `wdf` between stored the NEW value in 32 of 32 stores in 3 of 3 jobs (96 of
  96), where P37_F12b predicted at least 28 of 32 old in every job, so a load that was not waited
  for had landed within 32 instruction slots in a firmware task, in every job and for every
  register; in the 21 jobs the stores follow the loads by N + 1 slots (3 to 101), so the jobs with N
  = 32, 64 and 100 pass whether or not the `wdf` waits, and N = 2 to 16 were not run without it
  [HW]; whether a `wdf` is needed at a shorter distance or for loads from other memory was not run.
  *edm; HW, infer; data: `firmware-tasks-p1137-f12`, `vectors-firmware-tasks-p1137`.*
- `E603` In a firmware (EDM) task of ours armed with trc=31 (stage f11, p1137_regsA and p1137_regsB,
  one arm each, the landed verifier unchanged), every register r0 to r123 is real storage as a
  destination of `ldad` and a source of `stad`: a marker of its own per job, loaded from the page
  into each register and read back to the page, read back as written for r1 to r31 (20 of them
  outside the wrapper's), r32 to r63, r64 to r95 and r96 to r123 (28) one range at a time (12 jobs),
  for all 112 registers outside the wrapper's 11 at once (3 jobs), for the wrapper's 11 and r8 from
  a second wrapper that uses r12 to r22 (3 jobs), and for r0 (3 jobs, markers 0xb921ea5f, 0x8f940932
  and 0xb3b031b9): 21 of 21 jobs, no register reading a stale value, another register's marker or
  the sentinel, the tick advancing and the gate exact after each arm [HW]; the markers differ in
  every job and register, which extends E540's read of the top register r123 and E550's marker to
  every other register.
  *edm; HW, infer; data: `firmware-tasks-p1137-f11`, `vectors-firmware-tasks-p1137`.*
- `E604` In a firmware (EDM) task of ours (stage f15, p1137_strjob, slots=0x1 entry=0, the landed
  verifier unchanged), `str` then `ldr` of the two allow-list registers 0x0814 and 0x0a78 read back
  the stored value in 3 of 3 jobs, each time both right after the `str` and again at the end of a
  30000-iteration spin (about 2 ms): 12 of 12 reads equal the stored value (0x0814 stored 0x1d5de,
  0x1b85d and 0x1a355 with bit 16 always set, 0x0a78 stored 0x21, 0x24 and 0x27). A client fill
  (sgxfive-test fill) was started by the host 0.5 ms into the spin and drew exactly (diff 0 of 2048
  pixels, 3 of 3); that the fill reached the engine while the task was still spinning was not
  measured (the host process started 0.5 ms into a 2 ms spin and no job time was kept), so the run
  shows the read-back across the start of a client job and does not show an overlap.
  *edm; HW, infer; data: `firmware-tasks-p1137-f15`.*
- `E605` In a firmware (EDM) task of ours (stage f14a, p1137_slow4, all four slots armed with
  slots=0xf entry=0,1,2,3, ticks only, no job and no host event), with slot 0 held in the slow loop
  for n = 10000 (2 jobs) and n = 100000 (3 jobs) iterations, the overlap flag of every slot stayed 0
  and slots 1 to 3 counted 0 passes in 5 of 5 jobs, the task finished (done) inside the 400 ms
  window each time, no fault and one reset only; these two clauses could not have failed in this run
  (no event but the tick reaches slots 1 to 3, E538), so they show no more than that the tick
  reaches slot 0 only. The count clause of the prediction is not decided: slot 0's pass counter read
  17, 17 (n = 10000) and 20, 20, 21 (n = 100000) against 0.8 to 1.3 and 6.2 ticks expected from the
  wall time of the job, and the tick counter's delta read 10, 10, 13, 12, 12; both carry an offset
  of about 10 ticks that the instrument (the tick counter read through the `regs` debugfs dump
  before the command and after the job, and the page after that) adds, and the difference between
  the two n, 2.3 ticks and 3.3 passes against 5.2 expected, is about half the wall time, as the lag
  of E539 (1.9 to 2.2 ticks behind) would give [infer].
  *edm; HW, infer; data: `firmware-tasks-p1137-f14a`.*
- `E606` Over 1536 triangles with random sub-pixel vertices (integers in 1/256 pixel, within about
  -9% to +124% of the target) on 64 x 64, 128 x 128 and 256 x 128 targets (3112 jobs, none flagged),
  the ISP covers pixel (x, y) iff the sample at its centre (x + 0.5, y + 0.5) is inside the triangle
  whose vertices lie on the 1/256 pixel grid (the grid the ISP rounds every vertex to, E607;
  rounding to a coarser grid, 1/128 pixel, already mispredicts 61 pixels), the edge test exact, and
  a sample exactly on an edge belongs to the triangle iff the edge is a left or a top edge: 0 of
  14368768 pixels of all main images mispredicted (0 of 413856 pixels of the bounding boxes of the
  692 fit triangles, where the one cell of 15360 (snap x sample point in sixteenths of a pixel x ten
  tie rules) was chosen, and the same cell 0 of 1064683 on the 814 held-out triangles of 128 x 128,
  256 x 128 and a second seed batch at 64 x 64), 814 of 814 exact, edges through pixel centres,
  shared edges (110 pairs: no pixel drawn twice, none lost inside a triangle, 87 centres exactly on
  the shared edge each drawn once), zero-area and 1/256-wide slivers (0 pixels), 1/16-pixel needles
  and triangles with vertices off screen included; the coverage is the same under three pixel
  programs and with the depth store (1576 of 1576 images), and repeats byte-identical (30 of 30).
  The depth stored through the E465 layout and the iterated clip z and x (coordinate set 0, source
  1, two components, the program of E437) equal the plane through the vertices evaluated at the
  pixel centre up to an absolute error: for depth 99.3% of 409950 covered pixels within 1 unit (the
  unit is 2^-23 absolute, not a float32 ulp of the stored value), at most 1.9 units where the
  plane's gradient |dz/dx| + |dz/dy| is below 0.03 (330075 pixels, 3 units as the tolerance), up to
  145 units for gradients above 3; for the iterated clip z 3.7 units at most for triangles with a
  value range per root area below 0.05 (4 units as the tolerance). The stored depth is below the
  exact plane for 78.7% of the pixels, by 0.39 of 2^-24 on average, and no bit-exact model was
  found. The position iterated by source 0 (E502: x + 0.375, y + 0.125) is not the point at which
  these attributes are evaluated. The frozen primary prediction (snap to 1/16 pixel, R1 ties,
  iteration at x + 0.375) failed; the landed CPU reference (one-pixel band) cannot fail by
  construction.
  *isp; HW, infer; data: `isp-arith-1138`.*
- `E607` The ISP rounds every window-coordinate vertex at x >= 0 to the nearest 1/256 pixel, ties
  up, before it tests the pixel centres and builds the planes: on 874 cases with vertices at 1/4096
  and 1/65536 pixel (edge sweeps in single steps across the tie on 64 x 64 targets and at 1/65536 on
  256 x 128, 100 small, 60 medium and 60 near-centre random triangles) the rule (round half up to
  1/256, then the exact centre-sample test with the left/top tie rule of E606) mispredicts 0 pixels,
  against 145 for half-down, 1156 for floor, 4572 for ceil, 577 for rounding to 1/512, 1157 to 1/128
  and 4576 for no rounding; an edge moved in steps of 1/4096 pixel across a pixel centre changes the
  covered pixel 8 steps after the tie (a left or top edge loses the centre then, a right or bottom
  edge gains it), the depth stored through the rounded vertices is within 1 unit (2^-23 absolute)
  for 98.8 to 100% of the covered pixels of the sweeps (maximum 1.7 units), and a held-out
  confirmation, 422 further cases with 0 mismatching pixels in 342 of them, every sweep flip equal,
  and 80 edges passing a pixel centre at a cross product of plus or minus 1 unit of 1/65536 pixel
  squared all decided as the exact integer test does: the 40 at +1 are all drawn (the hardware does
  not drop a centre that is 1 unit inside an edge; one-sided: the 40 at -1 are not drawn, but
  another edge excludes their centre by 4.5e7 to 2.1e8 units squared, so they test nothing). The
  depth of 75 cases with exactly one coordinate on an exact tie (even and odd integer parts, x and
  y) fits the plane through the half-up rounded vertices (59 of 75 within 1 unit at the median, none
  within 1 unit rounded down) and 3 cases at 127/256 of a grid unit round down: the threshold is in
  (127/256, 1/2] of a grid unit. The frozen predictions PF1 (flips at the tie), PF2 (the exact model
  misses at most 0.05% and a 1/256 snap more than 50 pixels) and PF3 failed: the vertex grid exists
  and is 1/256.
  *isp; HW, infer; data: `isp-arith-1138`.*
- `E615` The address rule of E465 held to the 18 stored-depth dump pairs of E489 by a rule function
  written for the pipeline simulator (sgx-pipe zls::store_dword, in-tile order y0 x0 y1 x1 y2 x2 y3
  x3 x4, 512 * (ty * (G + 1) + tx)), replayed as 18 unit vectors: of 3415552 dwords stored 3279132
  are at the rule's address (3225000 for pixels of the target, which the replay counts fitted, and
  54132 for pixels past it, refused as Q122), 7780 are background depth (1124 at pixels past the
  target, refused as Q122, and 6656 in whole tiles of the two 4096 x 4096 jobs, refused as Q107) and
  128640 are zero in both ramps (the same two jobs, refused as Q107), none is at another address (0
  mismatches), the slots touched equal the rule's in 18 of 18 and 1098340 pixels walk to their own
  ramp values at their rule address in the four cases whose tiles do not overlap; every count equals
  recompute.txt's line of the case.
  *zls; HW, infer; data: `zls-store-layout-dumps`, `unit-vectors-12-0`.*
- `E616` The region test of E542 (a 16 x 16 tile lists a primitive iff the bounding box has max x
  and max y at or beyond the tile's low sides and min x and min y below its high sides, and no edge
  line has all four tile corners strictly outside it) held to the 35 jobs of ta-tri-boundary and
  ta-tri-corner by a rule function written for the pipeline simulator (sgx-pipe ta::tile_lists):
  14656 (primitive, tile) pairs (12242 checked per primitive, 2414 by presence only), 0 mismatches,
  replayed as 35 unit vectors whose listed tiles are those of each job's first control stream per
  region, as E542 counts them.
  *ta; HW, infer; data: `ta-tri-region`, `unit-vectors-12-0`.*
- `E617` The object layout of E541 (a vertex holds 1 + N dwords less, for each coordinate set whose
  format bit is set, the components its size code names minus half of them rounded up, with 1, 2, 3,
  3 and 4 components for the codes 1 to 5, the format word 0x0004 in bits 31:16 and 1 + N in bits
  15:8, and the four set masks) held to the 59 jobs of ta-object-format and ta-object-format2 by a
  rule function written for the pipeline simulator (sgx-pipe ta::object_layout): the stored dwords,
  the format word and the masks of 56 completed jobs agree in 56 of 56, and the three jobs that did
  not complete (N = 2 faulted, N = 3 and N = 8 hung) are refused as Q165 with the record named,
  recalled from E541 and not predicted (the rule says nothing of why they failed), 0 mismatches; a
  set of code 0 with its format bit set takes no component (4 of 4 completed jobs of the alt
  pattern).
  *ta; HW, infer; data: `ta-object-format`, `unit-vectors-12-0`.*
- `E618` The window rule of E503 (tile (tx, ty) of a multisampled render holds the source pixels x =
  32 tx + 16 b31 + a div sx, y = 16 ty + 8 b30 + b div sy, (sx, sy) = (1, 1), (2, 1), (2, 2) for the
  modes 0 to 2, b30 counting in mode 2 only) held to the 96 position dumps of the 48 runs of
  isp/msaa-ident by a rule function written for the pipeline simulator (sgx-pipe isp::msaa_source):
  of 786 tiles every one equals the rule on every decodable pixel (0 mismatches), 773 are decodable
  in all 512 pixels (matched) and 13 hold background pixels (refused as Q141), replayed as 48 unit
  vectors.
  *isp; HW, infer; data: `isp-msaa-ident`, `unit-vectors-12-0`.*
- `E619` Of the 2464 triangle-host vectors (717 files) of the data repository 2232 carry an image by
  pixels, 17 by value counts, 117 hung, 19 faulted and 24 wrote no pixel, and only 65 kept a render
  dump (`--dump-render`) beside them to check a rebuilt scene against, so the plan's "about 700
  dumps" are dump directories of other tables; the 197 directories named dumps are classified by
  unit and by what is missing (4 with unit vectors built in 12.0, 96 ready for one, 84 blocked by an
  open question, 12 usable only as a whole job, 1 already vectors in sgx-sim), and the MTE clipping
  and depth-range datasets establish a clip volume of z = -w to w, the w clamp word and no x or y
  clipping rule.
  *platform; HW, infer; data: `vectors-usse`, `mte-clipping`, `mte-depth-range`,
  `mte-depth-range2`.*
- `E620` A model of the transfer job written for the pipeline simulator (sgx-pipe xfer: the render
  box's 32x16 tiles, the pixel-event PDS program run per tile through sgx-sim with ir0 in the
  16-pixel units of E130 and ir1 = 6 on the last tile, the end-of-tile and end-of-render tasks, the
  pixel shader per pixel, a copy's texel through tex::sample, the PBE's rectangle and pack modes 0
  to 3) replays 13679 scenes (4398 fills, 9281 copies) rebuilt from 39 sweep files of fills and
  copies (command words, background object, PDS data and texture words poked one at a time): 5079
  match the recorded image hash and the dwords written outside the target, 8600 are refused under
  questions, none mismatches and none is refused under a question its vector does not list; of the
  5079, 45 are unpoked jobs, 172 poke words to the value they had, 2429 poke only words the model
  never reads (their match says the hardware ignored those words for the values tried) and 2433 poke
  at least one word the model reads, and 518 are 158 distinct images the pokes changed, 130 of them
  the one image of the alpha inversion (E268); the pixel-event program's tile_x mask (data dword 9,
  0xff8) with bit 4 cleared leaves the second column of 32-pixel tiles unwritten in the 64x32 fill
  (1024 pixels, the first at (32, 0)) and writes the second column's tile at the first column in the
  copy, so the end-of-tile task's x field is 2 for that column and not 1.
  *transfer; HW, infer; data: `transfer-command-words`, `isp-background-object`,
  `isp-render-only-registers`, `platform-untouched-registers`, `pds-end-of-tile`,
  `pds-pixel-event-word2`, `pds-data-words`, `pds-douti-fields`, `pbe-emit-words`,
  `pbe-emit-words-followup`, `texture-sampler-bits`, `texture-state-words`, `texture-tpu-csc`,
  `scene-vectors-12-1`, `unit-vectors-12-1`.*
- `E625` A one-triangle scene overflows the parameter buffer exactly when the first abort's page
  status P - 0x22 is below the scene's whole-buffer page need, measured at the boundary as 19 pages
  at 1024x768 and 287 at 4096x4096 (E310's 0x13 and 0x11f): 1024x768 overflows at 0x33 and 0x34
  pages and completes at 0x35 to 0x38, 4096x4096 overflows at 0x13e to 0x140 and completes at 0x141
  to 0x144 (13 of 13 boundary jobs, one run each; the declared need of 21 and 289, an assumption 2
  pages above the measure, missed 5 of the 13, those at 0x35, 0x36 twice, 0x141 and 0x142); the
  partial renders counted by the 0x0658 stretches are 1 at 1024x768 for every overflowing P from
  0x23 to 0x34 (29 jobs of the default triangle, with and without a depth buffer) and at 4096x4096
  10, 5, 3, 2, 2, 2, 1, 1, 1, 1 at 0x23, 0x40, 0x60, 0x80, 0x90, 0xa0, 0xb0, 0xb8, 0xc0 and 0x100,
  which fit 1 + floor((287 + k - thr0) / (thr0 + 0x1f)), thr0 = P - 0x22, for every k from 2 to 13
  (the thr0 = 1 cell, 10 partial renders, sets k >= 2 and the 1024x768 0x23 cell, count 1, sets k <=
  13; the spacing is not pinned either, 0x1e fits the 4096x4096 counts as well) and in 4 more cells
  of a poked descriptor; TA3DCtl dword 35 is the last abort's status less 2 (thr0 - 2 for one
  partial render, thr0 + 0x1e for more, 0 for a completing job) in all 59 jobs of the scene; dwords
  37 and 38 read (1 << 16 | P - 0x22) and 0x20, read as the threshold's raise by 0x20 (HW for the
  dwords, infer for the raise at 1024x768, where every count is 1 and the dwords are the only sign),
  in the 41 overflowed jobs for which 2 * thr0 < U + k and 0 and 0 in the other 29 (70 of 70 jobs of
  the selection below, with k = 2 or 3 at 1024x768 and 2 to 13 at 4096x4096; a rule read after the
  runs, no job held out); a kernel poke of the descriptor's dword 11 (the ZLS threshold) in a
  0x422-page buffer makes the 4096x4096 scene overflow with 5, 3, 2 and 1 partial renders for 0x20,
  0x40, 0x80 and 0x100 and not at the default 0x400 (5 of 5).
  *dpm; HW, infer; data: `dpm-partial-model-batch`.*
- `E626` In 26 jobs (8 whole-buffer jobs at 6 sizes from 64x64 to 1024x768 and 2 repeats of them, 3
  renders each; 12 jobs at 1024x768 in 0x23 to 0x38 pages, 10 sizes of the buffer and 2 repeats, 2
  renders each; 6 jobs at 4096x4096, 1 render each) the page table at 0x423000 of the slot (0x422000
  in the dump, which starts at slot offset 0x1000) walks to all P pages after every render (26 of 26
  jobs, every dump), the pages that changed between two consecutive dumps are, as a set, the first
  pages of the list the previous walk left (H-head, 28 of 28 predictions, fit 8, held out 14,
  controls 6; the order within a render is not visible in the dumps; one control statement missed),
  the first render on a fresh table takes pages 1 to 2, 1 to 3, 1 to 5, 1 to 5, 1 to 8 and 1 to 0x13
  at 64x64, 128x128, 192x128, 256x256, 512x384 and 1024x768 (H-first predicted three rows, 64x64,
  256x256 and the 64x64 repeat, 3 of 3; the other three sizes are observed, not predicted), and the
  list heads that a partial render stores appear in the walk in ascending macrotile order at its
  tail (H-free-O, 8 of 8 overflowing 1024x768 jobs, 0x23 to 0x34 pages); the same job after a reset
  and without one writes the same pages and holds the same lists (2 of 2).
  *dpm; HW, infer; data: `dpm-partial-model-batch`.*
- `E627` The TA data's state page after a job's partial renders holds two different things, split by
  whether the first abort's threshold was raised (E625; TA3DCtl dwords 37 and 38 non-zero): in 28 of
  28 jobs (8 distinct cells) that were not raised (1024x768 in 0x2d to 0x34 pages, 4096x4096 in
  0xb8, 0xc0 and 0x100, among them the 0x30 job after a reset, without one and in the other tables)
  the sum of the 16 macrotile lists' counts is exactly thr0 - 1 (the pages taken at the abort less
  one: E310's 13 and 221) and the macrotiles missing from the page are the last ones the TA tiled (7
  and 10 at 0x30 for the default triangle); in 38 raised jobs (about 12 distinct cells) the sum is,
  approximately, the pages the TA took after the last partial render, (U + k - thr0) - (n - 1) *
  (thr0 + 0x1f) with n the count of E625 and k = 2, differing by -2 to +2 in 35 jobs and by +4 in
  the 3 jobs at 4096x4096 in 0x23 pages (a loose fit, not an exact law), and the macrotiles missing
  are the earliest ones (0, 4, 8 at 0x28), so E464's 18 dwords at 0x28 (9 lists, pages 9 to 0x14)
  and E310's 0x30 and 0x100 rows are two regimes of one page, not a disagreement; entry 16 (the
  global list) is one page, page 1, in 9 of 9 scored jobs; the lists' end pages are distinct in 9 of
  9; in 24 of 26 jobs that held lists the lists name only macrotiles the triangle covers on the 4 x
  4 grid by an 8 x 8 sampling of each macrotile (the author's test, not in a declared file; the 2
  others, the triangle moved by (-128, 96), list macrotile 13, which that sampling does not cover,
  were not checked at a finer grid); the macrotile set follows a move of the triangle (0x30: 9, 9,
  9, 7 lists for the moves (0,0), (256,0), (0,192), (-128,96); the (384,288) move completes at 0x30
  with no list and has 3 lists at 0x28).
  *dpm; HW, infer; data: `dpm-partial-model-batch`.*
- `E628` In a job that overflows the parameter buffer the ZLS store holds, at every dword outside
  the zero region, the dword of the load buffer at that address (a load buffer of ascending indices,
  559104 of 559104 dwords outside tile rows 0 to 11 at 1024x768 in 8 of 8 jobs, at 0x28 and 0x30
  pages, scenes z = 0.5 and full-screen ramp) whether the control has the load bits 1 and 14
  (0x0017510e) or not (0x0017110c): the same job in 0x422 pages stores the scene's depth without the
  load bits (0 of 2) and the loaded buffer with them (2 of 2, E467); the load buffer itself comes
  back from those 8 jobs with 195583 dwords changed to zero, all in tile rows 0 to 11 and none
  elsewhere, and from the 4 jobs that complete untouched (0 changed), so a store reaches the load
  address; the zero region of the store at 1024x768 with no overlap between tiles (G = 33, 34 slots
  a tile row for 32 tiles) is 195584 dwords: 336 whole target tiles and 48 half-zero tiles, 360
  tile-equivalents of the 384 in tile rows 0 to 11 (24 tile-equivalents, 6.25 percent, short; the
  half-zero tiles sit at tx 6, 14, 23 and 31 of every row), and 22 zero slots of the 24 padding
  slots at tx 32 and 33 (11264 dwords) that are not target tiles (184320 = 360 tiles when the buffer
  is loaded), while at 4096x4096 with no padding (G = 127) it is 4193152 dwords, a prefix of 8189.75
  of the first macrotile row's 8192 tile slots (2.25 tiles short, not a whole number of tiles; the
  band of a first row, 4.0 to 4.2 million, hit 2 of 2 and that of a first macrotile, 0.9 to 1.1
  million, missed 2 of 2), so the zero rows are not one rule across the two sizes; with overlapping
  tiles the zeros are 15104 dwords at 1024x768 in all 26 overflowing jobs at G = 1 and 80640 and
  48000 at 4096x4096 at G = 1 and 0 (E465's counts, 4 of 4), and the store's window is E465's rule
  at every size (64512, 326656, 196096, 16777216 dwords; 755712 for the whole buffer at 1024x768
  with G = 33, 766976 in the overflowing jobs); two overlapping triangles whose depth decides the
  order (the first in a geometry kick, the second in the final render, the overflow coming while the
  second is tiled at 0x38 pages, 4 jobs) store the nearer one at 142323 and 141579 of 155833 overlap
  pixels (the 13510 others lie in the zero region, where the test sees nothing), A where the second
  is farther and B where it is nearer, 0 mixed, with the load bits and without (4 of 4), the store
  of each 0x38 job being equal to the 0x422 job's at all 571392 non-zero dwords; 12 more jobs at
  0x3c to 0x48 pages complete and store the same minimum at all 155833 pixels.
  *zls; HW, infer; data: `dpm-partial-model-batch`.*
- `E629` The depth a job that overflows stores has its sign bit set (every non-zero dword of the
  window: 49408 of 49408 at 1024x768 with G = 1, 571392 of 571392 with G = 33) in exactly the jobs
  whose first abort's threshold was raised (TA3DCtl dwords 37 and 38 read 1 << 16 | P - 0x22 and
  0x20, E625) and in none of the others: 44 of 44 overflowing depth jobs (the z = 0.5 triangle at G
  = 1 in 0x23, 0x24, 0x26, 0x28, 0x2a, 0x2c pages signed and in 0x2d, 0x2e, 0x2f, 0x30 and 0x34
  pages positive, 2 runs each; at G = 33 signed in 0x23 and 0x28 and positive in 0x30; the
  full-screen ramp signed in 0x23, 0x28 and 0x30 at G = 33 and in 0x28 and 0x30 at G = 1; the 6 jobs
  of 4096x4096 in 0x2000 pages positive, 246016, 148096 and 12584064 non-zero dwords, none raised),
  the pitch does not decide it (G = 1 and G = 33 agree in 5 of 5 cells), the number of partial
  renders does not (1 in the signed z = 0.5 cells and in the positive 0x30 one, 2 in the signed ramp
  cells in 0x23 and 0x28, 1 at 0x30), and the scene does only through its page need (the z = 0.5
  triangle is raised below 0x2d pages, the ramp at 0x30 as well); within the z = 0.5 scene a raise
  is the same as P below 0x2d, so the sign follows a scene-dependent P boundary that the raise
  follows too, and the one pair that tells them apart is the 0x30 z = 0.5 job (positive, not raised)
  against the ramp (signed, raised); the sign of a job is repeatable (2 of 2 runs identical in all
  22 cells: the table's 19 and 3 of 4096x4096).
  *zls; HW, infer; data: `dpm-partial-model-batch`.*
- `E630` Of the 3 wide-scene cases that E438 saw hang (300 vertices at 4096x4096 in 0x40 and 0x23
  pages, 900 in 0x100 pages) the 2 of 300 vertices logged, about 2 s after the case start in the
  kernel journal, `*ERROR* sgxfive: job hung, recovering` and `recovery held (debugfs
  hold_recovery)`, and still ended as overflows with the context kept (-ENOSPC) after 47 and 92
  partial renders counted by the 0x0658 stretches (the 900-vertex case, 33 partial renders, ended
  its timeline at 1.85 s and logged nothing): E438's hang is reproduced in 2 of 3 cases and the held
  recovery let the job run on, so that reading it as a hardware stop is not supported (infer: a
  kernel watchdog on a long job with many partial renders, delayed here by hold_recovery); the other
  25 jobs of the 28 (among them 600, 750, 801 and 849 vertices at 0x100 pages, with 22 to 32 partial
  renders) logged no hung, fault or reset line; the global list is 4 pages (list entry 16: count 4,
  head 1, tail 0x35c) and TA3DCtl dword 36 is 2 at 900, 1050, 1200 and 1350 vertices in 0x422 pages
  (1 partial render) and 5 pages and 3 at 1500 (2 partial renders): a step between 1350 and 1500
  vertices, E438's two cells fitting and no rule for dword 36 (E438 read 1 with a one-page list and
  0 with one or two pages elsewhere); the high halves of STATUS2 (0x0710, 0x071c) read 0 in every
  line of the 65 timelines that kept 0x0748 and the STATUS2 registers (21 of 21 scores); 0x0748 bit
  2 clear (the values 0xb and 0x1b) in a line of 23 of those 65 jobs, 66 lines in all, each of one
  reading, and in 10 of the 16 `wd-bit2` runs (300 vertices 5 of 8, 450 vertices 5 of 8; after a
  reset 4 of 8, without one 6 of 8).
  *dpm; HW, infer; data: `dpm-partial-model-batch`.*
- `E631` In one case, a kept partial-render owner of 1024x768 in 0x28 pages, the state page the
  owner left is zero after the second context's run, by an event of that run not separated (the
  1024x768 context in 0x28 pages: 18 non-zero dwords in page 6 alone and with the render flag poked
  0xc or 0x4 and no second context, 3 of 3 runs identical; read after the tool exits, page 6 holds 0
  non-zero dwords after the second context's run with flag 0xc and with flag 0x4, 2 runs of each, 4
  of 4, the cause (the creation, the render or the close of the second context) not separated for
  this owner, whose pages were not copied before the close; pages 1 to 3 (the control, OTPM and
  state pages) hold no owner word at all with either flag, so the owner words of the 64x64 owner are
  not seen here) and with flag 0x4 alone 5 dwords (0x200057, 0x2000ad, 0x20007e, 0x2000c0, 0x200087)
  are written into page 4, 2 of 2 (nothing in page 4 with flag 0xc); closing the partial owner
  without keeping it makes the second context's render fault (BIF fault status 0x90400 at
  0x3241100f, `job faulted, context lost`, recovered by a reset, flags 0xc and 0x4, 2 of 2, the
  address one page below the ctx word 0x32412000 of the job's words, so the second context's render
  reaches memory next to the closed first context's, a read or a store not shown); for a 64x64 owner
  the kept words land by the end of the second context's render, not at the close (a copy of
  render_kept made after that render and before the close equals the copy made after the tool exits:
  75 non-zero dwords, words 0x00200047, 0x04000417, 0x00020001 and 2 in pages 1 to 3, flag 0xc; with
  flag 0x4 alone the pages 1 to 3 are 0 in both copies, 71 non-zero dwords elsewhere, 2 of 2 runs
  each); the words do not follow the buffer: 0x04000417 at P = 0x422, 0x300, 0x200 and 0x100 (4 of
  4), 0 in page 2's word 0 when the first context rendered 2 or 3 times (0x00200047 and 0x00020001,
  2 stay; 2 of 2 each, repeated), and the first word follows the target size (0x00200047 at 64x64,
  0x00200044 at 64x32, 0x00200042 at 32x32); the state page's first words are (count << 16 | head)
  and tail of the owner's 2 pages in all 8 first-context jobs; junk written into the state page
  (page 6 of a 1024x768 context) between a geometry kick that overflows and the next render (zeros,
  and the ramp 0xa5000000 + i, at 0x30 and 0x28 pages, 4 jobs) leaves the page table walk and the
  image identical to a control without it (4 of 4); the next render's own partial render stores the
  lists over the page's first 34 dwords, so a load of the lists themselves is not separated, and the
  other 990 of the 1024 ramp dwords stay after the render with no effect on it.
  *dpm; HW, infer; data: `dpm-partial-model-batch`.*
- `E650` A model of the vertex side and the TA written for the pipeline simulator (sgx-pipe vdm,
  vtx, mte, ta, render: the VDM stream parsed, each state block and each vertex of a vertex task run
  through its PDS program and USSE task on sgx-sim unchanged, the clip position through the
  viewport, then the object, the region headers and the control streams written) reproduces the
  parameter buffer pages 0x1000 to 0x6000 and the TA data headers of 89 of 89 dumped one- to
  five-triangle jobs on 64 x 64 to 256 x 256 targets with no differing dword (21229 non-zero dwords
  compared, 79 distinct expected buffer sets), every one by a fitted rule so none is reported
  matched; of 266 more built scenes the model refuses all, each naming what blocks it (lines Q159
  and Q160 81, points Q161 26, a state word nobody flipped in a two-object stream Q047 and Q112 104,
  Q163 with Q047 and Q112 12, Q163 with Q112 5, Q112 alone 9, Q162 20, Q094 4, Q042 3, Q069 1, Q230
  1) and none mismatches; the 89 are 25 percent of the 355 built scenes and 15 percent of the 599
  dumped jobs, every one a job that keeps the library's pass-through vertex program, and the 130
  two-object jobs of vdm-state-units contribute none; the jobs no earlier record described are 3
  (ta-object-words 1, vdm-vtask-capacity 2), and the stream forms 0x88, 0x8a and 0x8c, the page
  order and the four non-square targets were read from no record before the replay.
  *ta; HW, infer; data: `ta-tri-region`, `ta-regions`, `ta-objects`, `ta-object-words`,
  `ta-line-point`, `ta-points`, `ta-zero-words`, `vdm-state-units`, `vdm-vtask-capacity`,
  `scene-vectors-12-2`.*
- `E651` The object's packed vertex block (E176's 8 dwords for 3 vertices) is a bit stream, least
  significant bit first, of 80 bits for each vertex: the window y as a 24-bit field of (y + 4096) *
  256, the window x the same way, then the 32-bit depth float; E176's 8 dwords for the plain probe
  decode to (8, 8), (56, 20), (20, 56) at depth 0.5, and 89 of 89 dumped jobs (up to 15 vertices, 38
  packed dwords) hold the packed block this rule writes from the vertices the vertex program gave
  and the viewport, with every window coordinate a multiple of 1/16 pixel.
  *ta; HW, infer; data: `ta-objects`, `ta-tri-region`, `ta-regions`, `scene-vectors-12-2`.*
- `E652` The TA's headers and streams of E177 and E180 follow these rules in 89 of 89 dumped jobs: a
  header's flags are 0x02 outside the target, 0x08 for a target region with no stream, 0x04 on the
  first and 0x10 on the last header of a macrotile with target regions and 0x80 on the last such
  header of the last such macrotile (headers in macrotile order, macrotile m = column * n + row of
  macrotiles, regions in raster order, 2 macrotiles in a row up to 256 x 256); a macrotile's streams
  share one page, the pages go 0x2000, 0x3000, ... to the macrotiles that have streams in raster
  order of the macrotiles (rows outer), and a stream block of 128 bytes goes to each region in the
  order of 64 x 64 pixel blocks (two regions across and four down, in raster order, regions in
  raster order within one); the forms of the primitive word are 0x90 with 0xffff when both tiles
  list every primitive, otherwise for one tile 0x80 (left) or 0x98 (right) with the primitive mask
  in bits 7:0 and the vertex mask (3 bits a primitive) in bits 15:8 while that mask fits a byte,
  else 0x8a or 0x8c with the vertex mask in bits 15:0 and the primitive mask in a further dword, and
  for both tiles with different masks 0x88 with the vertex mask of the union and a further dword of
  the right mask in bits 31:16 and the left in 15:0.
  *ta; HW, infer; data: `ta-tri-region`, `ta-regions`, `ta-objects`, `ta-object-words`,
  `vdm-vtask-capacity`, `scene-vectors-12-2`.*
- `E660` A model of the ISP written for the pipeline simulator (sgx-pipe isp, iter, objects, pixel:
  the exact integer centre test on vertices rounded half up to 1/256 pixel with left and top edges
  owning ties, the plane through the rounded vertices at the pixel centre) reproduces the colour
  image of 2752 of 2752 E606 and E607 depth jobs it is asked about, 0 of 14368768 + 11149312 +
  6586368 pixels wrong, of which 1566 jobs are the ones the rule was found on (E606's 692 fit cases,
  E607's 874 fine cases) and 1186 held out (E606's 814 held-out cases and 30 repeat cases, E607's
  342 fine2 cases of 422); the 1.0 stored where nothing is covered exactly, the stored depth of
  every covered pixel of a plane of gradient below 0.03 within E606's stated 3 units of 2^-23
  (330844 + 106639 + 201663 pixels, 0 outside; the largest error is 1.9, so the data do not pin the
  3 from below), and the iterated clip z of 700 triangles within E606's stated 4 units where its
  range per root area is below 0.05 (132050 pixels, 0 outside); it refuses what E606 and E607 did
  not measure, naming the open question: the 80 tiny-edge cases on 256 x 256 targets (Q240), the
  covered pixels of a plane of gradient 0.03 or more (80665 + 60412 + 26292 pixels, Q200) and the
  iterated clip x (Q200: its error in the record's own table reaches 23 units, E661). Run through
  the whole pipeline (the vertex tasks on sgx-sim, the MTE, the TA, the ISP, the pixel programs on
  sgx-sim, the end-of-tile task and the PBE) from the words the library's builder puts in its five
  pages, the first triangle reproduces the recorded image hash at the three target sizes E606 ran
  (64 x 64, 128 x 128, 256 x 128: 3 of 3, with E023's 1062 triangle and 3034 background pixels at 64
  x 64; the rule alone gives the hash at all 16 sizes, E662, and the pipeline refuses the 13 outside
  E606's three) and 92 of 92 built scenes of the 202 sampled (192 E606 depth jobs, every eighth, and
  10 E607 fine2 tiny-edge jobs) whose depth the model decides (the image hash and, for the 59 that
  store a depth by a plane of gradient below 0.03, the depth within 3 units, counted per scene as
  fitted with depth near; 33 more store only the background); every one of these rests on a fitted
  rule, so none is reported matched. It refuses 97 of the 202 sampled depth jobs (a depth compare
  against a plane of gradient 0.03 or more, Q200: the refusal drops the whole image, coverage
  included, so the replayed sample is skewed to planes of gradient below 0.03 although the coverage
  of those 97 is not in doubt), 10 (a 256 x 256 target, Q240) and 3 (a triangle with no area: the TA
  has no record for its winding mark, Q230), and of the 16 first-triangle sizes 2 by the TA (four
  macrotiles in a row, Q139, Q100, Q086) and 11 by the target size (Q240). It decodes the ISP words
  only as far as their records go (the unit tests check the model against itself there, see below):
  a vertex depth outside [0, 1] under a depth compare or write (the clamp of E287, one run), the ISP
  word 1 gate pairs E232 and E235 did not measure and a pass type 1, 2, 4, 5 or 6 with a pixel
  shader other than the library's colour write (E065's) refuse under Q241. Of the 2464 triangle-host
  vectors of the data repository 2281 were rebuilt as scenes (183 not: a kernel poke 159, a job that
  wrote no pixel 24) and replayed against the image each recorded; this census is a development set
  (its 71 first-run mismatches were removed by rules and refusals after they showed, so 0 mismatch
  is a figure after the fixes, not a test on unseen scenes) with 733 content duplicates among the
  2281 (1548 distinct: 1508 refused, 39 reproduced, 1 predicted hang): 47 reproduce (fitted; the 39
  distinct are the library's triangle with other programs, evidence of plumbing, not of coverage or
  depth), 1 predicted hang (E102: the record that defined the rule, a reproduction, not a
  prediction), 0 mismatch, 2233 refused by question, 97.9 percent of the census, 1231 of them at
  Q094 before the ISP is reached (Q094 1231, Q206 373, Q142 377, Q052 47, Q050 35, Q202 33, Q240 30,
  Q230 21, Q162 20, Q047 14, Q042 12, Q069 15, Q066 4, Q163 with Q047 4, Q241 4, Q076 with Q003 3,
  Q199 2, Q070 2, Q139 with Q100 and Q086 2, Q159 with Q160 2, Q163 2), so the census says almost
  nothing of the ISP itself.
  *isp; HW, infer; data: `isp-arith-1138`, `render-target-sizes`, `render-client-jobs`,
  `dpm-parameter-buffer`, `scene-vectors-12-3`.*
- `E661` In the iteration jobs of E606 the clip x iterated at the pixel centre (pa1) is not within
  the 4 units of 2^-23 that the record gives for the clip z: over the 700 triangles of the fit and
  held-out sets, in the bin whose value range per root area is below 0.05 (358 triangles, 257 of
  them with a covered pixel, 126104 pixels) 17 triangles all of the small class (8 of the fit set, 9
  of the held-out) have 19 pixels beyond 4 units, the largest 23.0 units (the record's own table of
  the bin gives max 23.0), against 0 of 132050 pixels in the 116 triangles of the same bin for the
  clip z (max 3.7); the plane through the vertices' clip x values stays the right plane (coverage 0
  wrong in 700 images), 99.69 percent of the bin's pixels (125718 of 126104) are within 1 unit,
  against 99.49 percent for the clip z (131381 of 132050).
  *isp; HW; data: `isp-arith-1138`.*
- `E662` The coverage rule of E606 (vertices on the 1/256 pixel grid, the pixel centre tested
  exactly, left and top edges owning ties) applied to the library's first triangle ((8, 8), (56,
  20), (20, 56) of a 64 x 64 target, scaled in 1/16 pixel) gives the recorded image hash of every
  render of the 16 sizes of E148, E023 and E174: 32 of 32 hashes of 14 sizes (both colour pairs, 64
  x 64 to 256 x 256, 128 x 96), the first render of 1024 x 768 (207456 triangle and 578976
  background pixels, hash 0xc9e301d225fe2325) and of 4096 x 4096 (4422528 and 12354688, hash
  0x08197f1b8b083325), 3 of the 16 sizes are sizes E606 ran (64 x 64, 128 x 128, 256 x 128) and 13
  are not (64 x 128, 128 x 64 and 256 x 64 of the same family among them, the half-sizes 72, 80, 96
  and 48, the heights above 128, 1024 x 768 and 4096 x 4096); those renders were checked before only
  against a CPU reference with a one-pixel undecided band around every edge, the hash is an exact
  image.
  *isp; HW; data: `render-target-sizes`, `render-client-jobs`, `dpm-parameter-buffer`.*
- `E663` A model of the ZLS store written for the pipeline simulator (sgx-pipe zls.rs store,
  encode_depth) rebuilds the 22 depth dumps of E490's store-format run (11 buffers of 1024 x 768 at
  G = 33, a ramp across x and one across y each) dword for dword where a record decodes the format:
  the float (format 0, within E490's 1e-5 of the geometry's depth: 1572864 dwords), the 24-bit
  integer round(z * 0xffffff) (1572864), the 16-bit integer round(z * 0xffffff) >> 8 packed two rows
  to a dword in 256-dword tiles with the dword index x0 y1 x1 y2 x2 y3 x3 x4 and the half y0
  (786432) and bit 19 on each of the three (1572864 + 1572864 + 786432), the integer ones over the
  float that the format-0 run stored at the same pixel, 7864320 dwords in 6 vectors, 0 dwords
  different and 0 left the fill that the model did not store; formats 4 and 7 without a stencil
  buffer (stated in the vector) store nothing (E490's 0 dwords: 2 vectors that compare no item, so
  the report counts them empty, not matched); formats 3, 5 and 6 are refused by question (Q120: 3
  vectors, 965120 + 965120, 96580 + 84480 and 86084 + 73760 dwords not modelled); every one of the 6
  stores rests on E465's fitted address rule, and the integer ones on the value rules E466 states as
  fitted, so all 6 are reported fitted and none matched; the model refuses what no run measured, by
  input alone: a 16-bit store at a pitch other than G = 33, overlapping tiles (a pitch under the
  tiles of a row), and an integer format over any depth but the ramp's 0.25 to 0.4166 and 1.0
  (Q242), a target with edge tiles or an odd height (Q122), bit 19 with an integer format over any
  depth but the ramp's (Q101), bit 0 with any control but 0x0017100c (Q244).
  *zls; HW, infer; data: `zls-store-format-dumps`, `unit-vectors-12-4`.*
- `E664` A model of the ZLS load and the pass over it (sgx-pipe zls.rs pass, load_word, Ctl)
  reproduces the 30 cases of E467's load run (a flat triangle at z 0.5 over the whole 256 x 128
  target, G = 33, depth test never or less) with 0 differences in 983040 counted stored dwords
  (counts, not dwords: no stored dump exists for this run, so what was compared is the run's class
  counts and value histograms; 8 x (32768 depth + 8192 stencil) in the ten controls' copy cases, 12
  x 32768 in the less cases and 8 x 32768 in the sign cases), as 30 vectors of the kind zls-load:
  with bit 1 and bit 14 the pass starts from the loaded depth with its sign bit cleared (0xbe800000
  stored as 0x3e800000, 0xdeadbeef as 0x5eadbeef, 0xffffffff as 0x7fffffff, 0x80000000 as 0),
  without them from the clear value 1.0 (every control without both bits stores 1.0 at 32768
  dwords); the depth test less against a depth loaded 0.25f and 0.75f by bit K of the dword index (K
  = 0, 3, 9) draws 16384 of 32768 pixels and stores 0.25f at 16384 and 0.5 at 16384, and against the
  clear value draws 32768; bit 13 with bit 1 copies each stencil dword of the load buffer to the
  same index of the store, per 128-dword tile slot (8191 loaded dwords and the dword 0 that is 0
  either way), without them the stencil store holds 0; the load-only controls store nothing; the
  counts are the same under any bijection of the dword indices, so the vectors do not test the
  address rule (the unit tests now pin the depth address to the store rule and the stencil slot to
  128 * (ty * (G + 1) + tx), the stencil slot resting on the identity copy alone, Q121); every
  vector goes through E465's fitted address rule (the load is read at the address the store writes),
  so all 30 are reported fitted and none matched; refused by input alone: a compare closer than 3
  units of 2^-23 (Q200, 12.3's rule), a compare against a loaded NaN or infinity and an integer
  format (Q243), a target with edge tiles (Q122), overlapping tiles and a triangle depth other than
  0.5 and the ramp's 0.25 to 0.4166 (Q242), bit 19 with a load (Q101), bit 0 (Q244).
  *zls; HW, infer; data: `zls-load-copy`, `unit-vectors-12-4`.*
- `E665` The fields of CR_ISP_ZLSCTL that the records read (the pitch G in bits 11:3, bit 1 the load
  with bit 14 loading the depth and bit 13 the stencil, bit 2 with bit 18 the depth store and with
  bit 17 the stencil store, bit 19 the negation, bits 26:24 the depth format, bit 0 the colour image
  off) decode, in 47 vectors of the kind zls-ctl, as the records state them, with 0 differences: 15
  matched (bit readings that use no address, pitch or format and no inferred load: bit 2 cleared,
  the five values the closed driver writes, nine of E467's ten controls), 23 fitted and 9 refused;
  the 32 single-bit flips of E411's 0x0017100c (bits 1, 12 to 16, 20 to 23 and 27 to 31 change no
  field, bit 2 clears both stores, bits 3 and 4 change G, 17 and 18 clear the stencil's and the
  depth's store, 19 negates, 24 selects the format 1) compare the pages of the 16-page scratch
  buffer that each flip stored in both runs of E411 (page 4 and 5 for the stencil, 12 to 15 for the
  depth) with the dwords the model's store writes (sums of 640 to 5120 dwords a flip, 0 pages
  different), so every flip that stores anything is fitted through E465's address rule, and a flip's
  pitch, a format or a load by bit 1 alone ([infer]: E411 part B saw no effect of bit 1 alone) makes
  a vector fitted as well; bit 0 stores what the control stores (the same pages in both runs: page 4
  and pages 12 to 15, 5120 dwords, the same first values) and writes no colour pixel (4096 of 4096
  pixels keep the sentinel), modelled for that one control, 0x0017100d, and refused (Q244) for any
  other control with bit 0 set, which nothing ran; the refused nine are the seven flips of bits 5 to
  11, whose jobs faulted (the pitch running out of the scratch buffer, [infer]: Q242, refused in
  that arrangement and nowhere else), bit 25 (the 16-bit format at G = 1: its layout was derived at
  G = 33, Q242) and bit 26 (format 4, Q120); the bits set in no value and flipped in no run (bits 15
  and 21 to 23 set together with others, any combination of the ignored bits) are not claimed, only
  the single flips.
  *zls; CAP, HW, infer; data: `zls-control-bits`, `unit-vectors-12-4`.*
- `E680` Over 590 random triangles with vertices on the 1/256 pixel grid (small, medium, large -9%
  to +124% of the target except at 4096 x 4096 where no x is negative, vertices at pixel centres, 75
  quads cut into two triangles) on 10 targets that E606 did not run or only partly ran (96 x 64, 130
  x 66, 200 x 120, 512 x 256, 512 x 512, 640 x 480, 1000 x 600, 1024 x 768, 2048 x 1024, 4096 x
  4096; 6 of them with a half-size that is not a power of two, 7 of them taller than 128), the ISP
  covers pixel (x, y) iff its centre is inside the triangle by the exact integer test with left and
  top edges owning ties, E606's rule without a change: 0 of 1092224240 pixels (whole images) differ,
  no tolerance, no clamp; the 75 shared edges leave 0 pixels drawn twice and 0 undrawn; the pixels
  that test the rule are the 603728 next to a triangle boundary, not the 1092224240 counted.
  *isp; HW, infer; data: `isp-coverage-envelope-1140`.*
- `E681` With an edge moved across the half-grid tie in steps of 1/4096 pixel (1/1024 pixel from
  2048 wide) at a positive coordinate, on 7 targets (96 x 64, 200 x 120, 512 x 256, 640 x 480, 1024
  x 768, 2048 x 1024, 4096 x 4096), the ISP's image equals E607's rule (vertex rounded half up to
  1/256 pixel, then the exact centre test) in all 588 cases, taking the nominal window coordinate of
  the vertex: 0 mismatching pixels, every flip of every sweep at the step the rule gives; round half
  down would mispredict 42 of the cases, flooring 204, no rounding 236.
  *isp; HW, infer; data: `isp-coverage-envelope-1140`.*
- `E682` For a long edge (the generator's bounds are 64 to 270 pixels on 512 x 512, 128 to 540 on
  1024 x 1024, 256 to 1090 on 2048 x 2048, 512 to 2170 on 4096 x 4096; the edge nearest the target
  centre measures 105 to 238, 218 to 442, 453 to 1064 and 961 to 2052 pixels; vertices on the 1/256
  grid) that passes the pixel centre (W/2, H/2) at a cross product of +1 or -1 in 1/65536 pixel
  squared (a distance of 1e-8 to 1e-7 pixel), the ISP draws that pixel iff the exact integer edge
  function says so, in 160 of 160 cases (40 on each of 512 x 512, 1024 x 1024, 2048 x 2048, 4096 x
  4096, half with the pixel just inside, half just outside), 0 wrong pixels in the whole images; an
  edge function in float32 from pixel-unit coordinates would be wrong in 42 of them (9, 13, 11 and
  9); only the target-centre pixel tests the edge; the prediction that the 4096 x 4096 cases would
  not be exact (P8b) failed.
  *isp; HW, infer; data: `isp-coverage-envelope-1140`.*
- `E683` With vertices at negative window coordinates (one to three negative coordinates per
  triangle, from -1/256 pixel down to -843 pixels, in x, in y or in both) with fractions of 1/4096
  pixel and an edge aimed at a pixel centre, E607's rule (every coordinate rounded half up to 1/256
  pixel, then the exact centre test) is wrong: 76 pixels in 51 of 80 fit cases and 212 pixels in 98
  of 160 held-out cases (criteria P5 and P6 failed), on 64 x 64, 96 x 64, 130 x 66, 512 x 256, 640 x
  480 and 1024 x 768; none of seven other rounding variants reproduces them (half away from zero: 23
  pixels in 16 fit cases and 78 in 51 held-out cases, the best; half down 33 and 109, half to even
  62 and 147, no rounding 84 and 240, floor 142 and 358, ceil 157 and 491, toward zero 153 and 379),
  and post hoc, the exact ties at a negative coordinate go away from zero in 82 of 99 decided cases
  (a coordinate of x -3.5/256 pixel goes to -4/256, not -3/256).
  *isp; HW, infer; data: `isp-coverage-envelope-1140`.*
- `E684` With one vertex at +-2^k pixels (k = 9 to 21, up to 2^29 units of 1/256, in x, in y or
  both, 8 directions) and the other two vertices inside a 64 x 64 or a 512 x 512 target (one far
  vertex only, on the 1/256 grid in all 208 cases: no sub-grid fraction; no 4096 target), 208 jobs,
  none flagged and none needing a GPU reset, the ISP's coverage equals the exact rule of E606/E607
  in 194 of 208 cases and differs by 1 or 2 pixels (16 pixels in all) in 14 (2 of 104 on 64 x 64, 12
  of 104 on 512 x 512), each of those pixels within 5.6e-4 pixel of an edge line of the triangle
  (median 1.2e-4, nearest 3.5e-5) and on edges from 1008 to 262551 pixels long; no case of any k
  shows a clamp or a wrap of the vertex range: every clamp to 2^20 pixels or less and every wrap
  into 2^21 pixels or less is excluded by the cases on which it would differ; criteria P9 (all cases
  with |v| <= 2^15 pixels exact: 9 mismatch) and P10 (first mismatch at k = 16: it is at 10 on 64 x
  64 and 9 on 512 x 512) failed.
  *isp; HW, infer; data: `isp-coverage-envelope-1140`.*
- `E700` In 52 jobs of five series of E545's two-block VDM stream (12 vertices, VDM_STATE1 bits 11:9
  set to v1 in block 1 and v2 in block 2), predicted before the run by one counter rule (c is 0
  after a GPU reset or a hang, which in these jobs are one observation, the harness resetting the
  GPU after every hang; a job adds the sum of v - 2 over its blocks and hangs iff c + add > 8; a
  completed job keeps c), 52 of 52 outcomes follow the rule (15 hangs), among them 16 of 16 (7
  hangs) on a seeded random walk (seed 1141, v from 2 to 7 in both blocks), the only series not
  built from the rule's own boundaries; a GPU reset clears c in the one job that could show it (c
  would have been 6).
  *vdm; HW, infer; data: `vdm-verification-1141ta`.*
- `E701` In 28 jobs of six series with VDM_STATE1 bits 11:9 below 2 (frozen predictions of three
  models, 22 of 28, 24 of 28 and 26 of 28 right), block-2 v = 1 at c = 0 hangs (4 of 4), block-2 v =
  1 at c = 8 completes and counts as -1 (the next v = 3 job completes, the one after hangs), v = 0
  at c = 8 in block 1 and in block 2 leaves c at 8 (the next v = 3 job hangs, 2 of 2 sequences: the
  model in which v = 0 resets c is refuted twice), and block-1 v = 1 at c = 0 completes (3 of 3); a
  post hoc variant of the counter of E700 fits all 80 jobs of the two tables.
  *vdm; HW, infer; data: `vdm-verification-1141ta`.*
- `E702` At R*V = 33 (N = 8 coordinate outputs, 3 output rows, 11 vertices a task) and 32 (N = 11, 4
  rows, 8 vertices; N = 2, 2 rows, 16 vertices), attribute rows from 1 to 24 (VDM_TASK1 bits 14:7)
  left the render unchanged in 13 of the 15 jobs that completed (the tool's o0 histogram equal to
  that of the other jobs of the same N); two jobs at N = 8 changed it, a = 7 (3 pixels differ; ids
  55, 66 and 77 hold one constant row) and a = 12 (260 pixels differ, though the decoder finds every
  vertex identity, in an irregular split of the objects), and the one job of E546 that lost a vertex
  at 33 with 8 rows was not seen again in the two a = 8 jobs here (another module and tool): the
  three are treated alike, each one an event not yet repeated, pending a repeat, and no limit at 33
  is concluded; by the vertex count the model in which attribute rows add to the budget (33 plus the
  rows over 8) was wrong in 10 of 15 jobs and the model in which they do not count wrong in 1 (14 of
  15 scored, 14 of 16 counting the job that hung); 32 attribute rows at N = 2 hung the job.
  *vdm; HW, infer; data: `vdm-verification-1141ta`.*
- `E703` With the output rows of VDM_TASK1 (bits 31:24) forced to a value other than the natural (4
  + N + 3) / 4 by a xor on VDM word 7, the hardware accepts rows 4 to 7 (10 of 10 jobs completed, no
  hang or fault) and the render of every one of the 8 forced jobs differs from that of the natural
  jobs (the tool's o0 histogram: 418 to 1320 background pixels in 4 jobs and none among the listed
  values in 4, against 2288 and 2821 in the two natural jobs), at R*V of 30 and 32 as at 35, 36 and
  40; the decoder reads 76 to 95 of the 126 vertices as lost in them (a reading under a layout
  assumption), none in the two natural jobs (R*V 32 and 33); no job with the forced field equal to
  the natural one exists (a xor cannot make it), so the forcing itself is not separated from wrong
  rows and the forced-rows route does not measure the capacity limit.
  *vdm; HW, infer; data: `vdm-verification-1141ta`.*
- `E704` At 4096x4096 with 1500 vertices (E630's wd-glist-1500 scene, the exception to E625's raise
  rule), the render_pb_pages value P = 0x422, 0x424, 0x430, 0x440, 0x442, 0x460 and 0x500 and a
  repeat of 0x422 (8 jobs) all give the same result: an overflow (-ENOSPC, context kept) after 2
  partial renders, the first at status 0x400, identical status peaks (0x400, 0x400, 0x11c) and
  identical control block dwords 34 to 40 (dword 35 0x3fe, 36 = 3, 37 = 0, 38 = 0, 39 = 6), no
  raise; but P above 0x422 did not reach the TA (its threshold register 0x0624 reads 0x400 at the
  first sample of every job, where P - 0x22 would be 0x4de at P = 0x500, and the parameter-buffer
  dumps are byte-identical), so the 8 jobs are one condition and 7 repeats if the debugfs knob or
  the page buffer clamps P at 0x422, which this table cannot exclude, and the threshold is held at
  0x3fe only for P in 0x422 to 0x500; of the frozen models HA (a non-zero dword 36 blocks the raise)
  was right in 8 of 8 on that condition and its repeats, and HP (the raise needs the pages) is
  untested above 0x422, not refuted; the jobs at 1400 and 1300 vertices did not run.
  *dpm; HW, infer; data: `vdm-verification-1141ta`.*
- `E705` The tool's -n 4 runs four renders one after the other, one triangle each, so the frozen
  'four stacked' and 'four apart' cases are not four-triangle scenes, and their two predictions
  (disj4 against stack4: HG, HT) are void, not right or wrong; the page need of one triangle at
  1024x768 depends on its position: moved by 0, 192, 384 and 576 pixels it reaches status 0x13,
  0x14, 0x11 and 0xc (19, 20, 17 and 12 pages) in 0x422 pages, four renders of the unmoved one 0x13
  four times; E625's overflow rule (overflow iff P - 0x22 is below the need) gives the outcome of
  all 8 distinct conditions (the 4 positions at each of P = 0x28 and 0x30; the 22 renders include 14
  repeats of an input already rendered, all with the same outcome) (post hoc), the raise of the
  threshold (dwords 37 and 38) being in all 4 conditions at 0x28 and in none of the 4 at 0x30.
  *dpm; HW, infer; data: `vdm-verification-1141ta`.*
- `E706` Without hold_recovery the 300-vertex scene at 4096x4096 in 0x40 pages logs `*ERROR*
  sgxfive: job N hung, recovering` and ends as `job hung, context lost` (rc 3, ETIMEDOUT, registers
  0 after the reset) after 35 partial renders in 2 of 2 jobs (a run and its repeat), the same job
  with hold_recovery logs the line and `recovery held` and ends as an overflow (-ENOSPC) after 47
  partial renders in 2 of 2, and 450 vertices in 0x100 pages overflow after 16 partial renders with
  no hung line with and without the hold (2 of 2): the line does not need hold_recovery, and E438's
  hang is a driver-side recovery that the hold does not cause, not a hardware stop; what triggers
  the recovery (a time, a count, no progress) was not read; the frozen model in which the line needs
  hold_recovery was wrong in the no-hold condition (2 jobs, a run and its repeat).
  *dpm; HW, infer; data: `vdm-verification-1141ta`.*
- `E707` A program equal to E572's eotst-e1 but for the address immediate (a `mov.skipinv r1` and
  one `stad [r1,+#0], r2` between the two emits, 32 temporaries) completed here, the store landed,
  where E572's run of it faulted (at 0x340042 or 0x340043): E572's fault was not reproduced; of 10
  variants of the form (mov flag, store before or between the emits, 32 or 8 temporaries, one
  store), 8 completed and 2 faulted, the two with `mov.skipinv` and 8 temporaries (BIF fault 0xd0400
  at 0x1, not E572's 0x340042; the value landed first in both), and none of the three frozen models
  (8 of 10, 6 of 10 and 4 of 10 right) predicted the control to complete; what differs from E572's
  run is listed in the record and none of it was tested.
  *usse; HW, infer; data: `vdm-verification-1141ta`.*
- `E708` The end-of-tile task's per-tile store of the global registers, with the E130 form (a
  register-offset store to r4 + a tile slot from sa15, 128x128 and 256x128, 5 jobs), completes in 5
  of 5 (no fault line, one job the sa-only control), and 32 tile slots hold their own g16 to g31 and
  g39 to g43 plus sa0 to sa10 in 16 dwords each (all 32 tiles at 128x128, 32 of the 64 at 256x128):
  g19 = 0x1a, g25 = 3, g16 and g26 to g31 = 0, g43 = 0xff000000, g17 in 0 to 3, g23 in {1, 0x11},
  g24 in {1, 9}, g18 and g21 changing from tile to tile, but g20, g41 and g42 read 0 where E572 read
  1, 1 and 1.0.
  *usse; HW, infer; data: `vdm-verification-1141ta`.*
- `E709` With the o4 write predicated on a test of g25 (`xor.testtaz.chan0 !c0, p1, g25, #1` and o4
  under p1, k = 0, 1, 2 and 3) or unconditional (5 configurations, each an x job and a y job, none
  repeated), the o4 writes (tag 5) are found at the same destination pixels in the x and the y job
  in 24, 25, 25, 17 and 29 pairs, 120 in all, every one from an even source x and an even source y:
  pairs exist for every k, so the predicate has no visible effect on whether o4 is written; the
  number of pairs (17 at k = 3 against 24 to 29) and of tag-5 pixels (25 to 48 a job) varies between
  configurations and no repeat says whether that is noise; the frozen lane-0-only model was right in
  4 of 10 jobs (two configurations) and the any-lane model in 10 of 10 only by predicting nothing
  the predicate could change; no job with a predicate that cannot hold was run, so the table does
  not say what g25 selects.
  *pds; HW, infer; data: `vdm-verification-1141ta`.*
- `E720` On 8 held-out bilinear jobs (random 8 x 8 texels, 6 strided and 2 twiddled, every fraction
  0 to 63) the sampler's bilinear result is the two-stage form, each 8-bit channel lerped in x then
  in y, with +32 and a 6-bit shift at each stage (weights on the 1/64 grid of these jobs; weight
  precision is not tested here): 8 of 8 jobs exact over their 2048 pixels (16384 of 16384), against
  0 of 8 for the joint (sum + 2048) >> 12 form, the y-then-x order and the rounded-down variant (and
  0 of 8 for stage roundings +32/+0, +0/+32, +31, +33 and mixed).
  *texture; HW, infer; data: `texture-isp-msaa-verification-1141`.*
- `E721` On 8 held-out gradient jobs with independent operands the footprint of E563's smp2dgrad is,
  to within 0.1% and fitted with a residual, the larger of the two Euclidean lengths of the vectors
  (op0, op2) and (op1, op3) scaled by the level size (the best of six declared footprints): it has
  the highest count on 8 of 8 jobs with 1992 to 2048 of 2048 pixels (4 jobs exact, residuals 19 to
  56 pixels on the others, whole columns or rows) against at most 256 for the five other footprints,
  and the LOD fraction is truncated to 1/64: 2016 to 2048 of 2048 on 8 of 8 ladders against 1160 to
  1840 for rounding.
  *texture; HW, infer; data: `texture-isp-msaa-verification-1141`.*
- `E722` On 13 of 16 held-out T3 address jobs the model of T3 bits 28:27 (level), 19:18 (address
  scale) and 10 (single texel) with the offset chain of the level sizes and the index scaled after
  the sum is exact over 2048 pixels (13 of 13 that completed), against 12 of 13 for the strided
  chain by stride x height and 10 of 13 for the scale applied to the index only; the 3 jobs with the
  largest address extent (86016, 87040 and 174080 bytes against at most 65536 for the 13 that ran)
  faulted the job with a BIF fault.
  *texture; HW, infer; data: `texture-isp-msaa-verification-1141`.*
- `E723` With T0 bit 27 set a point-sampled texel byte is decoded sRGB to half float: 4 of 4
  held-out fills exact over 2048 pixels (strided 8 x 4, twiddled 8 x 8 twice, twiddled 32 x 32); on
  2 held-out bilinear fills neither frozen order fits, filter then decode 0 and 0 of 2048 pixels and
  decode then filter 1147 and 876.
  *texture; HW, infer; data: `texture-isp-msaa-verification-1141`.*
- `E724` Format 27 is ETC1 with the 4 x 4 blocks of the texture in Morton order with y in the low
  bit: 6 of 6 held-out fills of random valid blocks exact over 2048 pixels (16 x 16 twice, 32 x 16,
  16 x 32, 8 x 16, 8 x 8), against 0 of 6 for raster block order and 0 of 6 for Morton with x low.
  *texture; HW; data: `texture-isp-msaa-verification-1141`.*
- `E725` Textures of type 3 and type 1 are read with a stride of the texture's width and the window
  wrapping at its size (8 of 8 held-out fills exact over 2048 pixels, 8 x 8 to 32 x 32), not the
  fixed 16 of E567's reading (0 of 8); type 4 is read with a fixed stride of 32 (4 of 4 sizes exact
  after the fact), which none of the three frozen hypotheses gives.
  *texture; HW, infer; data: `texture-isp-msaa-verification-1141`.*
- `E726` Exploratory (no rule was declared; the plan's prediction was only that faces 1, 3 and 5
  appear for the negative axes, which they do): with TEXTYPE 2 the 6 axis directions read one face
  each over 2048 of 2048 pixels, faces 0 to 5 for +x, -x, +y, -y, +z, -z in blocks of 256 dwords
  (the mapping and the dominant-axis rule are post hoc [infer]), and a w sweep moves the read from
  +x to +z.
  *texture; HW, infer; data: `texture-isp-msaa-verification-1141`.*
- `E727` In 4x multisampled renders of a 12 x 6 triangle placed in each region of tile (0, 0), the
  stored image is the one the region model predicts in 17 of 17 jobs (0 pixels off, 11 of 17 images
  empty), and the visibility counter 0x0498 is non-zero in the 7 non-control jobs whose stored image
  is empty (6 distinct jobs and a repeat, TE 0xe0, 0xa0, 0x60) but reads 0 with the same empty image
  in the 4 controls at TE 0x20, so the counter does not show that every region is walked [infer].
  *isp; HW, infer; data: `texture-isp-msaa-verification-1141`.*
- `E728` CR_TE_AA with bit 29 clear and bit 30, 31 or both set (0x40, 0x80, 0xc0) leaves the TA data
  identical to the same job with bit 29 set (0 of 6144 dwords differ in 6 of 6 comparable jobs) and
  the parameter buffer identical except a one-dword shift of the 16 dwords 11 to 26 (13 dwords
  differ in 6 of 6), and stores an empty image in 9 of 9 jobs; the same words differ from TE 0x00 in
  89 to 818 parameter and 132 to 367 TA dwords.
  *isp; HW, infer; data: `texture-isp-msaa-verification-1141`.*
- `E729` At CR_TE_AA 0xe0000000 mode 2, 256 x 160 and 320 x 128 complete and 288 x 144, 256 x 288
  and 384 x 384 fault the job at pages 0x20006, 0x20006 and 0x20008; with E507's 12 sizes this
  leaves the number f of region-header arrays the TA writes at 4 or 5 (f = 3 refuted; f >= 6 refuted
  post hoc; both under the layout formula as transcribed and integer f).
  *ta; HW, infer; data: `texture-isp-msaa-verification-1141`.*
- `E730` Re-scored post hoc, not a held-out confirmation (the frozen recompute scored 0 of 12 and
  favoured the alternative "whole tile area stored", 12 of 12, because its observable counted every
  dword not 0xdeadbeef): with E465's observable the set of stored non-background dwords of the ZLS
  store is the set x < 1.25 W and y < 1.25 H on 12 of 12 jobs (6 sizes, ramp in x and in y; the
  centre rule x + 0.5 < 1.25 W is inference, as the sets are the same for the edge forms), 924 on
  the 34 x 18 control as in E465, 484 at 18 x 18, 1984 at 50 x 26, 3444 at 66 x 34, 7564 at 98 x 50
  and 2604 at 34 x 50, with 0 mismatching pixels.
  *zls; HW, infer; data: `texture-isp-msaa-verification-1141`.*
- `E731` Under the premise that the stored word is trunc(T + A (x + 0.5) + B (y + 0.5)) with a
  tile-corner value T, the three frozen candidates for T (RN of the plane at the corner, its
  truncation, a walk fl(T(i) + RN(32 A))) fit, by direction and binade: for a dyadic gradient all
  three fit 378 of 384 tiles (a control that does not discriminate, and fails in binade 2: 3 tiles
  each in dp-ax-b2 and dp-ay-b2); for a non-dyadic gradient in y, truncation and the walk fit 63 of
  63 consistent tiles in b0 and 64 of 64 in b1 (RN 63 and 56); in x, 0 of 58 consistent tiles in b0
  and 34, 40, 38 of 43 in b1; in b2 no tile admits a single T, so the premise fails there; class c
  232, 200 and 64 of 384 in total; Q200 is not settled.
  *isp; HW, infer; data: `texture-isp-msaa-verification-1141`.*
- `E732` Of the 140 jobs of the 11.39 texture, ISP and multisampling batch, 108 returned rc 0, 26 rc
  1 with only the tool's image check failing (17 msaa-a-vis, 9 msaa-b-te29), 3 rc 1 and 3 rc 3 with
  a faulted job (q140: 3, tex-c-addr: 3), none a usage error and none void; the kernel lines naming
  sgxfive in isp-a-guard (60) and isp-b-depth (105) are the 5 kpoke acknowledgements of each job, no
  fault.
  *render; HW; data: `texture-isp-msaa-verification-1141`.*
- `E733` The simulator's bilinear sample in the two-stage form of E720 (each 8-bit channel lerped in
  x on both rows and then in y, each stage (a (64 - f) + b f + 32) >> 6, the weights truncated to
  1/64 as before) replays the 8 vectors made from E720's held-out jobs 8 of 8 over 2048 pixels,
  where the joint form it replaces, (sum + 2048) >> 12, differed on all 8; the outcome of every
  other vector of the data repository is unchanged (31727 match, of which the 8 new ones, 1112
  fitted, 1103 stop, 175 skipped, 1950 left out, 48 of 130 hung jobs predicted, none differs).
  *texture; HW; data: `texture-p1141-recomp`, `vectors-texture-p1141`.*
- `E734` Below P = 0x422 the render_pb_pages knob takes effect (the job's own threshold register
  0x0624 read P - 0x22 at P = 0x200, 0x300, 0x3e0, 0x400, 0x410 and 0x420, 15 jobs, and 0x400, the
  clamp, at 0x422 in the other 7), and at 4096x4096 the threshold was raised by 0x20 (TA3DCtl dwords
  37 and 38 = 1 << 16 | thr0 and 0x20, the second abort at thr0 + 0x20) in exactly 2 of 22 jobs,
  1350 vertices at P = 0x300 and 900 at 0x200, and in none of the 20 other jobs at P = 0x3e0 to
  0x422, in 19 of which the second run reached thr0 (1500 vertices at 0x3e0 twice, 0x400, 0x410,
  0x420 and 0x422; 1350 at 0x3e0; 1380 to 1497 at 0x3e0 and 0x422; the 20th, 1350 at 0x420, took one
  partial render and is void for the raise); the frozen scorer's verdict is METHOD BROKEN, nothing
  concluded, because the job that the design used as a positive control, 1350 vertices at 0x3e0, was
  predicted to raise by every frozen hypothesis and did not; dword 36 read 2 at 1350 vertices (at
  0x3e0, 0x420 and 0x300) and 3 at 1380 to 1500 (at 0x3e0 and 0x422, 1500 also at 0x400 to 0x420).
  *dpm; HW, infer; data: `render-closing-s1:out/g-e1/`.*
- `E735` At 1024x768 the page need U of scenes of K triangles submitted as one open scene (K - 1
  geometry-only kicks and a closing render, each kick's triangle moved) reads, by the peak of
  0x0724's status and by the free-list walk alike, 29, 35 and 37 pages for 2, 3 and 4 triangles
  apart (37 twice) and 19, 22 and 22 for 2, 3 and 4 stacked 16 pixels apart (22 twice), against 19
  for one triangle (the control, as E705); E625's overflow rule (overflow iff P - 0x22 < U) held on
  the 12 boundary jobs generated and frozen from those U before they ran (overflow at P = U + 0x21,
  completion at U + 0x22, 12 of 12, the frozen held-out verdict), in 10 of them on the K-triangle
  scene itself and in 2 (2 and 4 stacked, low side) on a smaller scene, because an earlier kick
  overflowed first; the two count jobs, frozen to narrow E625's k and spacing, could not: at thr0 =
  5 and 6 each of the first three kicks overflowed on its own, so no four-triangle scene formed.
  *dpm; HW, infer; data: `render-closing-s1:out/g-e2a/`, `render-closing-s1:out/g-e2b/`.*
- `E736` In 35 dumped 64x64 renders of the TA's object for clipped, perspective, off-target and
  1/1024-pixel triangles, the frozen scorer says cannot tell because one control failed: with the
  state block's WCLAMP word (blk:14) at 1e-3 and w = 1e-5 at every vertex, which E194 saw as a
  background image and the design read as no object, the TA wrote an object of 4 vertices, a square
  of 0.96 pixel centred on (32, 32) that covers no pixel centre, with every 1/w word 0x4479ffff
  (1/1e-3 toward zero); the other five controls reproduced E651's object or E650's no-object; read
  after the run, per group as the proposal's decision says (the frozen scorer voids all groups when
  one control fails): triangles wholly beyond z = w or -w leave no object, cut and w-clipped
  triangles are stored as clipped polygons of 3 to 5 vertices, a viewport offset of 8 or 64 pixels
  keeps the object and 128, 512 and 1000 leave none, 1/1024-pixel vertices are packed rounded to
  1/256, w = 2 and 0.5 store x / w exactly, and with the clamp one ulp above w = 1e-3 the stored 1/w
  is the clamp's reciprocal.
  *ta; HW, infer; data: `render-closing-s1:out/g-e3/`.*
- `E737` Flipping bits of the index list header (VDM word 2) of E414's five-copy job (15 vertices,
  16-bit indices) breaks the job, 2 of 2 runs each: bit 24 alone hangs it (job hung, recovering; 1
  event seen), bit 25 alone and bits 24 and 25 together fault it (BIF fault 0xd0008 at 0x1, 0 events
  seen, the same word in 4 of 4), while the unflipped control reproduced E414's object (15 vertices,
  67 dwords); the frozen verdict is HH for bit 24 and HW's signature (a fault) for bit 25 and for
  both, which by the proposal earns the positive test of a 32-bit index buffer.
  *vdm; HW, infer; data: `render-closing-s1:out/g-e4/`.*
- `E738` Repeated three times each after controls that reproduced E702's histograms (N = 8 base
  0xff203040 x2288, N = 2 base x2821), E702's events at R*V = 33 and 32 behave as follows: 7
  attribute rows at N = 8 give x2285 in 3 of 3 (the frozen verdict HD) and 32 rows at N = 2 hang 3
  of 3 (HD); 12 rows at N = 8 give x2582 in 3 of 3, which the frozen scorer labels HO but which is
  neither E702's x2028 (HD) nor the base x2288 (the proposal's HO); 8 rows at N = 8 give x2288 once
  and x2156 twice (HI, 2 of 3); read after the run with q164_fate.py's decoder, the a = 7 jobs lose
  ids 55, 66 and 77 in 3 of 3, the a = 12 jobs keep every vertex in the regular split, and the two
  changed a = 8 jobs lose vertex 70 with objects of 9, 9 and 3 vertices.
  *vdm; HW, infer; data: `render-closing-s1:out/g-e5/`.*
- `E739` Two objects over a depth buffer filled with 0.25 under the ZLS control word 0x0017100e did
  not test a loaded depth: that word has bit 1 and not bit 14, which E664 needs both of for the
  load, and the one-object control drew its whole triangle under the compare less (4284 green
  pixels, the tool's own check exact), so the frozen verdict is cannot tell; read after the run, the
  drawn mask of all 8 jobs is the frozen model's with the depth starting at 1.0 (0 pixels differ),
  and both objects of a two-render scene are drawn in the closing render's colour; separately, ISP
  pass type 1 (bits 27:25 of ISP word 0) on the second, the first or neither of two overlapping
  objects gives pixel-identical images to the opaque pair at both depth orders (6 of 6 jobs,
  controls passed), and the frozen verdict is that depth order and pass order both fit and list
  order does not.
  *isp; HW, infer; data: `render-closing-s1:out/g-e8/`, `render-closing-s1:out/g-e8b/`.*
- `E740` Eleven depth ramps on a 1024 x 32 target (a control, a dyadic control and nine ramp jobs,
  eight non-dyadic gradients with one of them twice) were frozen to give, per job, the joint range
  of gradients that fits every row with one line; the frozen reader returned no row for any job
  (EMPTY at row 0), because it counted the cleared depth 1.0 (20496 of 32768 pixels in the control)
  as covered, so the frozen verdict is cannot tell; read after the run with the clear excluded, the
  dyadic control fits all 32 rows (16 ulps wide, which the frozen width rule would still call wide),
  and for the control and every ramp one line fits only over the first 32 to 96 pixels of a row (the
  control up to 160 and 288 pixels in rows 16 and 31); the same plane stored on this target differs
  from E731's 256 x 128 dump by one ulp at 167 of 8192 shared pixels.
  *isp; HW, infer; data: `render-closing-s1:out/p-b1/`.*
- `E741` E731's deviation of the stored depth below trunc32 of the exact plane in dp-ax-b2
  reproduced on a new run as the frozen control, pixel for pixel (7680 pixels at -1 ulp and 1536 at
  -2, exactly those with x + 2y >= 319 on the 256 x 128 target); the frozen verdict on the held-out
  jobs is cannot tell (d-shift matches neither the target-tied nor the triangle-tied set), because
  the frozen deviation reader counted the cleared depth 1.0 as covered; read after the run with the
  clear excluded, the triangle moved by (64, 32), the same triangle on a 256 x 512 target (also in
  the 128 rows it shares with the control) and a y gradient on 256 x 512 deviate at no pixel, and z0
  = 0.0625 deviates at the same 9216 pixels by -1 to -3 ulps.
  *isp; HW, infer; data: `render-closing-s1:out/p-b2/`.*
- `E742` Two o1 writes under complementary predicates (the !p1 write tagged 2' first, the p1 write
  tagged 2 second, p1 set by a test of g25) were run with E709's layout; the controls were E709's o4
  job (22 tag-5 pairs, inside the frozen 17 to 29) and both writes unpredicated, which the design
  required to show the second write at every source pixel and which showed it at 492 of 497 and the
  first write at 5, one cluster (sources (16,25), (16,27), (17,27), (18,27), (19,27)), so the frozen
  verdict is cannot tell; read after the run, with k = 7 no pixel got tag 2, with k = 0 a quarter
  did, all at even x and even y, with k = 3 a quarter at odd x and odd y, and the replicate of the k
  = 7 x job differs from it in 36 dwords.
  *pds; HW, infer; data: `render-closing-s1:out/p-c/`.*
- `E743` With the probe's scratch at 64 pages the three T3 address jobs that faulted with 16 pages
  in E722 (L2e2 and L3e3 at 64x64, st-L3e2 at 128x32) completed (rc 0, no fault line), as did L2e2
  at 21 and at 20 pages, while 16 pages reproduced the fault (BIF fault 0x90002 at 0x3e017001, the
  scratch base plus 80 KiB) and the 64-page control reproduced E722's A4 image; the frozen verdict
  is cannot tell (mixed: the completing jobs differ from the frozen A4 images), because the frozen
  A4 hashes were taken from E722's 16-page predictions, which for these three cases are the image of
  the model's out-of-buffer sentinel; read after the run, E722's model rendered with each job's own
  page count equals all four completing images (2048 of 2048 pixels each), and at 20 pages the
  hardware read words past the scratch without a fault.
  *texture; HW, infer; data: `render-closing-s1:out/p-d/`.*
- `E744` Eight ladders of the LOD fraction over 64 columns, with the sampling coordinates u and v
  held constant and each ladder spanning 0.031 of a 1/64 level step around n/64 for n = 2, 13, 22
  and 56 (two runs each), wrote one constant dword over all 2048 pixels of each job (0xd00001aa,
  0xd00004aa, 0xd00006aa, 0xd0000eaa; the repeats equal), so no transition was measured and the
  frozen verdict is cannot tell, while the control reproduced E721's lf-r8 image hash; read after
  the run, the constant's bits 8 to 11 (1, 4, 6, 14) follow n coarsely, near n / 4.
  *texture; HW, infer; data: `render-closing-s1:out/p-g/`.*
- `E745` With the TA3D control block kept and buffers left out of the client directory's alias by
  alias_skip, leaving out the pairs {1,2}, {1,3}, {2,3}, {4,5} or {1,5}, or buffers 1 to 5 together,
  kept two-render jobs exact (2 of 2 runs each, 12 of 12), and leaving out 6, 7, 8, 10 and 11 kept a
  three-render job exact (2 of 2), while buffer 0 left out faulted 0x91000 at 0x3000b021 (2 of 2,
  the control: E573's status, which logged 0x3000b022): the frozen held-out verdict is that no pair
  among those is needed together (HJ refuted for them, HI holds); the 1024x768 partial-render jobs
  are labelled split and HJ by the frozen scorer, which read after the run are a regex miss (both
  runs exact, identical hashes, with both renders of each run overflowed) and a mask that included
  buffer 0 (its fault is buffer 0's).
  *bif; HW, infer; data: `render-closing-s1:out/p-f/`.*
- `E746` A firmware task of ours that logs every pass of the four PDS #13 slots with CR_TIMER
  (ring_e1, window 2) saw one GETMISCINFO kick with no job as exactly one entry that is not a plain
  tick, in slot 0, with pa0 = 0 and pa1 bits 23:0 = 0x100 in 3 of 3 jobs (a gated control, rebuilt
  after run 2 of the stage and so a fit of run 2); held out of that fit and read on the new run: pa1
  bits 31:24 are a count K that every event carries (2 on every tick before the first kick, K = 2, 3
  and 4 on the three kicks in job order, K + 1 on every tick after a kick, 3 of 3), and pa2 bits
  23:0 of the kick is a sample of EVENT_TIMER counting down from 400000 core clocks (the time since
  the last tick, (400000 - pa2) / 16 CR_TIMER units, agrees with the stamps within 5.3 units, 3 of
  3); the ticks were pa0 = 2, pa1 bits 23:0 = 0 and pa2 = 0x01061a70 on a grid of 25000 CR_TIMER
  units, and a filtered 50 ms window logged nothing before the kicks (3 of 3) and after them (2 of
  2); E538's 'kick' words (pa1 = 0x03000000, pa2 = 0x01061a70) are those of the tick after the kick.
  *edm; HW, infer; data: `edm-closing-s2:out/e1c/`, `edm-closing-s2:out/e1c.run2-gate-closed/`.*
- `E747` A firmware task of ours that logs every non-tick pass of the four PDS #13 slots (ring_e1,
  window 1) saw in 14 client jobs (fill x3, copy x3, 64x64 triangle x3, 256x256 triangles -n 3 x3,
  1024x768 partial render -n 2 x2) 138 event entries, each with pa0 = 0 and exactly one bit set in
  pa1 bits 23:0: (slot, bit) (0, 8) 68, (3, 4) 26, (3, 22) 20, (1, 9) 16, (2, 21) 4 and (2, 10) 4;
  the frozen witness of the bit order, the fill's end of render, arrived in slot 3 with pa1 bit 4 in
  3 of 3 fills (the reversed order of E155: pa1 bit = 22 minus the status bit, status bit 18
  PIXELBE_END_RENDER, against pa1 bit 18 in slot 0 for the same-position reading of E146), the
  frozen bit sets of the reversed order explained 132 of the 138 entries and those of the
  same-position order 88, every entry's slot equals PDS #13's dispatch of its own words (138 of 138,
  the instrument control) and pa2 is in EVENT_TIMER's format and range on all 138 (held out); bit 19
  never appeared (not in the 2 partial renders that overflowed the parameter buffer either) and bit
  8 only in slot 0 with pa0 = 0; the arrival order per kind was the same in every replicate (3 of 3,
  3 of 3, 3 of 3, 3 of 3, 2 of 2).
  *edm; HW, infer; data: `edm-closing-s2:out/e1j/`.*
- `E748` In a firmware task of ours in the general slot (slot 0), run on the 1 kHz tick, pa0 to pa4
  read the same words as sa64 to sa68 in 3 of 3 read passes (sa64 = 2, sa65 = pa1 = 0x02000000, sa66
  = pa2 = 0x01061a70, sa67 = pa3 = 0x04000004, sa68 = pa4 = 0x00030001), with sa0 = 0x32004000 and
  not pa0; the frozen held-out prediction sa66 = 0x01061a70 (from E537 and E532, never read before)
  held in 3 of 3 read passes, and a write of a marker to sa67 or to sa68 by the allowed mov to sa
  was read back through pa3 or pa4 in the same pass and through both banks in the next task, for 3
  of 3 markers each (0xb2a06701 to 0xb2a06703, 0xb2a06801 to 0xb2a06803), the tick staying alive and
  the values the control read written back and read back (restore67, restore68) in the same stage.
  *edm; HW, infer; data: `edm-closing-s2:out/e2r/`, `edm-closing-s2:out/e2w/`.*
- `E749` A firmware task of ours that held the EDM in a three-instruction loop for 0.6 to 90 tick
  periods (n = 10000 to 1500000 iterations, CR_TIMER 15015 to 2250017 units, 1.5 units an iteration
  plus 15 within 2) was never overlapped by a pass of any slot (no slot-0 entry stamped inside a
  hold, busy flags 0 and passes of slots 1 to 3 at 0 in 12 of 12 holds) and the ticks resumed on the
  original 25000-unit grid after it; the frozen classifier said LOST for both holds of n = 10000 (a
  hold that no tick fell inside) and 'cannot tell' for all 8 holds of n = 100000, 300000 and
  1500000, because every exit fell 79 to 86 units after a tick of the old grid (the design made it
  so); read after the run, every hold that covered 6, 18 or 90 ticks was followed by exactly four
  tick entries within 585 units (23.5 us) of its exit (10 of 10 holds: e4h, e4l and the two controls
  of e5c), the first three with pa2 = 0x01061a74 (400000 - 12) and the fourth with an EVENT_TIMER
  sample about 183 to 190 CR_TIMER units old, the age of the first entry after the last held tick,
  and a tick stream of 0x01061a70 on the old grid afterwards.
  *edm; HW, infer; data: `edm-closing-s2:out/e4c/`, `edm-closing-s2:out/e4h/`,
  `edm-closing-s2:out/e4l/`, `edm-closing-s2:out/e5c/`.*

### 2026-11-10

- `E750` A GETMISCINFO kick issued 3.4 to 3.6 ms after the command of a 90-period hold of the EDM by
  a task of ours (the hold's state read busy before the kick, 3 of 3) was not lost: the debugfs read
  was answered after 86.7 to 87.5 ms and the ring logged exactly one kick entry (pa0 0, pa1 bits
  23:0 0x100, count byte 2, 3 and 4) 328 to 552 CR_TIMER units after the hold's exit in 3 of 3 jobs,
  scored QUEUED by the frozen classifier (the other discriminant, LOST, was no kick entry and no
  answer); the stage's gate stayed closed because its control, the same hold without a kick, which
  had to reproduce e4l's shape class, had no told shape on either side (every shape 'cannot tell',
  E749), so the held triangle stage e5t did not run in this session; the kick entries' pa2 (age
  283.8 and 287.5 units for the first two, 22415 for the third) was read after the run.
  *edm; HW, infer; data: `edm-closing-s2:out/e5c/`.*
- `E751` With the exit of every hold designed to fall mid-period (about 12500 CR_TIMER units from
  the two neighbouring grid ticks), a firmware task of ours that held the EDM for H tick periods was
  followed by exactly min(H, 4) tick entries before the next grid tick in all 12 holds (H = 1 x2, 2
  x2, 3 x2, 4 x2, 6 x2, 90 x2 in e4m and e4l: ONE at H = 1, ALL at H = 2 to 4, PARTIAL(4) at H = 6
  and 90), the frozen held-out prediction q = min(H, 4) of the frozen classifier, which also fits
  ALL at H = 1 to 4 and ONE at H = 1, and which the 6 and 90 tick holds separate from ALL and the 2
  to 90 tick holds from ONE; the first min(H, 3) entries read pa2 = 0x01061a74 and for H >= 4 the
  fourth read an EVENT_TIMER sample 12599 to 12614 units old, within 25 units of the first entry's
  time after the last held tick (the frozen pa2 signature, 12 of 12), and the window count (entries
  logged plus drops) equalled open time x 0.99746 - H + min(H, 4) within 1.5 in 12 of 12 (the frozen
  second instrument; 0.8 at most); the three no-hold controls of e4c held (16 entries on the 25000
  grid, 3 of 3); the conditions H = 1 to 4 are new, H = 6 and 90 repeat run 3's holds of S2 (E749)
  with their exits moved mid-period.
  *edm; HW, infer; data: `edm-closing-s2b:out/e4c/`, `edm-closing-s2b:out/e4m/`,
  `edm-closing-s2b:out/e4l/`.*
- `E752` During a hold of the EDM of 90 tick periods by a task of ours (2262433 to 2262438 CR_TIMER
  units, 90.7 ms, ending mid-period), a GETMISCINFO kick issued 3.4 to 3.6 ms after the command (the
  hold's state read busy before it, 3 of 3) was queued and logged once after the hold's exit (pa0 0,
  pa1 bits 23:0 0x100, count byte 2, 3 and 4), in 3 of 3 jobs scored QUEUED by the frozen
  classifier, the debugfs read answered after 86.98, 87.99 and 88.03 ms, with the control (the same
  hold with no kick) reproducing e4l's shape class (PARTIAL, 2 of 2, E751) so that the stage gate
  opened; the kick took the fifth, third and third place of the entries drained after the exit
  (window 2), its pa2 age 12744 units (latched when the drain began, with the pending tick of E751's
  fourth entry, age 12604) in the first job and 19522 and 21884 units (latched on arrival, ahead of
  one pending tick of age 12612 and 12600) in the other two; and a 64x64 triangle (tool `tri`,
  hold_recovery Y for that job only, read back and put back) started in the same kind of hold
  completed rc 0 in 75230, 73184 and 74788 us against 5673 and 6038 us for the two no-hold controls,
  with the same 9 event entries (0:8, 1:9, 3:4, 3:22 and five more 0:8 as without a hold) all logged
  after the hold's exit, the first 552 to 567 units after it, scored QUEUED (the job's events at the
  exit) in 3 of 3.
  *edm; HW, infer; data: `edm-closing-s2b:out/e5c/`, `edm-closing-s2b:out/e5t/`.*
- `E753` At 4096x4096 with the green pixel program, the TA's threshold was raised by 0x20 (TA3DCtl
  dword 38 = 0x20, dword 37 = 1 << 16 | thr0) in all 6 ladder jobs at P = 0x320, 0x340 and 0x360
  (1350 and 1500 vertices each; thr0 = P - 0x22 = 0x2fe, 0x31e, 0x33e) and in none of the 8 jobs at
  P = 0x380, 0x3a0, 0x3c0 (1350 and 1500 each; thr0 0x35e, 0x37e, 0x39e) and 0x3e0 (1350 and 1380;
  thr0 0x3be), all 14 of which had a second run that reached thr0; the step is at the same P for
  both scenes, last raise 0x360 and first silent 0x380, so the limit C of the raised threshold
  (raise iff thr0 + 0x20 <= C) lies in [0x35e, 0x37e), inside the S1 post-hoc bound [0x2fe, 0x3de):
  the frozen held-out verdict HP1 (one step for both scenes), with both controls passing
  (c-1500-0x422 no raise, p-1350-0x300 raise, each as in S1); the job's own register 0x0624 read P -
  0x22 in 16 of 16 jobs (0x400 at 0x422).
  *dpm; HW, infer; data: `render-closing-s1b:out/g-e1/`.*
- `E754` With every vertex at one w inside the guard band (x and y scaled by w, so the stored x and
  y equal the original triangle's: 4 of 4 jobs, w = 3, 7, 0.003 and 3e-5), the 1/w word of the TA's
  object is the float32 reciprocal truncated toward zero in 4 of 4 (0x3eaaaaaa, 0x3e124924,
  0x43a6aaaa, 0x47023555 at all three vertices; round-to-nearest, one unit above, refuted 4 of 8
  checks), the frozen held-out verdict of group e3i with its control (w = 1, E651's object) passing;
  with w = 1e-5 under a clamp (block word 14) of 3e-5, 1e-4, 3e-4 and 1e-3 the stored object has the
  original's x and y shrunk about the centre by w / clamp (to the 1/64 pixel) and 1/w = 1/clamp in 4
  of 5 jobs (one of them with the clamp equal to w, so unshrunk), the fifth, at 1e-3, writing no
  object, and the clamp jobs' 1/w words are the truncated reciprocal in one case (3e-5) and the
  rounded one in another (3e-4), so every frozen clamp model (replace by the clamp with truncation
  or with rounding, the triangle shrinks, the object removed) is refuted at least once and none is
  consistent; the repeat of S1's cuts (z = +w and -w) gives clipped polygons of 4 and 3 vertices
  that are not the original three, 2 of 2.
  *ta; HW, infer; data: `render-closing-s1b:out/g-e3/`.*
- `E755` Of E702's three events, in S1b's run of the same VDM words at R * V = 33 on a 64 x 64
  target with 126 vertices, 8 coordinate outputs (the o0 histogram counts the pixels still reading
  0xff203040, x), the two controls reproduce E702 (attribute rows 1 at N = 8: x2288, no vertex lost;
  attribute rows 9 at N = 2: x2821) but the a = 8 job (attribute rows 8) is not a function of its
  words: three runs with a reset before each gave x2156 with vertex 70 lost and objects split 15,
  15, 15, 15, 9, 15, 9, 15, 15, 3; x2260 with vertex 70 lost and the regular split 15 x 8 and 6; and
  x2288 with no vertex lost, and three runs with no reset before gave x2260 with vertex 70 lost 3 of
  3, the lost-vertex patterns of the two triples differing (HC, state carry, held out: the frozen
  scorer prints DIFFERENT; not ruled out by this table); the a = 12 job (attribute rows 12) gave
  x2582 and x2313, neither E702's x2028, nor the base x2288, and not S1's x2582 in 3 of 3: frozen
  HI, not a function of the words, in 2 of 2 (repeat only).
  *vdm; HW, infer; data: `render-closing-s1b:out/g-e5/`.*
- `E756` With the index list of E414's five-triangle job (15 vertices) written as 32-bit words (the
  tool's --index-width 32, which sets bit 25 of VDM word 2 itself), the job faulted at BIF fault
  0xd0008 at 0x1 with 0 events seen (1 run), as it did with bit 24 set as well (1 run) and as the
  control with the 16-bit list and bit 25 does (ix-25, 1 run, the fault of S1's g-e4 in 2 of 2): bit
  25 does not select a 32-bit index width (the frozen HW32, predicted to draw E414's object, refuted
  in these 2 of 4 told rows; the frozen HX, bit 25 is something else, consistent in 4 of 4); with
  bit 25 cleared by a flip over the 32-bit list (ix32-n, 2 of 2) the job completed with an object of
  5 vertices (30 object dwords, against 15 vertices and 67 dwords of the 16-bit control ix-c) and an
  image of background only (4096 of 4096 pixels), which both frozen models predicted (not the
  control's object) and which is what a 32-bit list read as 16-bit indices gives (0, 0, 1, 0, 2, 0,
  ... name vertices 0 to 4); the two faulting conditions each ran once, because the stage's
  hypothesis limit skipped their replicates.
  *vdm; HW, infer; data: `render-closing-s1b:out/g-e4w/`.*
- `E757` Over two overlapping objects (green first at depth 0.5, red second at 0.25 or 0.75) a
  second object with the depth compare ALWAYS (ISP word 0 bits 24:22 = 7) and pass type 1 (word
  0x03c00200) drew over the first although it was the farther (0.75) in 2 of 2 runs (red 1098
  pixels, green 0), and a first object with compare always and pass type 1 under a nearer opaque
  second (0.25) left the second's colour in 2 of 2 runs (red 1098, green 0); the opaque always
  control (0x01c00200, second, farther) gave the same image (red 1098), as did both-opaque-less with
  the second nearer (red 1098) while the second farther lost (green 1062, red 36); the frozen
  verdict: controls pass; held out: list order and pass type changes nothing (S1 post hoc)
  consistent with 4 of 4, depth order and pass order refuted in 2 of 4 each; no hypothesis separates
  list order from pass type changes nothing here.
  *isp; HW, infer; data: `render-closing-s1b:out/g-e8b/`.*
- `E758` The lower-binade deviation of the dyadic depth plane of E731 (A = 1/8192, B = 0, depth
  0.125 at two vertices and 0.1875 at the third, stored minus truncated exact plane, the cleared 1.0
  excluded) reproduced exactly on 256 x 128 (the control, 2 of 2 runs: 7680 pixels at -1 ulp and
  1536 at -2, the set of dp-ax-b2) and was absent on the target 256 x 192 (0 of 49152 covered
  pixels), present on 256 x 256 (18528 of 65536: 13920 at -1 and 4608 at -2) and absent again on 256
  x 512 and with the triangle moved by (64, 32) (the two repeats, 0 deviating pixels), and a smaller
  triangle of the same plane (vertices at 448 and at 384 pixels) deviated at every one of the 32768
  covered pixels of 256 x 128 (-5 to -1 ulps); the frozen verdict: held out: no hypothesis
  consistent, HT (the region is tied to target coordinates) refuted in 4 of 4, HV (tied to the
  triangle) in 2 of 2 and HCLIP (the plane is set up from the clipped polygon in the parameter
  buffer: a job deviates iff its stored polygon is not the original triangle) in 1 of 4; as repeats
  HT and HV 2 of 2 and HCLIP 2 of 3.
  *isp; HW, infer; data: `render-closing-s1b:out/p-b2/`.*
- `E759` Rerun with the order control c-u three times and the frozen criterion that the tag-2
  fraction is at least 0.98 (S1 required exactly 1.0 and saw 0.990), the control passed in 3 of 3
  runs (tag 2 at 486, 482 and 488 source pixels, the first-write tag 2' at 5, 4 and 2: fractions
  0.990, 0.992 and 0.996; the first write survives at (16,27) and (17,27) in all three runs, at 5
  sources including (16,25) and (18,27) and (19,27) in the first, as in S1); with the control E709's
  o4g-3 at 26 tag-5 pairs (17 to 29), S1's post-hoc readings of the predicate guard repeated in the
  same numbers: g25 == 7 gives no tag 2 (0 of 486 o1 landings), g25 == 0 gives 0.253 of the
  landings, all at (even, even) sources, g25 == 3 0.248, all at (odd, odd) sources, and the g23 test
  0.237 (frozen 0.25 within 0.07); the frozen verdict is held out: none (no row of the table was
  held out), repeat only: HQ (g25 = the lane in the 2 x 2 quad) consistent 3, HP-g23 1, HA (all or
  nothing) refuted 3 of 3 and HN (both writes land, the second wins) 4 of 4, and the replicate
  c-k7-x-rep read the same tag-2 fraction (0.000) as c-k7-x with 61 dwords different.
  *pds; HW, infer; data: `render-closing-s1b:out/p-c/`.*
- `E760` With the probe's scratch at 20 and 19 pages (80 and 76 KiB) the L2e2 job (E722's extent
  86016 bytes) completed with rc 0 and no fault line, each image of 2048 pixels with 128 distinct
  words none of them tagged 0xD, the two images different (every pixel past the scratch in the
  model), and with 18 pages (72 KiB) the job completed in 545 us, wrote no pixel (the tool: `failed:
  no pixel written`, rc 3) and left no fault line and no BIF fault (bif_faults 0), an outcome
  neither HM (completes) nor HB-end (faults) predicted, which stopped the runner at the stage's
  eighth job: the 17-page job and the control d-L2e2-16 did not run, so the frozen verdict is cannot
  tell (the control void); the 64-page control d-ok-64 was A4 exact, and the repeats of S1's
  post-hoc fits gave the images S1 recorded byte for byte, the three jobs that faulted at 16 pages
  (L2e2, L3e3, st-L3e2) at 64 pages and L2e2 at 21 pages, each A4 exact at its own page count (4 of
  4).
  *texture; HW, infer; data: `render-closing-s1b:out/p-d/`.*
- `E761` With the debugfs alias_skip mask 0x1e (buffers 1, 2, 3 and 4 left out of the client
  directory's alias together) two 1024x768 renders that both overflow the parameter buffer at
  render_pb_pages = 0x23 (`tri: 0 of 2 renders ok, 2 overflowed`) were exact in 2 of 2 runs (every
  diff 0 of 786432, the same two target hashes as the run with no mask), as were the same jobs with
  the mask 0xdc0 (buffers 6, 7, 8, 10, 11 left out) in 2 of 2 runs, and buffer 0 left out faulted at
  BIF fault 0x91000 at 0x3000b021 (the control, 1 of 1, as in S1 and E573); the frozen verdict:
  controls reproduce (f-ctl0, f-dpm-0); held out: f-dpm-1e exact 2 of 2; repeat only: f-dpm-dc0
  exact 2 of 2.
  *bif; HW, infer; data: `render-closing-s1b:out/p-f/`.*
- `E762` S3's control a4 (tri --tri-full at 320 x 400, CR_TE_AA 0x20000000, mode 2 with E507's
  sample words, in a render context made for 544 x 400) completed and stored the triangle colour in
  all but 28 of 128000 pixels, the first wrong one at (304, 128) holding the clear colour
  0xff203040; E727's region model, unchanged and run after the session, predicts exactly 28
  background pixels with the first at (304, 128) (7 in each of the 32 x 16 tiles (9, 8), (7, 13),
  (5, 18), (3, 23), at their top-left corners), with the TA's own per-tile primitive masks as well
  as with the model's; the frozen prediction (diff 0) did not use the model, so the control's
  failure is a design error of S3, not a hardware fault, a layout effect or a scorer error [infer,
  post hoc].
  *isp; HW, infer; data: `render-closing-s3:out/20261110-003114/s3-a-safe/`.*
- `E763` In a render context made for 544 x 400, a 320 x 400 render at CR_TE_AA 0x20000000 mode 2
  (S3's a4) had a TA data buffer of 0xa000 bytes (the maximum's layout: --max-width takes effect)
  and the TA wrote in it one array of 512 region headers at 0x4000 to 0x57f4, the target's own
  layout (2 x 2 macrotiles of 8 x 16 regions, rgn_size 0x1800, not the maximum's 0x2400), 250 inside
  the target with a stream block each and 262 flagged outside it, and nothing below 0x4000 or from
  0x5800 to 0xa000 (1 run).
  *ta; HW, infer; data: `render-closing-s3:out/20261110-003114/s3-a-safe/`.*
- `E764` Held with debugfs hold_recovery and read 2.8 s and 3.8 s after the launch, E444's two
  faults reproduce word for word (1 run each): the TA's read of an unmapped stream page
  CR_EVENT_STATUS 0x20000000, CR_EVENT_STATUS2 0x480, CR_BIF_INT_STAT 0x90008, CR_BIF_FAULT
  0x3e000001, the background program's fetch 0x20000000, 0x440, 0xd0400, 0x0001f061, each stable
  between the two reads and clear after the debugfs reset (the frozen verdict, a control passing);
  and, read post hoc from the timeline rows (not frozen), sampled about every 4.3 us from the
  launch, the fault word and address appear first with CR_EVENT_STATUS2 still 0x400, and bit 7 (TA
  read) or bit 6 (background fetch) sets 121.2 and 121.1 us later, no other bit rising up to the
  reset.
  *edm; HW, infer; data: `render-closing-s3:out/20261110-003209/s3-e1-ctl/`.*
- `E765` Held with debugfs hold_recovery, S1's texture job that reads past the probe's 64 KiB
  scratch (s1d-tw64x64-l2e2, E722's ad-tw64x64-L2e2 at the 16-page scratch of E743) faults at
  CR_BIF_INT_STAT 0x90002 and CR_BIF_FAULT 0x3e017001 (page 0x3e017, as in S1) and reads
  CR_EVENT_STATUS 0x20000000 and CR_EVENT_STATUS2 0x440 at 2.8 s and 3.8 s, clear after the debugfs
  reset, the frozen HE (no status bit of its own; 1 run, held out); post hoc from the timeline rows
  (not frozen), sampled every 4.3 us the fault word appears with status2 0x400 and bit 6 sets 122.5
  us later, as for E444's background fetch.
  *texture; HW, infer; data: `render-closing-s3:out/20261110-003406/s3-e1/`.*
- `E766` debugfs xfer_ro (E021's 64 x 32 fill aimed at a read-only alias of a kernel buffer) on the
  current kernel writes nothing and faults at CR_BIF_INT_STAT 0x80020 and CR_BIF_FAULT 0x32200001 as
  in E021, and reads CR_EVENT_STATUS 0x20000000 and CR_EVENT_STATUS2 0x440 at 2.8 s and 3.8 s, clear
  after the debugfs reset: the transfer's write fault raises no status bit of its own and reads
  0x440, not the EDM write fault's idle 0x400 (the frozen HE, not HE-edm; 1 run, held out); post hoc
  from the timeline rows (not frozen), bit 6 sets 124.1 us after the fault word.
  *transfer; HW, infer; data: `render-closing-s3:out/20261110-003455/s3-xfer/`.*
- `E767` Sampled every 4.3 us through the debugfs reset of three held render faults (S3's
  e1-ta-read, e1-bg-fetch, e1-tex), CR_BIF_INT_STAT drops to the idle 0x80000 and CR_BIF_FAULT to 0
  in one row while CR_EVENT_STATUS and CR_EVENT_STATUS2 keep their held values (0x20000000 and 0x480
  or 0x440), and the two status registers read 0 only 11.3, 8.2 and 6.8 ms later; by the kernel's
  reset code the first change is the halt (the firmware's deinit script and the soft reset of every
  block) and the second the host clears that follow the CLEAR_FAULT write of CR_BIF_CTRL, so the
  fault already reads clear before CR_BIF_CTRL's clear bit is written [infer, post hoc, outside the
  frozen window].
  *bif; HW, infer; data: `render-closing-s3:out/20261110-003209/s3-e1-ctl/`,
  `render-closing-s3:out/20261110-003406/s3-e1/`.*
- `E768` The count byte of the event word (pa1 bits 31:24) that a firmware task of ours (ring_e1)
  read on every tick and kick equalled the number of commands (kicks) the kernel had sent through
  the CCB since the firmware load, mod 256 (GETMISCINFO, fill and copy alike), in all 15 jobs of the
  frozen stage: 2 after the arm (the boot's GETMISCINFO and the runner's own: 2 of 2 jobs, and 1 of
  1 after a debugfs reset and an arm), 1 when the runner's own read was left out of the arm (2 of 2)
  and 4 when two more were added (2 of 2), the kick's own entry 2 and the ticks after it 3 after one
  kick (2 of 2), 254 kicks after the arm wrapped it to 0 (the four logged kicks read 0, 1, 2 and 3
  and the ticks after them 4, 2 of 2, against 255 for a saturating byte), and in a 64x64 fill and a
  copy it rose by one after each of the job's two (slot 0, pa0 0, pa1 bit 8) entries and after no
  other entry (4 of 4); the CCB write offset ccbctl[0] equalled the count in every row; held out 31
  of 31, fit 13 of 13, replicate 3 of 3 rows as the frozen scorer printed, and none of the frozen
  predictions failed; whether the hardware counts the writes to CR_EVENT_KICK or reads the kernel's
  kicker word is not separated.
  *edm; HW, infer; data: `edm-closing-r1-events:out/k/`.*
- `E769` In fills of 2048 pixels whose pixel program is a loop of our own (every job after a debugfs
  reset, the register read 0x400 before it, o0 = 0 on all 2048 pixels after it: the loop ran to its
  end), CR_EVENT_STATUS2 bit 6 set at 26, 27, 28, 29, 30 and 56 iterations of a 16-instruction body
  (14 multiply-adds, a counter update and a branch; clear at 20; 1 run each) but at no point of a
  4-instruction body from 50 to 120 iterations (50, 80, 100, 105, 108, 110, 112, 115, 120; 1 run
  each) and at no point of an 8-instruction body with a load and a wait (ldad, wdf, four
  multiply-adds, counter, branch) at 40, 50, 53 and 56 iterations (1 run each), while E431's
  8-instruction body (six multiply-adds) was clear at 53 and set at 56 in 2 of 2 runs each (the
  control, 0x400 and 0x440), so the latch is neither a count of 54 to 55 iterations (the body of 16
  sets at 26) nor about 440 instructions of one instance (the body of 4 is clear at 480, the body
  with a load at 448, the body of 16 sets at 416); the frozen H-TIME = H-INSTR and H-ITER rows read
  refuted on these points, but the stage's own control rule (the job time must grow with the loop
  length in every fill ladder) failed for the 8-instruction ladder (4 jobs at 53 and 56) and the
  4-instruction ladder (9 jobs, 721 to 1421 us, not monotone, single runs), so the frozen scorer
  ended 'the ladders are cannot tell'; with a stock vertex program (0 iterations) the register read
  0x400 and a held TA fault 0x480 as predicted.
  *edm; HW, infer; data: `edm-closing-r1-events:out/t/`.*
- `E770` Our loop programs (E769's: 6 multiply-adds, a counter update and a branch an iteration, o0
  written from the counter) run as the pixel program of a probe --tri pixel triangle left the image
  with o0 = 0 in only some of the pixels, the same ones whatever the iteration count: 16 of 64
  pixels on 8x8 (with two stray words, 0x04000004 and 0x40800000, and 46 untouched; 12 jobs, T3 at
  53 to 440 iterations and T4's load body at 20 to 56), 85 of 1024 on 32x32 (6 jobs, 53 to 440), 204
  of 16384 on 128x128 at 53 iterations (with 18 pixels of 0xff00ff00, one of 0x881d6bc1 and 159
  others) and no pixel at all on 128x128 at 56, 80, 130, 220 and 440 iterations and on 256x256 at 53
  to 440 (the probe printed 'o0 0xff203040 (16384 of 16384)' and '(65536 of 65536)', rc 0 in all 11
  jobs), and CR_EVENT_STATUS2 read 0x400 after every one of the 30 triangle jobs; the loops did not
  run, or did not write, in most of the pixels the triangles cover, so the 30 triangle rows (T3's
  four sizes, T4's 8x8 ladder) are void as readings of bit 6 and the occupancy and load-latency
  questions are not answered; the fill ladders of E769 are not affected.
  *render; HW, infer; data: `edm-closing-r1-events:out/t/`.*
- `E771` In 8 jobs of a 4096x4096 render of 1500 vertices under our event ring (ring_e1 with 12
  rungs in slot 3, window 1) no entry of the ring carried pa1 bit 19 (22, 22, 22, 17, 17, 17, 17 and
  17 entries, no drops in any slot), whether the TA's threshold was raised (render_pb_pages 0x320:
  the job's own register 0x0624 read 0x2fe and TA3DCtl dword 38 0x20, 3 partial renders, 3 of 3
  jobs) or not (0x3a0: 0x37e, dword 38 0, 2 partial renders, 3 of 3; 0x422: 0x400, dword 38 0, 2
  partial renders, 2 of 2), and the parallel register timeline of CR_EVENT_STATUS (1064 to 1411
  samples a job, about 5.2 us apart at the median) showed no rising edge of status bit 3, which the
  reversed order of E155 maps to pa1 bit 19, in any of the 8 jobs; the controls of the stage
  reproduced E747 (a 64x64 triangle: its 9 entries in E747's order, 2 of 2 runs; a 1024x768 partial
  render: slot 2 bits 21 and 10, no bit 19, 1 of 1, the dispatch of every entry 100%); so the raise
  rule (H-RAISE: bit 19 only in raise jobs) and the threshold rule (H-THRESH: whenever the TA
  reaches its threshold) are refuted on these jobs and what stands is that bit 19 does not arrive
  here at all (H-NEVER), or arrives in a way neither the ring nor a sampled register shows; the
  frozen held-out rows read 12 held and 10 FAILED, the 10 being the three H-RAISE rows of the raise
  jobs and the order comparison of the timeline with the ring (D5) in 7 of 8 jobs.
  *edm; HW, infer; data: `edm-closing-r1-events:out/d0/`, `edm-closing-r1-events:out/d1/`,
  `edm-closing-r1-events:out/d0-try1/`, `edm-closing-r1-events:out/d1-try1/`.*
- `E772` R1-pixgeo stage p-c2 (41 jobs: 18 configurations of S1b's p-c program as an x job and a y
  job whose pixel words decode to their source pixel, the direct reads c-rd-g23 and c-rd-g25, the
  premise pair c-rd-pa and one replicate): the frozen verdict is CANNOT TELL, because the global
  control c-e709 (E709's o4g-3 unchanged) gave 10 tag-5 pairs against the frozen 17 to 29, so no
  held-out row was scored (the order controls c-u and c-u-r2 passed the frozen 0.98 with 0.990 and
  0.994, and c-rd-pa held 1.000 of 1062 pixels); read after the run and not held out [infer over
  data]: under `xor.testtaz.chan0 !c0, p1, g25, #k` the tag-2 write landed only at (odd x, even y)
  for k = 1 (120 of 489 o1 sources, 0.245), only at (even, odd) for k = 2 (118 of 484) and never for
  k = 5 or 7 (0 of 479 and 0 of 487), the replicate the same; the direct read of g25 gave o0 = (x &
  1) | (y & 1) << 1 in 1062 of 1062 written pixels and that of g23 gave o0 = x mod 32 in 1062 of
  1062, so the masks 0x01, 0x08, 0x10 gave tag 2 at x bit 0, 3 and 4 and 0x20 and 0x100000 never;
  the o4 writes were tag 5 and never tag 5' under k = 0, 3, 7 and unpredicated (37, 42, 21 and 23
  pairs); the tag-5 pair count of the 18 configurations ran from 10 to 42, 8 of 18 outside the
  frozen range.
  *pds; HW, infer; data: `render-closing-r1-pixgeo:out/p-c2/`.*
- `E773` R1-pixgeo stage g-u1 (21 jobs, P = 0x422 except the boundary jobs): the page need U of 17
  scenes (the default triangle of the tool, one to four copies, moved or apart, at 640x480,
  1024x768, 1280x1024, 2048x1536, 2048x2048 and 4096x4096) read as the peak of the low half of
  0x0724 and as the free-list walk (head - 1) agreed in all 17 and equalled HU1's frozen prediction
  (sgx-pipe's TA model as it stands, 128 bytes a stream, a page per macrotile that has streams, plus
  1 global page) with residual 0 in 15 of 15 held-out scenes (U = 21, 22, 22, 13, 24, 30, 21, 35,
  11, 31, 79, 60, 7, 275 and 438), the two controls 19 and 29 passed, HU2 (macrotiles with streams
  plus 8) was refuted in 8 of 8 held-out scenes where it differs (and in 1 of 2 repeats), and E625's
  rule (overflow iff P - 0x22 is below U) with HU1's U held in the 4 boundary jobs (overflow at P =
  0x39 and 0x36, completion at 0x3a and 0x37, 4 of 4, held out); the frozen verdict: controls pass,
  held out consistent HU1 (15) and E625's rule on HU1's U (4), refuted HU2 (8 of 8).
  *dpm; HW, infer; data: `render-closing-r1-pixgeo:out/g-u1/`.*
- `E774` R1-pixgeo stages g-c1 and g-c1f (23 jobs at 4096x4096 with 1500 vertices, 5 of them also
  with 1350, the tool's triangle and p1139-green, the first threshold thr0 = P - 0x22 set by
  render_pb_pages and proved by the job's own 0x0624 in 23 of 23): along P the TA's threshold was
  raised by 0x20 (dword 38 = 0x20, dword 37 = 0x10000 | thr0, the second run reaching thr0 + 0x20)
  at every cell from P = 0x360 to 0x373 and not at 0x374 to 0x380, one flip and no other, so the
  raise happens iff thr0 + 0x20 <= C with C = 0x371 (thr0 at most 0x351) for this scene and target;
  the controls reproduced E753 (raise at 0x360, none at 0x380), HP1 held (each of the 5 cells of
  1350 vertices, P = 0x366, 0x36e, 0x372, 0x376 and 0x37a, gave the outcome of the 1500 cell at that
  P, 5 of 5, held out), and the frozen verdict was H-abs holds with the last raise 0x372, the first
  silent 0x374 and C in [0x370, 0x372), the step-1 cell 0x373 (g-c1f, run after the verdict) raised
  and fixed C in [0x371, 0x372); the ladder moves P and the threshold together, so a limit tied to P
  is not separated from a constant C by it.
  *dpm; HW, infer; data: `render-closing-r1-pixgeo:out/g-c1/`,
  `render-closing-r1-pixgeo:out/g-c1f/`.*
- `E775` CR_DPM_GLOBAL_PAGE_STATUS (0x072c) was sampled in the register timelines of the DPM jobs of
  R1-pixgeo (the gate of two trial jobs, u-ctl-1 and u-ctl-2a, ran clean: normal class, no log line
  but ours, 0x0724 peaks 19 and 29 as the controls, a plain triangle exact after each; every later
  DPM job sampled it), its low and high halves equal at 0x10001 to 0x50005 in the 4096x4096 jobs,
  and the frozen side-table reading 'dword 36 of the control block = max(the 0x072c count in the
  sample before the first abort - 2, 0)' failed its held-out part: raised jobs 0 of 14 (g-c1 0 of
  13, g-c1f 0 of 1; every one read dword 36 = 3 against a predicted 1) and unraised jobs 6 of 9 in
  g-c1 and 2 of 2 in g-u1 (the three misses read 3 where the TA data's global list holds 4 pages and
  dword 36 = 2), while the 9 raised jobs of g-u2 (count 1, floor 0) fit trivially; read after the
  run and not held out [infer over data]: the page count of the global list in the TA data at the
  state page (E753's correction of 2026-11-10) equals dword 36 + 2 in the 9 unraised jobs of g-c1 (9
  of 9, a reading made before the run and tested on new jobs) and in none of the 14 raised ones (0
  of 14, as E627 says: after a raise the page holds the lists of the later runs), and the maximum of
  the 0x072c count over the whole job less 2 (floor 0) equals dword 36 in all 23 jobs of g-c1 and
  g-c1f (14 raised, 9 unraised; 3 in every raised job where the count reaches 5, 1 or 2 in the
  unraised where it reaches 3 or 4).
  *dpm; HW, infer; data: `render-closing-r1-pixgeo:out/g-u1/`, `render-closing-r1-pixgeo:out/g-c1/`,
  `render-closing-r1-pixgeo:out/g-c1f/`, `render-closing-r1-pixgeo:out/g-u2/`.*
- `E776` R1-pixgeo stage g-t1 (11 jobs, the tool's 64x64 triangle with the viewport's x offset
  (block word 6) or y offset (word 8) moved, the triangle spanning offset - 24 to offset + 24): with
  both controls passing (o-x64 an object, o-x1000 none) the TA wrote and listed an object at x
  offset 87.5 (min x 63.5) and y offset 87.5, wrote none at x offset 88.0, 88.5, 96 and 104 (min x
  64.0 and beyond) and none at x offset -24.0 and -24.5 (max x 0.0 and -0.5), and at y offset 88.0
  wrote the object's 23 words and no region listed it; the frozen verdict: held out consistent none,
  refuted HO-region (E542's tile rule on target regions only, low side closed, high side open) 1 of
  9 (the -24.0 cell, predicted present) and HO-band (a band beyond the edge) 3 of 6 (88.0, -24.0,
  -24.5), the written-unlisted cell undecidable for both.
  *ta; HW, infer; data: `render-closing-r1-pixgeo:out/g-t1/`.*
- `E777` R1-pixgeo stage g-t2 (7 jobs: vertex programs with z = A x + B or A y + B on the tool's
  triangle, w = 1, both controls passing, E651's z-flat099 object and the 4-vertex z-cut-p object of
  S1b): the objects of the five clipped polygons (z-cut-p05, z-slab, z-cut-ym, z-cut-m-slope and the
  replicate z-cut-p-r2) were written as clipped polygons (clip 5 of 5), their vertex sets equalled
  the Sutherland-Hodgman polygon over the edges A to B, B to C, C to A in 5 of 5 (nvert and set, HSH
  10 of 10 rows) and their prim lists were the strip triangles with entry = stored index | 16 for a
  boundary edge in 5 of 5 (HPR, (16, 1, 18) and (2, 17, 19) for 4 vertices, (16, 17, 18) for 3); the
  stored order and depth words (0.5 + 0.5 z at every vertex, the clip-made ones 0 or 1) were those
  of the strip zigzag of the polygon in the 2 four-vertex objects of the two-plane programs (z-slab,
  z-cut-m-slope) when the -w plane is applied first and not when the +w plane is (-w first 2 of 2,
  +w first refuted 2 of 2), and in 2 of 3 of the single-plane polygons (z-cut-p05 and its replicate)
  but not in z-cut-ym, whose 3 vertices were stored in the Sutherland-Hodgman order itself, one
  place from the frozen zigzag (the frozen rows HZZ and HDP without a plane order refuted 1 of 3
  each, the three being z-cut-p05, z-cut-ym and the replicate).
  *ta; HW, infer; data: `render-closing-r1-pixgeo:out/g-t2/`.*
- `E778` R1-pixgeo stage g-t7 (4 jobs): with the control e3f-ctl (coordinates on the 1/256 grid,
  E651's packing) passing, the window coordinates of three held-out triangles given on a 1/1024
  pixel grid at odd multiples (a quarter or three quarters of a 1/256 step from the 1/256 grid, no
  ties) were packed in the object's 24-bit fields as the nearest multiple of 1/256 in all 18
  coordinates (18 x and y of t7-a, t7-b and t7-c, the frozen words of HF-round equal to the stored
  words 3 of 3 triangles) and truncation (HF-trunc) was refuted in all three (3 of 3); the frozen
  verdict: controls pass; held out consistent HF-round (3), refuted HF-trunc (3 of 3).
  *ta; HW, infer; data: `render-closing-r1-pixgeo:out/g-t7/`.*
- `E779` R1-pixgeo stage g-u2 (9 jobs: the tool's triangle at 4096x4096, one render, render_pb_pages
  P = 0xa0 to 0xb0, U = 287 by E625 and HU1): the number of partial renders (0x0658 bit 0 stretches)
  was 2 at P = 0xa0 and 1 at P = 0xa3, 0xa4, 0xa5, 0xa6, 0xa7, 0xa8, 0xa9 and 0xb0 (the controls 2
  and 1 as E625 measured passed; every job's 0x0624 read P - 0x22), while the count formula of E625,
  partial renders = 1 + floor((U + k - thr0) / (thr0 + s)) with the first threshold thr0 = P - 0x22
  and every k from 2 to 13 and s = 0x1e or 0x1f (24 frozen pairs), predicts 2 at P = 0xa3 for every
  pair and 1 only from P = 0xa4 to 0xa9 according to k: the frozen verdict is that E625's count
  formula is REFUTED at U = 287, none of the 24 (k, s) pairs fitting the 7 held-out cells' counts;
  the thresholds were raised by 0x20 in all 9 jobs, as the rule of E774 says.
  *dpm; HW, infer; data: `render-closing-r1-pixgeo:out/g-u2/`.*
- `E780` R1-pixgeo stage g-t5 (9 jobs): with both controls passing (the 0.96-pixel square t5-ctl-sq
  of S1's e3k-ctl present with 1/w 0x4479ffff, the 0.48-pixel triangle none) the TA wrote no object
  for any of the six triangles centred on the pixel corner (32, 32), the tool's triangle scaled to a
  bounding box of 0.30, 0.50, 0.60, 0.75, 0.90 and 0.98 pixels (areas 0.042, 0.117, 0.169, 0.264,
  0.380 and 0.451 pixel), nor for the elongated 0.30 x 0.98 triangle (area 0.138), so the ladder had
  no flip; the frozen verdict reads `ladder monotone (flip at extent none); elongated none: HS-ext
  consistent (the 0.98 cell is none), HS-area consistent (area 0.138; absent up to 0.451, present
  from 0.000); the elongated cell does not separate them`, but the frozen row of the 0.98 cell
  predicted an object for HS-ext (extent at least T, T in (0.48, 0.96]) and the cell wrote none, so
  HS-ext as frozen is refuted by that cell and the scorer's word consistent compares the elongated
  cell with the top cell instead of the row.
  *ta; HW, infer; data: `render-closing-r1-pixgeo:out/g-t5/`.*
- `E781` R1-pixgeo stage g-t6 (7 jobs: a vertex program with x and y scaled by w = 1e-5 or 1e-4 and
  the state block's clamp (word 14) from 3e-5 to 1.2e-3): the control t6-ctl (clamp 3e-5, S1b's
  e3k-i-c3e5) held its stored 1/w 0x47023555, and in the six held-out cells the TA wrote an object
  each time with a 1/w that was always one of the two floats next to the exact 1/clamp,
  round-toward-zero in 2 cells (clamp 6e-5: 0x46823555; 7e-4: 0x44b29249) and round-to-nearest in 3
  (1.5e-4: 0x45d05555; 6e-4: 0x44d05555; 1.2e-3: 0x44505555) of the 5 where the two differ, the
  sixth (clamp 2e-4: 0x459c4000) being a cell where they agree, so the stored 1/w under a clamp is
  within 1 ulp of 1/clamp and not a rounding rule; the stored x and y were the program's x and y
  divided by the clamp (the triangle shrunk by w over the clamp, HREP-xy') in 6 of 6 held-out cells
  within 1/64 pixel; the frozen verdict: control holds; mixed (RZ 2, RN 3 of 5): within 1 ulp, not a
  rounding rule; position HREP-xy' 6 of 6.
  *ta; HW, infer; data: `render-closing-r1-pixgeo:out/g-t6/`.*
- `E782` R2-geo stage g-t3 (4 jobs: vertex programs with z = A x + B and w = C x + D on the tool's
  triangle on a 64x64 target; the control z-cut-p at w = 1, the held-out t3-w-pos (z = 2x + 1, w =
  0.5x + 1.25, cut by z = w at x = 1/6) and t3-w-neg (z = 2x + 1, w = -0.5x + 1.25, cut at x = 0.1)
  and t3-nocut (z = 0, w = 0.5x + 1.25, no clip)): the control reproduced S1b's object, and every
  frozen row about the clip held on both cut objects (HSH 2 of 2 on the polygon of 4 vertices cut in
  (x, y, z, w) against z <= w and z >= -w, the window position 32 + 32 x / w at every vertex the
  made ones included, HZZ the strip zigzag order, HPR the prim words (16, 1, 18) and (2, 17, 19))
  and on t3-nocut (nothing crosses: 3 vertices in input order, window 32 + 32 x / w per vertex,
  depth word 0x3f000000 at all three, w differing between the vertices); the stored 1/w of the 7
  original vertices (the two kept ones of each cut object and t3-nocut's three) equalled RZ of 1/w
  exactly, 7 of 7 (0x3f70f0f0, 0x3f924924, 0x3f321642 and 0x3f1d89d8, the first two again in
  t3-nocut with 0x3f1d89d8), but the 4 clip-made vertices' 1/w words were 0x3f400001 and 0x3f400000
  (HI-w predicted 0x3f400000, RZ of 1/(4/3)) and 0x3f555554 and 0x3f555556 (predicted 0x3f555555,
  1/1.2), so HI-w held within 1 ulp in 4 of 4 and exact in 1 of 4 (the frozen exact rows refuted 2
  of 2 jobs), and HI-rhw (the ends' 1/w interpolated with the cut parameter: 0x3f48c8c8, 0x3f520d20,
  0x3f626cc2, 0x3f6a0ea0) was refuted 2 of 2 in both its forms; the depth of the made vertices was
  0x3f800000 in 3 of the 4 and 0x3f7fffff (one ulp below 1.0) at one, t3-w-neg's (34.668, 39.332),
  so HDP-made (1.0 exactly whatever w) was refuted 1 of 2 jobs.
  *ta; HW, infer; data: `render-closing-r2-geo:out/g-t3/`.*
- `E783` R2-geo stage g-t4 (8 jobs: the tool's triangle with x and y scaled by w so that the window
  position is the original (8, 8), (56, 20), (20, 56) of a 64x64 target, z the same at all three
  vertices, z within +-w so that nothing clips; 2 controls t4-ctl-z0-w3 (z = 0, w = 3: depth word
  0x3f000000, 1/w 0x3eaaaaaa as E754) and t4-ctl-zm05-w1 (z = -0.5, w = 1: 0x3e800000), and 6
  held-out (z, w) pairs): both controls passed; the object was written unclipped at the original
  position (6 of 6) and the stored 1/w was RZ of 1/w in 6 of 6 pairs (0x3eaaaaaa at w = 3,
  0x3e124924 at 7, 0x43a6aaaa at 0.003, 0x3f68ba2e at 1.1; RN refuted 5 of 5 where it differs), but
  each of the six frozen depth formulas was refuted by at least one pair (D1 0.5 + 0.5 (z RZ(1/w))
  rounded to nearest by 1 of 6, D2 0.5 + 0.5 RZ(z/w) by 1 of 6, D3 0.5 + 0.5 RN(z/w) by 5 of 6, D5
  0.5 + 0.5 RZ(z RZ(1/w)) by 4 of 6, D6 RN(RN(z + w) / (2 w)) by 6 of 6, D7 by 5 of 6); the measured
  depth word (the same at the three vertices of a job) was 0x3e19999c for (-2.1, 3), 0x3d88888c for
  (-2.6, 3), 0x3df8af8c for (-5.3, 7), 0x3d4cccd0 for (-0.0027, 0.003), 0x3dfb5874 for (-0.83, 1.1)
  and 0x3d83a840 for (-6.1, 7), each above the exact 0.5 + 0.5 z / w by 0.27 to 0.57 of 2^-24.
  *ta; HW, infer; data: `render-closing-r2-geo:out/g-t4/`.*
- `E784` R2-geo stage g-t5v (13 jobs frozen, 11 run: a vertex program on the tool's triangle that
  loops N times on a backward br with an 8-instruction body, the loop count carried into the depth
  so that every vertex's stored depth word is 0x3f200000 + N if the loop ran N times;
  CR_EVENT_STATUS2 read from the debugfs registers after each job's reset and after the job): the
  controls passed (t5v-ctl0 without a loop, t5v-n1 and t5v-n3 with loops of 1 and 3: the stored
  depth words 0x3f200000, 0x3f200001, 0x3f200003 at every vertex, so a backward br loop in a vertex
  program runs on this hardware; STATUS2 0x400 after the reset and 0x400 after the job in all
  three), and the held-out ladder N = 28, 53, 55, 110, 220, 440 and 880 ran to its end on every
  vertex (stored depth words 0x3f20001c, 0x3f200035, 0x3f200037, 0x3f20006e, 0x3f2000dc, 0x3f2001b8,
  0x3f200370) with STATUS2 0x400 before and after each; N = 1760 (0x3f2006e0 at every vertex) ran to
  its end and STATUS2 read 0x480 after it (bit 7 set; 0x400 before): bit 7 first set at N = 1760 and
  last clear at 880, so the frozen H-ITER and H-INSTR (bit 7 set from 55 iterations, as the pixel
  latch of E769, clear at 53) are refuted, H-NEVER (never set) is refuted, and H-TIME (monotone in
  the run's length) is consistent, with the point between 880 and 1760 iterations (about 7000 and
  14000 instructions a vertex) not placed; the sweep stopped at the first set bit, so N = 3520 and
  7040 were skipped.
  *edm; HW, infer; data: `render-closing-r2-geo:out/g-t5v/`.*
- `E785` R2-geo stage g-c3 (11 jobs, the tool's triangle with 1500 vertices, p1139-green, the first
  threshold thr0 = P - 0x22 set by render_pb_pages and read from the job's own 0x0624 in 11 of 11):
  the controls at 4096x4096 passed (c3-4096-0x372 raised, thr0 0x350, run peaks 0x350, 0x370, 0x23d,
  dword 38 = 0x20; c3-4096-0x374 did not, thr0 0x352, peaks 0x352 three times: E774's flip
  reproduced), and at 2048x2048 the scene's page need was 0x213 (531 pages, the calibration
  c3-2048-cal at P = 0x422 overflowed no threshold, peak status 0x213, held-out 'no overflow'), so
  the five cells with thr0 from 0x332 to 0x400 (P = 0x354, 0x372, 0x374 and 0x394, and the
  calibration) never reached a first abort (0 partial renders: void), the cell P = 0x162 (thr0
  0x140) overflowed but its second run peaked at 0xe6 below thr0 (void), and the three cells that
  read: P = 0xa2 (thr0 0x80, peaks 0x80, 0xa0, 0xa0) and P = 0xe2 (thr0 0xc0, peaks 0xc0, 0xe0,
  0xe0) raised the threshold by 0x20 (dword 38 = 0x20), P = 0x122 (thr0 0x100, peaks 0x100, 0x100,
  0x4f) did not; the frozen verdict was a flip at 2048x2048 with C in [0xe0, 0x120) and H-same (the
  limit of 4096x4096, 0x371, at this target) REFUTED, 2 of 3 cells as 0x371 predicts (the cell 0x122
  predicted a raise).
  *dpm; HW, infer; data: `render-closing-r2-geo:out/g-c3/`.*
- `E786` R2-geo stage g-c2 (9 jobs at P = 0x422, the knob that clamps the first threshold at 0x400
  and above which nothing raised in E704, with the first threshold set instead by a poke of word 11
  of the render context's parameter-buffer descriptor, `pb:11` = V, applied once to the next
  render): the two E625 controls passed on the tool's default triangle (V = 0x80 raised, V = 0x100
  did not), the poke landed in 9 of 9 (the first partial render's status and the job's own 0x0624
  read V), and at 4096x4096 with 1500 vertices the threshold was raised by 0x20 (dword 38 = 0x20,
  run peaks V, V + 0x20, ...) at V = 0x300, 0x33e and 0x351 and not at 0x352, 0x35e, 0x3a0 and
  0x3de: H-abs (the limit C = 0x371 applies to the threshold the TA runs: raise iff V + 0x20 <=
  0x371, frozen before the run from E774) held in 7 of 7 held-out cells with the flip exactly
  between 0x351 and 0x352, H-P (the limit is on the knob P = 0x373 at its value 0x422, so nothing
  raises) refuted 3 of 7 and H-rel (the limit follows P, so every poke raises) refuted 4 of 7; dword
  37 read 0x10400 in all 5 raised jobs (the unpoked clamp value, not V).
  *dpm; HW, infer; data: `render-closing-r2-geo:out/g-c2/`.*
- `E787` R2-pixel stages r2-d-safe and r2-d-fault (7 jobs, the T3 address program s1d-tw64x64-l2e2
  whose A4 reads land 80 to 83 KiB above the probe's scratch base, with the scratch at N pages and
  the probe's 3-page coords surface after it): the controls passed (d-ok-64: A4 exact; d-L2e2-19:
  the image byte-identical to S1b's; d-L2e2-19x, the variant program that stores r10 xor 1 in o0:
  S1b's image xor 1; d-L2e2-16: fault 0x90002 at 0x3e017001 as E722) and both held-out rows agreed
  with HL, the reading that the 18-page outcome and the fault are the probe's own layout (the
  sampler reads what lies past the scratch: the coords surface's words, then its sentinel page, then
  an unmapped page): d-L2e2-18x (18 pages, the variant) completed with rc 0 and read 0xdeadbeee on
  2048 of 2048 pixels, the probe's sentinel 0xdeadbeef with the variant's xor, and d-L2e2-17 (17
  pages) faulted with BIF_INT_STAT 0x90002 at 0x3e017001, the address of the 16-page fault; the
  repeat d-L2e2-18 (the unmodified program, 18 pages, S1b's rc 3 'no pixel written' and no fault)
  was reproduced; the 18-page 'no pixel written' of E760 is therefore a sentinel image: the probe
  tests the target against 0xdeadbeef and the job wrote it.
  *texture; HW, infer; data: `render-closing-r2-pixel:out/20261110-105258/r2-d-safe/`,
  `render-closing-r2-pixel:out/20261110-105258/r2-d-fault/`.*
- `E788` R2-pixel stages r2-a-safe and r2-a-fault, the TA-array question (6 jobs, mode 2,
  --tri-full, the tool's triangle with CR_TE_AA 0xe0000000 unless noted): the controls passed (a4,
  320x400 at CR_TE_AA 0x20000000 in a render context made for 544x400: TA data 0xa000 bytes, one
  array of region headers from 0x4000, nothing below 0x4000 or from 0x5800, and the image of E727's
  region model, 28 of 128000 pixels wrong with the first at (304, 128), the control value frozen
  from the model; a6, 320x400 at 0xe0000000 in a context made for 320x400, held: BIF_INT_STAT
  0x90004 at page 0x20008), the TA data of the two completing sizes held four arrays and nothing in
  a fifth (a1, 256x160, own context: 0 of 40960 wrong, non-zero dwords in the slots of 0x600 bytes
  from 0x4000: 256, 160, 256, 160, 0, 0; a2, 320x128: 0 of 40960 wrong, 256, 256, 160, 160, 0, 0;
  nothing below 0x4000; the replicate a3 of a1 had a1's TA data sha256, eaa6c96c0b8d7739), so f = 4
  for what the TA writes, and the held-out sufficiency job a5 (320x400 at 0xe0000000 in the context
  made for 544x400, whose TA data is 0xa000 bytes = 0x4000 + 4 x 0x1800 and has no room for a fifth
  array at the 0x1800 spacing) completed with 0 of 128000 pixels wrong and four arrays written
  (non-zero dwords per array 1024, 800, 640 and 584), where a context made for 320x400 alone faulted
  (a6): four arrays suffice at 320x400; H4 (f = 4) held on the three frozen rows it predicted (slot
  4 zero in a1 and a2, a5 completes in 0xa000) and H5 (a fifth array written or needed) was not
  supported by any.
  *ta; HW, infer; data: `render-closing-r2-pixel:out/20261110-105258/r2-a-safe/`,
  `render-closing-r2-pixel:out/20261110-105258/r2-a-fault/`.*
- `E789` R2-pixel stage r2-a-fault, job a6-320x400-max320 (a 4x job, mode 2, CR_TE_AA 0xe0000000,
  320x400 in a render context made for 320x400, held with hold_recovery so that the registers are
  read before the kernel's reset; the control of the stage's sufficiency job a5, E788): the job
  faulted (rc 1, class fault) and the held registers read CR_BIF_INT_STAT 0x00090004 and
  CR_BIF_FAULT 0x20008061 (the faulting page 0x20008, the address the frozen model gave for a TA
  write past the layout), CR_EVENT_STATUS 0x20000000 and CR_EVENT_STATUS2 0x480; the frozen E1 row
  for the TA write (the TA's write of the region headers, E763) was HE, the fault raises no status
  bit of its own (extra bits: none; HF, some, refuted): STATUS2 0x480 is the 0x400 of the idle
  register plus bit 7, the bit a TA job that faults sets (E317, E764), as for the TA's read fault.
  *bif; HW; data: `render-closing-r2-pixel:out/20261110-105258/r2-a-fault/`.*
- `E790` R2-geo stages g-c3 and g-c2 (E785, E786), the frozen side table of dword 36 of the TA/3D
  control block against the page count of CR_DPM_GLOBAL_PAGE_STATUS (0x072c, low half) in the sample
  before the first abort (prediction: max(count - 2, 0)), never gating: of the 15 jobs with a first
  abort the register reading held in 8, unraised jobs 5 of 8 (g-c3 2 of 3, g-c2 3 of 5) and raised
  jobs 3 of 7 (1 of 3 and 2 of 4; the raised jobs of the two stages were held out), the misses being
  c3-4096-0x372 (count 3, dword 36 3), c3-2048-0x122 (4, 3), c3-2048-0xa2 (2, 2: predicted 0, read
  2), k-1500-0x33e (3, 3), k-1500-0x351 (3, 3), k-1500-0x3a0 (4, 3) and k-1500-0x3de (4, 3); read
  after the run [infer, a check of E775's post hoc reading, not frozen], the maximum of the 0x072c
  count over the job less 2 equalled dword 36 in 13 of these 15 jobs and failed in two raised ones,
  c3-2048-0xe2 (peak 4, dword 36 1) and k-1500-0x300 (peak 4, dword 36 1), and in the 5 jobs of g-c3
  that never overflowed (peak count 7, dword 36 0) it does not apply.
  *dpm; HW, infer; data: `render-closing-r2-geo:out/g-c3/`, `render-closing-r2-geo:out/g-c2/`.*
- `E791` R3-events stage a (Q152 rows A0 to A6, 19 jobs: a writer of ours, one entry of alias.s, 208
  instructions, wrote sa63, sa64 or sa65 (or none of them) and then called the closed general task,
  and our reader ran at the next event): the tick was kept in 19 of 19 jobs and no job stopped it
  (HostCtl dword 12 and USE0_SERV_EVENT advancing in every check after the reader, 912 to 1035 Hz);
  the controls held (A0 x2: the reader's pclink 0x98, p1 1, sa64 2, sa65 0x02000000, sa63 0); H-63
  (sa63 stops the tick) is refuted by A1, a marker written to sa63 and left there, kept in 3 of 3
  jobs and still read back 1200 ms later in 3 of 3, and H-P11 (p0 = p1 = 1 at the tail call with
  r20, r21, i0 and i1 written) is refuted by A6, kept in 2 of 2; A2 (sa65 written with its own entry
  value), A3 (sa65 written with a marker and restored before the tail call, 3 of 3 restored) and A4
  and A5 (sa64 written, E792) kept the tick 3 of 3 each; the frozen scorer printed fit 12 held and 0
  FAILED, held out 21 held, 4 FAILED and 1 cannot tell, replicate 40 held, 7 FAILED and 2 cannot
  tell, the FAILED rows being the kept-or-not rows of the two refuted hypotheses (H-63 in A1 x3,
  H-P11 in A6 x2) and the p1 rows of A2 and A5 (E792); the sa65 value E537's writer left
  (0xb009c5dc, with bits no event raised) was not written by any row, so the cause of E537's stop is
  not among these single writes, and no row reproduced that stop.
  *edm; HW, infer; data: `edm-closing-r3-events:out/a/`.*
- `E792` In the 17 R3-events stage a jobs that ran a writer (A1 to A6, 3, 3, 3, 3, 3 and 2 jobs; the
  two A0 jobs had none) the entry registers our reader stored at the next event after the closed
  task had run were: pclink 0x98 in 14 jobs and 6 in the 3 A4 jobs, the only writer that wrote sa64
  with bit 1 (the tick bit of pa0) clear (sa64 = pa0 & ~2, which the writer read back as 0 in the
  same pass), against 0x98 after A5's sa64 = pa0 (3 of 3, the tick bit set), A2's sa65 write, A3's,
  A1's sa63 write and A6's, as the frozen H-ALIAS predicted for A4, A2 and A5 (pclink held in 9 of 9
  of those jobs); p0 read 1 in all 19 jobs, whether the writer left it 0 (A1 to A5), 1 (A6) or the
  previous pass left 0 (A0); p1 read 0 in the 15 jobs of A1 to A5, whose writer set it 0 before its
  tail call, and 1 in A6 (p0 = p1 = 1 at the tail call) and in the two A0 jobs, so in this stage p1
  at the next entry is the value our task's tail left in 19 of 19 jobs (frozen rows for A2 and A5
  said 1 and failed, 6 of 6 jobs: the prediction took the reader's own p1 of A0, not the writer's
  setp, a design error found after the run, E791 and below); the A4 rows' dword 12 difference to the
  pass count, frozen as passes - 1, was cannot tell (the bracketed intervals (-9, 6), (-8, 5), (-7,
  6) contain -1 and 0).
  *edm; HW, infer; data: `edm-closing-r3-events:out/a/`.*
- `E793` R3-events stage b (Q152 rows B0 and B1; ring_skip.s, a firmware task of ours that logs
  every pass of its four PDS #13 slots in a ring and, in window 2, ends one plain tick pass with
  nop.end after an idf and a wdf, writing no sa, no r, no i and no p and not calling the closed
  general task, when the host has set SKIP to 1): the control B0 held in 3 of 3 jobs (14 entries
  each on the 25000-unit grid, SKIPPED 0, no drop); in B1 the pass was skipped as designed (SKIPPED
  1 in the task's own counter, the skipped pass logged with flag 3) and the tick stopped in 2 of 2
  jobs, b1 and b1-r2, with no entry after the skipped one (HostCtl dword 12 frozen at 2216 and at
  822 over three reads, USE0_SERV_EVENT at 0x8ad and 0x33b with its bit 16 (empty) clear and its
  count not moving): H-FREE (the hardware dispatches the next event after any task end) is refuted,
  2 of 2; the stop signature read twice (38 and 44 ms apart) before each reset was the busy one of
  E537, CR_CLKGATESTATUS 0x000ccfa0 (idle 0x20), CR_EVENT_STATUS 0x20000000 and EVENT_TIMER
  counting, in both jobs (the scorer: signature busy, matches E537), so E537's signature is what a
  stop looks like when the closed task never ran; the stage ended by design at its second stop (exit
  8, both resets and gates exact) and b1-r3, b2 and b2-r2 did not run (recorded void by the scorer,
  status NODATA), so a skip of five ticks (B2) was not measured; the frozen scorer printed B0 held,
  B1 reads H-STOP, held out 1 held and 1 FAILED (H-FREE's 'kept') with 6 void, replicate 7 held, 1
  FAILED and 11 void, control 3 held.
  *edm; HW, infer; data: `edm-closing-r3-events:out/b/`.*
- `E794` R3-events stage k7 (Q290 K7; a 90-tick hold of the EDM by ring_hold, S2b's blob byte for
  byte, n = 1508279, hold 2262434 units, window 2, 160 ms open): with no kick the exit was followed
  by a burst of 4 entries (k7-ctl: 16 entries, 0 kick entries, the ticks after the hold K 2,
  ccbctl[0] 2 to 2; S2b's ctl90, fit 3 of 3 rows), with one GETMISCINFO kick 3 ms into the hold the
  burst was 5 with one kick entry (K 2), the ticks after it K 3 and ccbctl[0] 3 (k7-one; S2b's
  kick90 and E746's identity, fit 4 of 4 rows), and with two real kicks inside the hold, the debugfs
  xfer_sync's TRANSFER and, 50 ms later, its PROCESS_QUEUES, both answered (read ok), the ring held
  two kick entries in 3 of 3 jobs (k7, k7-r2, k7-r3), K 2 and 3 in that order, all inside the burst
  after the hold, the ticks after them K 4 and ccbctl[0] 4 (burst 6, 5 and 6 entries): H-EACH (each
  kick is delivered as its own entry) held in every row of the three jobs (5 held-out rows and 10
  replicate rows) and H-MERGE (one entry and a read that times out) is refuted, 3 of 3, its 2
  held-out and 4 replicate rows being the FAILED rows the scorer printed; the hold band (the
  kernel's hold length, the knob of S2 run 3) held in 5 of 5 jobs (2262433 to 2262436 units against
  2262434); each ring held 16 entries and dropped 51 to 54 (k7-ctl 51, k7-one 52, k7 53, k7-r2 51,
  k7-r3 54), all of them ticks after the burst, which the 16 rungs of slot 0 could not hold, so the
  drops are harmless to every row (no drop inside the burst: late ticks were read in all five jobs).
  *edm; HW, infer; data: `edm-closing-r3-events:out/k7/`.*
- `E795` R3-geo stage g-da (27 jobs: the tool's triangle on a 64x64 target with x and y scaled by w,
  z and w the same at the three vertices, z / w in (-1, -0.5] so that the sum 0.5 + 0.5 q is exact;
  6 controls and 21 held-out cells placed by the fraction of |z RZ(1/w)| in its float32 ulp): the 6
  controls passed (E783's controls 0x3f000000 and 0x3e800000, the repeats of t4-m2p6-3 0x3d88888c
  and t4-m6p1-7 0x3d83a840, and w = 2 and 0.5 0x3e333340 and 0x3e1999a0), the object was written
  unclipped at the original position in 21 of 21 held-out cells, H-thr (the post hoc fit of E783's
  and Q230's notes: the product rounded away from zero iff its fraction exceeds one t in (0.3655,
  0.4667)) was REFUTED with 5 of the 11 outside cells off its frozen direction (da-lo1 at fraction
  0.0400 and da-mid2 at 0.3300 went up where it says down; da-mid3 at 0.3479, da-up1 at 0.5334 and
  da-up2 at 0.5916 stored a word that is neither neighbour of the product), and each of the six
  frozen depth formulas was refuted (misses of 21: D1 16, D2 10, D5 16, T26 8, T27 8, K23 19); the
  ten inside cells went down at fractions 0.3710, 0.3800 and 0.3989, neither neighbour at 0.4037 and
  up from 0.4112 to 0.4610; read after the run (no frozen row), the stored 1/w was RZ of 1/w in the
  6 controls and 16 of the 21 held-out cells and one ulp above it in the 5 at w = 9 and 0.7.
  *ta; HW, infer; data: `render-closing-r3-geo:out/g-da/`.*
- `E796` R3-geo stage g-db (16 held-out jobs, the triangle and template of g-da, whose controls it
  takes): six cells with z > 0 (z / w from 0.508 to 0.973), six with |z / w| in (0.25, 0.5) (three
  positive, three negative) and four with z = -0.750953436 at w next to 1 (1 + 2^-23, 1 - 2^-23, 1.5
  and 1.0000004); all 16 objects were unclipped at the original position; on the z > 0 cells every
  frozen product rule combined with every rounding of the sum was refuted (21 labels, 2 to 4 misses
  of 6 each), on the q cells every label (15 with the product at float32 precision, 1 to 4 misses of
  6; 4 with the product kept on the sum's 2^-23 grid, 4 or 5 misses), and on the four cells next to
  w = 1 D1 (the product z RZ(1/w) rounded to nearest) was consistent 4 of 4 while D2 missed 2, D5 1
  and T26, T27, K23, T26d and T27d 3 each; read after the run (no frozen row), the stored 1/w was
  one ulp above RZ of 1/w at w = 9 (db-pos1, db-q3) and RZ of 1/w in the other 14 jobs.
  *ta; HW, infer; data: `render-closing-r3-geo:out/g-db/`.*
- `E797` R3-geo stage g-dc (10 jobs: the viewport z words of the state block written by --blk 10 and
  --blk 11 on the triangle of g-da; 1 control and 9 held out): the control (blk 10 = blk 11 = 0.5
  written explicitly, z = -0.5, w = 1) stored 0x3e800000 as measured before; VS (blk 10 the scale
  and blk 11 the offset) was refuted 9 of 9, and at w = 1 the words were 0x3dc00000 for blk 10 =
  0.25, blk 11 = 0.5, z = -0.3125 and 0x3ed80000 for 0.5, 0.25 at the same z (blk 10 + blk 11 z, as
  VF, VT and VZ give), and 0x3eb3a2f3 for blk 10 = 0.6, blk 11 = 0.3, z = -0.830491483, which only
  VF gives (offset + scale z rounded once; VT, the product rounded first, gives 0x3eb3a2f2
  [arithmetic]); at w = 3 with blk 10 = 0.6, blk 11 = 0.3 and z / w from -0.995 to -0.827 the six
  words were 0x3ea8587b (VZ only), 0x3eb42c3e (VT, VZ) and four that VF, VT and VZ all give, so VF
  (2 of 9), VT (2 of 9) and VZ (1 of 9) were refuted; the objects were unclipped in 9 of 9.
  *ta; HW, infer; data: `render-closing-r3-geo:out/g-dc/`.*
- `E798` R3-geo stage g-dd (4 held-out jobs: the tool's triangle on a 64x64 target with z = A x + B
  and w = C x + D, one vertex beyond a plane; dd-p1 and dd-p2 cut by z = w with made w 11/7 and
  13/9, dd-m1 and dd-m2 cut by z = -w with made w 1.05 and 47/28): the structure (4 vertices, the
  vertex set, the stored order and the prim words) held in 4 of 4 jobs, and HSH (the
  Sutherland-Hodgman polygon in (x, y, z, w) against z <= w and z >= -w), its window rule (32 + 32 x
  / w, made vertices at the cut), HZZ (the strip zigzag order), HPR (index | 16 for a boundary edge:
  (16, 1, 18), (2, 17, 19)) and HDP-made (depth exactly 1.0 at a made vertex on z = w and 0.0 on z =
  -w, whatever w) were consistent in 4 of 4; HI-w (the made vertex's 1/w = RZ of 1/w_made) was
  refuted as an exact word (4 of 4) and within 1 ulp (3 of 4): the made 1/w words were 0x3f22e8bb
  and 0x3f22e8bc (dd-p1), 0x3f313b15 and 0x3f313b14 (dd-p2), 0x3f73cf3f twice (dd-m1) and 0x3f1882ba
  twice (dd-m2); read after the run (no frozen row), the kept vertices' 1/w was RZ of 1/w at w =
  1.3125, 1.0625 and 1.625 and one ulp above it at w = 1.40625, 1.59375 (twice) and 1.6875.
  *ta; HW, infer; data: `render-closing-r3-geo:out/g-dd/`.*
- `E799` R3-geo stage g-c4 (10 jobs, the tool's triangle with 1500 vertices, p1139-green, the first
  threshold thr0 = P - 0x22 set by render_pb_pages and read from the job's own 0x0624): the four
  controls passed (4096x4096: P 0x372 raised, 0x374 not; 2048x2048: P 0xe2 raised, 0x122 not; E785's
  cells repeated), and at 2048x2048 the six bisect cells the runner picked from the kept
  observations (P 0x102, 0x112, 0x10a, 0x106, 0x104 and 0x105, thr0 0xe0, 0xf0, 0xe8, 0xe4, 0xe2 and
  0xe3) raised the threshold by 0x20 at thr0 0xe0 and 0xe2 and not at 0xe3, 0xe4, 0xe8 and 0xf0,
  every cell's second run reaching thr0: one exact flip, last raise at thr0 0xe2 (C = 0x102), first
  silent 0xe3; LT, frozen before the run (last raise at thr0 floor(0x351 R / 32768) = 0xd4 at this
  target), REFUTED.
  *dpm; HW; data: `render-closing-r3-geo:out/g-c4/`.*
- `E800` R3-geo stage g-c6 (5 jobs, the tool's triangle with 1500 vertices at a 2048x2048 target in
  a render context made for up to 4096x4096, --max-width 4096 --max-height 4096): the calibration at
  P 0x422 (thr0 0x400) never overflowed (0 partial renders, peak 0x213, the page need of the plain
  2048x2048 context in E785), the cell at g-c4's last raise (P 0x104, thr0 0xe2) raised the
  threshold (peaks 0xe2, 0x102, 0x9b), the cell at g-c4's first silent (P 0x105, thr0 0xe3) did not
  (0xe3 three times) and neither did thr0 0x100 (P 0x122; 0x100, 0x100, 0x4f), and the cell at thr0
  0x120 was skipped by the runner (twice its thr0, 576, not below the page need 531); H-target (the
  flip of g-c4) HOLDS, 3 of 3 cells, and H-context (the 4096x4096 limit, a raise at every valid
  cell) is REFUTED.
  *dpm; HW; data: `render-closing-r3-geo:out/g-c6/`.*
- `E801` R3-geo stage g-c5 (36 jobs, the tool's triangle with 1500 vertices at three more targets,
  12 a target: a calibration at P 0x422, 5 fixed cells and 6 bisect cells the runner picked from
  kept output; 33 run, 3 skipped as the bracket had closed): at each target one exact flip, the last
  raise at thr0 0x1b2 and the first silent at 0x1b3 at 4096x2048, 0x1b6 and 0x1b7 at 2048x4096,
  0x1e8 and 0x1e9 at 3072x3072 (C = thr0 + 0x20: 0x1d2, 0x1d6 and 0x208 [arithmetic]); the two
  targets of equal region count, 4096x2048 and 2048x4096, have different limits, so every frozen law
  in the target's size was REFUTED at every target: LT (C proportional to the region count from
  0x351 at 4096x4096; it predicted 0x1a8, 0x1a8 and 0x1dd), and the affine laws through g-c4's
  measured 2048x2048 point and 4096x4096 in the region count (0x1b1, 0x1b1, 0x1e5), in the
  tail-pointer side squared (0xe2, 0x351, 0x351) and in the macrotile area (0x1b1, 0x1b1, 0x1e5);
  the three calibrations were void for the raise (page need read 0x3f7, 0x400 and 0x400).
  *dpm; HW; data: `render-closing-r3-geo:out/g-c5/`.*
- `E802` R3-geo stage g-c7 (11 jobs, --tri-full --vertices 1500 at 2048x2048, a scene whose triangle
  covers the target, run last behind a calibration gate): the calibration at P 0x422 (thr0 0x400)
  made 3 partial renders (peaks 0x400 three times, the gate allowed at most 3) and the scorer read
  its page need as 0x400; the six cells at and around g-c4's flip all raised the threshold by 0x20,
  thr0 0xd2 (P 0xf4, 67 partial renders), 0xde (0x100, 63), 0xe2 (0x104, 13), 0xe3 (0x105, 13), 0xe7
  (0x109, 13) and 0xf3 (0x115, 13), each second run peaking at thr0 + 0x20, so the four bisect cells
  were skipped (no silent cell above the last raise): no flip among the valid cells, the last raise
  above them (C at least 0x113 [arithmetic]), and g-c4's last raise 0xe2 outside that interval, the
  frozen verdict H-scene (the limit differs with the scene); every job ended in class ok with health
  ok after the stage.
  *dpm; HW; data: `render-closing-r3-geo:out/g-c7/`.*
- `E803` R3-geo, H-last (dword 36 of the TA/3D control block = the low-half count of
  CR_DPM_GLOBAL_PAGE_STATUS, 0x072c, in the sample before the LAST abort, less 2, floor 0; a reading
  chosen after R1's and R2's data, frozen before this run as held out): in g-d36, the stage that
  gates on it (6 jobs at 2048x2048 thr0 0x60, 0x70, 0x90 and 0xb0 and 4096x4096 thr0 0x2c0 and
  0x300, three to six aborts each), H-last HOLDS, 6 of 6 jobs and all 3 jobs that separate it from
  the peak and second-abort readings (d36-2048-0x90, d36-4096-0x2c0 and d36-4096-0x300: counts 2, 4,
  3 or 3, 4, 3, dword 36 1); in the never-gating side tables of the other DPM stages it fitted g-c4
  10 of 10 (1 separating, c3-2048-0xe2), g-c5 33 of 33 (none separating), g-c6 4 of 4 (none) and
  g-c7 7 of 7 (1 separating, c7-cal: counts 3, 3, 4, dword 36 2): 60 of 60 jobs, 5 of 5 separating;
  in no job did the count change between the two samples before the last abort.
  *dpm; HW; data: `render-closing-r3-geo:out/g-d36/`, `render-closing-r3-geo:out/g-c4/`,
  `render-closing-r3-geo:out/g-c5/`, `render-closing-r3-geo:out/g-c6/`,
  `render-closing-r3-geo:out/g-c7/`.*
- `E804` R3-pixel stage q-f0 (10 fill jobs of 2048 pixels, all controls: loops closed by a relative
  `p0 br` back to the body with a MARK proof, o0 = 0xC0DE0000 | N written only where the counter
  reached zero, and E431's absolute `ba` loop, which ends with o0 = 0): the relative loop ran to its
  end on 2048 of 2048 pixels in all 6 of its rows (N = 16, 53, 53, 56, 56 and 136), so a backward
  relative branch loops in a pixel task as in a vertex task (E784), and the `ba` loop wrote o0 = 0
  on 2048 of 2048 in its 4 rows; CR_EVENT_STATUS2 read 0x400 after every reset and, after the job,
  0x400 at N = 16 and 53 and 0x440 at 56 and 136 with either branch (2 of 2 each at 53 and 56), as
  E431; the burst was 200 us at N = 16 and 1284 us at 136 (frozen 205 +- 125 and 1287 +- 125 from
  E431's fit) and bit 6 showed 211 us after the burst began at 136 (frozen 120 to 340); the frozen
  scorer opened the loop gate with 0 misses of 13 frozen quantities.
  *edm; HW; data: `render-closing-r3-pixel:out/20261110-160415/q-f0/`.*
- `E805` R3-pixel stages q-f1a and q-f1b (54 fill jobs each, one table run in two opposite orders;
  relative loops with the MARK proof of E804 over six bodies, each with a counter update and the
  branch: b16 with 14 multiply-adds, b12 with 10, b4 with 2, b2 with none, b8n with six `or`, ld8
  with a load, a wait and 4 multiply-adds; the two shortest points of each ladder FIT, the other 42
  HELD OUT): every loop proof held and STATUS2 read 0x400 before every job (108 of 108); bit 6 set
  from b16 N = 25 (clear at 24 in both orders, at 25 in q-f1a only: an edge), from b12 35 (clear at
  34), from b4 130 (clear at 80), at every point of b2 (500 to 16000) and of b8n (60 to 3840) and at
  no point of ld8 (20 to 320, bursts up to 13.4 ms), the two orders agreeing everywhere else; H-MA
  (bit 6 when an instance's multiply-adds reach M* in (318, 336]) is REFUTED by all six ladders,
  H-WD (when a tile's time (B - 60.2) / 4 reaches 121.8 us, N* from each ladder's FIT points) and
  H-BURST (when the burst reaches 536 +- 20 us) are REFUTED by ld8 alone, and H-WD-busy (H-WD
  counting only time without a load) is open, ld8 having no set point; in the 48 jobs set at N >=
  1.3 N* bit 6 showed 120 to 340 us after the burst began (H-EARLY 48 of 48, H-END 0); read after
  the run (no frozen row), in the 106 fill jobs of q-f0, q-f1a and q-f1b without a load every job
  with bit 6 set had a burst of at least 535.9 us and every clear one at most 539.3 us.
  *edm; HW, infer; data: `render-closing-r3-pixel:out/20261110-160415/q-f1a/`,
  `render-closing-r3-pixel:out/20261110-160415/q-f1b/`,
  `render-closing-r3-pixel:out/20261110-160415/q-f0/`.*
- `E806` R3-pixel stage q-t (93 jobs: triangles that cover the whole target, `probe --tri pixel
  --tri-full`, at 8x8, 16x16, 32x16, 32x32, 64x32, 128x128 and 256x256, the pixel program in the
  --tri slot at code index 0x20 closed by a relative br with E804's MARK proof; 7 stock green
  controls, 7 loops at N = 1 and the 64x32 bridge at N = 53 and 56 as controls, the ladders N = 4 to
  3520 and three 4x4 rows HELD OUT, three exploratory rows on the default 64x64 triangle): all 90
  full-target jobs wrote their value on every pixel of the target (green or the MARK of their N, W x
  H of W x H) and STATUS2 read 0x400 after every reset, so the relative loop runs to its end in a
  placed --tri slot; the bridge FAILED (the 64x32 triangle was clear at 53 and at 56, where E804's
  fill of the same 2048 pixels set), so the frozen cells were scaled by 110 / 56; bit 6 first set at
  N = 56 at 32x16, 32x32 and 128x128 (clear at 53) and at 110 at 8x8, 16x16, 64x32 and 256x256
  (clear at 56), at 220 at 4x4 (clear at 56), every ladder monotone; the frozen first-set points of
  a per-instance threshold (which carries H-MA), a per-tile one (32x16 tiles, which carries H-WD)
  and a per-job one were REFUTED at 4, 6 and 6 of the 8 sizes; in 28 of the 32 jobs set at N >= 1.3
  times their size's first set point bit 6 showed 120 to 340 us after the burst began; on the
  default triangle (1062 covered pixels) the loop wrote its MARK on the 1062 and bit 6 stayed clear
  at 53, 56 and 110.
  *edm; HW, infer; data: `render-closing-r3-pixel:out/20261110-160415/q-t/`.*
- `E807` R3-pixel stage q-v (88 jobs frozen, 74 run and 14 skipped by the frozen sweep stops: a
  vertex program on the tool's triangle that loops N times on a relative br, every vertex's stored
  depth word 0x3f200000 + N the loop proof, as E784): the five controls passed (no loop, N = 1 and N
  = 3 with STATUS2 0x400 after the job; N = 880 clear and 1760 set, E784's points), every run job's
  depth word proved the loop on every decoded vertex and STATUS2 read 0x400 after every reset; with
  E784's eight-instruction body on 3 vertices bit 7 was clear at N = 1045 and set at 1100 in both
  orders (ladders of 935 to 1705 in steps of 55, up and down, monotone), so the frozen bracket of
  width 55 is (1045, 1100]; with a 16-instruction body it was clear at 601 and set at 649, with a
  4-instruction body set at 1760, the lowest point of its ladder (5 more run, 9 skipped), with 12
  vertices clear at 554 and set at 698 and with 48 vertices (15 decoded) clear at 329 and set at
  538; HV-INSTR (a fixed count of instructions a vertex) was REFUTED for the 16-instruction body and
  for 12 and 48 vertices and its window contradicted for the 4-instruction body (bit 7 already set
  at 1760), HV-MA (a count of multiply-adds a vertex) REFUTED for all four, and HV-JOB (a count a
  job) REFUTED for 12 and 48 vertices; bit 7 showed 184 to 195 us after the burst began in every set
  job [corrected 2026-11-11, see Correction].
  *edm; HW; data: `render-closing-r3-pixel:out/20261110-160415/q-v/`.*
- `E808` R3-pixel stage p-c3 (75 jobs: the frozen rerun of R1's p-c2 for Q276 with controls scoped
  to their group, 18 controls, 28 CONFIRM rows read post hoc in round 2, 28 HELD OUT rows never run
  before, 1 replicate; the pixel words of an x job and a y job decode to their source pixel, the
  direct reads write one global register to o0): the controls passed (G-o4 on c-e709 and c-o4-u,
  G-o1 with tag-2 fractions 0.988 and 0.988, the register-form c-g23r4, and the premises of the
  direct reads 1.000 of 1062, 0.995 of 4096 and 0.996 of 16384 pixels) but for the swapped-order o4
  control c-o4s-u, which read tag 5 in 42 and 39 words and tag 5' in none although 5' was the later
  write, so its three rows (c-o4s-k0, k3, k7) are cannot tell; the model M held in all 29 rows
  scored: g25 = (x & 1) | (y & 1) << 1 (the transpose refuted in every row that tests it), g23 = x
  mod 32 with the high half 0 (x, y << 16 | x and x mod 64 refuted; the exact-column test g23 == 20
  true at x = 20 and 52 only, g23 == 40 never), g24 = y mod 16 (E086's fill reading; y refuted), at
  the default 64x64 triangle and the full 64x64 and 128x128 triangles (direct reads 1.000 of 1062,
  4096 and 16384 written pixels), and in the original order every o4 word was tag 5 under k = 0, 3
  and 7 (G, the o4 write gated like o1, refuted 2 of 2); the frozen verdict is Q276 NOT ANSWERED (3
  rows cannot tell).
  *pds; HW; data: `render-closing-r3-pixel:out/20261110-160415/p-c3/`.*
- `E809` R3x-c3 stage c3 (13 jobs of start.s, a task of ours; S0 a reader alone, then 12 jobs in
  which a writer set sa63, r20, r21, i0 and i1 to random markers and p0 to p3 to the job's flags
  0011, 0100 or 1010, armed a reader for the next event and called the closed task, then a
  perturbation: N 1200 ms, F a client fill, L a firmware reload, R a debugfs reset and a reload,
  three jobs each): the tick was kept in 13 of 13 jobs; the reader at the next entry read all five
  markers in 12 of 12 writer jobs, pclink 0x98, p0 1 and p1 as the writer left it in 12 of 12, and
  p2 and p3 as the writer left them in 12 of 12 (1 1, 0 0 and 1 0), so in the 8 jobs where a flag
  was 0 H-KEEP (p2, p3 as left) held 8 of 8 and H-SET (p2 = p3 = 1 at the next entry) is REFUTED, 8
  of 8; after 1200 ms (N) the five markers and p2 p3 were still as written in 3 of 3 jobs, with p0
  p1 1 1 and pclink 0x98.
  *edm; HW; data: `edm-closing-r3x-c3:out/c3/`.*
- `E810` In R3x-c3 stage c3 (E809's jobs), after a client fill (F, 3 jobs) i0, i1 and sa63 kept the
  writer's markers in 3 of 3, r20 read 0 and r21 0x1000, 0x2000 and 0x3000; after a firmware reload
  (L, 3 jobs) and after a debugfs reset and a reload (R, 3 jobs) i0, i1 and r21 kept the markers and
  r20 and sa63 read 0 in 6 of 6; sa65 read 0x02000000 after every reload and reset and stepped by
  0x02000000 with each fill (0x04000000 to 0x08000000); sa100 0x3cc00010, sa127 0x3f800000, sa20 0
  and sa24 0 in every reading of the stage; after F, L and R alike p0 p1 read 1 1 and pclink 0x98,
  and p2 p3 read 0 1 where the writer had left 1 1 and 0 0 where it had left 0 0 or 1 0 (9 of 9); so
  the frozen H-KEEP (i and sa63 survive a reload or a reset, r20 and r21 do not) and H-ALL (r20 and
  r21 survive too) are both REFUTED, H-KEEP by sa63 (0 in 6 of 6) and H-ALL by sa63 and r20, E536's
  frozen p2 p3 readings held in 1 of 3 fills (0 1) and 4 of 6 reloads and resets (0 0); the start
  state S0, read after the stage's own arm and before any writer, was pclink 0x98, p0 to p3 1 1 0 0,
  r20 0, r21 0x2000, i0 0xcd7aa809, i1 0xff326b8c, sa63 0, sa64 2, sa65 0x02000000; the frozen
  scorer printed 'r20/r21 survived 3/3' for L and for R, a scorer bug (it counted a pair of values,
  always true, not the row), and two hypothesis lines that score the r20/r21 row alone, both
  corrected by a disclosed post-run fix.
  *edm; HW, infer; data: `edm-closing-r3x-c3:out/c3/`.*
- `E811` R3x-events stage h (6 jobs of ring_hold.blob, S2b's task byte for byte, a reset and an arm
  before each: H0 x3, no hold, the register signature at 20 and 60 ms after the window opened; H1
  x3, the signature at 20 and 60 ms inside a hold of one pass of 2262434 timer units, about 90.5
  ms): H0 read the idle signature in 3 of 3 (CR_CLKGATESTATUS 0x20, USE0_SERV_EVENT with bit 16 set
  and its count moving), and the hold of H1 was in its band (2262433, 2262434, 2262433 units);
  inside the hold all four samples of each H1 job read the busy signature of E537 and E793's stops
  (CR_CLKGATESTATUS 0x000ccfa0, USE0_SERV_EVENT 0x3ed, 0x3ea and 0x415 with bit 16 clear and its
  count frozen, EVENT_TIMER moving, CCB offsets 2 and 2, HostCtl dword 14 0), all elements as a
  running task in 3 of 3 jobs, so H-REARM (a stop that differs from a running task in some element)
  is REFUTED, 3 of 3; the control 'D0 one modal value' FAILED in 3 of 3 (no valid D0 read: in every
  triple the page's pass count moved between its two reads), so D in the hold could not be read and
  the frozen verdict for H-NOTENDED (the stopped pass never ended) is cannot tell.
  *edm; HW, infer; data: `edm-closing-r3x-events:out/h/`.*
- `E812` R3x-events stage c (13 jobs of alias2.s, one entry: C0 x2 the reader alone; C1 to C4 a
  writer leaving one sa65 word in place before calling the closed task, C1 x3 count byte K = 2 in
  bits 31:24 with bit 23, C2 x2 0xb0000000, C3 x2 K with bits 2, 3, 6, 14, 15 and 16, C4 x2 K with
  bit 19; C5 x2 sa64 = pa0 & ~2 written on 50 consecutive passes): the tick was kept in 13 of 13
  jobs; C0 read pclink 0x98, p1 1, sa64 2, sa65 0x02000000 and sa63 0 as E791's A0 (2 of 2); after
  each C1 to C4 writer the next entry read pclink 0x98 and sa65 0x02000000 (K << 24), the CCB write
  and read offsets 2 and 2 and HostCtl dword 14 0 (9 of 9); after C5's 50 passes pclink read 6 and
  HostCtl dword 12 less the passes counted was in (-57, -43) and (-58, -43) against the frozen -50
  +- 8 (2 of 2: dword 12 did not advance on those passes); the frozen scorer: held out 17 held, 0
  FAILED, 1 cannot tell (C5's D row, D0 never measured, E811).
  *edm; HW; data: `edm-closing-r3x-events:out/c/`.*
- `E813` R3x-events stage e (7 jobs of ring_end.s, which logs every pass of its four PDS #13 slots
  in a ring and acts on the passes of one kind in window 2: E0 x2 no act; X1 x2 one plain tick pass
  handed by a second continue patch, cont2, to the closed task of slot 2 at 0xace instead of the
  general task; X20 x2 twenty such passes; B3 x1, last, a kick pass made by one miscinfo and ended
  with our own idf, wdf, nop.end without the closed task): E0 held (13 and 14 entries on the
  25000-unit grid, nothing acted); X1 kept the tick in 2 of 2 jobs, the acted pass logged with its
  flag and the next entry 24995 units after it in both (frozen 25000 +- 50), the CCB offsets 2 and 2
  and HostCtl dword 14 0; X20 kept it in 2 of 2 with 20 of 20 passes acted (the ring of 16 rungs
  dropped 8 and 7 entries) and dword 12 less the passes in (-27, -14) and (-27, -13) against the
  frozen -20 +- 8; B3 stopped the tick: one kick entry with flag 3 and nothing after it, the
  miscinfo not answered, the CCB write offset 3 and read offset 2 (read = write - 1), dword 14 0,
  the busy signature of E537 (CR_CLKGATESTATUS 0x000ccfa0, USE0_SERV_EVENT 0x1365 frozen,
  EVENT_TIMER moving); so H-EXIT (any closed path that reaches the shared exit keeps the tick, a
  pass ended without it stops it) is supported, H-BODY (the general task's own path is needed: X1
  stops) is REFUTED, 2 of 2, and H-TICKONLY (only tick passes need the closed task: B3 keeps the
  tick) is REFUTED, 1 of 1.
  *edm; HW, infer; data: `edm-closing-r3x-events:out/e/`.*
- `E814` R3x-events stage d (alias2.s with a reset and an arm before each job; D0 the reader alone,
  D1 a writer leaving sa65 = 0xb009c4dc, E537's word with bit 8 clear, D2 one leaving sa65 =
  0x02000100, the count byte with bit 8 alone; each then calling the closed task): D0 held (pclink
  0x98, p1 1, sa64 2, sa65 0x02000000, sa63 0); D1 stopped the tick after the writer's pass with the
  busy signature of E537 (CR_CLKGATESTATUS 0x000ccfa0, USE0_SERV_EVENT 0x3f3 frozen, EVENT_TIMER
  moving), the CCB write and read offsets 2 and 2 (read = write) and HostCtl dword 14 0; D2 stopped
  it with the same signature (USE0_SERV_EVENT 0x3ee) and E537's two marks, read offset 3 against
  write offset 2 (read = write + 1) and dword 14 0xad002600; P3 (one miscinfo into the stopped EDM)
  was not answered in either stop; so H-CCB (bit 8 alone stops it with E537's marks and D1 keeps the
  tick) is REFUTED by D1, H-HANDLER (a job bit with no job stops it, no mark, D2 keeps it) by D2,
  H-ONCE (E537 does not repeat) by both, and H-REARM (P3 answered) by both; D2 held every frozen row
  of H-CCB's own (stop, read = write + 1, dword 14, busy); the stage ended by its stop budget at D2
  by design (the second stop), so D1's replicates, D3 (E537's own word, A8) and D4 were not run.
  *edm; HW, infer; data: `edm-closing-r3x-events:out/d/`.*
- `E815` R3k stages k0f and k0t (K0, the regression gate of the new module, stock firmware, no task
  of ours): F0 found all 15 debugfs files the kernel batch added or relies on and every default as
  designed (hold_recovery N, kick_no_bump N, render_pb_pages 0x00000422, render_rgn_arrays
  0x00000001, the kicker file 'kicker 2 ccbctl 2 2 kicks 2', six kregnow rows 0x4, 0x110, 0x130,
  0x740, 0xc00, 0xc04 and neither clear register), 12 of 12 rows held; the pinned old tool
  ~/sgxfive-test-r1 gave L1's geometry job dd-p1 (o0 mixed 0xff203040 x3622 and 0xff00ff00 x474, the
  line, parameter-buffer and TA-data hashes equal to the landed ones) and L2's pixel job
  t-ctl-green-16x16 (o0 0xff00ff00 in 256 of 256, CR_EVENT_STATUS2 0x400 before and after) exactly
  as they were kept, 11 of 11 rows held; two attempts of k0f before these stopped before any GPU job
  (the firmware was not loaded after the boot; the landed log filter read a new reset log line as a
  fault).
  *platform; HW, infer; data: `edm-closing-r3k-events:out/k0f/`, `edm-closing-r3k-events:out/k0t/`,
  `edm-closing-r3k-events:out/attempt1-nofw/`, `edm-closing-r3k-events:out/attempt2-logfilter/`.*
- `E816` R3k stages k0c and k0h (K0, tasks of ours unchanged from L3 and S2b on the new module):
  alias2 read its registers as E791 found them (C0: pclink 0x98, p1 1, sa64 0x2, sa65 0x02000000,
  sa63 0; C1, sa65 written with bit 23 set, kept the tick and the next entry read sa65 0x02000000
  again) and ring_hold read idle with no task (H0: signatures idle-empty twice) and busy in every
  element sampled inside a 90.5 ms hold (H1: hold 2262434 units, as wanted, signatures busy twice,
  all elements as a running task); G0, one ordinary miscinfo kick, was answered, logged one kick
  entry carrying the count 2 and moved the kicker file and the CCB offsets from 2 to 3 (kicker 3
  ccbctl 3 3 kicks 3), the ticks on the 25000 grid; one row (ticks_K_after, the count byte of the
  ticks after the kick) is void because the 16-rung ring ended at the kick entry: 7 held, 1 void.
  *edm; HW, infer; data: `edm-closing-r3k-events:out/k0c/`, `edm-closing-r3k-events:out/k0h/`.*
- `E817` R3k stage f (K1, 9 jobs of ring_exit.s, which logs every pass of its four PDS #13 slots in
  a ring and ends a tick pass of window 2 as ACT says; stops 1): the closed exit reached by a tail
  call from our page (cont4, to exit index 0x1974, the first run of the kernel's new patch kind)
  kept the tick in 2 of 2 jobs (FC4); our own replica of the exit, cfi.global, idf, wdf, phas ...
  end, nop.end, kept it in 2 of 2 (FB); cfi.global, idf, wdf, nop.end stopped it in the one job run
  (FCF: 4 ring entries, busy signature of E537 with CR_CLKGATESTATUS 0x000ccfa0, the miscinfo of P3
  not answered in 505 ms, CCB offsets 2 and 2, dword 14 0, not replicated by the stop rule); idf,
  wdf, phas ... end, nop.end kept it in 2 of 2 (FPH); frozen verdict 'H-PHAS (the phase end is what
  the EDM needs)', H-ANY, H-BOTH, H-CFI and H-PLACE refuted by the held-out rows and H-BEFORE
  refuted by the control.
  *edm; HW, infer; data: `edm-closing-r3k-events:out/f/`,
  `edm-closing-r3k-events:out/kev-attempt1-armlog/`.*
- `E818` R3k stage t (K1, 5 jobs of ring_timer.s, stops 1): a task of ours that stored the tick
  handler's own word 0x01061a80 to CR_EVENT_TIMER (str #691, the verifier's new row, the first str
  of the timer by a task of ours) and then called the closed task kept the tick in 2 of 2 jobs (T1)
  with the next entry 25114 units after the acted pass in both, outside the frozen 25000 +- 50; the
  same str followed by our own idf, wdf, nop.end stopped it in the one job run (T2: 4 ring entries,
  E537's busy signature, the miscinfo of P3 not answered, not replicated); frozen verdict 'H-NOTIMER
  (the timer write does not make our own end enough)', H-TIMER refuted by the held-out row,
  H-TIMERW-HARMLESS and H-TIMERW-STOPS refuted by the control.
  *edm; HW, infer; data: `edm-closing-r3k-events:out/t/`.*
- `E819` R3k stage kb (K1, 12 jobs of ring_hold.s, Q290, no stop): with the kicker word W written to
  0x42 (the debugfs kicker file; Q1, 3 jobs) the count byte pa1 bits 31:24 of the ticks after the
  write stayed 2 (3 to 4 ticks a job), so H-KW (the hardware reads the kernel's kicker word at each
  event) is REFUTED, 3 of 3; with the write followed by one ordinary miscinfo (Q2) the kicker file
  read 0x43 (67), the CCB offsets and the kicks counter 3, the miscinfo was answered, and the count
  after the kick is void because the 16-rung ring held 16 ticks and ended 11 ms before the kick
  (H-LATCH and H-HWC cannot tell); with the one-shot kick_no_bump (Q3, the command written and
  kicked, W not bumped) the miscinfo was NOT answered in 3 of 3 jobs (no answer in 504 ms), the CCB
  write offset moved to 3 and the read offset stayed 2, the kicks counter rose by 1 and W stayed 2,
  and the 3 controls that predicted an answer FAILED; frozen verdict 'Q0 held (ticks K = 2);
  consistent with [H-LATCH, H-HWC], refuted [H-KW]'.
  *edm; HW, infer; data: `edm-closing-r3k-events:out/kb/`.*
- `E820` R3k stage e2b (K1, 15 jobs of pa_write2.s, Q098, no stop; the first run of the verifier's
  mov to pa2, pa3 and pa4): the controls held (R x3: pa0 to pa4 read E748's words and the next pass
  the same; S: a marker written to sa67 read back through pa3 in the same pass and the next; Z67 and
  Z68 put E748's words back); a marker written by mov to pa3 was read in the same pass through pa3
  and sa67 and in the next pass (M, M and M, M) in 3 of 3 jobs, H-D alias; a marker written by mov
  to pa4 was read through neither pa4 nor sa68 in the same pass or the next (old, old and old, old)
  in 3 of 3, H-B lost; a marker written by mov to pa2 was read through pa2 and sa66 in the same pass
  (M, M, 3 of 3, H-D) and neither in the next pass (old, old, 3 of 3, not frozen); the neighbours
  were unchanged in every job; frozen verdict 'write direction: consistent with none, refuted [H-D
  alias, H-B lost, H-P private]'.
  *usse; HW, infer; data: `edm-closing-r3k-events:out/e2b/`.*
- `E821` R3k stage e3h (K1, 3 rounds, Q166, no stop): after a loop fill latched CR_EVENT_STATUS2 at
  0x440 (bit 6, TRIG_3D, and the idle bit 10; still 0x440 after 1 s), a host write of bit 15
  (0x8000, a bit that was not set) to CR_EVENT_HOST_CLEAR2 through debugfs kregnow 0x0114 left it at
  0x440, a host write of bit 6 (0x40) cleared it to 0x400, and a further loop fill latched it again
  to 0x440, in 3 of 3 rounds: frozen verdict 'CLEAR2 reads [H-W] in 3 rounds', H-W (the bits written
  clear), H-ALL (any non-zero write clears all) and H-NONE (no write clears) tested, H-ALL and
  H-NONE refuted.
  *platform; HW, infer; data: `edm-closing-r3k-events:out/e3h/`.*
- `E822` R3k stage e3a (K1, 3 rounds, Q166, no stop): the same five steps as E821 with the CLEAR2
  write made by a task of ours (strclr.s, `str #69`, the verifier's new row for 0x0114) in slot 0
  instead of the host: CR_EVENT_STATUS2 0x440 after the loop fill and after 1 s, 0x440 after bit 15,
  0x400 after bit 6, 0x440 after the next loop fill, in 3 of 3 rounds: frozen verdict 'CLEAR2 reads
  [H-W] in 3 rounds; the host route (e3h) ran: exit 0', H-ALL and H-NONE refuted; the firmware route
  and the host route agree.
  *platform; HW, infer; data: `edm-closing-r3k-events:out/e3a/`.*
- `E823` R3k stage e3b (K1, 4 jobs run of ring_skip3.s, 1 stop, last stage; Q111, Q166): the fill
  without the skip (B0 x3, controls) completed with one slot-3 end-of-render entry and the tick
  alive; with the end-of-render pass of slot 3 skipped once (B1: our own end in place of the closed
  handler, hold_recovery Y) the fill never completed (the tool timed out, job hung), the tick
  stopped with E537's busy signature (CR_CLKGATESTATUS 0x000ccfa0; the signature's EVENT_STATUS
  0x20040000), CCB offsets 3 and 3, dword 14 0, the miscinfo of P3 not answered (504 ms): frozen
  verdict 'H-STOP3 (a skipped end-of-render handler stops the tick)'; the readings of
  CR_EVENT_STATUS bit 18 and of the host writes of CR_EVENT_HOST_CLEAR are frozen 'refuted [H-FREE3,
  H-LEVEL, H-PULSE, H-REFIRE, H-W (stop only: ... bit 29)], cannot tell [H-ALL, H-NONE, H-W]'
  because bit 18 read clear in the first of 9 watch reads; read after the run, bit 18 was set in 8
  of 9 reads from 7.3 ms to the end of the 50 ms watch, a write of bit 15 left it set at 1 and 3 ms,
  a write of bit 18 cleared it at 1 and 3 ms and a write of bit 29 left CR_EVENT_STATUS bit 29 set;
  B2 (the firmware route) did not run.
  *platform; HW, infer; data: `edm-closing-r3k-events:out/e3b/`.*
- `E824` R3k stage k-f4 (K2, 11 jobs, Q140): with the new debugfs knob render_rgn_arrays at 4 (four
  region-header arrays), mode 2 and CR_TE_AA 0xe0000000, 8 of 8 held-out sizes (288 x 144, 256 x
  288, 384 x 384, 320 x 160, 512 x 384, 640 x 480, 320 x 400, 1024 x 768) completed with 0 wrong
  pixels of 41472 to 786432 and the TA data size the four-array layout gave (0x8000, 0x8000, 0xb000,
  0x8000, 0xb000, 0x13000, 0xc000, 0x1e000); the controls passed (64 x 64 at knob 1 and at knob 4
  complete with the same TA data size 0x6000, and 288 x 144 at knob 1 faulted at BIF_INT_STAT
  0x90004, page 0x20006, as E729 did): frozen verdict 'k-f4: 8 of 8 held-out rows complete with 0
  wrong pixels and four arrays in the four-array layout; controls PASS'.
  *ta; HW, infer; data: `render-closing-r3k-pixel:out/20261110-193547/k-f4/`.*
- `E825` R3k stage k-pb0 (K2, 3 jobs, Q285, controls of the parameter-buffer pokes, split flow -n 2
  --geometry 1 at 64 x 64, mode 2): TE 0x40 (the dump run pb-d0 and p1) reproduced E728's empty
  image (3969 of 4096 pixels wrong, 0 triangle pixels, first wrong pixel (1, 1) 0xff000080) and its
  parameter buffer words 0 to 26 (stream 04000004 00030001 04000000 at 0 to 2, E728's stretch at 11
  to 26), with parameter buffer and TA data identical between the two jobs; TE 0x60 (p0, the twin)
  drew the whole triangle (4096 pixels, 0 wrong) with dwords 0 to 25 as the twin's; the three
  controls nevertheless FAILED against values frozen from jobs of another shape (E728's and the
  twin's one-render jobs; this stage ran two renders and the tool checks the image of render 2,
  which it draws on background 0xff000080, so an all-background hash differs by construction): the
  target hash of d0 and p1 0x8ea26cdfee74a325 against 0xfc5ff15e0434a325, p0's target hash
  0xd2bfb75560f4c325 against 0xd0530839d87ea325, and p0's dword 26 0x04000004 against 0; the gate
  closed, which says nothing about the module ('closed: k-pb0 controls pb-d0-te40 FAIL, pb-p0-te60
  FAIL, pb-p1-te40 FAIL') and stage k-pb (5 jobs, Q285's pokes) was skipped; frozen verdict 'Q285:
  not run (no kept k-pb)'.
  *isp; HW, infer; data: `render-closing-r3k-pixel:out/20261110-193547/k-pb0/`,
  `render-closing-r3k-pixel:out/20261110-193547/gate-k-pb.txt`,
  `render-closing-r3k-pixel:out/20261110-193547/verdict.txt`.*
- `E826` R3k stage k-bif (K2, 5 jobs, Q003 what clears a latched fault, 4 held bus-interface faults:
  a TA read (f1, f1r, CR_BIF_INT_STAT 0x90008, CR_BIF_FAULT 0x3e000001), a TA write (f2, E788's a6,
  0x90004 and 0x20008061) and a texture fetch (f3, 0x90002 and 0x3e017001), plus the idle row n0):
  n0 passed (the four writes with nothing held changed nothing, BIF_CTRL restored); in each held row
  the write of 0x1 (an unset bit) and the write of the fault word without bit 19 to CR_BIF_INT_STAT
  (0x10008, 0x10008, 0x10004, 0x10002) left CR_BIF_INT_STAT and CR_BIF_FAULT as they were at the
  kernel's read after the write (4 of 4); setting bit 4 of CR_BIF_CTRL (the debugfs flip,
  CLEAR_FAULT) made the kernel's read after the write return 0x80000 and 0 (f1, f1r, f3) or 0 and 0
  (f2); clearing the bit again returned both registers to the fault's values (4 of 4); the registers
  stayed latched through the 2.5 s watch, the jobs never completed and only the debugfs reset
  cleared them; all four held rows are OTHER by the frozen rule: 'Q003: cannot tell: no held row
  could be read'.
  *bif; HW, infer; data: `render-closing-r3k-pixel:out/20261110-193547/k-bif/`.*
- `E827` R3k-regress (the lead's regression session on the new module, srcversion 230E0EF5): 23 of
  23 rows of stage rg-ctl, taken from closing sessions that passed on the old module (E773 g-u1 tri
  and geometry jobs at 1024 x 768 and other sizes, E806 green fills 8 x 8 to 256 x 256, E798 g-dd
  probes, E763 and E788 r2-a-safe TE 0x20 and 0xe0 jobs; 2 controls, 21 held out), reproduced their
  old kept values (return code, echo, target hash, diff, first wrong pixel, triangle counts, renders
  ok and the dump hashes where the old job had a dump); in stage rg-pb 7 of 7 held-out rows in
  E728's one-render shape (TE 0x40 four times, one in mode 0 and one at 128 x 128, TE 0x80 and 0xc0,
  all held out) and its two controls (TE 0x20 and 0xe0) reproduced E728's target hash, diff,
  parameter buffer dwords and dump sha256s, so the module did not change E728's image; the same job
  in K2's shape (-n 2 --geometry 1, TE 0x40) gave 0x8ea26cdfee74a325, 3969 of 4096 pixels wrong, in
  3 of 3 jobs, the value of E825's k-pb0, and the twin row (TE 0x60) gave 0xd2bfb75560f4c325, 0
  wrong, again E825's twin value (H-SHAPE: the hash difference of E825 belongs to the job shape, not
  to the module [infer]); frozen verdicts 'rg-ctl: control 2 PASS of 2; heldout 21 PASS of 21; every
  row reproduced its old value (no module regression in these classes)' and 'rg-pb: E728-shape 7 of
  7 held-out rows as H-OLD, controls {'pb-e20-m2-64': 'PASS', 'pb-ee0-m2-64': 'PASS'}; -n 2
  --geometry 1: 3 of 3 as H-NEW, twin row H-NEW; H-SHAPE'.
  *isp; HW, infer; data: `render-closing-r3k-regress:out/20261110-222647/rg-ctl/`,
  `render-closing-r3k-regress:out/20261110-222647/rg-pb/`,
  `render-closing-r3k-regress:out/20261110-222647/score-rg-ctl.txt`,
  `render-closing-r3k-regress:out/20261110-222647/score-rg-pb.txt`,
  `render-closing-r3k-regress:out/20261110-222647/gate-rg-pb.txt`.*
- `E831` R3-geo-c stage g-z (15 jobs, E730's isp-a-guard rows: a depth ramp drawn by the full-screen
  triangle or by one placed triangle, the depth buffer pre-filled with 0xdeadbeef, a dword stored
  iff it is not 1.0f as E465 reads it): the three controls reproduced E730 (924, 924 and 3444
  stored, rule A's sets), and on the 10 held-out full-screen cells at even sizes (widths 20, 36, 44,
  76, 32 and 64 at H 18; heights 20, 28, 36 and 32 at W 34) the stored set was the frozen rule A's,
  x + 0.5 < 1.25 W and y + 0.5 < 1.25 H cut at the target's tile area, in 10 of 10 (FLOOR, x <
  floor(1.25 W), gives the same sets at every even size and was consistent too), while ROUND and
  CEIL were refuted in 10 of 10 and RSTRICT (x + 1 < 1.25 W) in 6 of 10; where 1.25 W or 1.25 H
  passes the tile area (W 32 and 64, H 28 and 32) the store stopped at the last tile (extents 32,
  64, 32 and 32); two single triangles that do not cover the band stored exactly their own
  pixel-centre raster cut by the band (z-tri-in 96 of 96 at 34x18, wholly inside the band;
  z-tri-cross 357 of 357 at 36x20, crossing its edge; RSTRICT's raster refuted by 37 pixels): the
  band rule of E730 holds held out at every even alignment, and only the fraction .75 of 1.25 W,
  which needs odd sizes, still separates rule A from FLOOR.
  *zls; HW, infer; data: `render-closing-r3-geo-c:out/g-z/`.*
- `E832` R3-geo-c stages g-qf and g-qh (36 jobs at 4096x4096, the first threshold thr0 = P - 0x22
  set by render_pb_pages and read from the job's own 0x0624, the count of partial renders read as
  the 0x0658 bit 0 stretches of the job's timeline): at U = 287 (the tool's triangle, one render)
  the controls passed (2 at P 0xa0, 1 at 0xb0 and 0xa3, as E625 and E779) and the 19 fit cells read
  a count that never rises with P, 9 at P 0x24 and 0x25, 8 at 0x27 to 0x29, 7 at 0x2c to 0x31, 6 at
  0x32, 5 at 0x39 to 0x43, 4 at 0x44 and 0x53, 3 at 0x54 and 0x6d, 2 at 0x6e to 0xa2: the frozen
  verdict is that E625's count formula 1 + floor((U + k - thr0) / (thr0 + s)) is REFUTED at U = 287,
  none of the 20 (k, s) pairs that fit E625's and E779's cells (k -8 to 0, s 0x1b to 0x1e, the only
  pairs of k -60 to 60 and s 1 to 0x5f that do) fitting the 19 cells; in g-qh both scene gates
  passed (U 275 and 438, no partial render at P 0x422), the scene s275 (one triangle moved by 1024,
  0) read 8 at P 0x26 and 0x27, 7 at 0x2a and 0x2b, 6 at 0x31 and 3 at 0x52, and the six cells of
  s438 were void by the frozen rule (the geometry-only first render overflowed before the last); the
  held-out verdict (REFUTED, none of the 0 pairs the fit left) follows from g-qf's and tests nothing
  more.
  *dpm; HW, infer; data: `render-closing-r3-geo-c:out/g-qf/`, `render-closing-r3-geo-c:out/g-qh/`.*

### 2026-11-11

- `E828` R3-rgn4 (the laptop check of the linux fork's 4x render contexts, fork resgx545 a2788bd8,
  module srcversion 99CD90DA): at render_rgn_arrays 0 (automatic) a 288 x 144 job at CR_TE_AA
  0xe0000000, mode 2, on a context made with DRM_SGXFIVE_CTX_RENDER_AA_4X completed with 0 of 41472
  pixels wrong, hash 0x4a61860dcb4ab325, TA data 0x8000 bytes, its target and both dumps equal to
  E824's h1; the same job on a context made without the flag was refused with EINVAL at submission;
  at render_rgn_arrays 1 the job faulted as in E729 (BIF_INT_STAT 0x90004, BIF_FAULT 0x20006061,
  recovery held; then one health triangle failed before one passed), and E827's row
  ctl-a1-256x160-tee0 reproduced byte for byte (hash 0x845a011c4fbf2325, 0 of 40960 wrong, TA data
  0x6000 bytes, sha256 eaa6c96c...4372992); the 1x control reproduced E827's ctl-u-1024-n1; a 4096 x
  4096 context with the flag was created and its 4x job faulted (BIF_INT_STAT 0x90100, BIF_FAULT
  0x10000011) with 1048576 of 16777216 pixels right, the first wrong at (1024, 0), no dump written,
  health ok 3 of 3 after.
  *ta; HW, infer; data: `render-closing-r3-rgn4:out/rgn4/`,
  `render-closing-r3-rgn4:rgn4-REPORT.md`.*
- `E829` R4-A stages a-pb0 and a-pb (Q285 rerun, 8 jobs, split flow -n 2 --geometry 1 at 64 x 64,
  CR_TE_AA 0x40000000, forced render_rgn_arrays 1, module srcversion 99CD90DA, controls frozen from
  E827's two-render jobs of the same shape): the four controls passed (pb-d0-te40, pb-p1-te40 and
  pb-p2-own11: hash 0x8ea26cdfee74a325, 3969 of 4096 pixels wrong, first (1, 1) 0xff000080,
  parameter buffer sha256 b8ada427...; pb-p0-te60: hash 0xd2bfb75560f4c325, 0 of 4096 wrong) and the
  gate opened; poking the twin's 16 words into dwords 11 to 26 of render 1's parameter buffer
  between the two renders gave the twin's picture in 2 of 2 jobs (pb-p3a, pb-p3b: 0 of 4096 wrong,
  render 2 4096 triangle pixels, hash 0xd2bfb75560f4c325, the dump's dwords 11 to 26 the poked
  words, 16 of 16 pokes applied) and poking dword 11 with 0xffffffff drew nothing in 2 of 2 (pb-p4a,
  pb-p4b: 3969 of 4096 wrong, render 2 0 triangle, 4096 background, 0 other pixels); frozen verdict
  'Q285: H-OLD: the 3D reads render 1's object in the old layout (4 of 4 rows decided)', both
  readings H-FIELD needed (p3 not the twin's picture, p4 drawn) contradicted by both replicate
  pairs.
  *isp; HW, infer; data: `render-closing-r4-q285:out/20261111-081210/`.*
- `E830` R4-B stage fr (Q152 replicate of E817's FCF, 21 jobs in 3 blocks and 3 recoveries,
  ring_exit.s as in E817, module srcversion 99CD90DA, no reset between the arm and fcf in a block,
  one stop a block): in each block the controls kept the tick (e0; fc4 and fc4-r2, the tail call to
  the closed exit, next entry after the acted pass +24994 to +24995; fb and fb-r2, our replica with
  cfi.global, idf, wdf, phas end, nop.end, +24994 to +24995, 3 blocks of 3 each) and the pass ending
  cfi.global, idf, wdf, nop.end (fcf1, fcf2, fcf3) stopped it in 3 of 3 with E817's signature (4
  ring entries, ACT_SEEN 3, both samples busy with CR_CLKGATESTATUS 0x000ccfa0, EVENT_STATUS
  0x20000000, the EVENT_TIMER counting, USE0_SERV_EVENT bit 16 clear and frozen at 0x1114, 0x1114
  and 0x1133, CCB read = write = 2, HostCtl dword 14 0, P3 one miscinfo not answered in 505 ms with
  0 new ring entries); after each stop the reset, gate and health were ok, the re-armed pass idf,
  wdf, phas end, nop.end (fk1 to fk3, E817's fph) kept the tick (+24994 to +24995); every control
  PASS, frozen verdict 'H-REP held (3 held, 0 FAILED, 0 cannot tell of 3); H-NOREP refuted (0 held,
  3 FAILED)'.
  *edm; HW, infer; data: `edm-closing-r4-q152:out/20261111-082403/`.*
- `E833` Converted from the published closing-pass sessions (R3-pixel, R3-geo, R3-geo-c, R3k-pixel)
  as vectors, sgx-sim replays all 204 pixel-loop proofs of R3-pixel (q-f0 10, q-f1a 54, q-f1b 54,
  q-t 86) and its 8 direct-read jobs (48038 pixels, 0 mismatches); it refuses R3-pixel's 73 vertex
  loops (a `phas` wait on vcull, E121) and the 14 tables of depth words (57 jobs, E795-E798), dword
  36 (60 jobs, E803), DPM counts (R3-geo, R3-geo-c), ZLS extents (15 jobs, E831) and
  parameter-buffer pages (10 dumps, E824), each with its reason; R3-pixel's 285 timing rows are
  data, not a prediction.
  *usse; HW; data: `vectors-closing-r3-pixel-loops`, `vectors-closing-r3-pixel-direct-reads`,
  `vectors-closing-r3-pixel-timings`, `vectors-closing-r3-geo-depth`,
  `vectors-closing-r3-geo-dword36`, `vectors-closing-r3-geo-counts`,
  `vectors-closing-r3-geo-c-counts`, `vectors-closing-r3-geo-c-zls`,
  `vectors-closing-r3k-pixel-pb-pages`.*
- `E834` R4 stage kb2 (r4-events, 10 jobs of ring_hold.s, each a reset and an arm, the writes made
  before the logging window and one miscinfo 1 ms after it opened, no stop; Q290): the ordinary
  kicks (g0p x2, the timing control) gave one kick entry with K 2 6.45 and 6.46 ms after the call's
  stamp, 8 ticks before it and 7 after, the ticks after K 3 and pa2 0x01061a70, answered; with the
  kicker word W written to 0x42 before one ordinary kick (q2p x3) the kernel's bump made W 0x43
  (67), the kick was served (one entry, K 2, answered, CCB offsets 3 and 3) and the 6 ticks after it
  carried K 3 in 3 of 3, so the count is not W as latched (H-LATCH refuted); a kick without the bump
  (q3p x3, q4 x2) raised no kick entry in 5 of 5 (the ring reached 5 to 6 ticks past the call's
  stamp + 8 ms), the ticks after it kept K 2 (H-HWC, a count of CR_EVENT_KICK writes, refuted),
  carried pa2 0x01061a74 (E751's latched mark) from the first tick 6.75 to 7.94 ms after the stamp
  on, and USE0_SERV_EVENT bit 16 read set in both samples after the 504 ms timeout; an ordinary kick
  sent after it in a second window (q4 x2) was served at once (one entry with K 2, answered in 3.5
  ms) and read one command (CCB 4 and 3, W 3), and its ticks still read 0x01061a74; frozen verdict
  'count byte: H-LATCH REFUTED, H-CNT consistent (3 row groups), H-HWC REFUTED; unbumped kick:
  H-PEND REFUTED, H-NOEVENT REFUTED, H-LATE REFUTED'.
  *edm; HW, infer; data: `edm-closing-r4-events:out/a1/kb2/`.*
- `E835` R4 stage kp (r4-events, 4 jobs of ring_exit2.s, no stop; Q152): with the controls passing
  (e0, 14 entries on the 25000-unit grid, nothing acted; fk, a plain tick pass ended idf, wdf, phas
  #0, #0, pixel, end, parallel, nop.end, kept with the next entry +24994, CCB 2 and 2, dword 14 0),
  a kick pass made by one miscinfo and ended the same way (kp held out, kp-r2 replicate, each after
  a reset and an arm) kept the tick in 2 of 2: the kick entry logged with flag 3 (ACTED 1, ACT_SEEN
  4), then 14 and 15 ticks on the grid in the 16-rung ring (kp: the first 24994 units after the tick
  before the kick, as after fk's acted pass, then 25006 and 25000) and 539 and 537 more entries
  dropped by the full ring while the call waited, the signature idle in both samples
  (CR_CLKGATESTATUS 0x20, USE0_SERV_EVENT bit 16 set and counting, CR_EVENT_STATUS 0x20000000), the
  miscinfo not answered in 504 ms, the CCB write offset 3 and read offset 2 (read = write - 1) and
  HostCtl dword 14 0, the ticks after the kick carrying K 3; frozen verdict 'H-PHAS-ANY consistent
  (3 row groups), H-KICK-MORE REFUTED', 19 of 21 non-control rows decided (H-KICK-MORE's P3 row
  cannot tell: no stop).
  *edm; HW, infer; data: `edm-closing-r4-events:out/a1/kp/`.*
- `E836` R4 stage e3p, the end of the pass (r4-events, ring_skip3p.s, 2 of its 4 jobs run, the stage
  ended by its stop rule at its first B1P; Q152's slot 3 clause): the fill without the skip (b0,
  control, E823's B0) completed with one slot 3 end-of-render entry and the tick alive; with slot
  3's first end-of-render pass skipped once and ended by our task idf, wdf, phas #0, #0, pixel, end,
  parallel, nop.end instead of the closed handler (b1p, held out, hold_recovery Y) the fill was held
  (the tool's job hung, rc 1) and the tick was found stopped after the 50 ms status watch, with
  E537's busy signature (CR_CLKGATESTATUS 0x000ccfa0, USE0_SERV_EVENT 0x422, bit 16 clear and
  frozen, the event timer counting, CR_EVENT_STATUS 0x20040000), CCB read = write = 3, HostCtl dword
  14 0 and P3 one miscinfo not answered in 505 ms with 0 new ring entries; frozen verdict
  'H-PHAS-ANY REFUTED, H-SLOT3-MORE consistent (1 row groups)'; read after the run, the ring held 10
  more ticks on the 25000-unit grid after the slot 3 entry (then full), where E823's B1, which ended
  the same pass idf, wdf, nop.end, logged nothing after it, so the phase end let the tick run on for
  at least 10 ticks and the stop came later.
  *edm; HW, infer; data: `edm-closing-r4-events:out/a1/e3p/`.*
- `E837` R4 stage e3p, the status bits (r4-events, the same two jobs as E836; Q166, Q111): in b0
  (the fill without the skip, control) CR_EVENT_STATUS read 0x20000000 in 9 of 9 watch reads from
  the slot 3 entry to 54 ms (bit 18 never set) and STATUS2 0x400; in b1p (slot 3's end-of-render
  pass skipped once, the watch started when the page showed the slot 3 entry, 4.76 ms after the fill
  began) CR_EVENT_STATUS read 0x20040000, PIXELBE_END_RENDER (bit 18) set, in 7 of 7 reads from 0.01
  to 54.5 ms, STATUS2 0x400 throughout; after the tick had stopped, a host write of bit 15 (0x8000)
  to CR_EVENT_HOST_CLEAR (0x0134, debugfs kregnow) left bit 18 set at 1 and 3 ms, and a write of bit
  18 (0x40000) cleared it, 0x20000000 at 1, 3 and 20 ms; frozen verdict 'H-LEVEL consistent (1 row
  groups), H-PULSE REFUTED; H-W consistent (2 row groups), H-ALL REFUTED, H-NONE REFUTED' on one B1P
  job (H-LEVEL held out, the clears a fit to E823's one job), the two replicates not run.
  *platform; HW, infer; data: `edm-closing-r4-events:out/a1/e3p/`.*
- `E838` R4-pixel stage p4-o4 (Q276, 36 jobs in E808's p-c3 shape: a triangle's pixel program
  writing tagged words to o0 to o7 in E709's four-output setup, the words at bits 3:0, a job marker
  at bits 15:6, x and y jobs decoding to source pixels): the 8 controls passed (G-o4 on c-e709 and
  c-o4-u, c-o4-u and the swapped c-o4s-u reading tag 5 as E808, G-o1 tag-2 fraction 0.994 of 486
  sources) and the replicate of c-o4-u read its class; in the 7 held-out value configurations (A3 =
  tag 13 alone, A4 = tag 5 with bit 4 alone, A then A4, A4 then A, A then A5, A5 then A, A3 then A4;
  14 of 14 jobs) every o4 word read was the plain A (tag 5, bits 5:3 clear, the job's marker, 22 to
  63 words a job, no A3, A4 or A5 word), so none of the 12 frozen models (single-write path V1 drops
  bit 3, V2 refuses a word with bit 3, V3 as written, by combine rule last, first, and, or, min)
  fits; frozen verdict 'family REFUTED: no (single-write path, combine rule) model fits the value
  rows; a new reading is needed'; the 12 predicate jobs (6 configurations, also all tag 5) are
  cannot tell by the frozen gate (the bit-4 pairs read one class in both orders).
  *pds; HW, infer; data: `render-closing-r4-pixel:out/20261111-205726/p4-o4/`,
  `render-closing-r4-pixel:fold/`.*
- `E839` R4-pixel stage q4-v (Q082 bit 7, 28 jobs, 27 scored: a vertex program on the tool's
  triangle looping N times on a relative br, the stored depth word 0x3f200000 + N the loop proof,
  every job under regtimeline 0x0008, 0x0118, 0x012c; L = the longest run of CR_CLKGATESTATUS
  0x000ccff8): the four bridge controls to E807 passed on the rgn4 module (no loop and N = 1 clear
  with L 9.4 and 4.6 us, E807's 880 clear with L 105.1 us and 1760 set with L 207.3 us); on three
  ladders E807 never ran (10 multiply-adds an iteration on 3 vertices, counter and branch only on 3,
  E807's 8-instruction body on 24 vertices) the six FIT points were clear as the model placed them,
  and the frozen rule 'bit 7 set iff L >= 129.5 us' held in 14 of 14 decided held-out rows (clear to
  L 119.5 us, set from 138.6 us; the one row in the edge 122 to 136 us, L 133.2 us, set, not
  scored), the bit showing 121.9 to 129.7 us after the run began in 10 of 10 set jobs (frozen window
  118 to 138); the stock program with 1500 vertices at 2048 x 2048 kept bit 7 clear in 2 of 2 with L
  11189.2 and 11209.7 us (H-STALL, frozen: a long but progressing TA does not latch; H-PHASE refuted
  in those rows); the 4096 x 4096 row returned -ENOSPC (the scene overflowed the parameter buffer at
  the default pages), void; frozen verdict 'bit 7 follows the TA clock run L (set iff L >= 129.5 us,
  edge 122..136) (14 of 15 rows decided)'.
  *edm; HW, infer; data: `render-closing-r4-pixel:out/20261111-205726/q4-v/`,
  `render-closing-r4-pixel:fold/`.*
- `E840` R4-pixel stage q4-f (Q082 bit 6, 16 fills of 64 x 32 whose pixel program ends in a MARK
  only when its loop counters end): the five bridge controls to E804 and E805 passed on the rgn4
  module (the relative 8-instruction loop clear at 16 and 53, set at 56 and 136 iterations; E805's
  load body ld8 clear at 70); in 11 of 11 held-out jobs whose program waits on a load, one load then
  the 8-instruction ALU loop K times (K = 28, 53, 70, 110) or M rounds of a load and K iterations
  ((K, M) = (28, 4), (28, 16), (40, 8), (70, 1), (70, 4), (110, 2), (220, 1)), bit 6 stayed clear,
  with bursts of 311 us to 4.2 ms, also where the ALU loop after the load ran 70 to 220 iterations,
  longer than the 56 that sets it without a load; frozen verdict 'q4-f H-LOADOFF alone is consistent
  (H-YIELD, H-SUM refuted)' (H-LOADOFF 11 held of 11, H-YIELD 4 held 6 FAILED 1 cannot tell, H-SUM 1
  held 9 FAILED 1 cannot tell).
  *edm; HW, infer; data: `render-closing-r4-pixel:out/20261111-210423/q4-f/`.*
- `E841` R4-pixel stage q4-t (Q082 bit 6 in triangles, 54 jobs: E806's relative 8-instruction loop
  with a MARK as the pixel program of the tool's triangle covering a W x H target, `--tri-full`):
  the 12 controls passed (the green triangle and the loop at N = 1 at 4x4, 8x8, 16x16, 32x16 and
  64x32 clear with the MARK or green on every pixel; the 64 x 32 fill clear at 53 and set at 56,
  E804); bit 6 first set in (96, 104] at 8x8, (140, 170] at 4x4, (56, 60] at 32x16 and (60, 66] at
  64x32, and 16x16 stayed clear at 46, 56 (twice), 60, 66 and 72; frozen verdict 'q4-t consistent
  none, refuted ['H-SEG', 'H-N', 'E806-DISC']': H-SEG (no progress for about 125 us, a piece of work
  at most a tile) REFUTED by 16x16 clear at 66 and 72 (21 held, 2 FAILED, 15 cannot tell of 38), H-N
  (a pass count near 57 to 62 at every size) REFUTED (18 held, 10 FAILED, 10 cannot tell), E806-DISC
  (56 or 110, 220 at 4x4) REFUTED (31 held, 7 FAILED); the time of the latch held the frozen
  first-piece reading (t6 = 250 + 0.43 N us after the burst's start to N = 290, then 250, +- 15) in
  8 of 8 rows at 8x8 and 64x32, N 150 to 330 (t6 252 to 357 us).
  *edm; HW, infer; data: `render-closing-r4-pixel:out/20261111-210423/q4-t/`.*
- `E842` R4-pixel stage g4-rw (Q230, 24 jobs: R2's t3-nocut shape, z = 0 and w = C x + D on the
  tool's three vertices, a table of 60 w split 30 FIT and 30 HELD OUT by the sha256 of their bits
  before the run): the four controls passed (w = 1; 3, 9, 4.5; 7, 10, 7.75; 1.40625, 1.78125, 1.5:
  three vertices at the window rule's positions, depth 0x3f000000, the known words exact); in the 14
  jobs at scale 1 and 4 (42 w in 1.03 to 7.84) the PB_OBJ.RHW word of every kept vertex was RZ of
  1/w (31) or RZ + 1 (11: w 1.125, 1.40625, 1.49219, 1.75638, 4.2782, 4.67374, 6.375, 6.75, 7.125,
  7.375, 7.83901), 19 of 19 FIT and 23 of 23 HELD OUT words read; the 6 jobs at scale 1/4 (18 w in
  0.254 to 0.443) read no word: frozen verdict 'every table word is RZ or RZ+1 of 1/w (42 of 60 rows
  decided); analysis not run: 19 of 30 FIT and 23 of 30 HELD OUT words read' (job shape 14 held, 6
  FAILED), so the frozen fit of the algorithm families did not run; read at the fold, those 6 jobs'
  window coordinates 32 + 32 x / w (frozen from -62.4 to 120.9) lie beyond the guard band of the 64
  x 64 target, and the TA cut each triangle to a polygon of 5 to 7 vertices every one of which lies
  on x or y = -16 or 80, so no kept vertex, and no 1/w of a table w, was stored.
  *ta; HW, infer; data: `render-closing-r4-pixel:out/20261111-210423/g4-rw/`,
  `render-closing-r4-pixel:fold/`.*
- `E844` R4-render4x stage c (3 probe fills of 64 x 32, TEXTYPE 2 sampled with smp3d): E726's own
  cu-xn program, run again as the control, read face 1 (-x) on 2048 of 2048 pixels with E726's
  pixels byte for byte, and two new off-axis programs, frozen before the run with the dominant-axis
  rule (face = 2 x axis + (coordinate < 0), axis u, v, w; +x, -x, +y, -y, +z, -z are faces 0 to 5 of
  256 dwords each), read every pixel's predicted face, 2048 of 2048 each (r4g-cube-a: faces 0, 643,
  0, 882, 235, 288 pixels; r4g-cube-b: 903, 0, 235, 261, 0, 649; all six faces between them, the
  dominant axis changing inside each image and no pixel within 0.0078 of a tie): the face select of
  E726, post hoc there, held out.
  *texture; HW, infer; data: `render-closing-r4-render4x:out/20261111-211315/c/`.*
- `E845` R4-render4x stages s0 and p: the three controls reproduced as frozen (1x 1024 x 768 hash
  0xc9e301d225fe2325; 4x 288 x 144 hash 0x4a61860dcb4ab325, 12 parameter pages; 4x 1024 x 768 hash
  0xde0b9233c9822325, 193 pages, all 0 wrong), then the 4x full triangle on a context made for 4x
  targets (four region-header arrays, CR_TE_AA 0xe0000000, parameter buffer 0x422 pages) faulted at
  1280 x 1024 and at 2048 x 1536, whose frozen page need U4 = 1 + ceil(2 tiles16 / 32) is 321 and
  769 of the 1024 usable pages, with E828 j4's word (BIF_INT_STAT 0x90100, BIF_FAULT 0x10000011:
  page 0x10000, SB 1, CID 1), no pixel right and health ok after each; the stage stopped at its
  second fault and its four other sizes did not run: H-PB not supported (0 held, 2 FAILED, 4 cannot
  tell), so a 4x render on four arrays faults where its scene fits the buffer, and E828's 4096 x
  4096 fault is not a parameter-buffer overflow.
  *dpm; HW, infer; data: `render-closing-r4-render4x:out/20261111-211315/s0/`,
  `render-closing-r4-render4x:out/20261111-211315/p/`, `render-closing-r4-render4x:postrun/`.*
- `E846` R4-render4x stage o (7 of 8 jobs run, o6 skipped by its condition): the frozen verdict is
  cannot tell for Q292 and for H-SPM4 because the control o2 (1x 1024 x 768 at render_pb_pages 0x82,
  frozen to overflow) completed with 0 wrong pixels; read after the run, its row ran the tool's
  default triangle, whose dumps hold 19 scene pages (o1, o2 and E845's s0), while its frozen need of
  97 was the model of the full-screen triangle, so the control's prediction was made for another
  scene; post hoc and not rescored, the 4x full triangle on four arrays completed at 1024 x 768 with
  P 0xe3 (193 pages) and ended in -ENOSPC without a fault one page lower (0xe2), as did 288 x 144 at
  P 0x23 (need 12), while 4096 x 1152 at 0x422 (need 1153) faulted with E828 j4's word (BIF_FAULT
  0x10000011) and the 1x full triangle at 4096 x 4096 ended in -ENOSPC: an overflowing 4x scene ends
  as a 1x one does, and the 4x fault is not the overflow.
  *dpm; HW, infer; data: `render-closing-r4-render4x:out/20261111-211649/o/`,
  `render-closing-r4-render4x:postrun/`.*
- `E847` R4-render4x stage t (7 jobs, 64 x 64): the frozen verdict for Q293 is cannot tell, because
  its two baseline controls (the line and the point object of the 11.31 sessions without a poke) are
  NODATA: the scorer reads a job's dump as NAME.tri.param.bin.gz and the probe rows kept theirs
  under the program's name (NAME.p1131-green__0.param.bin.gz, NAME.p1131-psizes__1.param.bin.gz), so
  neither the baselines nor the poked line and point were compared; the control t6 (E827's
  pb-e40-m2-64a) passed and on a context made for 4x targets CR_TE_AA 0x40000000 and 0x80000000 gave
  dword 11 = 0, the format word 0x00040101 at dword 12 and an empty image, as on one array (rows
  held, gated); read after the run from the kept dumps with the frozen insertion check, the
  baselines equal their frozen heads and CR_TE_AA 0x40000000 inserted one zero dword right before
  the format word of the line (dword 9) and of the point (dword 11), the image then empty: H-PAD's
  frozen positions and value, post hoc.
  *ta; HW, infer; data: `render-closing-r4-render4x:out/20261111-211649/t/`,
  `render-closing-r4-render4x:postrun/`.*
- `E848` R4-render4x stage h (4 held cells, each a 4x job on one array of region headers that
  faulted with a TA write, BIF_INT_STAT 0x90004, as frozen, then the debugfs reset, the cell's
  follow-up and health triangles until one passed): every failing health triangle named the failed
  job's page and SB 6, at 0x20006061 once after a 288 x 144 job (h1) and at 0x2000a061 twice after a
  640 x 480 job (h2), a page never seen in a health fault and not the health context's own end
  (0x20006); a 64 x 64 triangle on a context made for 1024 x 768 run first passed and the health
  triangle after it too (h3, no replay seen); after a fill that passed, the first health triangle
  faulted at 0x20006062, the job's page and SB with directory list 2 in place of 1 (h4); the frozen
  verdict over both attempts: H-REPLAY not supported, 3 held, 1 FAILED (h4, which froze the job's
  whole word); CR_CLKGATESTATUS read 0x78 after every fault and after the fill and 0x20 once a
  render had completed; the kernel's 'SGX recovery failed: -110' followed 3 of the 4 held resets and
  2 of the 4 health faults, its register dump reading BIF_INT_STAT 0x000d0004 every time.
  *bif; HW, infer; data: `render-closing-r4-render4x:out/20261111-211649/h/`,
  `render-closing-r4-render4x:postrun/`.*

### 2026-11-12

- `E849` Read offline after the hypothesis (post hoc, no frozen prediction; round 5 plan
  closing5/events, step F0): E836's b1p stop dump, taken at the stop's signature before the host's
  clears, holds HostCtl dword 3 (host_ctl.ukernel_detected_lockups) = 1 and dword 8
  (host_ctl.interrupt_flags) = 1, dword 9 0, dword 14 0, sw_events 1 and TA3DCtl dwords 56 to 58 =
  0, 0 (ta3d_ctl.kick_clear_3d), 0xaac267c2, where the dumps of the same job at the arm read 0
  throughout; its page counts exactly 20 slot 0 passes after the fill's kick entry (10 ticks logged
  in the ring, then 10 counted with the ring full), 2 x host_ctl.hw_recovery_sample_rate (dword 5 =
  10), against 0 in E823's b1 and 302 and 289 in the two fills that completed; of the 23 published
  dumps past the boot with CR_CLKGATESTATUS 0x000ccfa0, b1p's alone has dword 3 or dword 8 set (the
  other 22 read 0, 0 and dwords 56 to 58 = 0): [infer] the stop is the EDM's own lockup routine of
  E353, its second sample of a 3D progress word equal to the first.
  *edm; HW, infer; data: `edm-closing-r4-events:out/a1/e3p/`, `edm-closing-r3k-events:out/e3b/`,
  `cited-scratch:cited/closing5/events/offline/`.*
- `E850` Offline reading of kept images (Q276; no new job, post hoc against E838's reading, no
  held-out row): E838's reading 'the path that brings o4 out clears bits 5:3 of the word' is refuted
  on the kept data of E808 and E838: in E808's p-c3 (words marker * 16 + tag, so the marker's two
  low bits sit at bits 5:4) the 44 of 58 jobs whose marker has a non-zero bit there held 1525 tag-5
  words, all 1525 with the job's whole marker and none with bits 5:4 cleared, and E838's bridge
  control c-e709-x (E709's own program, every output word 0xcfN) read 0xcf5 at all 39 of its tag-5
  words; so bits 5:4 of the tag-5 word are kept when every output carries them and absent when only
  o4 does (E838's v-a4), which no rule local to o4's word gives [infer]; of a family of 821 bitwise
  models declared before the check (OR, AND, XOR over every subset of one instance's o0 to o7, and
  MUX of bits 2:0 of one output with bits 5:3 of another), 9 reproduce the tag-5 word in all 8 kept
  configurations: OR(o0, o3), AND(o4, o6), XOR(o0, o2, o6), XOR(o3, o5, o6) and MUX(bits 2:0 of o4,
  bits 5:3 of o_i) for i = 0, 2, 3, 5, 6; no kept job changes o0, o2, o3, o5, o6 or o7, so nothing
  kept separates the nine.
  *pds; HW, infer; data: `render-closing-r3-pixel:out/20261110-160415/p-c3/`,
  `render-closing-r4-pixel:out/20261111-205726/p4-o4/`, `render-closing-r4-pixel:fold/`,
  `cited-scratch:closing5/pixel/`.*
- `E851` Offline reading of E842's kept words (Q230; no new job): the frozen analysis of g4-rw is
  decided without its 18 unread words: its rule adopts a model only at 30 of 30 FIT words, and none
  of the 225 frozen models (score/rwfam.py, five families) reproduces all 19 FIT words that were
  read (best per family a 14, b 13, c 16, d 14, e 14 of 19; HELD OUT words not touched), so no
  completion of the table can make one fit and the frozen verdict stays 'no rule adopted'; read post
  hoc over all 65 known 1/w words of kept vertices (E754, E782, E795, E796, E798, E842; 49 RZ, 16 RZ
  + 1), H-MANT, 'whether the word is RZ or RZ + 1 follows the mantissa of w alone', is consistent
  with 6 of 6 mantissas read at two or three exponents (1.0625, 1.125, 1.5, 1.59375, 1.6875, 1.75:
  none shows both), a reading made after the data, not held out; a wider declared family
  (fixed-point table plus Newton steps with truncated products, 32000 models) fits none (best 49 of
  54 distinct mantissas, 'always RZ' 42).
  *ta; HW, infer; data: `render-closing-r4-pixel:out/20261111-210423/g4-rw/`,
  `render-closing-r4-pixel:score/`, `cited-scratch:closing5/pixel/`.*
- `E852` Round 5 offline reading of the kept DPM timelines (Q210; post hoc, a FIT on one positive,
  nothing held out): in the first TA run of every kept job the high half of 0x072c (the global page
  count) steps at page counts of 0x0724 that are the same in every job of a target and scene, S_k
  being the count read before global page k appears: S2, S3, S4, S5 = 0x51, 0x9d, 0xe8, 0x132 at
  2048x2048, 0x125, 0x240, 0x35b at 4096x4096 (1350 vertices as 1500 for S2 and S3), 0x97, 0x126,
  0x1b9 at 4096x2048, 0x9a, 0x12c, 0x1be, 0x255 at 2048x4096 and 0xa9, 0x14d, 0x1ef, 0x293 at
  3072x3072 (the tool's triangle, 1500 vertices), S4 lying 6, 10, 7, 8 and 7 pages above the last
  raise of E799, E774 and E801; of the 107 kept jobs with a partial render E799's c4-b3 (thr0 0xe8 =
  S4 at 2048x2048) is the only one whose first threshold equals a step, and the only one of 495 TA
  runs with the global list grown (0x0628) before an abort; two readings of its missing raise are
  named and not decided: H-PEND (the page the TA asked for is served after the resume read the
  count, so the guard is right and our resume count one page high) and H-BLOCK (the grow leaves a
  state that prevents the raise).
  *dpm; HW, infer; data: `render-closing-r3-geo:out/g-c4/`, `render-closing-r3-geo:out/g-c5/`,
  `render-closing-r3-geo:out/g-c6/`, `render-closing-r3-geo:out/g-c7/`,
  `render-closing-r3-geo:out/g-d36/`, `render-closing-r2-geo:out/g-c3/`,
  `render-closing-r2-geo:out/g-c2/`, `render-closing-r1-pixgeo:out/g-c1/`,
  `render-closing-r1-pixgeo:out/g-c1f/`, `render-closing-r1-pixgeo:out/g-u1/`,
  `render-closing-r1-pixgeo:out/g-u2/`.*
- `E853` Round 5 offline test of R-5's guard of the firmware's raise (Q210, Q211): the guard as
  written on 2026-11-11 (closing4/p7/guard.py, imported unchanged) on the kept timelines of R3-geo-c
  that R-5 never read placed 121 of 121 decisions in g-qf (22 jobs, 88) and scene s275 (6 jobs, 33),
  held out by construction, every job one raise at its first decision and aborts after it, and the
  dword rule (dword 35 the page count at the last abort less 2, dword 36 the global page count less
  2, floor 0) in 34 of 34 jobs; the two-kick scene s438 gave 27 of 33 as run and 27 of 27 only after
  each timeline was cut at its second kick, a cut added after the 6 misses were seen (SEMI); every
  cell holds one global page, so these test the floor of dword 36 and bit 9, not the compare of two
  counts.
  *dpm; HW, RE, infer; data: `render-closing-r3-geo-c:out/g-qf/`,
  `render-closing-r3-geo-c:out/g-qh/`.*
- `E854` Round 5 offline fit of the partial-render count (Q211; a FIT, nothing held out by a frozen
  prediction): for the tool's triangle at 4096x4096 the count n at the first threshold thr0 = P -
  0x22 fits n = min{n >= 1 : thr0 + n (thr0 + 0x20 - 7/4) >= U}, the one rule left by the 4 of 2716
  members of thr0 + n (thr0 + 0x20 - d) >= U + k (d 0 to 6 in sixteenths, k -12 to 15) that fit
  E832's 22 cells at U = 287 (d 1.5625 to 1.75, k 0 or 1, the same count at every thr0 for U 287 and
  275); it gives s275's 6 cells (U 275; SEMI, their counts had been seen; 754 of the 2716 members
  give them too), E625's ten 4096x4096 cells, E779's nine and E625's 18 cells at 1024x768 (U 19),
  none used in the fit, and E625's form with an integer spacing fits none of the 22; the rule does
  not hold for the 1500-vertex scenes, whose pages taken less pages kept are not U (544 to 898 at
  2048x2048 for U = 0x213) and whose counts at 2048x2048 it gives in 11 of 17 jobs (post hoc).
  *dpm; HW, infer; data: `render-closing-r3-geo-c:out/g-qf/`, `render-closing-r3-geo-c:out/g-qh/`,
  `render-closing-r3-geo:out/g-c4/`, `render-closing-r3-geo:out/g-c5/`,
  `render-closing-r3-geo:out/g-c6/`, `render-closing-r3-geo:out/g-d36/`,
  `render-closing-r2-geo:out/g-c3/`, `render-closing-r2-geo:out/g-c2/`,
  `render-closing-r1-pixgeo:out/g-c1/`, `render-closing-r1-pixgeo:out/g-c1f/`.*

## By unit

### bif

Records: E151, E457, E573, E592, E745, E761, E767, E789, E826, E848.

### dpm

Records: E199, E200, E201, E202, E204, E205, E206, E203, E253, E256, E309, E310, E311, E312, E313,
E327, E358, E362, E438, E442, E443, E446, E447, E453, E456, E461, E463, E464, E468, E574, E591,
E625, E626, E627, E630, E631, E704, E705, E706, E734, E735, E753, E773, E774, E775, E779, E785,
E786, E790, E799, E800, E801, E802, E803, E832, E845, E846, E852, E853, E854.

### edm

Records: E009, E014, E017, E084, E146, E152, E153, E154, E155, E156, E157, E158, E159, E160, E161,
E162, E163, E164, E165, E166, E167, E013, E168, E317, E319, E320, E321, E353, E402, E431, E444,
E450, E531, E532, E533, E536, E537, E538, E539, E540, E550, E600, E601, E602, E603, E604, E605,
E746, E747, E748, E749, E750, E751, E752, E764, E768, E769, E771, E784, E791, E792, E793, E794,
E804, E805, E806, E807, E809, E810, E811, E812, E813, E814, E816, E817, E818, E819, E830, E834,
E835, E836, E839, E840, E841, E849.

### firmware

Records: E001, E002, E003, E004, E005, E010, E011, E012, E352.

### isp

Records: E064, E065, E066, E067, E068, E069, E070, E071, E072, E073, E074, E210, E211, E213, E214,
E215, E216, E217, E218, E219, E220, E222, E224, E225, E226, E227, E228, E229, E230, E209, E231,
E232, E233, E234, E235, E249, E278, E279, E281, E282, E283, E284, E285, E289, E290, E291, E330,
E332, E334, E338, E339, E340, E410, E415, E416, E417, E439, E502, E503, E504, E508, E510, E590,
E606, E607, E618, E660, E661, E662, E680, E681, E682, E683, E684, E727, E728, E731, E739, E740,
E741, E757, E758, E762, E825, E827, E829.

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
E395, E396, E400, E420, E421, E428, E430, E436, E437, E454, E459, E460, E709, E742, E759, E772,
E808, E838, E850.

### platform

Records: E006, E007, E008, E025, E026, E122, E150, E149, E246, E258, E357, E359, E365, E401, E403,
E404, E405, E434, E445, E547, E548, E619, E815, E821, E822, E823, E837.

### render

Records: E023, E049, E050, E051, E052, E053, E148, E169, E252, E301, E302, E303, E304, E314, E315,
E316, E323, E324, E325, E326, E354, E355, E356, E360, E361, E363, E408, E412, E422, E433, E435,
E448, E449, E451, E458, E462, E732, E770.

### ta

Records: E054, E055, E056, E172, E174, E175, E182, E183, E176, E177, E178, E180, E181, E247, E257,
E288, E305, E306, E307, E308, E322, E328, E329, E331, E407, E409, E424, E505, E506, E507, E509,
E511, E541, E542, E543, E544, E616, E617, E650, E651, E652, E729, E736, E754, E763, E776, E777,
E778, E780, E781, E782, E783, E788, E795, E796, E797, E798, E824, E828, E842, E847, E851.

### texture

Records: E033, E034, E035, E036, E037, E038, E039, E040, E041, E042, E114, E116, E242, E254, E271,
E273, E274, E275, E276, E277, E341, E342, E397, E399, E425, E426, E432, E441, E560, E561, E562,
E563, E564, E565, E566, E567, E568, E569, E720, E721, E722, E723, E724, E725, E726, E733, E743,
E744, E760, E765, E787, E844.

### transfer

Records: E015, E016, E018, E019, E020, E021, E022, E024, E027, E028, E272, E398, E455, E620, E766.

### tsp

Records: E236, E237.

### usse

Records: E075, E076, E077, E078, E079, E080, E081, E082, E083, E085, E086, E087, E088, E089, E090,
E091, E092, E093, E094, E095, E096, E097, E098, E099, E100, E101, E102, E103, E104, E105, E106,
E107, E108, E109, E110, E111, E112, E113, E115, E117, E118, E119, E120, E121, E123, E124, E147,
E244, E245, E255, E292, E293, E294, E295, E296, E297, E298, E350, E351, E366, E367, E368, E369,
E370, E371, E372, E373, E374, E375, E376, E377, E378, E380, E406, E423, E452, E469, E470, E471,
E472, E473, E474, E475, E476, E477, E478, E479, E480, E481, E482, E483, E484, E485, E486, E487,
E488, E491, E492, E493, E494, E495, E496, E497, E498, E499, E500, E501, E512, E513, E514, E515,
E516, E517, E518, E519, E520, E521, E522, E525, E526, E527, E528, E529, E530, E534, E535, E549,
E570, E571, E572, E593, E594, E595, E596, E597, E598, E599, E707, E708, E820, E833.

### vdm

Records: E059, E060, E184, E185, E186, E187, E189, E190, E191, E188, E299, E300, E318, E346, E349,
E413, E414, E427, E440, E545, E546, E700, E701, E702, E703, E737, E738, E755, E756.

### zls

Records: E057, E058, E250, E335, E336, E337, E411, E465, E466, E467, E489, E490, E615, E628, E629,
E663, E664, E665, E730, E831.
