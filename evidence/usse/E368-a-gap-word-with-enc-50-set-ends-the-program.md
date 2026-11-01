+++
id = "E368"
claim = "A word of class 2, 22 or 26 that no form decodes ends the program when its enc[50] is set: of the nine 11.7 words, each with enc[50] set (as run or flipped) lost the sixteen stores after it and the pixel's own final write, the pixel keeping what the job before left (nine of nine), and each with it clear kept them (six) or hung the job (three); flipping any other bit of enc[49:0] of a class 2 and a class 26 word keeps the end, and of a class 22 word with enc[50] clear, bits 32, 33 and 51 remove the pixels it writes 0 (3 or 4 in the base) and bits 44, 45 and 46 raise them to 7, 12 and 15, while the other bits give 2 to 6 (one run, so the 3-or-4 spread of the base is not told from the flips' by repeats)"
unit = "usse"
method = "on the laptop, linux fork b5a86838ae59 with the debug option on: probes/usse/encoding-gaps-end.toml (dump.s with r9 = 0x600DF00D moved right after the word and r9 as the pixel): the nine 11.7 words of classes 2, 22 and 26 as run and with enc[50] flipped (flips that decode left out, none did), then each of enc[58:0] flipped alone on 0x16FD0F56289DA082 (class 2), 0xD36FCF73F0E8CF91 (class 26) and 0xB21880B46C3C406D (class 22), 175 cases; one run"
tiers = ["HW", "infer"]
date = "2026-11-03"
data = ["usse-encoding-gaps-end"]
terms = []
+++

**What runs.** The word in place of an instruction after the presets, then the marker move, the
template's sixteen stores and `mov.end o0, r9`. A program that runs on writes the marker to
every pixel and the stores; one that ends at the word writes neither, and o0 keeps what it held:
the value the job before left in that instance's output register (E373).

**Results (words).**

| word | enc[50] | as run | flipped |
|---|---|---|---|
| class 2 0x16FD0F56289DA082, 0x174767201E0A5FA1, 0x14BEA76C90F608E3 | set | no stores, the pixel the job before's | stores; two of three hang |
| class 22 0xB7ECF778F9B27E62 (bilin, format 3) | set | no stores | stores, 26 pixels not the marker |
| class 22 0xB21880B46C3C406D, 0xB5D2715A97A5103A | clear | stores, marker (3 pixels 0) | no stores |
| class 26 0xD4616B86E7DA59C9 | clear | stores, marker | no stores |
| class 26 0xD12855E58CE5D732 | clear | hangs (it completed in 11.7) | no stores |
| class 26 0xD36FCF73F0E8CF91 | set | no stores | stores, r10-r17, r7 and r8 written |

Where the job before wrote the marker, a word that ends the program shows the marker as its
pixel; where the jobs before ended too, it shows the colours left by the baseline triangle
(0xff203040 on 1432 pixels, 0xff00ff00 on 616), as a fill that never writes o0 does (E373).

**Results (flips).** On the class 2 and class 26 words every flip that leaves the word
undecoded (57 and 58 of enc[58:0]) loses the stores and the pixel's write, but enc[50], which
hangs the job; after that hang the pixels the hung job's instances wrote read the marker (240
and 1336), the same in every later case. enc[35] of the class 26 word changes which pixels hold
which of the two left colours (1490 and 558). On the class 22 word, enc[50] loses the stores;
enc[32], enc[33] and enc[51] remove its pixels of 0 (3 in the words run, 4 in the flips run's
base case); enc[44], enc[45] and enc[46] leave 7, 12 and 15 of them; enc[11], enc[26] and enc[29]
give 6, 6 and 2, and the other flips 3 to 5 (the count is not fixed, 3 and 4 for the unflipped
word, so the one-off 3 and 5 are not told from it without repeats). Bits 44-46 are the ones that
surely matter; each flip was run once.

**Reading [infer].** In these classes enc[50] is the `.end` it is in mov, nop, fmad and bilin.
The 11.7 run's "pixel as the base" for the class 2 words is the job before's o0, which held the
base's value.

**Not shown.** What the words write before ending (which pixels the zeros are, and what bits
44-46 do), and what the words of class 31 do with
enc[50] (one changed nothing in 11.7). One run.
