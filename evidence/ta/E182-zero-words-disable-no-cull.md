+++
id = "E182"
claim = "With each of the TA command's twelve zero register words loaded with ~0, the culled triangle and the off-target triangle leave byte-for-byte the baseline's render memory (no object written), and the registers keep three words as aligned addresses (low 4, 4 and 2 bits clear) and four as full 32-bit values"
unit = "ta"
method = "the register readback and the cull dumps of probes/ta/zero-words.toml (script zero-words.sh and 26 dump probes) on the laptop, linux fork with the debug option on: each word loaded with ~0 by kernel poke, the register read back after the job, then the triangle culled (MTECTL cull mode 1) and moved off the target (viewport x offset 1000), the render memory dumped and compared with the dump of the same case with no word poked; one run"
tiers = ["HW", "infer"]
date = "2026-11-01"
data = ["ta-zero-words"]
terms = [
    "cmd_ta.use_reg_0a04", "cmd_ta.use_reg_0aa0", "cmd_ta.ta_reg_02b0", "cmd_ta.ta_reg_02b4",
    "cmd_ta.ta_reg_02d0", "cmd_ta.ta_reg_02d4", "cmd_ta.reg_0324", "cmd_ta.reg_0364",
    "cmd_ta.reg_0368", "cmd_ta.reg_0370", "cmd_ta.reg_0374", "cmd_ta.te_reg_02a8",
]
+++

**What runs.** E054 and E056 give the words and what loading them does to the image. This record
adds two tests of the reading that these words might be cull disables (a zero leaves the cull on).

*Readback.* The twelve words are `cmd_ta.use_reg_0a04` (`ta:155`), `cmd_ta.use_reg_0aa0` (156),
`cmd_ta.ta_reg_02b0` (158), `cmd_ta.ta_reg_02d4` (159), `cmd_ta.ta_reg_02d0` (160),
`cmd_ta.ta_reg_02b4` (161), `cmd_ta.reg_0324` (162), `cmd_ta.reg_0368` (163), `cmd_ta.reg_0364`
(164), `cmd_ta.reg_0370` (165), `cmd_ta.reg_0374` (166) and `cmd_ta.te_reg_02a8` (168). For each the
script loads ~0 and reads the register the word lands in after the job (the baseline read is the
same register with the word 0).

*Cull dumps.* The triangle is made to be culled twice, once by cull mode 1 in the MTE control
word and once by moving it 1000 pixels off the target in x, and each of the twelve words is loaded
with ~0 in turn, the render memory dumped after the job (the parameter buffer and the TA data).
Each of the two baselines has the same case with no word poked, 26 dump probes in all.

**Results.**

*Implemented bits* (the register value after ~0; the baseline reads 0 except where noted):

- 0x0a04 (`ta:155`), 0x0324 (`ta:162`): 0xfffffff0, bits 3:0 do not stick.
- 0x02d0 (`ta:160`): 0xfffffffc, bits 1:0 do not stick.
- 0x0aa0 (`ta:156`), 0x0364 (`ta:164`), 0x0370 (`ta:165`), 0x0374 (`ta:166`): 0xffffffff.
- 0x02d4 (`ta:159`): 0x03ffffff; 0x0368 (`ta:163`): 0x00007fff; 0x02b0 (`ta:158`): 0xff000000;
  0x02a8 (`ta:168`): 0x000ff000.
- 0x02b4 (`ta:161`): 0x000000ff both with ~0 and in the baseline.

*Culled and off-target.* The 12 culled and 12 off-target dumps with a word at ~0 are
byte-identical to the baseline dump of their case, in the parameter buffer (three non-empty pages,
at offsets 0x422000, 0x423000 and 0x463000; none at offsets 0 and 0x1000, where the triangle's
object and streams are in the drawn case, E185) and in the
TA data (every region header present and empty). The culled and off-target baselines are
byte-identical to each other, and the culled baseline is byte-identical to the dump of the VDM
state word with bits 11:9 at 0 (E185).

So none of the twelve words, loaded with ~0, makes the TA write an object for a triangle it
would cull. Three of the registers hold an aligned address (16-byte aligned for 0x0a04 and 0x0324,
dword aligned for 0x02d0) [infer: the clear low bits read as an address alignment]; four take
every bit of the 32; the other five take a field.

**Not shown.** That a word is an address is the reading of its clear low bits only: no run
shows it used as one (E056 sets the word to a scratch page and finds no access). Other cull
causes (a sub-pixel or back-facing triangle) were not tried with the words loaded. `ta:167`
(register unreadable here; faults at some values, E056) is not part of this record. One run.
