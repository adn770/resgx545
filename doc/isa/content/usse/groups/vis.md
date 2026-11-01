<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### Visibility tests: `pcoeff`, `ptoff`, `atst8`, `depthf`

Class 31 with `enc[53:52]` = 3 **[RE]**: operation 0 is `pcoeff` or `ptoff` (by `enc[47]`), 1
`atst8`, 3 `depthf`. `atst8` writes a destination and a predicate `p0`-`p3` (or not, `!`),
with `.c10`; `atst8` and `depthf` test three sources with `twosided` and a feedback mode
(`fb`, `nfb`, `optdwd`) and take a two-bit predicate.

- **`ptoff`** signals the end of the punch-through phase for the pixels of the task
  **[infer]**: our 3D render's PTOFF task is the single instruction `ptoff.end`, and renders
  run with it **[HW]**.
- **`atst8 dst, [!]pN, src0, src1, src2[, twosided], mode`** is an alpha test **[HW]**
  (table `probes/usse/alpha-test.toml`, measured 2026-10-27 in a
  fill's pixel task, E083): it compares src0's top byte (bits 31:24, the alpha) with src2's top
  byte (the reference) by the function in src2 bits 15:13, numbered as the ISP's compares (0
  never, 1 less, 2 equal, 3 lequal, 4 greater, 5 notequal, 6 gequal, 7 always; `alpha FUNC
  reference`, every function checked just below, at and above the reference). On a pass it
  writes src0 to the destination and makes the predicate true; on a fail it leaves the
  destination and makes the predicate false. `!pN` does not write the predicate. No other bit
  of src2 changed the result from ~0 down, src1 (0 or ~0) changes nothing, and in a fill
  `fb`, `nfb`, `optdwd` and `twosided` give the same result: what the feedback does reaches
  only a punch-through pass. A discard shader ends its `pt` phase with an `atst8` in feedback
  mode whose third source holds the compare function and the reference.
- **`depthf`** (depth feedback) and **`pcoeff`** (plane coefficients) **[HW]**. In a fill's
  pixel task neither does anything seen (`usse-alpha-test-pcoeff-depthf`): what they do, like
  `atst8`'s feedback, reaches only a punch-through pass.
- **Punch-through feedback [HW]** (E083): in a punch-through
  pass a pixel is kept only if its `pt` phase runs `atst8 ... fb` or `depthf src0, src1,
  src2, fb` with a control word in src1 that has bits 0 and 14 set (either bit
  clear discards the pixel, bit 2 or 3 set makes its depth win as if the test were always;
  the glossary's `FEEDBACK_CTL` rows);
  a failing alpha test, `nfb` or no feedback discards it and the object behind shows. The
  kept pixels' depth is resolved by the ISP the same every run only with `pcoeff pa2, pa3,
  sa4` fed by iteration source 34 (`DOUTI0.ATTR_SOURCE` 34): `pcoeff` hands the ISP the
  depth plane its feedback test uses; its third source changed nothing seen.
  `atst8` must not directly follow `pcoeff`: with no instruction between, the object is not
  drawn at all **[HW]**.
- **The stencil in a punch-through pass [HW]**: the pass neither tests the
  ISP stencil (all eight compares draw alike) nor writes it (a later opaque object testing
  for the reference finds nothing), with `fb`, `optdwd` and each with `twosided`. What
  `twosided` and `optdwd` change is **[open]**.
- **`depthf src0, src1, src2, fb` [HW]**: src0 is the pixel's depth, which
  replaces the iterated one in the depth test and the depth written (1.0 fails a less test
  against the background's 1.0; 0.5 - z reverses the copies' order), in pass 4 and 5 alike.
- **In the firmware:** not used.

<!-- @prog use_ptoff.s -->

<!-- @example usse ptoff.end -->

<!-- @group usse class=31 pat='pcoeff|ptoff|atst8|depthf' -->
