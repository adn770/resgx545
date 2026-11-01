+++
id = "E142"
claim = "In a PDS program with no load or store, rfence and rwfence leave the data-segment registers as they are: with no fence, with rfence and with rwfence the sixteen registers handed on through douta equal the inputs, and with both fences between three dependent mov32s each mov reads what the one before wrote; all four jobs complete"
unit = "pds"
method = "probe pds-memory-fence of probes/pds/memory.toml on the laptop, linux fork with the debug option on: the fill's secondary PDS program (pds_dump.s) runs the case's instructions on ds0[48-55] and ds1[48-55] (the sixteen inputs 0x11111111 to 0xffffffff and 0x11111110), then douta passes the registers to the shader sa_dump.s, which stores them to scratch; four cases, two runs (the second is the follow-up run)"
tiers = ["HW"]
date = "2026-11-01"
data = ["pds-memory", "pds-memory-followup"]
terms = []
+++

**What runs.** The PDS program copies the sixteen inputs to ds0[48-55] (A to H) and ds1[48-55]
(I to P), runs the case, and passes ds0[48-55] to `sa0` to `sa7` and ds1[48-55] to `sa8` to `sa15`
with `douta`. The shader stores `sa0` to `sa15` to scratch dwords 0 to 15. The cases are `nop`
(the control), `rfence`, `rwfence`, and `mov32 ds0[48], ds1[48]; rfence; mov32 ds1[48], ds0[49];
rwfence; mov32 ds0[49], ds0[48]`. No load or store is in any of them, and the scratch is mapped at
0x10000 as for the other cases of the table.

**Results.**

- Control, `rfence` and `rwfence`: the sixteen dwords read back are the inputs, unchanged.
- The case with movs: ds0[48] = 0x99999999 (the input I), ds1[48] = 0x22222222 (the input B, read
  from ds0[49]) and ds0[49] = 0x99999999 (the new ds0[48]); the other thirteen are the inputs.
  These are the values that sequential execution of the three movs gives.
- All four jobs complete, and the render after the table has 0 of 4096 pixels wrong.
- The follow-up run gives the same sixteen dwords in all four cases and the same four completions,
  with the same pixel check afterwards.

**Not shown.** What the fences order: with no load or store in the program there is nothing for
them to order, and these cases do not test it. The three-mov case has no run without the fences,
so that the fences do not disturb it rests on the sequential values. Two runs that agree, one job
per case in each.
