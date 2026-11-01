+++
id = "E407"
claim = "CR_TE_MTILE1 (0x0208) and CR_TE_MTILE2 (0x020c) take the TA command's te_mtile1 (ta:143) and te_mtile2 (ta:144) as poked (but for te_mtile1 bits 8 and 20 at 256x256 and bits 8 to 10 at 1024x768, which do not take), and the render changes with them in three of three runs: at 256x256 flipping te_mtile1 bit 12, 15 or 16 leaves 6144 to 16384 pixels wrong and bit 13 or 31 faults the job, while te_mtile1 bit 24 and te_mtile2 bit 0 draw the target exactly with a register value that is not the rule's; at 1024x768 te_mtile1 bits 0, 1, 2 and 5 and te_mtile2 bits 0 and 1 leave pixels wrong and te_mtile2 bits 2 and 8 fault the job"
unit = "ta"
method = "probes/ta/te-words.toml (te-words.sh, part A: every bit of both words, one run each at 256x256 and 1024x768, 130 jobs) and probes/ta/te-words-repeat.toml (te-words-repeat.sh: the flips below three runs each with the registers read back after the job, 81 jobs) on the laptop (direct cable), linux fork f1fad0ed9d0e with the debug option on"
tiers = ["HW"]
date = "2026-11-07"
data = ["ta-te-words", "ta-te-words-repeat"]
terms = ["CR_TE_SCREEN", "CR_TE_MTILE1", "CR_TE_MTILE2", "cmd_ta.te_screen", "cmd_ta.te_mtile1", "cmd_ta.te_mtile2"]
+++

**The words.** The rule's words after the control job (read back with --regs after the job): 256x256
0x0208 = 0x01004004, 0x020c = 0x02008008; 512x512 0x02008008 and 0x04010010; 1024x768 0x82010018 and
0x03018024. In every flipped run of part B the register of the poked word reads that word after
the job (for example 0x01005004 for te_mtile1 bit 12; the runs that fault included), except for
the bits that do not take (te_mtile1 bits 8 and 20 at 256x256, bits 8, 9 and 10 at 1024x768: the
register reads the rule's value), so the TA command's words reach the registers.

**The single-run sweep (part A, bit 31 to bit 0 listed as bit numbers).** At 256x256 te_mtile1 drew
wrong at bits 12, 15, 16 and faulted at 13, 14, 17, 18, 19 and 31; te_mtile2 drew wrong at 12, 13,
14 and faulted at 15 to 20; every other bit gave the control's image. At 1024x768 te_mtile1 drew
exactly only at bits 8 to 11, 20, 21 and 30, wrong at 0, 1, 2, 5, 17, 18, 19, 27 and 31 and faulted
at the other 16; te_mtile2 drew exactly only at bits 9, 10, 11, 17 to 21 and 31, wrong at 0, 1, 3,
26 and 27 and faulted at the other 18.

**The repeats (part B, three runs each, every run the same).**

| size | word, bit | register after | image |
|------|-----------|----------------|-------|
| 256x256 | te_mtile1 bit 8 | 0x01004004 (the bit does not take) | exact |
| 256x256 | te_mtile1 bit 20 | 0x01004004 (the bit does not take) | exact |
| 256x256 | te_mtile1 bit 24 | 0x00004004 | exact |
| 256x256 | te_mtile2 bit 0 | 0x02008009 | exact |
| 256x256 | te_mtile1 bit 12 | 0x01005004 | 6144 wrong |
| 256x256 | te_mtile1 bit 15, bit 16 | 0x0100c004, 0x01014004 | 16384 wrong |
| 256x256 | te_mtile1 bit 13, bit 31 | 0x01006004, 0x81004004 | job faults |
| 256x256 | te_mtile2 bit 12 | 0x02009008 | 6144 wrong |
| 256x256 | te_mtile2 bit 15, bit 16 | 0x02000008, 0x02018008 | job faults |
| 1024x768 | te_mtile1 bit 0, 1, 2, 5 | one bit changed | 24576, 49152, 98304, 180224 wrong |
| 1024x768 | te_mtile1 bit 8, 9, 10 | 0x82010018 (the bits do not take) | exact |
| 1024x768 | te_mtile2 bit 0, 1 | one bit changed | 16384, 32768 wrong |
| 1024x768 | te_mtile2 bit 2, 8 | one bit changed | job faults |

The words of a 512x512 target on a 256x256 one fail the job in three of three runs (two runs with
65536 wrong pixels, one with 49152), and those of the 1024x768 target on a 256x256 one draw 32768
wrong pixels in two runs and fail the job in one.

**What it shows.** The image follows the words poked into the TA command, which reach 0x0208 and
0x020c: a wrong word gives wrong or missing pixels or a fault, reproducibly. That the tiling
engine reads the registers, and not only the TA command's own copy of the words, is an
inference [infer]; the runs do not tell the two apart. And more
than one set of words draws a target exactly: te_mtile1 with bit 24 flipped (0x00004004) and
te_mtile2 with bit 0 flipped (0x02008009) at 256x256 draw it exactly with registers other than the
rule's (3 of 3 each). Bits 8 and 20 of te_mtile1 at 256x256 and bits 8 to 10 at 1024x768 do not take
(the register reads the rule's value, as E247's implemented bits).

**What it does not show.** What each field means (the macrotile counts and strides); the words of a
larger context's other targets beyond the two tried; te_screen (ta:142).
