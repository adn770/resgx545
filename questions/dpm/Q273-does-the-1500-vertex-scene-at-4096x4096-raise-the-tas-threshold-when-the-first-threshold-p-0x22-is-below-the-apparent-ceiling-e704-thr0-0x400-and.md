+++
id = "Q273"
question = "does the debugfs knob render_pb_pages take effect above 0x422 (E704: the TA's threshold register read 0x400 and dword 35 0x3fe for every P from 0x422 to 0x500, no raise in 8 of 8), does the 1500-vertex scene at 4096x4096 raise the TA's threshold when the first threshold P - 0x22 is below the apparent ceiling, and what steps dword 36 from 2 to 3 between 1350 and 1500 vertices"
unit = "dpm"
kind = "hw"
value = "high"
phase = 11
evidence = ["E704", "E625", "E630"]
terms = ["Dynamic Parameter Management (DPM)", "ta3d_ctl"]
+++
E625's rule for the raise (overflow, then a second run reaching the first threshold) fits 109 of the
110 timeline jobs of the partial-model batch and not wd-glist-1500 (E630: dword 36 = 3, no raise).
E704 ran that job at P = 0x422 to 0x500: the same timeline and control block in 8 of 8, thr0 0x400,
dword 35 0x3fe, dwords 37 and 38 zero. The register 0x0624 never read P - 0x22 above 0x422 (it reads
0x400 at the first sample of every job, where E705's jobs read P - 0x22), and the parameter-buffer
dumps are byte-identical, so the 8 jobs may be one condition and 7 repeats: the knob or the page
buffer may clamp P at 0x422. Whether pages beyond the first threshold plus 0x20 make the scene
raise (HP) is therefore untested above 0x422, not refuted. The first thresholds of the raises that
did happen at 4096x4096 (E625) are at most 0x100.

Open: whether the knob takes effect above 0x422 at all and where it clamps; whether a raise happens
at this scene when the first threshold is lower (P - 0x22 below 0x3e0), which would read the
exception as the threshold's ceiling [infer]; whether dword 36 (2 at 1350 vertices and below, 3 at
1500, both from E630 alone, the count of the global list's pages less 2) has a part; the vertex
count where dword 36 steps; and whether the two are one effect. The controls E704 planned below the
step (1400 and 1300 vertices) did not run: the tool takes whole triangles, a multiple of 3.

To settle it, in this order. First confirm that the knob takes effect: read it back and read the
first sample of register 0x0624 (P - 0x22 as in E705) at P = 0x400 and 0x420 before any P is
interpreted. Then 1500 vertices at P = 0x3e0, 0x400, 0x410 and 0x420 (predictions from the ceiling
reading frozen first: raise below 0x3e0 + a margin, none at and above). Then, at 0x422, the counts
1380, 1410, 1440, 1470, 1491 and 1497 (all whole triangles) with the control block and the global
list's count read after each. Pages above 0x422 only if a way is found that supplies them.
