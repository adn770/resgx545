# Pipeline simulator: the inventory of data for unit and scene vectors (12.0)

What of the recorded data can become a unit vector (one unit, one rule) or a scene vector (a
whole job), by unit and by what is missing. Counts are from the data repository at the time
of the scan (`tools/usse-asm/pipe_inventory.py`); the classification rules are the table in
that script, so a new dataset must be classified on purpose.

## 1. The triangle-host vectors

2464 vectors in 717 files carry `--tri` in `provenance.options`; the instruction replay leaves
them out (the readback is the scene's image, not the shader's output). As scenes:

- `scene-pixels`, `scene-mixed`: the image is the recorded result (`expect.image` as every
  pixel, or as value counts); `+pb`: the run kept a render dump (`--dump-render`) beside it,
  so a rebuilt scene's words can be compared with the parameter buffer of the same run.
- `hang`, `fault`: the job did not complete; `expect.outcome` of a scene. Whether a hang
  repeats is not in the vector (D5: a repeated measurement turns it into an `either`).
- `excluded`: `no pixel written` (the probe reported a draw of nothing: no image).

| unit | total | pixels | +pb | mixed | hang | fault | excluded |
|---|---|---|---|---|---|---|---|
| isp | 493 | 455 | 0 | 0 | 36 | 2 | 0 |
| mte | 218 | 210 | 4 | 0 | 0 | 4 | 0 |
| pbe | 206 | 192 | 0 | 0 | 10 | 4 | 0 |
| pds | 683 | 588 | 0 | 17 | 46 | 8 | 24 |
| ta | 26 | 0 | 26 | 0 | 0 | 0 | 0 |
| texture | 213 | 213 | 0 | 0 | 0 | 0 | 0 |
| usse | 582 | 567 | 0 | 0 | 14 | 1 | 0 |
| vdm | 43 | 7 | 25 | 0 | 11 | 0 | 0 |
| all | 2464 | 2232 | 55 | 17 | 117 | 19 | 24 |

What every one of them is missing: the scene's `memory` and `regs` (the words the kick
submitted). Until a run records them (`--record-scene`, vectors.md 6.4) they come from
`--emit-scene`, an offline rebuild through libsgxfive's mock backend from `provenance.options`
and the recorded programs, tagged `rebuilt`. Only the 65 that kept a render dump (55 of them
with an image, the rest hangs and faults) can be checked against their own run's parameter
buffer; the other 2399 would be rebuilt unchecked, and the plan's
figure of about 700 dumps to check them against counts dump directories of other tables
(section 2), not dumps of these runs.

The units a scene goes through decide what it can check before its unit models exist: the
pixel side (`pbe`, `texture`, `pds`, `usse` rows) needs 12.1 and 12.3, `ta`, `vdm`, `mte`
rows need 12.2, and every `isp` row needs the ISP's arithmetic (E606, Q200) to be pixel exact
(at 12.0; the coverage half is now E606 and E607, section 3).

## 2. The dump directories

197 directories named `dumps`. Status: `built` (unit vectors made in 12.0), `unit-ready` (data
and a decoder exist, the rule is not coded), `unit-blocked` (an open question blocks the
model), `scene-only` (a whole job only), `exists` (vectors already in the data repository).

| kind | status | dirs | files | records | blocked by | phase |
|---|---|---|---|---|---|---|
| isp-tile | built | 1 | 96 | E503 E502 E953 | - | 12.8 |
| ta-object | built | 1 | 177 | E541 | Q070 Q165 | 12.2 |
| te-region | built | 1 | 105 | E542 | Q070 | 12.2 |
| zls-store | built | 1 | 36 | E465 E489 E831 | Q107 | 12.4 |
| ta-object | unit-ready | 26 | 52 | E054 | Q068 | 12.2 |
| ta-object | unit-ready | 28 | 56 | E176 E181 E306 | Q070 | 12.2 |
| ta-object | unit-ready | 2 | 62 | E306 E308 | Q070 | 12.2 |
| te-region | unit-ready | 37 | 74 | E177 E180 E305 | Q070 | 12.2 |
| te-region | unit-ready | 2 | 591 | E543 E544 | Q159 Q160 Q161 | 12.2 |
| zls-store | unit-ready | 1 | 22 | E466 E490 | Q120 Q121 | 12.4 |
| bif-walk | unit-blocked | 2 | 118 | E457 E573 E592 | Q076 Q108 | 12.5 |
| dpm | unit-blocked | 5 | 229 | E200 E456 E464 | Q045 Q038 Q191 Q192 | 12.7 |
| events | unit-blocked | 1 | 226 | E154 E357 | Q111 | 12.6 |
| isp-tile | unit-blocked | 1 | 511 | E069 E590 | Q066 | 12.1 |
| mte | unit-blocked | 12 | 78 | E061 E063 E194 E287 | Q069 Q162 | 12.2 |
| pbe-emit | unit-blocked | 1 | 158 | E043 E044 | Q044 | 12.1 |
| te-macrotile | unit-blocked | 4 | 348 | E174 E175 E331 | Q100 Q139 Q086 | 12.2 |
| te-region | unit-blocked | 1 | 49 | E507 E511 | Q086 Q003 | 12.8 |
| vdm-stream | unit-blocked | 37 | 693 | E185 E191 | Q047 Q042 | 12.2 |
| vdm-stream | unit-blocked | 16 | 192 | E188 E300 E346 E414 | Q112 Q092 | 12.2 |
| vdm-stream | unit-blocked | 4 | 252 | E189 E190 E571 | Q094 Q163 | 12.2 |
| isp-tile | scene-only | 8 | 16 | E210 E211 | Q030 | 12.8 |
| isp-tile | scene-only | 1 | 66 | E281 | Q089 Q089 | 12.8 |
| te-region | scene-only | 3 | 6 | E306 | Q070 | 12.2 |
| vertex-task | exists | 1 | 103 | E372 | Q053 | - |

By status: built 4, unit-ready 96, unit-blocked 84, scene-only 12, exists 1 (directories).

The directories of each rule, with what is special about them:

- `bif/`: 2 dirs; client and render directories.
- `dpm/`: 5 dirs; state page, free list, partial renders.
- `(followup/)?vdm/(state1|state1-split|state-units|state2-)`: 37 dirs; state word fields.
- `isp/bg-object-pokes/`: 1 dir; 169 jobs, the background object's words.
- `isp/msaa-ident/`: 1 dir; 48 runs, 96 dumps.
- `isp/msaa-layout/`: 8 dirs; sample layout.
- `isp/msaa-resolve/`: 1 dir; resolve.
- `isp/msaa-te-dumps/`: 1 dir; TE words under 4x.
- `mte/`: 12 dirs; viewport, clip, 1/w, OUTSEL.
- `platform/event-bits/`: 1 dir; EVENT_STATUS per event.
- `render/kick-objects/`: 3 dirs; 3 kicks' PB.
- `ta/(line-point|points)/`: 2 dirs; lines and points; rules in recompute_p1131.py, not coded.
- `ta/mtile-`: 4 dirs; fitted table (tiling3d.py); other words refuse.
- `ta/object-format/`: 1 dir; 59 jobs.
- `ta/object-words/`: 2 dirs; random words.
- `ta/objects/`: 28 dirs; one object per state-word setting.
- `ta/regions/`: 37 dirs; region_tiles.py's sweeps; E542's rule covers them.
- `ta/tri-region/`: 1 dir; 35 jobs.
- `ta/zero-words/`: 26 dirs; the twelve zero words: refuse a non-zero one.
- `usse/globals-vertex-eot/`: 1 dir; vertex vectors of 11.33 replay in sgx-sim.
- `usse/output-room-tiles/`: 1 dir; end-of-tile output room per tile.
- `vdm/(index-list|index-trailing|index2)/`: 16 dirs; index list words.
- `vdm/(vtask-capacity|vertex-tasks)`: 4 dirs; vertices per task.
- `zls/store-format-dumps/`: 1 dir; formats 0 to 2 and the sign bit; the format rule is not coded.
- `zls/store-layout-dumps/`: 1 dir; 18 cases, 36 depth dumps.

## 3. What is missing, by unit

*Written at 12.0; revised 2026-11-11 against the records landed since (E606 to E830). The counts
of sections 1 and 2 are those of the 12.0 scan and were not redone.*

- **zls**: built since 12.0: the address rule (E615), the store of formats 0 to 2 and the
  negation bit over E490's 22 dumps (E663; formats 4 and 7 store nothing without a stencil
  buffer), the load pass over E467's 30 cases (E664: the loaded depth loses its sign bit) and the
  control word's fields (E665), and the pixels past the target at even sizes: the depth inside
  the band x + 0.5 < 1.25 W and y + 0.5 < 1.25 H, cut at the tile area, the background 1.0 past
  it (E730, E831). Refused: formats 3, 5 and 6 (Q120), the stencil store's order and its edge
  tiles (Q121), the overflow store (E628, E629: the loaded buffer and the sign bit after a raised
  abort; Q107) and an integer format at an edge (Q242); the band at odd sizes follows rule A
  (E885, E903).
- **ta**: the region test, the object layout and its failures are built, and since 12.2 the
  vertex side and the TA as a whole (E650: 89 of 89 dumped one- to five-triangle jobs byte for
  byte, every one fitted; 266 more scenes refused by question). Missing: the macrotile table of
  the target (a fitted table, `tiling3d.py`, right on 123 and 69 only: Q100, Q139, Q086), lines and
  points (Q159 to Q161), the object's format bits above 7:0 and the masks beyond the settings seen
  (Q070), the prim word's extra dword (Q164), a state word nobody flipped in a two-object stream
  (Q047, Q112), the 4x object with `CR_TE_AA` bit 29 clear (E728, E829, E906; refused as Q142).
- **vdm, mte**: the stream parser and the MTE's viewport are in E650's model; the dump directories
  it refuses wait for Q047, Q069, Q112 and the state word rules. No unit vector is built: the
  inputs are in the render dumps only through the PB, so they need the scene's `memory`.
- **isp**: the multisample window is built (786 tiles, 13 with seam holes refused: E953).
  The coverage rule is a record and is built (E606, E607: 1/256 grid, half up, exact centre test,
  left and top ties; E660 reproduces 2752 of 2752 images through the pipeline), held on ten more
  targets up to 4096 x 4096 (E680 to E682; `sgx-pipe`'s `isp.rs` names the targets it admits); the
  depth plane is within E606's tolerance and has no bit-exact rule (Q200, Q262, Q288); negative
  sub-grid vertices and far vertices refuse (E683, E684; Q199, Q260, Q261). `doc/specs/3d.md`
  §11.13 states them. The sample position, line, polygon offset and stencil rules (E214, E279,
  E071, E216) are in `isp` triangle-host vectors, not in dump directories.
- **pbe, iter**: only whole-job vectors (`pbe` 206, the pixel-event and texture runs): the
  end-of-tile words and the pixel PDS launch are not in any dump. 12.1 needs `memory` from a
  scene.
- **dpm, bif, events**: dump directories of text (the state page, the directory words, EVENT_STATUS
  per event) that need their units (12.7, 12.5, 12.6) and the registers' semantics (`regs.rs`).
  The events side gives two STATUS2 latches as rules over a measured timing, bit 6 of a 64 x 32
  fill without a load (E805) and bit 7 of a vertex loop (E839), and refuses the other latches
  (E806, E840, E841; Q082), and of the clears takes `CR_EVENT_HOST_CLEAR` bits 15 and 18 against a
  held bit 18 (E855, E857) and refuses the rest (E821 to E823; Q111). The BIF side gives one
  rule, the word of the replay after a held TA write fault (the held page and `SB` through
  the list of the next TA run, a flush while held changing nothing: E848, E891, E892), and
  refuses the other faults, the number of replays and the boots that time out (Q003).

## 4. The MTE clipping and depth-range datasets

Read in 12.0: `mte/clipping` (E194, E063), `mte/depth-range` and `depth-range2` (E287); the
probes' images only, no dump. What they establish:

- The MTE clips in clip space at z = -w and z = w (E287: a flat triangle at clip z from -1 to 1
  draws whole at w 1, one at -1.01 or 1.01 is removed, a sloped one is cut where z passes the
  bound). The viewport's z offset and scale come after the clip and are not clipped to [0, 1]: a
  depth above 1 reaches the test as itself, a negative one compares as 0 (inferred from two
  values a side).
- The size of a triangle goes as 1/w, and below w 1e-5 it shrinks away; the state block's w clamp
  word (blk:14) sets that threshold (E194, four values of the word). The two TA command floats
  (ta:152, ta:153) change no clipping scene (E063: 176 images equal their baselines).
- A vertex crossing w = 0 draws (1216, 1258, 1273, 1394 pixels at the w values of E063): the
  hardware clips or handles it in a way the pixel counts show but no record states as a rule.
- **Not established**: whether x and y are clipped at a guard band or only at the z planes; the
  clipped polygon's vertices (only pixel counts of the result exist); anything below the 64 x 64
  target. So an MTE model can state the z clip volume and the w clamp as measured and must
  refuse x or y clipping (Q069, Q116), and the pixel counts of the clipped scenes can only be
  reproduced by a model of the ISP arithmetic (E606, Q200).

## 5. Corrections to the plan's numbers

- Dump directories that sit beside triangle-host vectors are 65 of the 2464 vectors' runs (the
  `--dump-render` ones), not "about 700": the other directories of section 2 belong to
  script tables with no vectors of this kind.
- The plan's 197 dump directories are right (a directory named `dumps`, any depth).
- The plan names `zls/store-layout-dumps` 36 and `store-format-dumps` 22 dumps: right.
