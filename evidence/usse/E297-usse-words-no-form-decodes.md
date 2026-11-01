+++
id = "E297"
claim = "Of twelve words the decoder rejects, three each of classes 2, 22, 26 and 31, run in place of an instruction in a fill, none hangs or faults the job; eleven match no form's mask and one of class 22 is bilin's word with a reserved format value; the three of class 31 change nothing; the three of class 2, the bilin word and one of class 26 leave the program's sixteen stores unwritten, exactly the five with enc[50] set among classes 2, 22 and 26, and two of class 22 change some pixels"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/encoding-gaps.toml (written by tools/usse-asm/usse_bits.py table --group gaps --gaps-by-decoder: seeded random words of each class that the decoder rejects), each word as a raw .long in dump.s after the presets, case 0 a nop; readbacks compared by usse_bits.py eval; one run, 12 words and 4 bases; offline, each word against every form's mask and value, and 20,000 seeded random words through both rules"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["usse-encoding-gaps"]
terms = []
+++

**What runs.** About 4 percent of random 64-bit words match no form's mask and value (819 of
20,000 seeded words), all in classes 2, 22, 26 and 31 (the knowledge inventory). The decoder
rejects more, about a quarter (4,594 of the same 20,000, in 19 classes): a word can match a
form's mask and still hold a value no field allows. The table took the words the decoder
rejects, three of each class, so one of them is not a gap: 0xB7ECF778F9B27E62 matches bilin's
mask and value (form 216) and fails only on its format field (enc[41:40] = 3); with bit 40 or 41
flipped it decodes as bilin. It is a reserved value of bilin's format, and its effects are
plausibly bilin's. The words ran in a fill between the presets and the template's sixteen
`stad`s; the pixel is r10. `usse_bits.py` now selects gap words by "no mask matches".

**Results.** Every job completed.

| class | word | readback |
|---|---|---|
| 2 | 0x16FD0F56289DA082, 0x174767201E0A5FA1, 0x14BEA76C90F608E3 | the pixel as the base; none of the sixteen stores landed (the scratch keeps its fill) |
| 22 | 0xB7ECF778F9B27E62 (bilin, format 3) | the stores missing and the pixel mixed (0xa0a1a2a3 on 2016, others on 32) |
| 22 | 0xB21880B46C3C406D | the stores as the base; one pixel of 2048 reads 0 |
| 22 | 0xB5D2715A97A5103A | as the base |
| 26 | 0xD4616B86E7DA59C9, 0xD12855E58CE5D732 | as the base |
| 26 | 0xD36FCF73F0E8CF91 | the stores missing, the pixel as the base |
| 31 | 0xFF14652B9F5E11E9, 0xFF321261689C40C4, 0xFDA82CD6975E1BA1 | as the base |

So these encodings are not all inert: some stop the stores that follow (or send them elsewhere)
and some write registers. Which, and why, is open (Q080); the simulator stops on a word no form
decodes.

**Reading [infer].** The stores are lost in exactly the five words of classes 2, 22 and 26 with
enc[50] set, the bit that is `.end` in mov, nop, fmad and bilin; the words of those classes with
it clear keep them. A word that ends the program before the stores would give this. One class
31 word has enc[50] set and no effect. One run of twelve words: a correlation, not a test.

**Not shown.** Three words a class; one run.
