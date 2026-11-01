+++
id = "E420"
claim = "With DOUTI0 bits 23:22 = 3 the pixel shader reads pa3 = 1.0 on 1038 to 1062 of the triangle's 1062 pixels and a texel-valued dword (0xd0......) in pa4 on all 1062, in ten of ten runs; the exceptions in pa3 (up to 24 pixels with other values) came in the first runs after a baseline job"
unit = "pds"
method = "probes/pds/douti-four.toml on the laptop (direct cable), linux fork f1fad0ed9d0e with the debug option on: pds_tex_iter.s with DOUTI0 0x40c00801 (4 components) and the pixel shader storing pa3, pa4 or pa5 to o0, five runs each in two tables (30 jobs) and the controls 0x40400801 and 0x40800801 (12 jobs), every pixel read"
tiers = ["HW"]
date = "2026-11-07"
data = ["pds-douti-four"]
terms = ["DOUTI0.ATTR_SOURCE", "DOUTU1.WAIT_FETCH"]
+++

**What was seen.** With bits 23:22 = 3, pa3 (probes of 5 jobs, run twice): 1.0 (0x3f800000) on 1038,
1062, 1058, 1062, 1062 pixels and 1060, 1062, 1062, 1062, 1062; the few other pixels (24, 0, 4, 0, 0
and 2, 0, 0, 0, 0) hold other values, one 0xd0ce0000, in the first runs of their probes mostly. pa4:
a texel-valued dword (top byte 0xd0) on all 1062 pixels in all ten runs, the same two commonest
values (0xd0cc0000 on 12 pixels, 0xd0c90000 on 10) every time. pa5: floats (0x3e500000, 0xbd400000:
the x and y of E132's iteration) with 3 or 4 texel-valued pixels. The controls: with 2 components
pa3 holds the texel on 1062 pixels (two runs, texel values in pa3 and pa4 both). With 1 component
pa3 is 1.0 on all 1062 and pa4 texel-valued on 1059 and 1062.

**What it shows.** With four components the texel is in pa4, the dword after the components, and pa3
is 1.0: the rule of the other values (the texel after the components) holds, and the odd pixels of
E132 recur as a few pixels of the first run. [infer: pa3 = 1.0 is a fourth component (w) or a
constant; no source whose fourth component differs was run.] That pa4 also holds texel-valued dwords
with 1 and 2 components (1054 to 1062 pixels) means the fetch writes more than one dword or pa4
keeps older fetched data there [infer].

**What it does not show.** Whether the 1.0 is read from the source; the texel's position with the
fourth component from a source whose value is not 1.0.
