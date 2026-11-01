<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### Texture sampling `smp`

*Measured on the hardware (2026-10-22).* **`smp2d d, c, s, drcN` samples the texture whose four
state words are in `s`, `s + 1`, `s + 2`, `s + 3` at the normalized coordinates in `c` and
`c + 1`, and writes the texel to `d` when the fence `drcN` is waited for** **[HW]** (probe
`texture-sampler-smp-point`). The state words are those the PDS gives
the
texture unit for our copies (`doutt`, `doc/specs/transfer.md` §4.4), built in temporaries
by the program itself:

- point sampling picks texel `floor(u × width)`, `floor(v × height)`; coordinates outside
  `[0, 1)` **clamp to the edge**; the texel arrives as stored (the raw B8G8R8A8 dword);
- `smp1d` reads `u` alone, row 0; `.flt16` takes both coordinates as halves of one register
  (`u` low); `smp2dbias`, `smp2dreplace`, `smp2dgrad` with a LOD of 0 sample the same texel;
- with `.repeat2` or a write mask the job faults at an address made of the state's fourth word,
  as if the next iteration read the state one register on **[infer]** (probe
  `texture-sampler-smp-repeat-mask`).

**Undecided:** the LOD of a quad's own derivatives, `.sinf`/`.rsd`, `.c10` coordinates, `smp3d`
beyond the point-sampled textures of E567, and state read from `sa` or `c` (only temporaries were
used); the state fields, the mip chains and the LOD values are measured in *Sampler state* and
E041, E441, E562 and E563.
