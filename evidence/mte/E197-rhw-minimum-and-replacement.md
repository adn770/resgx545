+++
id = "E197"
claim = "With 0x0240 (ta:152) at 0.3, 0.5 and 0.7 and 0x0244 (ta:153) at 0.25, the TA keeps a vertex's stored 1/w when it is above 0x0240 and stores 0.25 in its place otherwise: of the 1/w values 0.8, 0.364 and 0.615, none is replaced at 0.3, the 0.364 at 0.5, and the 0.364 and 0.615 at 0.7"
unit = "mte"
method = "the probes mte-rhw-03, -05 and -07 of probes/mte/rhw.toml (vtx_persp.s, w = x + 2, the TA command words poked through the kernel's kpoke, render memory dumped and read with tools/usse-asm/pbdump.py), 64x64 target, on the laptop with the linux fork and the debug option on, one run each"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["mte-rhw"]
terms = ["CR_MTE_RHW_MIN", "CR_MTE_RHW_CLAMP", "cmd_ta.mte_rhw_min", "cmd_ta.mte_rhw_clamp", "PB_OBJ.RHW", "WCLAMP"]
+++

**What runs.** The vertex program gives the three vertices w = x + 2, so their 1/w is about 0.8,
0.364 and 0.615. Three jobs poke ta:152 to 0.3, 0.5 and 0.7 and ta:153 to 0.25. Each dumps the
parameter buffer after the render. The pixel reports of the three jobs list the same colours with
the same counts (3034 background pixels).

**Results.** The TA's object has 29 dwords in all three dumps. The three vertices' 1/w sit in dwords
3, 6 and 9:

| ta:152 | dword 3 (0.8) | dword 6 (0.364) | dword 9 (0.615) |
|---|---|---|---|
| 0.3 | 0.8 | 0.364 | 0.615 |
| 0.5 | 0.8 | 0.25 | 0.615 |
| 0.7 | 0.8 | 0.25 | 0.25 |

Every other dword of the three objects is the same.

**Reading [infer].** The TA keeps a vertex's 1/w only when it is above 0x0240, and stores 0x0244 in
its place otherwise: 0x0240 is a minimum 1/w and 0x0244 the value it is clamped to. The three
settings fit it, with a threshold between 0.364 and 0.5 and between 0.615 and 0.7 as the table
requires. The images do not change, so the stored 1/w is not what draws these pixels here (E063).

**Not shown.** Only three values of 0x0240 and one of 0x0244 were run. The extreme values (~0, 1,
-1, NaN, 1e-45) and the effect of 0x0244 at other values are not in this table. Whether the test is
on the value or its magnitude is not separated, as every 1/w here is positive. One run each.
