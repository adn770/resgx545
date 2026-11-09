+++
id = "Q273"
question = "does the debugfs knob render_pb_pages take effect above 0x422 (E704: the TA's threshold register read 0x400 and dword 35 0x3fe for every P from 0x422 to 0x500, no raise in 8 of 8), does the 1500-vertex scene at 4096x4096 raise the TA's threshold when the first threshold P - 0x22 is below the apparent ceiling, and what steps dword 36 from 2 to 3 between 1350 and 1500 vertices"
unit = "dpm"
kind = "hw"
value = "high"
phase = 11
evidence = ["E704", "E625", "E630", "E734"]
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

Narrowed 2026-11-09 by source, not by a measurement. The first clause is answered for the module
that ran. In the kernel fork `sgx_render_pb_pages()` returns the default 0x422 for a `want` below
0x23 or above 0x422 (`sgx_render.c`; its KUnit asserts that 0x423 gives 0x422, 0x22 gives 0x422
and 0x23 gives 0x23); the knob `render_pb_pages` is an unclamped `debugfs_create_x32` read back as
written and clamped where it is used (`sgxfive_render.c`, `sgxfive_drv.c`). So E704's eight jobs
at P = 0x422 to 0x500 are one condition and seven repeats, as the record feared, the threshold
0x400 being 0x422 - 0x22, and a read-back of the knob after a write above 0x422 shows the value
written and not the value used. The knob's effect at its low end is separately shown (E705:
overflow at P = 0x28 and 0x30 follows P - 0x22). Read from the working tree of the fork's `sgx545`
branch; the commit that added the clamp (reported as f5bd8b434ad5a, 2026-10-22) and that no later
commit changed it were not rechecked here, and E704's installed module was not compared with this
tree. What stays open is what the first clause never tested: whether a raise happens at this scene
when the first threshold is below 0x3e0 (P below 0x402), which would read the exception as a
ceiling, and the part of dword 36.

Narrowed 2026-11-09 (S1, E734; the knob clause only). The knob takes effect below 0x422: in the
22 jobs of the stage the job's own 0x0624 read P - 0x22 at P = 0x200, 0x300, 0x3e0, 0x400, 0x410
and 0x420 (15 jobs) and 0x400, the clamp, at 0x422 (7 jobs), as a frozen per-job proof, so P down
to 0x200 reaches the TA. The raise clause is not answered: the frozen verdict is METHOD BROKEN
(the job used as a positive control, 1350 vertices at P = 0x3e0, was predicted to raise by every
hypothesis and did not), and nothing is concluded from it. Measured, and not held out: the
threshold was raised by 0x20 in 2 of the 22 jobs (1350 vertices at 0x300, 900 at 0x200) and in
none of the 19 other jobs whose second run reached thr0, among them 1500 vertices at P = 0x3e0 to
0x422 and 1350 at 0x3e0. Post hoc (read after the run, a reading and not a result): no raise at
any P from 0x3e0 up for 1350 or 1500 vertices; a limit on the raised threshold between 0x2fe and
0x3dd, or a P-only rule, fits; the dword-36 step lies between 1350 and 1380 vertices and, at P =
0x3e0, is not the step of the partial-render count. What stays open: where between P = 0x300 and
0x3e0 the raise stops and whether it is the same P for 1350 and 1500 vertices (1500 was not run
below 0x3e0), and what steps dword 36.
