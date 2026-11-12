<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### Synchronisation and misc: `nop`, `wdf`, `idf`, `setm`, `wop`, `lock`, `release`

Class 31 **[RE]**: `nop` is flow-control operation 5; the rest are the "other" group
(`enc[53:52]` = 2) with the operation in `enc[58:56]`: 0 `idf`, 1 `wdf`, 2 `setm`, 5
`lock`/`release` (by `enc[0]`, a three-bit mutex number), 7 `wop`.

- **`nop`** does nothing **[infer]**; with `.end` it ends the program **[HW]** (our USE
  secondary program). `.tog` and `.trigger` are **[open]**.
- **`wdf drcN`** waits for the loads counted on `drcN` **[RE/HW]**, all of them whatever their form,
  up to 192 distinct `ldad` seen (E518 read 4 or 5 reloaded registers per job), and not for those of
  another counter (E478, E518, E479); with nothing outstanding it returns at once (E480). **`idf
  drcN, bif`** is a fence on memory writes counted the same way **[infer]**, which no fill case
  needed (*Memory, data fences and the register file*). **`idf drcN, pixelbe`** hangs a fill,
  waiting for something a fill never gives (the pixel back end?) **[HW]** (E114).
- **`wop #n`** waits for the outputs to drain before an emit **[infer]**: our state programs
  issue `wop #0` between `emitvcbst` and `emitmtest`, as the captured ones do **[CAP/HW]**.
  `.twopart` is **[open]**.
- **`lock #n` / `release #n`** take and give back one of eight mutexes **[HW]** (table
  `probes/usse/quad-lock.toml`,
  measured 2026-10-27): every pixel
  instance of a 64x32 fill adding 1 to one scratch dword ends at 44 without a mutex (lost
  updates), and at exactly 512 inside `lock #0` ... `release #0` or `lock #3` ...
  `release #3`, each of the 512 values seen by the four pixels of one aligned 2 x 2 quad: the
  mutex serialises quads, in no screen order, and the four instances of a quad load and store
  together. A `lock` never released hangs the job, the next quad waiting for it. A second
  `lock` of a mutex the quad still holds blocks the quad itself: with `lock #0` twice the fill hung
  with no update stored, whether one or two `release #0` followed; `lock #0` then `lock #1` does
  not hang (E921) **[HW]**. The firmware executes `lock` twice and never `release` (R-6 reads
  the two as `lock #0`, on the EDM's lockup path); that the EDM blocks at its second `lock` as a
  pixel program does is **[infer]**, and whether something else releases its mutex is **[open]**.
- **`setm #n`** (a four-bit number): `#0`, `#1`, `#2`, `#4`, `#8` and `#15` before a locked update
  leave it as without (E088),
  mask no pixel of a fill and none of a single-sample triangle (E099), and no sample at 4x under
  any `phas` rate, nor once any task or render word tried enables per-sample shading, which
  none did (E103, E115, E117) **[HW]**; the closed compiler never emits it **[CAP]**. What it
  sets is **[open]**.

**In the firmware [RE].** 807 `wdf` (711 on `drc0`), 124 `idf ..., bif`, 87 `nop` (5 with
`.end`, 1 with `.nosched`), 2 `lock`.

<!-- @prog use_mtest18.s match='wdf|wop|nop' -->

<!-- @example usse idf drc1, bif -->

<!-- @group usse class=31 pat='^(nop|idf|wdf|setm|wop)|^\{0\}\{1\} #\{2\}$' -->
