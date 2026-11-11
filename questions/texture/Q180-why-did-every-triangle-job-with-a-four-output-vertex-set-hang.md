+++
id = "Q180"
question = "why did all 28 triangle jobs of the four-component DOUTI0 probes hang (E569), the two controls with the old source word 0x40800801 included (is it the four outputs o4 to o7, the two extra temporaries, or something else in the vertex program), and with 4 components (DOUTI0 bits 23:22 = 3) where does the texel land, given pa3 reads 1.0 on most pixels"
unit = "texture"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E569", "E420", "E541", "E132"]
terms = ["DOUTI0.COMPONENTS", "DOUTI0.ATTR_SOURCE", "DOUTU1.WAIT_FETCH"]
+++

E569: 28 of 28 hung, each recovered by a reset. To settle it: E420's own probe re-run unchanged in
the same session (is the module the cause), then the vertex program changed one step at a time (the
temporaries, the output count, the o6 constant) with a reset and the health triangle after each
job. The four-component question (formerly Q021) waits on it. E541 (the TA's object tables of 11.31: jobs that hung or faulted where a
set was described past what the vertex program writes) is a lead: here the set has four outputs and
the program writes o4 to o7.

**Correction 2026-11-11:** Q021 is merged into this question (retired as folded into Q180; a fold is not an answer), and its question is now a clause of the one above. Its question was: with 4 components (DOUTI0 bits 23:22 = 3) where does the texel land, given pa3 reads 1.0 on most pixels. Q021 waited on this question's hang. The merged question takes Q021's value, medium, over this one's low.

Its text: the textured triangle's primary program issues a `douti` of source 1 with the fetch wait and a `doutt` (E132). Bits 23:22 of DOUTI0 at 0, 1 and 2 put one, two and three components in `pa0` onward, the third 0, and the texel in the dword after them: `pa1`, `pa2`, `pa3` at every pixel (1062 of them). With bits 23:22 = 3, `pa0` is x on 1058 pixels and `pa1` is y on 1031, `pa2` is 0 on 1062, and `pa3` is 1.0 on 1004 pixels and the texel on 58 (columns 20 to 54); in the follow-up run `pa3` is 1.0 on 1056 and the texel on 6; `pa4` was not read. Narrowed in 11.15 (E420, ten runs): the shader reads pa3 = 1.0 on 1038 to 1062 of the 1062 pixels and a texel-valued dword in pa4 on all 1062, in ten of ten runs; the odd pixels of E132 recur as 24, 4 and 2 pixels with other values in the first run of a probe; two components give the texel in pa3 and one component 1.0 in pa3, but pa4 also holds texel-valued dwords there (1054 to 1062 pixels), so the fetch may write more than one dword. Not run: a source whose fourth component is not 1.0, to tell a component from a constant. Run again in 11.32 (E569, no result): the 28 triangle jobs of the probes all hung, so whether pa3 is a fourth component or 1.0 and where the texel lands is not shown; the hang is this question's first clause. To settle it, once the hang is understood: run bits 23:22 = 3 with the shader writing `pa3`, `pa4` and `pa5` out in turn, each probe at least five times in a fresh context, counting per pixel which of the three holds the texel and which 1.0, and compare with a source whose fourth component is not 1.0.
