+++
id = "E836"
claim = "R4 stage e3p, the end of the pass (r4-events, ring_skip3p.s, 2 of its 4 jobs run, the stage ended by its stop rule at its first B1P; Q152's slot 3 clause): the fill without the skip (b0, control, E823's B0) completed with one slot 3 end-of-render entry and the tick alive; with slot 3's first end-of-render pass skipped once and ended by our task idf, wdf, phas #0, #0, pixel, end, parallel, nop.end instead of the closed handler (b1p, held out, hold_recovery Y) the fill was held (the tool's job hung, rc 1) and the tick was found stopped after the 50 ms status watch, with E537's busy signature (CR_CLKGATESTATUS 0x000ccfa0, USE0_SERV_EVENT 0x422, bit 16 clear and frozen, the event timer counting, CR_EVENT_STATUS 0x20040000), CCB read = write = 3, HostCtl dword 14 0 and P3 one miscinfo not answered in 505 ms with 0 new ring entries; frozen verdict 'H-PHAS-ANY REFUTED, H-SLOT3-MORE consistent (1 row groups)'; read after the run, the ring held 10 more ticks on the 25000-unit grid after the slot 3 entry (then full), where E823's B1, which ended the same pass idf, wdf, nop.end, logged nothing after it, so the phase end let the tick run on for at least 10 ticks and the stop came later"
unit = "edm"
method = "R4 session r4-events stage e3p (round 4, decision 9; plan closing4/events/exp-events-r4.md section 4), dataset edm-closing-r4-events, attempt out/a1 (run 2026-11-11 20:56:46 Mac time, gated on kp's kept stage.json, the session's last stage; b0 and b1p run, then the stage ended with exit 8 by its rule (its first stop ends it; the runner's line says 'a control stopped the tick'), the stop signed and recovered (reset, gate and health exact); the lead did not resume, so b1p-r2 and b1p-r3 did not run), the laptop (host cedar), kernel 7.3.0-resgx545, module of the linux fork's branch resgx545 at a2788bd8 (srcversion 99CD90DA26E3AFF9C450517, installed = loaded), stock firmware sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a, fill tool ~/sgxfive-test-s1b (sha256 46a2d063...); the task ring_skip3p.s (sha256 3b35d3af..., gen/r4blobs.py: R3k's ring_skip3.s without its str #77, the skipped end ended by the landed own_end), which logs every entry of the four PDS #13 slots in rings and, when the host's flag is set, skips slot 3's first end-of-render pass (pa0 0, pa1[23:0] 0x10) once, logging it with flag 3; each job a debugfs reset and an arm, hold_recovery Y in b1p (put back to N and read back after), a fill through the tool, a bounded wait for the slot 3 entry in the page, the status watch (below, E837), the tick checked (a stop signed first: signature twice, then the host's clears, P3, dumps), the tool collected (6 s, killed), then reset, gate and health; predictions frozen in predictions/e3p.tsv before the run; scored by the frozen score/score_r4e.py e3p (out/a1/score-e3p.txt, scorekit from resgx545 5a13042), re-run on the kept files on 2026-11-11 with byte-identical output; the ring of b1p and of E823's b1 (the session's fixture tests/fixtures/real/e823-b1.json) read after the run with the session's own reader (score/r4common.py read_page) by a scratch script, not in the copy"
tiers = ["HW", "infer"]
date = "2026-11-11"
data = ["edm-closing-r4-events:out/a1/e3p/"]
terms = ["Event Data Master (EDM)", "CR_CLKGATESTATUS", "CR_USE0_SERV_EVENT", "CR_EVENT_STATUS"]
+++
**What ran.** E823 skipped slot 3's end-of-render pass once and ended it `idf, wdf, nop.end`: the
fill never completed and the tick stopped (1 job). After E817, E830 and E835 found the phase end
to be what a tick pass and a kick pass need, B1P asks the same of the slot 3 pass: H-PHAS-ANY (the
pass ended with the phase end is finished for the EDM: the tick alive through the watch, the fill
held because the closed handler never ran) against H-SLOT3-MORE (it needs more: a stop with E537's
signature). The stage's stop rule ends it at its first stop, so a stop leaves the two replicates
unrun by design.

**Frozen verdict (as printed).** `SUMMARY: e3p: B0 held; H-PHAS-ANY REFUTED, H-SLOT3-MORE
consistent (1 row groups); H-LEVEL consistent (1 row groups), H-PULSE REFUTED; H-W consistent (2
row groups), H-ALL REFUTED, H-NONE REFUTED; stops 1 ['b1p']; every control PASS (10); 12 of 12
non-control rows decided; ... stage exit 8: b1p: a control stopped the tick: the stage ends (reset
and gate exact)` (out/a1/score-e3p.txt; the status rows are E837's).

**Results [HW].**

| job | class | skipped | slot 3 entries | slot 3 seen after | tool | tick after the watch |
|---|---|---|---|---|---|---|
| b0 | ok | 0 | 1 (flag 1, `pa1` 0x03000010) | 4.52 ms | rc 0, the fill completed | alive |
| b1p | stop | 1 | 1 (flag 3, `pa1` 0x03000010) | 4.76 ms | rc 1, job hung | stopped |

b1p's stop: HostCtl dword 12 frozen at 1051 and `USE0_SERV_EVENT` at 0x422 (bit 16 clear) in the
three alive reads and the two signature samples, `CR_CLKGATESTATUS` 0x000ccfa0, the event timer
counting (0x105c76d, 0x101e9f0), `CR_EVENT_STATUS` 0x20040000 (bit 18 set), CCB 3 and 3, dword 14
0; the host's writes of `CR_EVENT_HOST_CLEAR` (E837) came after the signature, and P3, one
miscinfo sent after them, was not answered in 505 ms (the CCB write offset 4, read 3, no new ring
entry). The reset, the gate and the health check after it were exact.

**Read after the run [HW, post hoc].** b1p's slot 0 ring holds 5 ticks, the fill's kick entry
(`pa0` 0, `pa1` 0x02000100), the slot 3 entry, then 10 ticks with K 3 and `pa2` 0x01061a70 on the
grid (6686 units after the slot 3 entry, then 24990, 25000 seven times and 25005), and is then
full; b0's has the same shape. E823's b1 (the same pass ended `idf, wdf, nop.end`) logged nothing
after the slot 3 entry: the tick stopped at its end. HostCtl dword 12 froze 59 passes after the
last read before the job (992 to 1051), against 39 in E823's b1 (970 to 1009), whose ring ended
at the slot 3 entry: [infer, the time from that read to the window assumed equal in both jobs]
about 20 more passes, so the tick ran on for about 20 ms after the skipped pass and stopped inside
the watch. A host write that cleared `CR_EVENT_STATUS` bit 18 did not bring it back (P3 after it
not answered).

**What it shows.** The slot 3 end-of-render pass skipped once and ended with the phase end
stopped the tick by the end of the watch, as frozen (H-SLOT3-MORE consistent, 1 job): a held
render with its end-of-render pass skipped does not keep the tick even with the phase end. Read
with the ring, the phase end did end the slot 3 pass for the EDM (at least 10 ticks were served
after it, where E823's pass without it stopped at once), and what stopped the tick came later:
[infer] something the closed end-of-render handler does for the held render that a later pass
needs (an acknowledgement, the render's state), the EDM stopping in a later closed pass that waits
for it; not tested. So "the phase end is what the EDM needs at the end of a pass" holds for the
slot 3 pass's own end too, and skipping the closed slot 3 handler is a different fault.

**What it does not show.** One job (the stage's rule ends it at the first stop, and the lead did
not resume): the replicates did not run. When the tick stopped and in which pass (the ring was full
after 10 ticks; dword 12's 20 passes are an estimate); whether a slot 3 pass that is not skipped,
or the closed handler called after our phase end, keeps it; whether the later stop needs the held
render (the fill) or the unacknowledged bit 18 (clearing bit 18 from the host did not restart a
stopped EDM, which does not say what would have kept it).

**Correction 2026-11-12:** Read offline after the hypothesis (E849, post hoc), the stop's time is
no longer an estimate: b1p's page counted 10 more slot 0 passes with the ring full (dword 16), so
the tick stopped after exactly 20 slot 0 passes after the fill's kick entry, the twentieth about
19.3 ms after it, which is 2 x HostCtl dword 5 (`host_ctl.hw_recovery_sample_rate`, 10); "about 20
passes", "about 20 ms" and "dword 12's 20 passes are an estimate" above give way to that count.
And "something the closed end-of-render handler does for the held render that a later pass needs
(an acknowledgement, the render's state), the EDM stopping in a later closed pass that waits for
it" becomes, on the stop dump: the EDM's own lockup check. The dump taken at the signature holds
dword 3 (`host_ctl.ukernel_detected_lockups`) = 1, dword 8 (`host_ctl.interrupt_flags`) = 1,
`sw_events` 1 and TA3DCtl dword 58 = 0xaac267c2, all 0 at the arm, the marks of E353's routine;
[infer] its 3D check sampled a progress word at pass 10 and found it unchanged at pass 20, which
the skipped closed handler would have prevented. Which state it reads stays open (Q295).
