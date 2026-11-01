+++
id = "E056"
claim = "None of the TA words that are zero in the triangle job (ta:155, 156, 158 to 168) nor render-detail words rd:9 and rd:19, set to a scratch-buffer page in six numberings, is used as an address: no job writes the scratch buffer or changes a pixel, except ta:167 at 0x700, which faults"
unit = "ta"
method = "hand-run sweep probes/ta/zero-words.toml (sweep run by zero-words.sh) on the laptop, linux fork with the debug option on: sgxfive-test tri --scratch 16, 15 words times 6 values by kernel poke, one run each"
tiers = ["HW"]
date = "2026-11-01"
data = ["ta-zero-words"]
terms = [
    "cmd_ta.dpm_reg_074c", "cmd_ta.use_reg_0a04", "cmd_ta.use_reg_0aa0", "cmd_ta.ta_reg_02b0",
    "cmd_ta.ta_reg_02b4", "cmd_ta.ta_reg_02d0", "cmd_ta.ta_reg_02d4", "cmd_ta.reg_0324",
    "cmd_ta.reg_0364", "cmd_ta.reg_0368", "cmd_ta.reg_0370", "cmd_ta.reg_0374",
    "cmd_ta.te_reg_02a8", "CR_REG_0148", "CR_ISP_SAMPLE_POS",
]
+++

**What runs.** The triangle job runs with a 16-page scratch buffer at 0x3e001000, every dword
0.25f before the render, and the tool reports the dwords the render changed. A kernel poke sets
one word to an address of a page of that buffer, in six numberings that each name another page:
0x3e003000 (absolute, page 2), 0x5000 (an offset), 0x700 (16-byte units), 0x3e009001 and
0xb001 (absolute and offset, each with bit 0), and 0xd (4 KiB pages). The words are the 13
TA command words ta:155, 156, ta:158 to ta:168, and rd:9 and rd:19 of the render details,
15 words, 90 cases and a baseline. The kernel poke applied in all 90.

**Results.** 89 of the 90 cases give the baseline image (1062 triangle pixels, 3034 background,
hash 0x99385a04ee01c585) and no change in the scratch buffer. The visibility counters stayed
at 0. The one exception is `ta:167` set to 0x700, which faults the job; the other five values
of that word do not. The same word faults with bit 8 alone (E054), and 0x700 has bit 8 set.

**Not shown.** The six values per word are a small set of guesses, and the scratch buffer is
the only memory watched; an address word the triangle's units do not read in this job could
still be read by another job. Each case ran once.
