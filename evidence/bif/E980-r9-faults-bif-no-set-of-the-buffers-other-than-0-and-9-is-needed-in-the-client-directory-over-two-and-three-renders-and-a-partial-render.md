+++
id = "E980"
claim = "R9-faults stage bif (Q076; debugfs alias_skip on tri -n 2 --keep-going on a new VM, E457's form, 14 jobs, every control passed): with the pairs and the three of buffers 12 to 14 left out of the client directory's alias, with 6, 7, 8, 10 to 14 (the 0x32 heap without TA3DCtl) and with every buffer but 0 and 9 (mask 0x7dfe) left out, two renders were exact (8 of 8 held-out rows and a replicate: every diff 0, the mask-free control's hashes), and so were three renders and two 1024 x 768 renders that both overflow at render_pb_pages 0x23 under 0x7dfe; TA3DCtl left out faulted 0x90400 at 0x32004001 and buffer 0 left out 0x91000 at 0x3000b021, as E457 and E745; frozen verdicts 'H-ONLY09 ... (8 of 8 rows decided)' and H-SET 'is not supported: 0 held, 8 FAILED, 0 cannot tell of 8'"
unit = "bif"
method = "R9-faults stage bif of the question-closing pass, round 9 (decision X-4 (a) of closing9/DECISIONS-R9.md; plan closing9/rank/rank-round9.md R9c-G, its held-out masks replaced by the builder with masks no record had run: closing-r9-faults README, Deviations 1), on the laptop (host cedar), 2026-11-13, one attempt out/20261113-084720 (dataset render-closing-r9-faults; lead log out/run-r9f.log; no stop, no lead decision; xf2 from 08:47, tri2 from 08:50, bif from 08:51 Mac time), kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (the linux fork r8-kernel at 2a650d74: debugfs vm_pte_flags, vm_pte_addr, alias_skip (commit 42) and render_pb_pages; the round 9 test boot, installed = loaded, every knob at its default at each stage start), stock firmware, tool ~/sgxfive-test-rgn4 (t4, sha256 e6951558..., resgx545 4623753 bound by source, TOOLSRC.sha256, recipe userspace/libsgxfive/Makefile; every row replayed on the library mock before the run, none refused), built on the session kit of resgx545 f32dfac (kit/run_stage.sh with run/hooks.sh: a debugfs reset before each job, the row's knobs written and read back before it and restored after it, the kernel's recovery then the kit's reset and strict health fill and triangle after every fault and every knob row, all drawing at the first try; no SGX recovery failed line); frozen before the first job: FROZEN.sha256 675739af..., PREDICTIONS.sha256 ae76ed3f..., FROZEN.commits (kit and replay inputs at resgx545 f32dfac, control outputs at data 2d666bfa); scored by the frozen score/score.py (out/ATT/score-STAGE.txt), re-run at the fold on the kept files with byte-identical output, every kept file decompressing to the raw sha256 the laptop logged (fold/reproduce.sh, reproduce.out). Each row wrote alias_skip (and render_pb_pages 0x23 for the 1024 x 768 rows) after the job's reset, read it back, and restored it after the job; the alias is made when the new VM's first render context is created, so each job's mask is its own. Jobs tri -n 2 --keep-going --wait-ms 6000 (E745's), tri -n 3 for bif-most-3r, and tri -n 2 ... --width 1024 --height 768 --keep-overflow for bif-c-ovf and bif-most-ovf. Outcomes as frozen: exact (every render's job line ok, or overflowed with its context kept for the 1024 x 768 rows, every diff 0, the hashes of the mask-free control of the same scene, the count of renders), needed (a BIF fault whose page lies in a buffer the mask leaves out, the buffers' addresses from E573's debugfs layout), fault-elsewhere, hang. Rows in order: bif-c0 (no mask), bif-c9 (0x200), bif-1213 (0x3000), bif-1214 (0x5000), bif-1314 (0x6000), bif-12to14 (0x7000), bif-h32 (0x7dc0), bif-most and bif-most-r2 (0x7dfe, replicates), bif-most-3r, bif-c-ovf (no mask), bif-most-ovf, bif-c1 (0x1), bif-c0-end (no mask); 0 faults of the held-out rows against the stage's #limit 10 and the two controls' own faults"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["render-closing-r9-faults:out/20261113-084720/bif/", "render-closing-r9-faults:fold/"]
terms = ["CR_BIF_DIR_LIST_BASE1", "ta3d_ctl", "CR_BIF_FAULT"]
+++
**What ran.** E457, E573, E745 and E761 had left out of a render VM's client directory alias
each of the buffers 0 to 14 alone, pairs among 1 to 5, 1 to 5 together, 6, 7, 8, 10 and 11
together over three renders and 1 to 4 or those five under partial renders: only buffer 0 (the
EDM's code heap) and 9 (TA3DCtl) were needed. The plan's rows would have repeated those; the
builder kept its form, its count and its controls and held out the masks no record had run:
the pairs and the three of 12 to 14 (Q076's open "pairs among 12 to 15"; 15 names no buffer,
E573), the 0x32 heap without TA3DCtl (6, 7, 8, 10 to 14), and every buffer but 0 and 9 (twice,
over three renders, and with both renders of a 1024 x 768 job overflowing the parameter buffer).
Frozen: H-ONLY09 (HI: only 0 and 9 are needed, so every held-out mask renders exactly) against
H-SET (HJ: a set each unneeded alone is needed together, a fault in a left-out buffer).

**Frozen verdict (as printed).** `Q076 alias_skip, H-ONLY09: a buffer is needed in the client
directory only if leaving it out alone faults: of 0 to 14 only 0 and 9 (E457, E573, E745, E761:
HI), so any mask without them renders exactly (frozen) (8 of 8 rows decided)`; H-SET `is not
supported: 0 held, 8 FAILED, 0 cannot tell of 8`; the replicates of 0x7dfe held. Every control
passed.

**Results [HW].** Every held-out row rc 0: two renders (three for bif-most-3r) each `job: ok`,
`diff: 0 of 4096 pixels`, hashes 0x99385a04ee01c585 and 0xab267bd98022a81d (the third
0x99385a04ee01c585), as the mask-free bif-c0 and bif-c0-end; bif-most-ovf `tri: 0 of 2 renders
ok, 2 overflowed`, `diff: 0 of 786432 pixels` each, hashes 0xc9e301d225fe2325 and
0xed1bce7108aded25, as bif-c-ovf and E761. No BIF fault line in any held-out row. bif-c9: `BIF
fault 0x90400 at 0x32004001` (E457's word and page); bif-c1: `BIF fault 0x91000 at 0x3000b021`
(E745's). The kit's health drew exactly at the first try after every row, the faults included.

**What it shows.** [HW] In the client directory of a render VM, the read-only aliases of the
EDM's buffers 1 to 8 and 10 to 14 are not needed, together, by a two- or three-render 64 x 64 job
or by a 1024 x 768 job whose two renders overflow the parameter buffer: of the EDM's buffers only
0 and 9 must be there (H-ONLY09 held out 8 of 8). So no pair or larger set of the buffers that
are unneeded alone is needed together, for these scenes.

**What it does not show.** Which requestor walks which list; a buffer reassigned within a job; the
requestors when their list is given to another directory while a job runs; a DPM reload under
other memory pressure (the partial renders here are those of a context that keeps its scene);
scenes other than these two.
