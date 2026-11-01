+++
id = "E091"
claim = "A recorded case for each of 16 groups of USSE forms that had no hardware readback (140 cases): 136 complete and record their registers and pixel, the 4 smp repeat forms fail on the hardware, and ima16 with word bit 37 or 47 set (form 172) gives the same 0x0025001c as the plain form 27"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/form-coverage.toml, fills whose pixel program runs one instruction of the target form (bitwise and test variants, ld/st with a pre-increment, fsc and smp repeats, dual-issue variants, lapc and pclink moves, pack, ima16, rlp, movc and movmsk) on preset inputs; one run"
tiers = ["HW"]
date = "2026-11-01"
data = ["usse-form-coverage"]
terms = []
+++

**What runs.** 16 probes and 140 cases, each decoded to confirm that it contains its target
form. Each case is a fill whose pixel program runs the instruction on preset inputs and dumps
the registers to scratch.

**Results.** Of the 140 cases, 4 fail on the hardware (the job faults or hangs and the context
is lost): the smp repeat forms. The other 136 complete, each with its scratch dwords and pixel
recorded: the readback a model of these forms is checked against.

The ima16 probe runs form 27 (`ima16.u r10, r1, r2, r3, u16, u16`) and two raw words of form
172 (the ima16 word with bit 37 or bit 47 set, which the assembler never chooses): all three
give 0x0025001c in r10, so those bits change nothing.

**Not shown.** What the 136 readbacks mean beyond the ima16 case: this record keeps them as
measured, one run each.
