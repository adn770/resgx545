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
  the mip level, with `grad` from the larger derivative (E041); `.sinf` returns the level and
  the blend fraction instead of a texel, and `.rsd` the 2x2 texels per level that a filtered
  sample blends (E042). Our copy path does not use it: the PDS issues the texture fetch
  (`doutt`) and the result arrives in `pa0` before the task starts (`doc/specs/transfer.md`
  §4.4.3) **[HW]**.
- **In the firmware:** not used.
- **The sampler cache [HW]** (E114). The sampler keeps what it fetched, in lines that hold at
  least two neighbouring texels: once a texel is sampled, a USSE store to it or beside it is
  not seen by later samples in the job, whatever fence or cache operation comes between. A
  texel not yet fetched shows the store.

<!-- @example usse smp2d r0, r4, c0, drc0 -->

<!-- @group usse class=28 -->
