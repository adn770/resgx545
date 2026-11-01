# Phase 11.32 (draft) laptop batch: the texture unit and sampler

Scratch, gitignored, written without laptop access. Nothing staged or committed, nothing written
under `~/src/resgx545` (landed at d994a37, read only), `tools/rewrite/`, the git index or any
other p11xx directory. Questions: Q104, Q078, Q050 (smp mipmaps and LOD, border modes, compressed
and YUV formats), Q115, Q113, Q114, Q021, and one proposed new question, N1 (the twiddle law above
16 texels, section 1). The direction is hardware facts a simulator needs: which texel, which
level, which LOD a sample reads, so that `crates/sgx-sim/src/tex.rs` can stop on fewer vectors and
every result becomes a vector of 2048 samples a job.

## 0. What is here

- `plan.md`: this plan.
- `templates/tx_map.s`: the one program, three inputs (PRE, SETUP, SMP), section 3.
- `gen/catalog.py`, `gen/build.py`, `gen/gen_p1132.py`, `gen/shell.py`: the cases, the program
  text, the writer of everything below, the scripts' text.
- `probes/texture/tx-*.toml`: the landed table form (host fill, `coords`, `pixels`), 18 tables.
- `stage-p1132.sh`, `stage-bins/`: Mac side, regenerate, check the hashes, copy to the laptop.
- Safe scripts: `tx-gate.sh`, `tx-twiddle.sh`, `tx-shapes.sh`, `tx-fields.sh`, `tx-lod.sh`,
  `tx-border.sh`, `tx-t3.sh`, `tx-types.sh`, `tx-formats.sh`, `tx-douti4.sh`.
- Risky, last, a health check after every job: `tx-t3-risky.sh`, `tx-types-risky.sh`.
- `gen_p1132.py --follow TAG T0 T1 T3`: the second step of Q113 and Q114 (section 4.7).
- `run-all-1132.sh`: the order of section 8.
- `declared.tsv`, `predictions-declared.tsv`, `gen/specs.json`: every case with its set, the
  predictions, every case's spec.
- `recompute/recompute_p1132.py`, `recompute/texmodel.py`: the recomputation and the sampler
  model.
- `validate/` (`mockrun.sh`, `fakehw.py`, `selftest.py`): the validation without the laptop.
- `simtree/`: a copy of the simulator with `examples/texpred.rs` and the E276 patch.
- `tool-tests/`: three tests of what the scripts assume of the tool, none failing (section 7).

Totals: 456 jobs, 428 fills and 28 triangle jobs (Q021), the two risky scripts 20 of them. A fill
job takes a few seconds; about 1 hour with the health checks. Every script keeps the whole raw
output of every job, gzip, with its raw sha256 printed (as p1126 did), standard error apart, the
case table beside the dumps and the kernel log of the run (`journalctl -k`) gzipped.

## 1. What the landed records give, read again, and what they cannot give

- Method of every job: a fill (`probe --coords --pixels`, 2048 pixels, pa0 = (y << 16) | x) whose
  pixel shader builds each pixel's own coordinates from pa0 and does one `smp`. The scratch buffer
  is the texture: dword i holds `0xD0000000 | i` (E441), so the value read names the dword. One
  job is 2048 samples; the vectors (doc/specs/vectors.md section 4) compare every pixel.
- E441: level = min(round_half_up(LOD), maximum, last) on a square chain of eight levels,
  MIPFILTER blends the two levels. The texel read in levels 0 to 2 of that chain is not where
  plain twiddling puts it: (84, 28) reads the dword of (20, 108), (42, 14) that of (10, 46), (21,
  7) that of (5, 23). The decoded x lost its top bit and y gained one; indices 0x2370 against
  0x1670 at level 0. That stays "not run" in E441 and is the N1 question here (the indices are my
  computation from E441's coordinates, plain Morton of each). Plain Morton is measured at 16x16,
  8x8, 16x4, 4x16 only (E035, doc/specs/usse_isa.md 7.37).
- E276 (all 64 bias values, all 16 maxima on a 16x16 chain of five levels) and E441: bits 20:17
  are a maximum level (0 and 15 read level 0), 26:21 a LOD bias in eighths. The simulator does not
  model this yet: `tex.rs` `pick()` reads bit 18 as "no mipmaps" (E041) and 20:19 as the chain
  switch. Read against the landed tree: `g3-tw16-lod2` (T0 `0x07fc0000`, LOD 2) reads level 0 in
  the simulator and level 2 on the hardware. `simtree/tex-e276.patch` is the update (section 6);
  the 11.32 programs that read a chain only agree with the simulator after it.
- E033: modes 4 to 7 on a 16x16 twiddled texture at one position (u = 17.5, v = 0.5 texel) read
  the dwords 0xb6, 0x94, 0x15e, 0x15e of the texture's own 256: (13, 6), (12, 2) and two past the
  end; not a clamp, repeat or mirror. Recorded, not explained. E274: the T3 bits in a copy, once
  each.
- E342 lists TEXFORMAT 25, 26 and 27 twice (alpha, luminance, luminance-alpha and, further down,
  PVRTC and ETC1); the formats group below does not assume which. E037, E040: formats 28 and 29
  through colour-space set 0 are opaque black when the set is not loaded (and smp of the names
  gave `0xff000000` at all four texels of `texture-sampler-smp-formats-other`).
- r1126 and r1127 faults avoided by construction (checklist, section 10): the hypotheses are named
  in code and the plan text is the code's; every case lists its set; the scripts print a health
  line on success; the kernel log is kept per script; standard error is kept apart (an F7 fault: a
  tool message was mixed into the last row of each dump); no claim that a job could not show.
- N1 is a proposed question, not a record: where texel (x, y) of a twiddled texture of 32 or more
  texels lies, as an index, at the sizes the records did not run. It comes from E441's remark, and
  the number is left to the fold.

## 2. Declared before any run: sets, hypotheses, predictions

Declared files (sha256 of the file as written by `gen/gen_p1132.py`; `stage-p1132.sh` refuses to
run if they change): `declared.tsv`
`9395f6ddd2371127c9439a1f72f42838e6913918a7af86888a430248ebff7b2a`, `predictions-declared.tsv`
`4ee35db3dbd9dca6273e6329de54d077dcb750d9a93620f7903bbfedc5484beb`. A prediction is the sha256 of
the 2048 pixels (8 hex digits each, comma joined, raster order) that `recompute/texmodel.py`
renders for one named hypothesis; the scripts print the same digest of what they read. Sets: fit:
the cases on which a rule may be chosen after the run; heldout: cases whose predictions (one per
declared hypothesis) are written first and never used to choose; control: the cases whose result
the records already give; explore: no prediction is a test, the output is a table. A repeated case
counts as fit (r1127 F3). The model shares no code with the program builder (`gen/build.py`); the
simulator agrees with both: 141 of the 428 programs run on it, 0 pixels differ from the model
(`out/check4.txt`), the rest are what the simulator stops on.

Hypotheses are the names of `texmodel.RULES`; "fit" and "held out" are sets of jobs. No prediction
is declared for the names maps and block jobs of the formats and for the risky TEXTYPE jobs (no
model of them exists): their dumps are tables.

- shapes, fields (Q104): `chain=A` (both sides halve to 1), `B` (the chain stops when the short
  side is 1), `D` (A with square-padded offsets). Fit: 32x16 (8 LODs, 22 field jobs). Held out:
  128x16, 16x32, 64x4, 8x64 (49 jobs) and the 128x16 field jobs (22).
- twiddle (N1): plain Morton at every size. Fit: 32x32, 64x32, 64x16. Held out: 64x64, 128x16,
  128x32, 32x128, 128x128, 16x64, 8x128.
- lod-grad, lod-auto (Q050): `lodf=max4`, `euc`, `min`, `pwl_max4`, `pwl_euc`. Fit: diagonal, x
  and y, swapped and one-vector gradients (k = 0 to 5 and 2); automatic LOD at equal footprints
  and one vector. Held out: off-diagonal, signed and all-four gradients, k = 4; automatic LOD at
  unequal footprints, rotated, with a bias.
- anisotropy (Q115): the same formulas, one bilinear level. Fit: five ratios 2 to 32. The 14 bit
  flips are exploration.
- border (Q050): modes 0 to 3 as E033 (control); for 4 to 7 `mode47=clamp`, `nomask`, `border`.
  Held out: another base address, a 32x8 texture, a strided texture.
- t3 (Q078): `t3off=pre` or `post`, `t3rows=after` or `fixed`. Fit: strided 64x32 (22 flips, 46
  values). Held out: strided 64x16 and 32x32, twiddled 32x32 (16 flips) and 24 values.
- types (Q113, Q114): `w3d=ignore`. Fit: TEXTYPE 0 and 6 under smp3d. The rest is exploration.
- formats (Q050): the YUV conversion of E037. Fit: pattern 0. Pattern 1 and every block job are
  exploration.

Why these sets can fail (r1127 F2, F7: a test that cannot show the thing is not one). Each case
lists under `out/discrimination.tsv` how many of its hypotheses predict different images; a
control case on which every hypothesis agrees is a control, not a test of the hypotheses. Where
the fit set could not tell two hypotheses apart, the case that does is moved into it: `gr-vx-k2`
and `au-vx` make max4 and Euclid differ (the diagonal and x-and-y cases give them the same
footprint), so the held-out off-diagonal cases test the choice and do not make it. The shapes'
32x32 control gives A, B and D the same prediction on purpose (a square chain); the 32x16 cases
separate B from A at LOD 5 and D from the others at LOD 1.

## 3. The program and the jobs

`tx_map.s`: `and`/`shr` of pa0 give x and y; for a "map" rule u = 1 + (2 X' + 1) / 2^(a + 1) with
X' = (x | X0) and (2^a - 1), exact in single precision, so a repeat-mode texture reads texel X' at
pixel x; for a "lin" rule u = (1 + x / 64) K + C by `fmad`, so a sweep of coordinates (borders,
gradients, the third coordinate) needs no integer-to-float instruction. The state words go in r20
to r23 (T2 is `0x5CAF0000` + the texture's byte offset, which the tool patches), the LOD, the
gradients or the third coordinate in r26 to r29. PRE writes block data with `stad` for the formats
and waits (`idf`, `wdf`: E114, a texel not yet fetched shows the store). Every program is at most
256 words and needs 16 pages: the simulator's and the converter's fixed 64 KiB scratch (section
6).

Fallback if the gate fails (section 8): the hosts differ only in where pa0 comes from. The tri
host (`probe --tri pixpds:12`, E437's PDS program: pa0 = x + 0.5, pa1 = y + 0.5, as bg_reload_*.s)
runs the same shader with a `fmad` on pa0 and pa1 in place of the integer rule; its readback is
the scene's and does not become a vector (doc/specs/vectors.md section 3). Not built here.

## 4. Per question: open, experiment, cases, outcomes

### 4.1 Q104: mip chains of other shapes (`tx-shapes.sh` 64 jobs, `tx-fields.sh` 44)

Open: how many levels, where each lies, and whether the T0 fields read a non-square chain as the
square ones. Experiment: T0 `0x07fc0000` (maximum 14, point filters), smp2dreplace at a whole LOD
for every level and one or two past the end, the window the whole of level 0 (two jobs at 128 wide
or 64 high, `-x64`, `-y32` in the names). Cases: 32x16 (LOD 0 to 7), 128x16 (0 to 8), 16x32 (0 to
6), 64x4 (0 to 7), 8x64 (0 to 7), 32x32 as the square control. Kept: all 64 outputs; D2 prints per
shape and LOD the dwords read (first, last, count) against level base and size under A, B and D.
Outcomes. A exact on 32x16 and on the 49 held-out jobs: 1x1 is the last level on both sides, the
levels follow at `sum of max(1, w >> l) * max(1, h >> l)`, `tex.rs`'s `last` is log2 of the longer
side and its offsets are the sum of the level sizes (E441's rule for squares). B exact: the chain
ends at the short side's 1; LOD above that clamps at 2x1 (32x16: level 4 at 680). D exact: levels
are as big as the square of the longer side. None exact: D2's base and size per level is the
table. `tx-fields`: max (8 values), bias (7) and MIPFILTER (7 fractions) at 32x16 and 128x16 under
the same three hypotheses; exact under the shape's winning hypothesis means the fields read it as
the square chains; the first LOD at which a job leaves it says what differs.

### 4.2 N1: the twiddle law at size (`tx-twiddle.sh` 28 jobs)

Open: E441's top bit. Experiment: the identity map of level 0, replace LOD 0, 16x16 (control),
then 32x32, 64x32, 64x16 (fit), 64x64, 128x16, 128x32, 32x128, 128x128, 16x64, 8x128 (held out),
in windows of 64 by 32 texels (up to 8 jobs a size); each pixel names the dword of its texel.
Outcomes. Plain Morton exact everywhere: E441's levels 0 to 2 anomaly was something else (the
24-page buffer, the position) and the model of `morton()` stands; D1 prints "plain Morton
throughout". A size where it fails: D1 fits each index bit as an exclusive or of coordinate bits
(a GF(2) system, solved on the texels read) and prints the dependencies: that is the new
`morton()`; a size that is not affine in the bits is a table (print it from the dumps). The fit
sizes are those on which a law may be adjusted; the seven held-out sizes test it.

### 4.3 Q050: LOD of gradients, of the quad, a bias (`tx-lod.sh`, 45 jobs of its 66)

Open: the function log2 and the footprint (E041: `smp2dgrad`, du/dx against dv/dy at powers of
two, without off-diagonal terms; the quad's own LOD is `Lod::Open`). Experiment: a chain of 64x64
(7 levels), MIPFILTER set, point filters, so every pixel's value is the blend of two named levels
by the LOD's fraction in 1/64 (E441). Each pixel's gradient is (1 + x / 64) 2^(k - 6) (or y / 32),
so a job sweeps a LOD in [k, k + 1) in 64 steps, 32 rows alike or differently. Cases: gradients
(diagonal; x and y; swapped; one vector of two components; two u terms; two v terms; all four; a
negative; both u terms mixed) at k = 0 to 5 and 2, 4; `smp2d` whose LOD comes from the quad's
coordinate differences (equal and unequal footprints, a diagonal vector, rotated, k = 1 to 32);
`smp2dbias` (bias 0.5, 1, -1, 2) and T0's bias field on the automatic LOD. D3 inverts every pixel
to (level, fraction), prints the first row's LOD against x and the exact-pixel count per formula.
Outcomes. `pwl_*` exact: the hardware computes the exponent plus the mantissa, not a logarithm;
`max4` or `euc` exact: the footprint is the largest component or the largest axis vector (the
simulator needs the second if `euc`); `min`: the smaller. None: D3's curve is the table. The
fraction's resolution is 1/64: a function that rounds before that shows as a step in D3.

### 4.4 Q115: anisotropic filtering (`tx-lod.sh`, 21 jobs: five ratios and 15 bit flips)

Open: whether anything filters along the longer axis. Experiment: bilinear magnification and
minification (T0 bits 13:12, 11:10 = 1), explicit gradients of ratio 2 to 32 (one component of 2
texels, the other 2^k to 2^(k+1)), compared with one bilinear tap at the level the footprint
formula picks (D4); then, at ratio 8 (control `an-ctl`), flips of T0 bits 14, 15, 16, 27, 28, 29,
30 and T3 bits 8, 9, 11, 12, 15, 20, 21, 22 (T3 10, 14, 18 are in the T3 script; 13 and 19 fault,
section 4.6). Outcomes. Every ratio exact under one formula and every flip equal to the control:
no anisotropic filtering in the bits tried (not "none on this core": the closed driver's own
request is the capture of section 7). A ratio not exact under any formula with a pixel value that
is not a one-level blend: extra taps, the formula `min` at a lower level is the first candidate; a
flip that moves the level or the values is the enable. The names make an average visible: taps
that differ give a value that is no texel of the level.

### 4.5 Q050: border modes 4 to 7 (`tx-border.sh`, 37 jobs)

Open: what the modes read (E033). Experiment: a 16x16 twiddled texture, u = -1.5 + (x + 1/2) / 16
down the 64 columns (v inside, mode clamp), v swept likewise (u inside), and both: modes 0 to 7
each (24 jobs). Held out: the texture at another base address (modes 4 to 7), a 32x8 texture, a
strided 64x32 (modes 0, 4 to 7). D5 prints the decoded (x, y) along row 8 and column 8. Outcomes.
Modes 0 to 3 must reproduce E033 over 64 positions (they are the control; a failure is a failed
model, not a result). For 4 to 7: `clamp`, `nomask` (the unwrapped coordinate in the twiddle:
indices past the texture) and `border` (a constant outside) are declared; a constant that is not a
name is a border colour that something must load (a register or a state word: not run here); names
past the texture fix the address arithmetic; a pattern none of them gives is D5's table.

### 4.6 Q078: T3 and T0 bits in smp (`tx-t3.sh` 111 jobs, `tx-t3-risky.sh` 5)

Open (the question's own list): whether bits 7:0 are a texel offset at every value, and in smp;
what 18, 19, 27, 28, 10, 14 and T0 27 are. Experiment: a strided 64x32 texture (the copy's
geometry, T3 base `0xa0800000`), each bit flipped once (bits 0 to 7, 8 to 12, 14, 18, 20, 21, 22,
27, 28; T0 27, 30; 22 jobs and a control); the identity map decoded to (column, row) (D6); then
the bits whose effect depends on the geometry at 64x16, 32x32 (strided) and 32x32 (twiddled). The
rows of 27 and 28 are the point: `after` (the rows come after the source's height: 16 + y/2 at
64x16, 32 + y/2 at 64x32) against `fixed` (32 and 40 whatever the height); they coincide at the
fit size and separate at 64x16. Values: bits 7:0 at 31 single-nibble values and 16 seeded
combinations on the strided texture (fit), then 12 values under repeat, 6 under mirror and 6 under
clamp on the twiddled one (held out), declaring `pre` (offset, then the address mode) against
`post` (the address mode, then the offset clamped). Outcomes. `t3off=pre` exact on the twiddled
values: the offset is added to the texel coordinate before the mode (what `Texture::fetch` does);
`post`: after, clamped at the edge, so `fetch` changes. `t3rows`: which hypothesis holds is the
geometry dependence of 27 and 28 (the question's "mip level" reading needs `after`). None: D6
prints, per job, the most common column-x and row-y offsets. Risky, last, one job at a time with a
health check each: T3 bit 19 (E274: faults past the source), bit 13 (faults), bits 18 and 19, 27
and 28, 10 and 14 together. A fault is a result.

### 4.7 Q113, Q114: cube maps and volume textures (`tx-types.sh` 24 jobs, `tx-types-risky.sh` 15)

Open: which TEXTYPE or word makes a cube map or a volume, and how the third coordinate is used.
Nothing in the records says smp3d ever ran. Experiment: `smp3d` (the form without a LOD mode, the
only one that assembles) on a 16x16 twiddled texture at the third coordinate 0, 0.5, 1, 1.5, -0.5,
4 (declared: `w3d=ignore`, the image of the 2D control); the same on strided (TEXTYPE 6) at 0 and
1; TEXTYPE 3 on a power-of-two texture (explore); the third coordinate swept 0 to 2 down the rows
on types 0, 3, 6 (D7 prints the dwords); and, at a third coordinate 0.625, single flips of T3 bits
10, 14, 18, 27, 28 and T0 27, 30 against the control (the indicator: a bit that makes w act).
Risky, last: TEXTYPE 1, 2, 4, 5, 7 under smp2d, smp3d at 0.5 and 1.5 (a health check after every
job: an undefined type may hang the unit). Outcomes. Every image equal to its control: smp3d
ignores the third coordinate on these words, and nothing here names a cube or a volume; the
capture of section 7 is the way. A job whose image differs from its control is an indicator; D7
lists them and the second step is `gen_p1132.py --follow TAG T0 T1 T3` for that configuration: six
cube directions (the major axis +-1) and two slice sweeps (-1 to 1 and 0 to 2), eight jobs, the
faces' dword offsets read from the names, the face select from which direction gives which block.
The follow-up is generated and checked for assembly and `bash -n`, not run against any model
(there is none to declare).

### 4.8 Q050: compressed and YUV formats (`tx-formats.sh`, 30 jobs)

Open: layout and decode of formats 23 to 27 (E342's "other" row: four texels recorded) and YUV 28,
29. Experiment: names maps of 23 to 27 (16x16) and 28, 29 (64x32), kept; for 23, 24, 27 five block
jobs each, the 16 blocks (two dwords each) written by the program: constant (`base`), block i = i
x 0x11111111 (A), (5 i + 3) mod 16 (B), then dword 1 = 1 << i (`lo`) and 1 << (16 + i) (`hi`). D8
reads the order from A against B (a block i of B has the colour of block (5 i + 3) mod 16 of A in
the cell the order puts i: raster, Morton; reversing the blocks would pass for every order that
only permutes the index bits, and was not used) and each index bit's pixel from `lo`, `hi` against
`base`. YUV: formats 28 and 29 on sixteen texels (eight dwords; two patterns) with and without the
colour-space load in the fill's transfer command (`xfer:17^=1`, `xfer:18` to `22` = the BT.601
words of E037; the command words of a fill are those of the copy: the filter-set probes poke
`xfer:17` in fills). Declared (YUV pattern 0, fit): black without the load, the E037 conversion
with it, Y0 for even x, YUYV for 28, UYVY for 29. Outcomes. Black with the load: the poke did not
reach the set in a fill (a limit of the job), not a result about the format. Block order raster or
Morton, bit-to-pixel: the table. A format whose cells are not constant under A (one that blends
neighbouring blocks) says so; the exact decode of compressed data is a capture (section 7).

### 4.9 Q021: the fourth component (`tx-douti4.sh`, 28 triangle jobs)

Open: whether pa3 = 1.0 under bits 23:22 = 3 is a fourth component or a constant, and where the
texel lands (E420: pa4). Experiment: E420's probes with the vertex shader writing a set of four
(o4, o5 = x, y, o6 = 0.25, o7 = x + y: `templates/vtx_coords4.s`, two temporaries more than
E420's), pa2, pa3, pa4, pa5 each stored by the pixel shader, five fresh runs of 0x40c00801 and two
controls of 0x40800801. Outcomes. pa3 = x + y (a float, many values): a fourth component, and the
texel stays at pa4; pa3 = 1.0 still: a constant of the iterator and the plane equation of the
fourth dword is read elsewhere; pa2 = 0.25 shows the third. The vertex program is not run by the
simulator (not validated). Triangle jobs do not become vectors.

## 5. Outputs kept, what each result updates

Per job: `NAME.txt.gz` (the whole stdout, 2048 `row` values), `NAME.err.gz` when standard error is
not empty, the raw size and sha256, the case table, `journal-k.txt.gz`. The recompute prints, for
each group and set, how many cases were exact under each declared hypothesis, then D1 to D9.
Results go to a record only after the recompute, and an outcome the tables do not show is not
stated (section 10).

## 6. The simulator: what changes, and how a result becomes a vector

Landed `tex.rs` stops with `Err(why)` where this batch measures; each result replaces one
`open(...)`:

- E276, E441 (landed, no run needed): `pick()` reads bits 20:17 as a maximum (0 and 15 level 0,
  else min(max, last)) and 26:21 as a bias in eighths (`simtree/tex-e276.patch`, 51 lines). One
  landed unit test changes, `t0_fields_enable_the_chain`, which asserts "26:21 = 0x10 is not
  measured". 141 of the 428 programs agree with the model on the patched simulator.
- shapes (Q104): `pick()` drops "mipmaps of a 1D or non-square texture"; `last` and `level()`
  follow the winning chain rule. Vectors: the shape ladders, 2048 pixels each.
- twiddle (N1): `morton()`. Vectors: every window.
- LOD (Q050): `lambda()`, the function and the footprint, the "exact" flag, `Lod::Open` for the
  quad. Vectors: the gradient and automatic jobs.
- border (Q050): `Texture::axis`, modes 4 to 7. Vectors: the border jobs.
- T3 (Q078): `t3_fields`, the unmeasured masks shrink; `fetch` gets the rows rule and `pre` or
  `post`. Vectors: the T3 jobs, the copy-geometry ones first.
- formats (Q050): `bytes()` and `colour_texel()` for the compressed formats; YUV through a
  colour-space set the job carries (`init.job`). Vectors: the formats jobs.
- smp3d (Q113, Q114): a third coordinate in `Sample`, only if an indicator is found. Vectors: the
  follow-up jobs.

How a result becomes a vector, with the landed tools and nothing new: `recompute_p1132.py DIR
--raw OUT` writes `OUT/tx-GROUP.toml` (the table), `OUT/tx_map.s`, `OUT/tx-GROUP/raw.txt` (the
`probe-case` blocks) and `OUT/tx-GROUP/bins/`; `tools/usse-asm/vectors.py convert OUT/tx-*/raw.txt
-o V --root OUT` makes the `.vec.json` (the converter finds the table next to the run directory);
the vectors go to `vectors/nokernel/texture/`; `RESGX545_DATA=... cargo run --release -p sgx-sim
--example replay` lists pass, unsupported and mismatch. A fill with `--coords` and `--pixels` is
compared pixel by pixel (`run_pixels`: every pixel as the fill's 2 x 2 quads, which the automatic
LOD needs). Two limits: the simulator's `Memory` and the converter's `init.scratch.bytes` are 64
KiB (a larger texture, E441's chain of 128x128 in 24 pages, needs both to honour
`--scratch-pages`; every job here fits), and the triangle jobs are not compared (vectors.md
section 3). `validate/selftest.py` step 4 runs exactly this chain on the fake-hardware dumps: the
landed converter takes the 428 jobs and the patched simulator replays them without a mismatch.

## 7. Tool changes, kernel and firmware; what cannot run in this batch

No tool change is needed by any case: the options used are `--coords`, `--pixels`, `--temps`,
`--poke xfer:N`, the tri options `--vtx-coords`, `--slot`, `--tri`, and the 256-word program limit
(every program is below it, the largest 88 words). Rejected: a `--scratch-fill FILE` (block data
comes from the program's own stores, so that the vector, whose scratch is `0xd0000000 | i`,
reproduces the job); a repeat option (five runs of Q021 are five cases).
`tool-tests/test_tx_tool_assumptions.py` pins what the scripts read (the `row` lines without `0x`,
pa0's layout, the `pokes` line, the refusal above 256 words): 3 tests, passing on the landed tool,
so no test fails. No kernel change and no firmware change: the writes are the debugfs reset and
`/dev/kmsg`; no `kreg`, no `kregnow`, no `/dev/mem`; no clock-gate register and no register at all
is written. Cannot run in this batch:

- Q113, Q114: what the closed driver writes for a cube map and for a 3D texture. E342: its
  cube-map runs give no doutt with data-segment operands, so its T words are not read; that needs
  a harness capture and a host-side read of the smp operands in the pixel programs' constants. The
  records show no volume texture path of the closed driver either. This batch can only find a
  configuration of ours that makes the third coordinate act.
- Q115: the closed driver's anisotropic request (a capture with the extension on) fixes which word
  bit it sets; the bits flipped here are a negative, not a proof.
- Q050 compressed formats: the exact decode of known PVRTC and ETC1 data through the closed driver
  (render and compare) is a capture; the block jobs give layout and index bits, not the decode.
- A border colour, if the modes read one from a register: no register is known; a kernel change (a
  debugfs poke of the TPU register) would follow a constant outside the texture.
- Textures over 64 KiB as vectors: simulator and converter change first (section 6).
- Q021 beyond four components: a second source with a different component count.
- Not touched: formats 6, 14, 20, `.pcf` splits, the sampler cache, anything of Q050's other
  groups (visibility, `fdpc`, `firh`).

## 8. Run order, risk, recomputation

Order (`run-all-1132.sh`): `tx-gate` (the first jobs ever to run `smp` in a `--coords` fill: four
controls with declared images; one that is not read stops the batch and the fallback of section 3
is the plan), `tx-twiddle`, `tx-shapes`, `tx-fields`, `tx-lod`, `tx-border`, `tx-t3`, `tx-types`
(first smp3d: a health check after every job), `tx-formats`, `tx-douti4`, then the risky ones one
job at a time: `tx-t3-risky`, `tx-types-risky`. Before the first job, and after any failed job,
the script resets the GPU (debugfs `reset`) and requires a plain 64x64 triangle to draw exactly,
with one retry after a second reset and five seconds, before counting a failed recovery; three
failed recoveries stop the script. A health line is printed on success. `journalctl -k` of the run
is kept. Stop at the first script that stops itself and read `dmesg` before another run.

Recomputation: copy `~/p1132-dumps/*` to a directory with one subdirectory per script and run
`python3 -B recompute/recompute_p1132.py DIR` (with `--raw OUT` for the vectors). It reads each
`cases.tsv` and gz output, does not read the scripts' reductions, re-renders the declared
predictions and checks their sha256 (`declared predictions that the model no longer renders` must
be 0), and lists any case not in `declared.tsv`.

## 9. Validated without the laptop

- `bash -n` on all scripts; no trailing whitespace; this plan at most 100 columns.
- Every table loads with the landed `probe.py`; 428 programs and the helpers assemble with the
  landed `usse-asm`, `pds-asm` (`stage-bins/`, 461 files); every program is at most 256 words.
- The simulator (copy in `simtree/`, the E276 patch applied) runs the programs and its pixels
  equal the model's on 141 of 428 (`gen/check_build.py`, `out/check4.txt`), among them the gate,
  the twiddle windows, the shape ladders to 32x32, the strided T3 values and most of the offsets.
  The rest stops on what the simulator does not model (T0 and T3 bits, smp3d, gradients, formats).
- `validate/selftest.py`: every script end to end through `fakehw.py` (the model as a tool):
  default hypotheses all exact (the scripts' MATCH lines too, no case outside the declaration);
  other hypotheses (chain B, Euclid, no mask, T3 after) are recognised by the recompute tables; a
  failing gate stops `tx-gate` with rc 1 and `run-all` after it; the dumps convert and replay
  (section 6).
- `validate/toy_blocks.py`: D8 against a toy compressed format (4x4 blocks, raster order, one
  pixel a bit) finds the order and the bit map; no model of the real formats exists to test it
  further.
- The scripts also ran against `sgxfive-test --mock` (shims for `sudo`, `modinfo`, `journalctl`):
  the mock faults on `smp`, so every job took the failure and recovery path.
Not validated: that `smp` runs in a `--coords` fill (the gate), that the fill's transfer command
takes the colour-space words (`xfer:17^=1`), that the added vertex temporaries are accepted,
smp3d, any outcome, the run time, the kernel's reaction to an undefined TEXTYPE.

## 10. Faults of r1126 and r1127 that this plan avoids

- r1126 F1, F10 (statements about scripts run or not run, health claims): records after the run;
  `health: ok` lines are printed and kept.
- F2 (prose and code of a hypothesis differ): the hypotheses are the names of `texmodel.RULES`.
- F3, F17 (a test that cannot show the effect): `out/discrimination.tsv`; the fit set holds a case
  that separates.
- F5, F6 (counts, "every value"): counts printed by the generator; the bits and values tried are
  listed.
- F7 (a message mixed into the last row of a dump): standard error is kept apart.
- r1127 F2 ("none lost" from registers not sampled): every pixel of every job is compared.
- r1127 F3 (a replication called a prediction): repeats count as fit; predictions are hashed
  before the run.
