+++
id = "E409"
claim = "CR_DPM_STATE_CONTEXT_ID (0x0630) reads 0 at every one of 2.96 million samples taken in 15 runs of one to three 1024x768 renders, so it cannot show the 3D's DPM slot; CR_TE_PSG (0x0218) drops from 0x01400000 to 0x00400000 for 8 to 25 microseconds at each render's kick, and with the command's bit 21 set it reads 0x01600000 before the first dip and shows one dip across two renders"
unit = "ta"
method = "probes/ta/te-words.toml (te-words.sh, part C) on the laptop (direct cable), linux fork f1fad0ed9d0e with the debug option on: regtimeline over 0x0630 and 0x0218 around tri at 1024x768 with one, two and three renders and with a geometry-only first render (three runs each, 12 runs), and two renders with the TA command's te_psg (ta:147) at 0x01600000 for the first (three runs)"
tiers = ["HW"]
date = "2026-11-07"
data = ["ta-te-words"]
terms = ["CR_TE_PSG", "CR_DPM_STATE_CONTEXT_ID", "REGION_HDR.FLAGS"]
+++
 **What was seen.** Over 15 runs and 2959937 samples 0x0630 never left 0, with one, two, three
renders or a geometry-only render. 0x0218 read 0x01400000 at the start, and for each render the
timeline shows 0x00400000 for 8 to 25 us (17 us, 123688710 ns to 123705958 ns, in the first run)
before 0x01400000 returns: one dip for one render, two for two, three for three (9 of 9 runs). With
a geometry-only first render the register went 0x00000000 for 25 us, then 0x01000000 for about 15
ms, then the dip: the same sequence in two of three runs; in the third the dip did not show. With
ta:147 = 0x01600000 on the first render the sequence was 0x01400000, 0x01600000, 0x00400000,
0x01400000 in all three runs: bit 21 was read before the dip and one dip showed across the two
renders. Every image was exact.

**What it shows.** The slot register is zero at every sample the sampling (about 120 kHz) gives
while jobs run, so bit 1 of it, the 3D's slot (Q064), cannot be read this way. Bit 24 of CR_TE_PSG
is cleared briefly at each kick (the firmware clearing and setting it again [infer]).

**What it does not show.** What the 3D does with region headers that bit 21 marks, which needs RT
data whose state bit 8 is set: no switch sets that bit (the render context flags are not it).
