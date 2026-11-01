+++
id = "E109"
claim = "moest does not load the MOE state word its selector names from its register: after moest r17, #0 to #8 with r17 = 0x00000001, 0x00001001 or 0x01010101, a mov and a mov.repeat4 land and every dumped register reads as with no moest (28 of 28 cases identical); setfc #0-#1, #0-#1 changes neither how a quad whose instances disagree branches (2048 of 2048 pixels give the control's value) nor what ldad.fetch4 loads (5 of 5 identical)"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/moe.toml, probes usse-moe-moest-load (28 cases), usse-moe-setfc-branch (5) and usse-moe-setfc-fetch (5), plus usse-moe-setfc (5) for the plain load (client fills, every pixel and 32 scratch dwords read back), two runs (the second is the follow-up run)"
tiers = ["HW", "infer"]
date = "2026-11-01"
data = ["usse-moe", "usse-moe-followup"]
terms = []
+++

**What runs.** The moest probe puts a value in r17, runs `moest r17, #sel` for each selector 0
to 8 (the low and high data of smoa, smlsi, smbo and smr, and the index data) with each of three
values (27 cases and a control with no `moest`), then `mov r20, r1` and `mov.repeat4 r24, r5`.
If `moest` loaded the state word its selector names, the operands of those moves would shift.
The scratch holds r1-r16 and r20-r39 and the pixel is r20. The `setfc` probes run `setfc` with
each of its two operands at 0 or 1 (four cases and a control) before a plain load and
`mov.repeat4` (setfc), before a predicated `br` that splits every quad by x parity, p0 on even x
(setfc-branch), and before `ldad.fetch4` (setfc-fetch).

**Results.** moest-load: all 28 cases give the control's pixel (`0x01010101` on 2048 of 2048)
and the control's 32 scratch dwords. setfc: all five cases in each of setfc, setfc-fetch and
setfc-branch give the control's result: the branch probe writes 4 on all 2048 pixels (the whole
quad goes where its top-left instance goes) with every `setfc`, and the fetch probe loads the
same dwords. Both runs agree on every case. Baselines before and after every probe were exact;
the visibility counters read 0.

**What it shows.** Neither instruction has an effect a fill shows, in either direction: `moest`
does not apply a register to the state it names, and `setfc` does not change flow control or
the fetch. A fill never makes a context switch, which would be where they act **[infer]**.

**Not shown.** The selectors' values were only 0x00000001, 0x00001001 and 0x01010101; the
effect of other values is not shown.
