+++
id = "E218"
claim = "In the full punch-through shader the feedback's control word (src1 of atst8 with fb) keeps a pixel only with both bit 0 and bit 14 set: of the 32 single-bit flips of 0xe001 only those two lose the image, and flipping bit 2 or bit 3 makes the last copy win (1074 pixels of depth 1/4, 24 of 1/8); 15 words with bits 15:13 and the low bits varied agree, and pcoeff's third source (12 values) changes nothing, in two runs"
unit = "isp"
method = "probes isp-punch-through-pt-ctl-flip, -pt-ctl-func and -pt-pcoeff-src2 of probes/isp/punch-through.toml on the laptop, linux fork with the debug option on: five copies of the 64x64 triangle at depths 0 to 4/16 in the punch-through pass (render block word 1 = 0x08400200), pcoeff on the source-34 iteration, the pt phase ending in atst8 with fb whose src1 is loaded with the case's word, every pixel read back, each probe fenced by a baseline render before and after; two runs (the second is the follow-up run)"
tiers = ["HW"]
date = "2026-11-01"
data = ["isp-punch-through", "isp-punch-through-followup"]
terms = ["FEEDBACK_CTL.ENABLE", "FEEDBACK_CTL.KEEP", "FEEDBACK_CTL.DEPTH_ALWAYS", "ISP0.PASS_TYPE"]
+++

**What runs.** The working scene of E217 with the control word varied. In the flip probe the word
is 0xe001 with one of its 32 bits inverted (32 cases). In the function probe it is 15 words:
bit 0 alone, 0x2001, 0x4001, 0x6001, 0x8001, 0xa001, 0xc001, 0xe001, and 0xe003, 0xe011, 0xe101,
0xf001, 0x1e001, 0xe005, 0xe009 (bits 15:13 at each value 0 to 7 with bit 0 set, then low and high
bits added to 0xe001). The pcoeff probe leaves the control word at 0xe001 and loads the case's
value into pcoeff's third source: 0xee00, 0, ~0, 0xe000, 0xe00, 0x8000, 0x4000, 0x2000, 0x800,
0x400, 0x200 and 0xff. The colour written is the copy's depth, as in E217.

**Results.** Pixel counts per copy depth, the same in both runs:

| control word | copies drawn |
|---|---|
| 0xe001, and the flips of bits 1, 4 to 13 and 15 to 31 | depth 0 on 1062, 1/16 on 36 |
| bit 0 or bit 14 flipped (0xe000, 0xa001) | none |
| bit 2 or bit 3 flipped (0xe005, 0xe009) | depth 1/4 on 1074, 1/8 on 24 |

In the function probe the words with bits 0 and 14 set (bits 15:13 at 2, 3, 6 and 7: 0x4001,
0x6001, 0xc001, 0xe001) give the image of 0xe001, and so do 0xe003, 0xe011, 0xe101, 0xf001 and
0x1e001; words without bit 14 (0x1, 0x2001, 0x8001, 0xa001) give none; 0xe005 and 0xe009 give the
last-copy image. All 12 values of pcoeff's third source give the image of 0xe001.

**What it shows.** The control word needs bit 0 and bit 14 for the feedback to keep a pixel: with
either clear no pixel is kept. Bit 2 or bit 3 set keeps the pixels but the last copy wins over the
nearer ones, as if the depth test were always; E217's ~0 gives that image too. The other bits of the
word change nothing with one sample, and the third source of pcoeff changes nothing seen.

**Not shown.** What the bits do in other passes, with more than one sample, or with the depth
taken from somewhere other than this iteration. Of bits 15:13 only bit 14 matters here, so they
show no compare function (the compare function is src2's, E083). Why bit 14 and bit 0 are needed
is not shown. Two runs.
