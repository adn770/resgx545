+++
id = "E620"
claim = "A model of the transfer job written for the pipeline simulator (sgx-pipe xfer: the render box's 32x16 tiles, the pixel-event PDS program run per tile through sgx-sim with ir0 in the 16-pixel units of E130 and ir1 = 6 on the last tile, the end-of-tile and end-of-render tasks, the pixel shader per pixel, a copy's texel through tex::sample, the PBE's rectangle and pack modes 0 to 3) replays 13679 scenes (4398 fills, 9281 copies) rebuilt from 39 sweep files of fills and copies (command words, background object, PDS data and texture words poked one at a time): 5079 match the recorded image hash and the dwords written outside the target, 8600 are refused under questions, none mismatches and none is refused under a question its vector does not list; of the 5079, 45 are unpoked jobs, 172 poke words to the value they had, 2429 poke only words the model never reads (their match says the hardware ignored those words for the values tried) and 2433 poke at least one word the model reads, and 518 are 158 distinct images the pokes changed, 130 of them the one image of the alpha inversion (E268); the pixel-event program's tile_x mask (data dword 9, 0xff8) with bit 4 cleared leaves the second column of 32-pixel tiles unwritten in the 64x32 fill (1024 pixels, the first at (32, 0)) and writes the second column's tile at the first column in the copy, so the end-of-tile task's x field is 2 for that column and not 1"
unit = "transfer"
method = "offline, no new run: tools/usse-asm/transfer_scenes.py rebuilds each case's words with sgxfive-test --mock --emit-scene (the builder's words, not a capture: the fill and copy sweeps print no layout line and no dump of a transfer's words exists to check them against) and pairs them with the case's recorded outcome from the sweep's raw output; cargo test --release -p sgx-pipe replays them through the Rust model and cargo run --release -p sgx-pipe --example scene_stats prints every count below (the populations by probing each poked word on the unpoked job with 0, all ones and each bit flipped, the model alone); the first version of the model gave 143 mismatches, each traced to a missing refusal and none fitted away; the model uses no fitted rule, so no result is fitted; every refusal is selected by the scene's words alone, never by the recorded result"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["transfer-command-words", "isp-background-object", "isp-render-only-registers", "platform-untouched-registers", "pds-end-of-tile", "pds-pixel-event-word2", "pds-data-words", "pds-douti-fields", "pbe-emit-words", "pbe-emit-words-followup", "texture-sampler-bits", "texture-state-words", "texture-tpu-csc", "scene-vectors-12-1", "unit-vectors-12-1"]
terms = ["PIXEL_EVENT.END_OF_TILE", "PIXEL_EVENT.LAST_TILE", "DOUTU1.BITS11_3", "DOUTU1.BITS21_12", "EMIT2.BITS15_8"]
+++

**What ran.** 13679 scenes of 39 sweep files: 4398 fills and 9281 copies, 45 of them unpoked jobs.
The six kernel-register files (the `kreg` sweeps) hold one scene each, the unpoked job: their 1020
register-write cases are listed as excluded because a scene cannot carry a kernel register, as are
477 cases the kernel rejected before they reached the hardware. The model computes a scene only
when every word it reads is one a record explains, and refuses otherwise, naming a question that
depends on the scene's words and not on what the hardware did.

**Results.** [HW] 5079 scenes match and 8600 are refused; none mismatches, none is unsupported
(a refusal under a question the scene's vector does not list) and none is fitted.

What the 5079 show differs by population, counted by the model alone:

| population | scenes | what the match shows |
|---|---|---|
| unpoked jobs | 45 | the builder's words, the model and the hardware agree on the image |
| a poke to the value the word had | 172 | the same as the unpoked job |
| poked, model-inert | 2429 | the model never reads the words poked: the hardware ignored them too |
| poked, model-live | 2433 | the model reads a poked word and still gives the hardware's image |

A word is model-inert when 0, all ones and each of its bits flipped (34 values), tried on the
unpoked job, leave the model's image and its count of dwords outside the target as they were; a
refusal counts as live. The inert matches are a regression statement (the hardware ignored the
word for the values the sweep tried) and not an explanation: they are the pixel-event program's
data words the program does not use (1104), the background object's words (995, a fill's
words 3 to 16 among them, which E069 and E590 found change nothing: for a copy's object the model
merely never reads some words no record names), and primary (231) and secondary (99) program data
words.

4561 matches give the unpoked job's image and 518 give an image the poke changed: 158 distinct
images. 130 scenes are one image, the alpha inversion of CR_REG_0400 bit 25 (E268, the command's
word 14), and 27 another (the last tile left unwritten, E265); the rest are the render box (command
words 12 and 13), the end-of-render mask (E265), the background object's coordinates, the copy's
source address and coordinates (the primary program's data dwords 6 to 9) and the texture state
words through `tex::sample`. The 18 matches that move the copy's source address (data dword 6) are
the only ones that corroborate a builder address: see the caveat below.

The 8600 refusals by question, with the hardware's recorded result beside them (the model never
reads it): Q206 4506 (4227 image, 234 fault, 45 hang), Q207 890 (466 image, 338 fault, 86 hang),
Q074 1813 (1801 image, 12 hang), Q066 466 (452 image, 14 hang), Q205 326, Q076 and Q003 together
186 (138 fault, 48 image), Q021 291 (284 image, 7 hang), Q078 96 (62 image, 34 fault), Q011 14,
Q003 alone 12 (all hang). 3150 of the Q206 refusals are a coefficient group (command word 17 or
above) that is set.

**What the first version got wrong, and what refuses it.** Each of its 143 mismatches was a scene
the model computed where no record gives the rule: 62 vertices that are not the target's rectangle
or a coordinate that is not finite (Q205; the texture unit returns a texel for a NaN coordinate,
a gap in sgx-sim to close there later), 40 texture reads outside the scene's memory (the source
moved onto the target's pages, which hold what the tiles stored so far; Q076 and Q003), 15
secondary programs that do not start the template's task (Q207), 8 background word 10 values with
bits 31:16 set, past the two bytes E069 swept (Q066), 6 last tiles whose task does not end the
render and 6 tiles whose event starts no task (Q003: whether the job completes is not in the
records), 3 pixel-event programs whose code is not the template's (Q207) and 3 tile masks (Q074).
The 26 `tex:` scenes among them refuse as reads past the source (Q076 and Q003), not as sampler
words (Q078). Each now refuses; none was made to match.

**Where the questions come from.** Q206 is the command's and the tasks' words with no record.
Q207 is a PDS program or input the PDS simulator does not know: an instruction or input no
record measured, and any program that is not one of the three templates the records ran (the code
of the secondary, primary and pixel-event programs is pinned by hash). Q003 is an access outside
the scene's memory (with Q076) and a job whose words leave it unknown whether it completes: a
program that does not end, a tile that starts no task, a last tile that does not end the render.
Hangs and faults the hardware recorded are not selected by input, so they are spread over the
questions of the words that caused them; Q004 (a context's flags and priority) is not one the
sweeps' words reach. [HW] The PBE predicts hangs from E266 (an odd count up to 0x80) and E267
(EMIT1 bit 31); no scene of the replay reaches that path, because the builder's emit words are
fixed, so the replay predicts no hang and no fault.

**What the model assumes.** None of these is a fitted rule of a record, and none is checked by
a result of its own. [infer]
- `alu_specials_in_movs`: a `movs` reads `ir1.l` and `tim.l` as the ALU reads `ir1` and `tim`.
  Measured for a fill's secondary program and for the pixel-event program (pds_isa 8.9, E263); the
  primary program's use of it is supported only by the unpoked jobs' image hashes. With it off 24
  of the 13679 scenes match.
- `if0`, `if1` and `ir2` are unknown inputs to every program: a program that reads one refuses
  (Q207). The three template programs read none of them; the replay is the same with them
  unknown.
- The three programs' code is pinned by hash; any other refuses (Q207), so the two assumptions
  above reach only the programs the records ran.
- The pixel-event program's ir0 is `tile_y << 10 | tile_x` in the units E130 states, 16 pixels
  across and 16 rows: tile_x is 2 for the second 32-pixel column. The first version of the model
  counted 32 pixels, against E130 and the fact below; the images did not change, because the
  tile written is the loop's and not decoded from the end-of-tile task's U1, and the U1 check
  compares the task's tile fields with the program's own.
- A copy's texel fetch has the LOD 0 on the identity plane (the unit square over the target) and
  an open LOD on any other plane, where the texture unit reads level 0 only for a stride texture
  and refuses otherwise. The pixel side's LOD is not a record.
- RGB565 (pack mode 3): E031 holds two colours, 0xff203040 and 0x80ff8040, whose channels
  truncate and round to nearest to the same values. The model stores mode 3 only for colours
  where the two agree and refuses the rest (Q044). No scene reaches mode 3.
- The builder's addresses (the target, a copy's source, the pages of the programs and of the
  background object) are the mock's. They are not read from a dump, so the 13679 scenes confirm
  them only through what the hardware read: a copy's source address moved by a poke gives the
  shifted image (18 matches). The target address is the harness's own readback and no match
  corroborates it.

**One fact.** [HW] In the 64x32 fill, flipping bit 4 of data dword 9 of the pixel-event program (the
mask that cuts the tile_x field out of ir0 << 3, 0xff8 to 0xfe8) leaves 1024 pixels unwritten, the
first at (32, 0): the right column of tiles. The same flip in the copy leaves every pixel different
from the reference, the first (0, 0) holding the source texel (32, 0): the right tile's colours
reach the left column. No other bit of the dword changes a pixel. So the end-of-tile task of the
right column has bit 4 of its U1 set, the x field 2, not 1. This is the unit E130 records for ir0
(tile_x 0 or 1 across a 32-pixel render): the model drives the program with it. [infer] Read with
E043, E044 and E126, where x or y = 1 changes nothing and 2 or 3 loses a column or a row of
tiles, the field counts in units of 16 pixels in x and, by ir0's high field being tile_y << 10, a
field of 2 for each 16 rows in y. The model does not use that reading as a rule to place a tile
from a U1 it was not given: it refuses a U1 that differs from the program's own (Q074).

**The pack-mode vectors.** [HW] The 74 `pbe-emit` unit vectors (data `unit-vectors-12-1`, written by
`tools/usse-asm/unit_vectors.py` from the datasets pbe-pack-modes and pbe-pack-colours, the stored
values the datasets' own reports give) are replayed by `pbe.rs`: 14 match and 60 are refused, 58
under Q044 (a colour whose RGB565 truncation and rounding differ) and 2 under Q012; none
mismatches. They check the pack modes 0 to 3 alone, with no tile loop in front of them.

**What it does not show.** The scenes' words are rebuilt, not captured: an address a poke moves off
the builder's buffers reads memory the scene does not hold and is refused. The ISP coverage of a
transfer is modelled as whole tiles of the render box, the PBE rectangle clipping (E069, E590,
E267); what the vertices do to a copy's iterated coordinates beyond the target's rectangle is Q205.
The arithmetic of the texture coordinates is the exact plane (E048), checked only where it is the
identity. The unpoked baselines' hash equals the CPU reference's only for a job that completed
with no pixel different from the reference and has a reference formula (not the ramp copies); the
other baselines carry the recorded hash alone.
