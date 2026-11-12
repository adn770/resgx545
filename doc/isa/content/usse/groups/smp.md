<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### Texture sampling: `smp1d`, `smp2d`, `smp3d`

Class 28 **[RE]**: the dimension (`1d`, `2d`, `3d`, `enc[43:42]`) and a LOD mode (none,
`bias`, `replace`, `grad`, `enc[41:40]`; `3d` with a LOD mode does not decode); flags
`.skipinv`, `.syncs`, `.nosched`, the PCF mode (`.pcf`, `.pcff16`) and the SRD mode (`.sinf`,
`.rsd`); a destination `r` or `pa` with a two-bit write mask or a repeat count; the
coordinates as a source-0 operand with a format (`.flt16`, `.c10`); the texture state as a
source-1 operand; the LOD value as source 2 when a LOD mode is set; a data fence `drc0`-`drc3`.

- **Semantics [HW].** Source 1 holds the four texture state words (`s` to `s + 3`, the `doutt`
  words of our copies), source 0 the normalized coordinates (`c`, `c + 1`; `.flt16`: two halves
  of one register); the texel arrives in the destination once `drcN` is waited for. Point
  sampling clamps to the edge (*Texture sampling*); filters, address modes, formats, conversions
  and `.pcf` follow the state words (*Sampler state*). **[HW]** A LOD mode's source 2 selects
  the mip level, with `grad` from the logarithm of a footprint of the four derivatives (E041): the
  largest component fits where only `dudx` and `dvdx` are set and the Euclidean length where all
  four are, on the cases run, neither on the rest (E563); held out with independent operands
  the footprint is the larger of the two Euclidean lengths and the fraction of the LOD in 1/64 is
  truncated (E721; the residual pixels and the quad's own derivatives are Q280); a non-square
  twiddled chain halves both sides down to 1x1 (E562); `.sinf` returns the level and the blend
  fraction instead of a texel, and `.rsd` the 2x2 texels per level that a filtered sample blends
  (E042). Our copy path does not use it: the PDS issues the texture fetch (`doutt`) and the result
  arrives in `pa0` before the task starts (`doc/specs/transfer.md`
  §4.4.3) **[HW]**.
- **`smp3d` without a LOD mode [HW]** (E567, in a fill of our own): on TEXTYPE 0, 6 and 7, point
  sampled, a 16x16 twiddled texture and a 64x32 stride one, the third coordinate is not read and
  the texel is the `smp2d` one (8 of 8 jobs, 3 sweeps, `rt7` at two values); on TEXTYPE 2 it
  changes the image (three images for `smp2d`, 0.5 and 1.5): type 2 is the cube layout, its face
  chosen by the dominant coordinate (E725, E726, E844). The
  simulator reads `smp3d` as `smp2d` on the first and stops on every other state.
- **In the firmware:** not used.
- **The sampler cache [HW]** (E114). The sampler keeps what it fetched, in lines that hold at
  least two neighbouring texels: once a texel is sampled, a USSE store to it or beside it is
  not seen by later samples in the job, whatever fence or cache operation comes between. A
  texel not yet fetched shows the store.

<!-- @example usse smp2d r0, r4, c0, drc0 -->

<!-- @group usse class=28 -->
