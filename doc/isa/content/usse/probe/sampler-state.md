<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### Sampler state

*Measured on the hardware (2026-10-22).* A later series varied the four state words an `smp` program
builds (T0-T3, the `doutt` words; `doc/specs/transfer.md` §4.4) on a texture in the
scratch buffer whose dwords count up, so every result names the texels it came from **[HW]**
(table `probes/texture/state-words.toml`):

- **Filtering (T0 bits 13:12, probes `texture-sampler-smp-bilinear`,
  `texture-sampler-smp-filter-modes`).** 1 and 2 are
  bilinear, 0 and 3 point. **Bilinear weights are truncated to 1/64 and each 8-bit channel is
  filtered in two stages, x on both rows and then y, each stage `(a (64 - f) + b f + 32) >> 6`**
  (E720: 8 of 8 held-out jobs on the 1/64 grid, the joint sum rounded to nearest with halves up
  0 of 8; the 21 `smp-bilinear` vectors give the same words under both forms), before any
  conversion: between texels 255 and 15 at `v + k/256` the f32 result steps every four `k`. The
  minification field does not act while magnifying (every case magnifies: the LOD forms never left
  level 0).
- **Addressing (T0 bits 8:6 U, 5:3 V; `texture-sampler-smp-address`).** A stride texture (T1 type 6,
  our copy
  sources) clamps to the edge whatever the modes say. On a twiddled texture (type 0) **0
  repeats, 1 mirrors (period twice the size), 2 clamps to the edge, 3 mirrors once** (the
  absolute coordinate, then clamped); bits 2:0 do not act on `u`. **Modes 4-7 (E565):** on the
  v axis 6 and 7 clamp and 4 and 5 repeat (held out at a pitch of one texel, E932); on the u axis
  none of clamp, nomask or border fits, and every read is the v rule's index plus 180 dwords in
  modes 4, 6 and 7 at 16 x 16 (post hoc, at three bases, E932; whatever T3 or the v mode, E957),
  116 at 8 x 8 and 308 at 32 x 32 (E957; 8 N + 52 fitted), and 308 on every pixel of E565's
  32 x 8 jobs (SEMI, E983). On held-out textures of W != H (E1000) the frozen rivals (the width,
  the height, the size as a square, the mean side) each fail a shape: 8 x 32 reads the height's
  308; post hoc every read of eleven jobs is **8 max(W, H) + 52** dwords past the index, mode 5's
  reads left and right of the texture 5 max(W, H) + 52 + t and 6 max(W, H) + 52 + t, t the texel
  row, and one dword per corner with v outside too (E983) [fitted, not held out]. No kept job
  outside those eleven parts max(W, H) from W; mode 5 with s inside and t outside reads 7 M + 52 + s
  above and 4 M + 52 + s below, not the inside offset, and the corner dwords move with the shape
  (16 to 19 at 16 x 16, 20 to 23 at 32 x 8) (E1017, held out offline against the frozen form,
  the forms post hoc). **Held out (E1026): 8 max(W, H) + 52 texels** at 32 x 64, 8 x 64 and 128 x 32
  in modes 4, 6 and 7 and on a u16 texture (texels, not dwords), and with u and v in mode 5 the
  side, above and below reads follow max(W, H) too; the corner base is 24 at 64 x 16 and 16 x 64, no
  frozen form (post hoc 4 log2 max(W, H)); a strided texture reads modes 4 to 7 as mode 0 (E565).
  Why, the corner base and types 1, 3 and 4 are open (Q177).
- **Twiddled layout (`texture-sampler-smp-twiddled`).** Texel `(x, y)` lies at the Morton index with
  **`y` in
  bit 0, `x` in bit 1**, and so on; a non-square texture puts the longer side's extra bits
  above (16 × 16, 8 × 8, 16 × 4 and 4 × 16 tried). **Above 16 on a side the texture is tiles
  (E561, 32-bit texels, sizes 8 to 128 on a side):** each tile of up to 16 × 16 texels is
  interleaved as above and the tiles follow in raster order, `x` first; 32-bit texels of 14
  sizes were run, and other sizes and texel sizes were not. The mip chain of a non-square
  texture halves both sides down to 1 × 1 and the T0 fields read it as a square chain (E562).
- **Formats (T1 bits 28:24, no conversion; `texture-sampler-smp-formats`).** 0 and 1 return the byte
  (`s8`
  not extended), 7-11 the half, 12, 15-18, 22 and 31 the dword; **2, 3, 4 and 5
  (`4444`, `8332`, `1555`, `565`) expand to B8G8R8A8 by repeating each field's bits**, alpha
  `0xff` when the format has none; 13 swaps red and blue (R8G8B8A8), 19 clears the sign bit,
  21 the top byte, 30 sets it. 6, 14, 20 and 23-29 (signed, 10-bit, compressed or YUV
  layouts) are recorded (`texture-sampler-smp-formats-other`); 14 writes two registers. **28 and
  29 (YUV) read opaque black** in a fill with the colour-space set not loaded, and the poke of the
  fill's transfer command did not load it (E568, Q181); E037 gives the conversion with the set
  loaded in a copy.
- **Conversion (T3 bits 17:16, normalization bit 15; `texture-sampler-smp-convert`).** 1 gives
  **c10**: the
  B, G, R channels in the 10-bit fields of the first register (the 8-bit value unscaled,
  1.0 = 255 as `.c10` operands read it) and A in the second; 2 gives **f16** pairs R, G then
  B, A (alpha 1.0 when the format has none); 3 gives **f32** B, G, R, A, one register each.
  Values are the integers (0-255, 0-65535) unless bit 15 is set, which divides by 255 (by
  65535 for `u16`). T3 26:23 changes no `smp` result (fetch spacing). **Without alpha
  (565) c10 and f32 leave its register unwritten** (c10 one register, f32 three) and f16 gives
  1.0 even unnormalized. **The other formats convert their channels** (cases 24-47): format 0
  is one u8 channel, 7 two (the low byte first), 9 one u16; c10 puts channel k in the k-th
  10-bit field of one register (a u16 as its top byte: `0xd000` gives `0xd0`), f16 packs the
  channels in pairs (low half first: format 7's `0x0451` gives `h(81) | h(4) << 16`), f32 gives
  one register per channel.
- **PCF (`texture-sampler-smp-pcf`).** `smp2d.pcf` compares **texel OP reference**, the reference
  being the
  f32 in the register after the coordinates (`.pcff16`: the f16 in its low half, full precision
  and signed, E116), by T3 bits 31:29
  (0 never, 1 `<`, 2 `==`, 3 `<=`, 4 `>`, 5 `>=`, 6 `!=`, 7 always), and returns 1.0 for an f32
  texture (format 18) or `0xffff` for `u16` (format 9, compared as texel / 65535) when it
  holds, else 0; with bilinear filtering the four results are averaged (`0x8000` for one of two
  texels at half weight, the only split measured). A colour format ignores `.pcf`.
- **Other state bits (exploration `x-smp2`, E566, E564).** In `smp` T3 bits 3:0 and 7:4 are the
  row and column offsets at every value tried (E566). Bits 8, 9, 20, 21 and 22 change nothing on a
  strided texture, nor do 11 and 12, but on a twiddled chain texture bits 11 and 12 change every
  pixel (E564): bit 11 cleared reads level 0's texel (x, y) and bit 12 set the 1 x 1 level, at
  one LOD on one chain (post hoc). **Held out with smp2dreplace (E1027): bits 12:11 pick the level
  whatever the LOD: 00 level 0, 01 the LOD's level, 11 and 10 the last level T0's max level allows**
  (not a LOD bias, not a constant address). Bits 10, 14, 18, 27 and 28 offset the texel by an amount
  that changes with the
  pixel position, and bit 13 faults the job. Setting T0 bits 30 or 31 reads other values: they
  act, how is not known.
- **The address bits (E722, 13 of 16 held-out fills; the other 3 faulted past the probe's
  scratch, E743, E787).** **T3 bits 28:27 pick a level L and bits 19:18 a scale e: the texel is
  read at base + ((off + idx) << e) dwords**, off the sum over k < L of max(1, w >> k) max(1,
  h >> k) (the level sizes, not the stride times the height) and idx the tile-law index of (X >>
  L, Y >> L), or X >> L + stride (Y >> L) on a strided texture; **bit 10 reads the base dword**;
  the offset bits 7:0 act before. Run on twiddled textures up to 64 x 64 and strided 128 x 32, a
  32-bit format only; the scale shifts the dword address, not the index alone (3 jobs). Bits 11
  and 12 select the level (above, E1027). **Bit 14 shears a strided read** (E968): at a width equal
  to the
  stride (64) the dword plus 32 plus 64 per column, held out offline on a second job; at width 32,
  stride 64 the six frozen forms fail, and post hoc dword + floor(S * S * u), u clamped to [0, 1],
  fits all three strided jobs; on a twiddled texture it faulted (E566). **It moves the read by
  floor(4096 clamp(u, 0, 1)) texels** (E975 post hoc in dwords on 32-bit texels; E1003 held out
  on six strided geometries: strides 16 and 256, u off the grid and past both ends, v varying, and
  a 16-bit format, where it is texels, not dwords, 6 of 6; sgx-sim models it point sampled at
  formats 9 and 12); under a bilinear sample it moves the whole footprint by that count, u the
  sample's coordinate (E1027, one row); on a twiddled texture it is open (Q078).
- **sRGB (T0 bit 27; E723).** **A point-sampled texel byte is decoded sRGB to half float** (4 of
  4 held-out fills exact over 2048 pixels: strided 8 x 4, twiddled 8 x 8 twice, twiddled 32 x
  32). Under bilinear filtering neither declared order fits (filter then decode 0 of 2048 pixels,
  decode then filter 1147 and 876 of 2048, 2 held-out fills). **Each lerp stage floors both
  halves to the larger one's ulp, lerps exactly and rounds to nearest with ties up** (weight
  0 returns the first half unchanged), x then y: fitted on single stages and held out offline on
  three two-stage fills, every pixel, with weights on the 1/64 grid (E982); a later held-out row
  missed it where a stage result is subnormal (E1004), and **a stage result below 2^-14 is
  flushed to +0**: held out offline on an-t0b27's 12 halves that part it, one pixel column
  (E1016), **the y stage's own result included** (E1025: held out on five strided rows, every 1/64
  weight of each stage alone and both together; the threshold between 5.69e-5 and 6.16e-5, the
  smallest normal half [infer]). A trilinear sample's level lerp is not that stage rule (E1025, one
  row; post hoc the exact lerp of the levels' halves rounded ties up fits 4091 of 4096 halves); it
  and bytes 2 and 3 are open (Q282).
- **ETC1 (format 27; E724).** **Format 27 is ETC1 with the 4 x 4 blocks in Morton order, y in the
  low bit** (6 of 6 held-out fills of random valid blocks exact over 2048 pixels, 8 x 8 to 32 x
  16; raster block order and Morton with x low 0 of 6). Formats 23 to 26 are not decoded.
- **Texture types (E725, E726, E910, E940, E941, E958).** **Types 3 and 1 are read as a raster, the
  window wrapping at the texture's size** (8 of 8 held-out fills exact, 8 x 8 to 32 x 32; E567's
  fixed 16 refuted, 0 of 8; held out again at 64 x 8 and 128 x 8, E910). **Type 1's rows are the
  width apart, type 3's max(8, w) texels**: type 3 at 1, 2 and 4 wide pads a row to 8 texels (5 of
  5 held out at format 12, where a texel is a dword, E940, after E910's one row at 4 x 16; at
  format 5, 16 bits a texel, the low half of a dword first, rows of 8 texels, not 8 dwords: 2 of
  2, E958), type 1 at 1, 2 and 4 wide does not (E910, E940); at 24 and 40 wide the rows of type 3
  and of type 1 are the width apart, not a power of two above it (E940, E958, 2 of 2 each).
  **Type 4 stores 32 x 32 blocks of 1024 dwords, raster inside a block, the blocks row by row**:
  texel (X, Y) is dword ((Y div 32) ceil(w / 32) + (X div 32)) 1024 + (Y mod 32) 32 + (X mod 32)
  (18 of 18 held-out windows of 64 x 64 to 128 x 128 and 256 x 32, E941; read post hoc at
  64 and 128 wide by E910); up to 32 wide that is E725's stride of 32. At widths that are not
  multiples of 32 a block row keeps ceil(w / 32) whole blocks (7 of 7 held-out windows of 48 x
  64, 80 x 64 and 96 x 32, E958; the power of two above the width and a partial block refuted).
  **Type 2 is a cube map: six 16 x 16 faces consecutive at 256 dwords a face, read for
  +x, -x, +y, -y, +z, -z as faces 0 to 5** (each axis direction reads one face over 2048 of 2048
  pixels, E726). **The face is that of the coordinate of largest magnitude, with its sign**: E726's
  post hoc rule held out on two off-axis programs whose dominant axis changes inside the image,
  2048 of 2048 pixels each, all six faces between them (E844). **In a face, (s, t) is the public
  cube-map table** (+x s = -w, t = -v; -x s = +w, t = -v; +y s = +u, t = +w; -y s = +u, t = -w;
  +z s = +u, t = -v; -z s = -u, t = -v; over |ma|, texel floor((q + 1) / 2 * 16), Morton with t
  in bit 0), fitted on E726 and held out on E844's jobs at 4090 of 4096 pixels, the misses exact
  texel boundaries at a |ma| not a power of two (E923); held out on hardware on four new 16 x 16
  programs and at 8 x 8 faces (the rule with 8 for 16, faces 64 dwords apart); 32 x 32 faces read
  the fifth bits of s and t in the other order (post hoc, E930), which is E561's twiddle law, tiles
  of 16 x 16 in raster order with s first (E951), held out at 32 x 32 and 64 x 64 faces, and 4 x 4
  faces sit 16 dwords apart (E955). A face tie reads the higher axis's face on every sweep run (z
  over y over x, E931, E956) but not on 7 of 599 kept tie pixels with a large third coordinate; a
  tie of two bit-identical fmad ramps with x the lower axis reads +x on 58 of 64 columns (E1001,
  three rows of six; constant ties and ties of y and z read the higher axis, 9 of 12 rows), and
  bilinear at a face edge mixes in a texel of the neighbour face near the adjacent one (E931, E956),
  the neighbour face's bilinear at the outer tap centre's direction on -y/+x and not on +z/+x
  (E1002).
  The ties, texel boundaries and face edges: Q284.
  **Type 5 reads one bit per 8 texels**: with format 12 texel t = (Y mod h) w + (X mod w)
  returns `0x0000ffff` iff bit 0 of texture dword floor(t / 8) is set, else 0 (E942: 13 of 13
  held-out rows with stored dwords that part it from bit 1 of dword floor(t / 4), and 8 of 8 rows
  where the two agree; E911's memory rows and size steps, E894's 16-column step, are this rule
  on the map fill). With format 9 one row read bit 0 of 16-bit word floor(t / 8), and format 18
  and the bilinear filter gave the format 12 point images (post hoc, one row each, E942).

*Simulator check, 2026-10-23.* The simulator's texture unit
(`crates/sgx-sim`, `tex.rs`) follows this page and *Texture sampling*; it reproduces every
recorded sampling vector it models and stops on the rest: the LOD values, the bits above, the
recorded formats and modes, tiled textures, and filtered `.pcf` at other weights. After the
11.32 tables it also takes the tile law of E561 on 32-bit texels in the sizes run, non-square
chains in the five sizes run, `smp3d` as `smp2d` where it ran, and the YUV formats as black only
for a job that records the colour-space set as unloaded.

**Undecided:** why type 3 pads to 8 texels and the other 16-bit and 8-bit formats on types 1, 3
and 4 (E958 ran format 5 on type 3), type 5 with other formats, the LOD fraction's residual
(Q280), the border modes on the u axis, formats 23 to 26 and the YUV conversion in a fill,
sRGB under bilinear filtering beyond E982's rule (Q282), the cube
map's edges and (s, t) within a face (Q284), `smp3d`
beyond the textures it ran on, `.sinf`/`.rsd`, and state from `sa` or `c`.
