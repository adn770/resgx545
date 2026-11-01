+++
id = "E663"
claim = "A model of the ZLS store written for the pipeline simulator (sgx-pipe zls.rs store, encode_depth) rebuilds the 22 depth dumps of E490's store-format run (11 buffers of 1024 x 768 at G = 33, a ramp across x and one across y each) dword for dword where a record decodes the format: the float (format 0, within E490's 1e-5 of the geometry's depth: 1572864 dwords), the 24-bit integer round(z * 0xffffff) (1572864), the 16-bit integer round(z * 0xffffff) >> 8 packed two rows to a dword in 256-dword tiles with the dword index x0 y1 x1 y2 x2 y3 x3 x4 and the half y0 (786432) and bit 19 on each of the three (1572864 + 1572864 + 786432), the integer ones over the float that the format-0 run stored at the same pixel, 7864320 dwords in 6 vectors, 0 dwords different and 0 left the fill that the model did not store; formats 4 and 7 without a stencil buffer (stated in the vector) store nothing (E490's 0 dwords: 2 vectors that compare no item, so the report counts them empty, not matched); formats 3, 5 and 6 are refused by question (Q120: 3 vectors, 965120 + 965120, 96580 + 84480 and 86084 + 73760 dwords not modelled); every one of the 6 stores rests on E465's fitted address rule, and the integer ones on the value rules E466 states as fitted, so all 6 are reported fitted and none matched; the model refuses what no run measured, by input alone: a 16-bit store at a pitch other than G = 33, overlapping tiles (a pitch under the tiles of a row), and an integer format over any depth but the ramp's 0.25 to 0.4166 and 1.0 (Q242), a target with edge tiles or an odd height (Q122), bit 19 with an integer format over any depth but the ramp's (Q101), bit 0 with any control but 0x0017100c (Q244)"
unit = "zls"
method = "offline, no new run: sgx-pipe zls.rs (store, encode_depth, in_tile_index16, unexplained) and the unit kind zls-format of unitvec.rs against the dumps of the dataset zls-store-format-dumps (tests/zls_vectors.rs, the vectors of unit-vectors/zls-store-format/ built by tools/usse-asm/zls_vectors.py with the dump counts of E490 checked against the dumps by the generator); the integer formats' depth input is the dump of the float format's run of the same ramp (the depth the pass left, a measured input), the float format's is the ramp's geometry in single precision; the rounding (half up) was chosen before the first run among the two the record names, and flipping it to a floor, or the 16-bit index's x4 position, made the vectors fail (the mutated model was run once each and reverted); the first unit tests of the formats were written after the model, not before it; the review r124 was folded test first: each test below (the integer formats' range, the exhaustive agreement of the two rules, the edge, overlap and odd-height refusals) was written and run failing before its code, and 33 mutations of zls.rs plus five new ones were run afterwards"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["zls-store-format-dumps", "unit-vectors-12-4"]
terms = ["CR_ISP_ZLSCTL", "CR_ISP_ZSTORE_BASE"]
+++
 **What ran.** `zls::store` takes the control word, the target and a depth per pixel and writes the
dwords the control says: nothing with bit 2 or bit 18 clear (E411, E466), nothing in formats 4 and 7
without a stencil buffer (E490), the float or the 24-bit value at `512 * (ty * (G + 1) + tx) +
in_tile_index` (E465) and, for the 16-bit format at G = 33, two rows to a dword at `256 * slot +
in_tile_index16` with the even row in bits 15:0 (E490). `encode_depth` gives the dword of one pixel:
the float's bits with bit 31 flipped by bit 19; the integers by half-up rounding of `z * 0xffffff`
in double precision, the 16-bit one shifted right by 8. The vectors are `zls-format`: the control
word, the two dumps and the source of the depth of each.

**Results.** [HW] Per vector, the dwords the model stores equal the dump's at every address (matched
items counted by dword over both ramps) and no dword other than the model's left the fill: f0
1572864 (the float within 1e-5 of the single-precision geometry), f1 1572864, f2 786432, b19_0
1572864 (the float negated: the dword is f0's with bit 31 flipped), b19_1 1572864 and b19_2 786432
(the dumps equal those without bit 19: the depth lies in 0.25 to 0.4166, E490). The unit tests give
the clear value 1.0 as 0x00ffffff and 0xffff (E411's bit 24 and bit 25 rows) and the sign of -1.0
for bit 19. [HW] f4 and f7 store nothing, as E490 counts. [infer] f3, f5 and f6 are refused with
Q120. The three counts of dwords left in E490 for them are recalled by the generator from the dumps,
not modelled.

**What is fitted.** The address rule is E465's fit, so each of the 6 stores is fitted. The 24-bit
rule is a choice made on the dumps of the run (E466: "in-sample") among four candidates: floor and
ceil of z * 0xffffff differ from the dumps (452477 and 333955 of 786432 dwords of f1), round(z *
0xffffff) and floor(z * 2^24) clamped to 24 bits both give 0 differences. The two agree on every
single-precision depth of 0.25 to 0.4166 (checked exhaustively by a unit test) and on 1.0, and
differ for most depths from 0.5 up (0.6, 0.75, 0.9), so the dumps do not separate them and the model
answers only where they agree: the ramp's range, which is where the measured depth lies (the f0
dumps hold 0.250081 to 0.416585), and 1.0 (E411's bit 24 and 25 rows). Any other depth refuses
(Q242; with bit 19, Q101). E466's "agree on 0.25 to 0.75" for the 16-bit pair was a copied range,
not a measurement. The 16-bit rule is E466's own "fit to this data's twin" with its layout derived
at G = 33 only; both carry `Fitted(E466)` in rules.rs. The format-0 vector compares the model's
single-precision ramp with a stated tolerance (1e-5), which is E490's, not a bound of ours: the
other five take the depth the hardware left and are exact. The format-4 and 7 vectors compare no
item (the dump is empty and the model stores nothing), and the report counts them empty, not
compared: they are not matched.

**What it does not show.** Anything outside 1024 x 768 at G = 33 for the integer formats (the float
store at other sizes is E489's); formats 3 to 7 with a stencil buffer; the stencil store (Q121); the
pixels past the target (Q122: a store of a target with edge tiles refuses); an integer format over a
depth outside 0.25 to 0.4166 and 1.0; the 16-bit store at another pitch, and a store whose tiles
overlap, where the dwords counted by E465 are known but not which pixel's value a shared dword holds
(Q242); how the hardware rounds ties (no pixel of the dumps is a tie: the generator did not count
them).
