+++
id = "E206"
claim = "The TA command word the EDM copies into CR_DPM_REG_074C (ta:167) faults the job when bit 8 is set in every value tried (0x100, 0x700, 0xffffffff) and never when bit 8 is clear (31 other single bits, 0 and five address-like values), so the data fit an enable at bit 8 and do not fit an address field"
unit = "dpm"
method = "reading of the kernel-poke sweep of render-kernel-words (ta:167, 34 values, run twice, the second being the follow-up run) and of the hand-run zero-word sweeps of ta-zero-words (six address-like values per word) on the laptop with the linux fork and the debug option on, against the glossary's reading of the word as the register's source"
tiers = ["HW", "infer"]
date = "2026-11-01"
data = ["render-kernel-words", "render-kernel-words-followup", "ta-zero-words"]
terms = ["CR_DPM_REG_074C", "cmd_ta.dpm_reg_074c"]
+++

**Reading.** Register 0x074c (the value of `ta:167`, 0 in every job our kernel builds) sits among
the DPM's registers, so it could be an address with an enable bit. That reading is ours: no
citation record of this tree covers a register of this kind on another GPU. The data below test it
against the cases E054 and E056 already hold.

**What the data show.** `ta:167` was set to each of its 32 single bits, to 0 and to 0xffffffff in
the sweep (both runs), and to six values naming a page of a 16-page scratch buffer in the zero-word
sweep (0x3e003000, 0x5000, 0x700, 0x3e009001, 0xb001, 0xd; one run). The job faults for bit 8 alone
(0x100), for 0xffffffff, and for 0x700; the other 32 values of the sweep and the other five
address-like values complete, with the baseline image where it was compared (E054, E056). Bit 0
alone, and 0x3e009001 and 0xb001 with bit 0 set, complete, so bit 0 is not the enable.

**Reading [infer].** Bit 8 alone decides in the cases tried: set, the job faults; clear, it does
not, whatever the other bits among those tried (the 31 single bits cover bits 0 to 7 and 9 to 31).
An address field would be expected to follow the page named in the value, and no job wrote the
scratch buffer (E056). So the word reads as an enable in bit 8 that makes the DPM use a structure
the host has not set up, off in every job here; that structure could be a second list a
partial-render or context-switch arrangement needs, which is a guess.

**Not shown.** Where the fault lies: the BIF fault address was not recorded in these tables, so the
page, and any link to the TA data, is not measured. Values with bit 8 set and other bits set beyond
0x700 and 0xffffffff were not tried. A mapped buffer at the faulting page, and the DPM's writes to
it, would settle whether it is a structure at all.
