+++
id = "E830"
claim = "R4-B stage fr (Q152 replicate of E817's FCF, 21 jobs in 3 blocks and 3 recoveries, ring_exit.s as in E817, module srcversion 99CD90DA, no reset between the arm and fcf in a block, one stop a block): in each block the controls kept the tick (e0; fc4 and fc4-r2, the tail call to the closed exit, next entry after the acted pass +24994 to +24995; fb and fb-r2, our replica with cfi.global, idf, wdf, phas end, nop.end, +24994 to +24995, 3 blocks of 3 each) and the pass ending cfi.global, idf, wdf, nop.end (fcf1, fcf2, fcf3) stopped it in 3 of 3 with E817's signature (4 ring entries, ACT_SEEN 3, both samples busy with CR_CLKGATESTATUS 0x000ccfa0, EVENT_STATUS 0x20000000, the EVENT_TIMER counting, USE0_SERV_EVENT bit 16 clear and frozen at 0x1114, 0x1114 and 0x1133, CCB read = write = 2, HostCtl dword 14 0, P3 one miscinfo not answered in 505 ms with 0 new ring entries); after each stop the reset, gate and health were ok, the re-armed pass idf, wdf, phas end, nop.end (fk1 to fk3, E817's fph) kept the tick (+24994 to +24995); every control PASS, frozen verdict 'H-REP held (3 held, 0 FAILED, 0 cannot tell of 3); H-NOREP refuted (0 held, 3 FAILED)'"
unit = "edm"
method = "R4-B (decision 10, reruns; each replicate a block that reproduces E817's stage f from the arm to fcf, job for job), dataset edm-closing-r4-q152, 2026-11-11, attempt out/20261111-082403 (run 08:24 Mac time, one stage fr, one attempt, no refreeze, stage exit 0, 21 jobs run and 0 void, 3 stops, 3 recoveries, health ok at the end), the laptop (host cedar), kernel 7.3.0-resgx545, module of the linux fork's branch resgx545 at a2788bd8 (srcversion 99CD90DA26E3AFF9C450517, installed = loaded, checked at the preflight; E817 ran on 230E0EF5), stock firmware sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a, health tool ~/sgxfive-test-s1b (sha256 46a2d063...), the task ring_exit of E817 byte for byte (sha256 3c031d998489f1699d53b469d5aae6403dd0beec2fc51e35ddb29556955a19cb, exit index 0x1974 read at each arm); per block bNe0 (after a reset, then the arm), bNfc4, bNfc4-r2, bNfb, bNfb-r2, fcfN, then fcfN's stop signed twice (signature, P3 one miscinfo, dumps), reset, fill, triangle, health and re-arm, then fkN, E817's fph; block N+1 only if fkN kept the tick; a stop in any other row ends the stage; fcf1 held out, fcf2 and fcf3 replicates; predictions H-REP (E817's exact signature) and H-NOREP (the tick kept) frozen in predictions/fr.tsv before the run; scored by the frozen score/score_r4b.py (out/20261111-082403/score-fr.txt, one SUMMARY line, scorekit from resgx545 6421c1c, the readers of R3k byte for byte); the signature match is the scorer's (busy, clk 0xccfa0, EVENT_STATUS 0x20000000, CCB read = write, dword 14 0, P3 not answered), the USE0_SERV_EVENT and EVENT_TIMER values are read from its lines. E817's fph and fph-r2 ran after fcf's stop and the re-arm; here fkN is that job, once a block, without a replicate. README.md and PREFLIGHT.md of the dataset are the pre-run documents"
tiers = ["HW", "infer"]
date = "2026-11-11"
data = ["edm-closing-r4-q152:out/20261111-082403/"]
terms = ["Event Data Master (EDM)", "CR_CLKGATESTATUS", "CR_USE0_SERV_EVENT"]
+++
**What ran.** E817 found that a plain tick pass ending `cfi.global, idf, wdf, nop.end` (FCF) stopped
the tick in the one job run, while the same pass with `phas ... end` (FB, FPH) kept it, giving the
verdict H-PHAS on one stopping job: the stage's rule never replicates a stopped row, so `fcf-r2`
was skipped. R4-B asks whether FCF's stop repeats, with E817's signature. Each replicate is a block
that reproduces E817's stage f from the arm to fcf, with no reset between the jobs of a block, so
the context FCF ran in is E817's. H-REP: each replicate stops the tick with E817's signature.
H-NOREP: each keeps it.

**Frozen verdict (as printed).** `SUMMARY: fr: every control PASS; FCF replicates {'fcf1': 'REPRO',
'fcf2': 'REPRO', 'fcf3': 'REPRO'}; block gates shut: none; H-REP held (3 held, 0 FAILED, 0 cannot
tell of 3); H-NOREP refuted (0 held, 3 FAILED, 0 cannot tell of 3)`.

**Results [HW].**

| block | e0, arm | fc4, fc4-r2 (next entry after the acted pass) | fb, fb-r2 | fcfN | fkN |
|---|---|---|---|---|---|
| 1 | ok, exit 0x1974 | +24995, +24995 | +24994, +24994 | stop, 4 entries, timer 0x103686a, serv_event 0x1114 | kept, +24995 |
| 2 | ok, exit 0x1974 | +24994, +24994 | +24994, +24995 | stop, 4 entries, timer 0x1018ffe, serv_event 0x1114 | kept, +24995 |
| 3 | ok, exit 0x1974 | +24995, +24995 | +24994, +24995 | stop, 4 entries, timer 0x101a10c, serv_event 0x1133 | kept, +24994 |

The passes acted as in E817 (ACT_SEEN 6 for fc4, 5 for fb, 3 for fcf, 4 for fk); every control row
had CCB read = write = 2 and dword 14 0 (E817: the same). The three stops share the signature
quantities E817 gave for FCF (and E537's): CR_CLKGATESTATUS 0x000ccfa0, EVENT_STATUS 0x20000000, the
timer counting between the two samples, the miscinfo of P3 not answered (505 ms, no new ring entry);
USE0_SERV_EVENT differs between the runs (0x1114, 0x1114, 0x1133 here, 0x1149 in E817) as a count
would, bit 16 clear in all [infer: the count of E154's event queue, not tested]. After each stop the
debugfs reset, the fill and triangle gate and the health check passed, and the re-armed fk pass kept
the tick.

**What it shows and does not.** FCF's stop repeats: 3 of 3 more jobs in E817's context, so the
frozen H-PHAS now rests on four stopping FCF jobs (E817 one, here three) against eight keeping FB
jobs (two in E817, six here) and five keeping jobs of the pass `idf, wdf, phas end, nop.end` (E817's
two FPH, the three fk here) rather than on one stopping job, and H-NOREP is refuted. In a plain tick
pass the `cfi.global` alone does not do what the `phas ... end` does for the tick; the `phas` end is
what the pass must reach [infer, as in E817: the phase end tells the EDM the task is finished]. It
does not show that the `phas` is sufficient in a pass that differs from these (a kick pass, E813's
B3, was not run with a `phas`), that the stop depends on the cfi's absence rather than on the order
of the three words, or what the P3 miscinfo's silence means beyond E814's and E817's (0 of 4 stops
answered in E817 and here). The signature is identical to E537's and E793's stops, so it does not
locate the stop by itself (E811).