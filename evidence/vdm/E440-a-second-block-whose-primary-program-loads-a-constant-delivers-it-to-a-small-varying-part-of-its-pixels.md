+++
id = "E440"
claim = "In a two-object stream whose second state block's primary pixel PDS program writes a constant (0xff00ff00, douta to sa0) for a shader that writes sa0 as the colour, the constant reaches 24 to 270 of the 978 non-background pixels in the 3 control runs (138, 270 and 24; the others read 2, 6 and other leftovers) and 24 to 270 pixels with every field of either state word flipped (bit 8, bits 11:9 at 1, 3 and 4, bits 15:13 at 2, 3 and 4: 42 jobs of which 37 complete), so no field changes the load beyond that spread; bits 11:9 at 0 in the second block remove the second object (3 of 3 runs, the first object's 1098 pixels showing), in the first block they leave 398 green pixels (3 of 3); bits 11:9 at 1 hang in the second block (3 of 3) and at 4 hang in one of three runs of each block"
unit = "vdm"
method = "probes/vdm/state2-consts.toml on the laptop (direct cable), linux fork f1fad0ed9d0e with the debug option on: probe --tri with --vertices 12 --obj2 6 --obj2-blk 4=0x130004 --obj2-pixel sa_pixel.s --obj2-pixpds pds_obj2_const.s:8 (the second object's primary program douta 0xff00ff00 to sa0 and starts the shader; the first object's shader writes 0xff0000ff) and --vdm 1^=X or 9^=X: bit 8, bits 11:9 at 0, 1, 3 and 4, bits 15:13 at 2, 3 and 4 of each block, plus controls, three runs each (51 jobs), the pixels and the render's PB and TA data dumped"
tiers = ["HW", "infer"]
date = "2026-11-07"
data = ["vdm-state2-consts"]
terms = ["VDM_STATE1.BIT8", "VDM_STATE1.BITS11_9", "VDM_STATE1.BITS15_13"]
+++
 **What runs.** The tool builds the second block's primary pixel PDS program (obj2 pixpds): data
dwords 0 and 1 the shader's, one row of constants and a douta that writes the constant to the
secondary attribute named by its control word (sa0), the state block giving the task sixteen
attributes of room (word 4 = 0x130004, as the douta probes have it). It is the pixel-side constant
load of Q047's plan. The second object covers the first (E427): the controls' 978 non-background
pixels show the first object's blue nowhere (E427's one-block controls drew 1098; the 120 pixels'
absence is not explained here).

**Results.** Of 51 jobs, 46 complete and 5 hang.

| case | runs | green pixels (of the 978 non-background) |
|---|---|---|
| control | 3 | 138, 270, 24 |
| bit 8 set, block 1 / block 2 | 3 + 3 | 182, 138, 138 / 138, 138, 24 |
| bits 11:9 = 1, block 1 | 3 | 138, 138, 138 |
| bits 11:9 = 3, block 1 / block 2 | 3 + 3 | 270, 138, 24 / 138, 24, 24 |
| bits 11:9 = 4, block 1 / block 2 | 2 + 2, one hang each | 24, 138 / 138, 138 |
| bits 15:13 = 2, 3 and 4, block 1 | 9 | 24 to 270 |
| bits 15:13 = 2, 3 and 4, block 2 | 9 | 24 to 182 |

Bits 11:9 at 0 in block 2: 1098 blue (the first object) and 0 green in 3 of 3 runs, 2998
background pixels, as E427 found without the constant; in block 1: 398 green and 2998 background in
3 of 3 runs. Bits 11:9 at 1 in block 2 hang in 3 of 3 runs. The other pixels of the object hold
2 (21200 pixels over the 46 jobs), 6, 0xbf3f0000, 0xbde00000, 0x40000, 0xdf43 and 0: leftovers as
E430's no-wait registers show. The TA data is the same in all 46 completed jobs (one hash), the
parameter buffer's differs between the runs of one case in 7 of the 16 cases with completed jobs.

**What it shows.** The constant a second block's program loads does not reach most of the pixels
(24 to 270 of 978 in the controls), so this load is not a clean signal for the question: a field
that "loads constants" would change the count, and none of bit 8, 11:9 at 1, 3 and 4 or 15:13 at
2, 3 and 4 does beyond the controls' own spread. Bits 11:9 at 0 act on the whole block as E427
found (the second object's removal), here with the first block giving a steady 398 green pixels
[infer: the first object's removal changes what the second's tasks find in sa0]. Bits 11:9 at 4
hang once in three runs of each block, where E427 saw four completions of four.

**What it does not show.** Why the douta reaches so few pixels (E381 found a douta in a primary
program reaching sa in one job of thirteen; Q020 asks of the douta in the
primary program); the fields separating units remains unseen.
