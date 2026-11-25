+++
id = "E1200"
claim = "r44-n3i-n3 stage lf (row LF, module 079DD0D1, fork ec6511d5de87, emitsb_sbc43s, image land at fw14, form=sbc43, sideband 0xc43, s2 0, flagged, user present): after the plant WF (E1199) and one stock fill as the begin draws (K7): job 1 done with post sa0 0x00000002, sa1 = M1 0x005d1000 (the plant kept), sa2 0x01049b60, sa13 = M13; then, before job 2 was served, BIF_FAULT 0x0000000f (list 15, page 0; the scorer: job 1's post sa0), the tick stopped and job 2 was never served; the runner stopped (class hang, rc 4) and the kit's reset recovered it; 'Q128-N3I-LF RULE: LF-EARLY0'; LF-SA1 FAILED against its prediction (held), LF-EVT FAILED against its prediction (held), LF-EARLY0 held, every other prediction held: one fill left M1 in attribute 1 and changed sa0 and sa2, and the stop faulted at page 0 with sa0 = 2"
unit = "edm"
method = "r44-n3i-n3 (render/closing-r44-n3i-n3), stage lf of the question-closing pass (round 44: row LF, closing29/n3i/design.md section 3.5; flagged class, the user present with a reset ready; the user's decisions A-E of the design all (a), 2026-11-23), dataset render-closing-r44-n3i-n3; attempt out/20261124-010057 (01:01:18; stage lf exited 4 at its one row, the runner's stop the design planned, so the driver did not score it); on the laptop (kernel 7.3.0-resgx545, module srcversion 079DD0D13F231EEAC52FE0F installed and loaded alike, linux fork r42-kernel ec6511d5de87 built on cachix 2026-11-21 (closing29/kernel39c/deliver/ec6511d5de87/manifest), the one-shot boot of 2026-11-22, no rebuild or boot for round 44; stock firmware), the kit's owntask job kind with a job list per row, each job's BIF_INT_STAT and BIF_FAULT read before and after it (K5), K7's per-stage draws and K8's draw lists (begin_draws a comma list of fill and tri, run once in order, each draw kept and exact) (kit/ = resgx545 ce01a0c4, branch r44-n3i, its fwtask_run.py byte for byte): our task owntask/emitsb_sbc43s.blob (asm/fwtask/emitsb_sbc43s.s, sha256 987b0e4e1dc0ba9ec6e2583bb0edd77afef230d7121070daa18a8171dd4a86ad, asm/fwtask/fwtask.map at ce01a0c4; emit word 0xfb20b18800c08184, sideband 0xc43) armed once with own_arm `slots=0x1 entry=0 pds=land pdsat=fw14 form=sbc43` after the stage's reset and its begin health (begin_draws fill: one stock fill, no triangle), then one row of two jobs: command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223), then command 6 (the after-read: entry 0 stores sa0-sa31 into dwords 224-255, which the host first fills with 0xdeadc0de) on the next tick pass (no kick); the results page, the registers (snap0, snap9, the runner's stop dump) and the record kept; the blob and form of rounds 42-43, unchanged on the running module (E1184-E1187), and the land image of rounds 40-41 (E1176, E1178), its first run on this module; health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 3e1deb89dc43485bb968787baf3d6d05800ccbe438fddb773c8d927d08b319c0 (66 lines), PREDICTIONS.sha256 3c04abf89f20aee2f3a4b02ef2be1cc381b6665321e01412a1beae425c09c7c3 (2 files), pins in FROZEN.commits (the kit and the blob sources at ce01a0c4; round 43's kept stages N1 w, N1 v and N2 f at data b3df8fc21; t30's source 42c4de7); the frozen predictions predictions/lf.tsv, the rule score/score.py, scored after the session (closing29/r44-n3i-logs/score-r44-n3i-n3-lf.txt) and again by hand on the kept directory (fold/reproduce-lf-20261124-010057.out), the same bytes; the JOB, BIF, FAULT, SURVEY, ATTR and EVENTS lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen"
tiers = ["HW", "infer"]
date = "2026-11-24"
data = ["render-closing-r44-n3i-n3:out/20261124-010057/lf/", "render-closing-r44-n3i-n3:fold/"]
terms = []
+++
**What ran.** land (rows L, H3 and LC2's 16 dwords byte for byte: Ma and Mb to attributes 24 and 26,
the doutu, no V0 or V2 and no `tim`, so the tick runs) right after the plant WF (E1199), with
`begin_draws = "fill"`: between the plant's emit and land's ran the plant's disarm and exit resets,
this stage's begin reset with one stock fill and the arm [HW, the stages' kernel logs; DR passed].
Jobs: V's two (E1185): job 1 the emit on the tick pass, job 2 command 6 on the next tick pass. The
question: what does one fill leave in attributes 0, 1 and 2 (LF-SA1: 0x01000000 as in F; LF-EVT: sa0
0 and sa2 an event's timer word; LF-TICK; LF-ONE), and where does land's early stop fault with them
(LF-EARLY0 or LF-EARLY1)?

**Frozen verdict (as printed).** The stage stopped, so the driver did not score it; the frozen
scorer was run after the session (closing29/r44-n3i-logs/score-r44-n3i-n3-lf.txt) and again by hand
on the kept directory, the same bytes:

```
SUMMARY: lf: controls: lf1-a:B: FAILED; lf1-a:J2: FAILED
Q128-N3I-LF RULE: LF-EARLY0
PREDICTION LF-AOTHER: predicted printed, read held: printed
PREDICTION LF-EARLY0: predicted held, read held: held
PREDICTION LF-EARLY1: predicted failed, read FAILED: held
PREDICTION LF-EVT: predicted held, read FAILED: FAILED
PREDICTION LF-ONE: predicted failed, read FAILED: held
PREDICTION LF-SA1: predicted held, read FAILED: FAILED
PREDICTION LF-SERVE: predicted failed, read FAILED: held
PREDICTION LF-TICK: predicted failed, read FAILED: held
```

PLANT (W-SA1 of stage wf), PG, E0, T0, J1 and DR passed; B (BIF_FAULT 0 after the row) and J2 (job 2
done) failed, read by LF-EARLY0, which names the stop (the frozen rule of X, LC2, LV, V and F).
**LF-SA1 failed against its prediction (held): post sa1 was M1, not 0x01000000.** **LF-EVT failed
against its prediction (held): post sa0 was 2, not 0.** LF-EARLY0 held as predicted; LF-TICK,
LF-ONE, LF-EARLY1 and LF-SERVE failed as predicted; LF-AOTHER (printed) read held. LM-V0 held in N2
(E1198), so the design's fold-time cannot-tell rule for LF's attribute 0 and 2 outcomes is not met.

**Results [HW].**

- Job 1 done: X0 0x5a5a3303, run id 1, cmd_after 0, 8 ticks; K5 BIF_FAULT 0 before and after.
- Job 1's post sa0 0x00000002, sa1 = M1 0x005d1000, sa2 0x01049b60, sa13 = pa1 = M13; post sa3-sa31
  and pa0-pa15 equal WF's word for word. The survey's pre (before the emit) read sa0 = V0 and sa2 =
  V2.
- Job 2's K5 pre already BIF_INT_STAT 0x000d0400, BIF_FAULT 0x0000000f (list 15, page 0), post the
  same; job 2 not done (cmd_after 6, dwords 224-255 still 0xdeadc0de); the tick stopped; snap9 and
  the stop dump the same fault. The kit's reset and both draws recovered it (health ok,
  closing29/r44-n3i-logs/health-r44-n3i-n3.log).
- The kernel: lf's arm after the one fill "1 events seen".

**What it shows.** One stock fill after W's plant left attribute 1's M1 **[HW]**: LF-SA1 failed, and
row F's 0x01000000 after the same plant, boundary and one fill (E1187) did not repeat. With FF's two
fills (E1191) that is two fill sequences that left the planted word, against one that rewrote it
**[HW]**. The same fill changed what the rewrite left in sa0 and sa2: 2 and 0x01049b60, where with
no draws (LM, E1198) they were V0 and V2 **[HW]**. On that bank land stopped at page 0 **[HW]**,
while sa1 held the unmapped M1: with LM, where sa0 = V0 and the stop faulted at sa1's page, the stop
faults at page 0 when sa0 holds a word below one page and at sa1's page when sa0 is V0 **[HW, two
rows of this round; LC's (E1176, E1178) and LV's and V's (E1183, E1185) fit]**. That the tick pass
reads through sa0, then sa1 (H-SA0), is **[infer]**. sa2 0x01049b60 has an EVENT_TIMER sample's
shape (bit 24 alone in 31:24, bits 23:0 below 400000, E1133) **[infer]**; sa0 2 is not the 0 LF-EVT
named.

**What it does not show.** Why F's fill wrote attribute 1 and this one did not (the image read after
it differs: crumb3 in F, land here); where sa0's 2 comes from; which access read page 0; one run.

**Correction 2026-11-25:** Round 45 answered two of this record's open points. Where sa0's 2 comes
from: crumbz, which stops the tick and writes no attribute, read sa0 2 and an EVENT_TIMER-shaped sa2
after one fill and M1 kept (ZF, E1225), so the fill's events, not land's running tick, wrote them
(R-DRAW held) **[HW]**; LF2 (E1213) read this record's triple shape and page-0 stop again **[HW]**.
And "that the tick pass reads through sa0, then sa1 (H-SA0)": row Q (E1233) faulted at sa1's page
with both sa0 and sa1 holding words our rows never saw mapped, sa0 the higher, so H-SA0 is falsified
unless sa0's word is mapped; the lowest faulting page fits every stop read so far as well
**[infer]**. This record's frozen verdict and readings stand.

**Correction 2026-11-25 (round 46):** Round 46's land rows on module 10BBF3BF (fork r46-kernel
c5094783eb88) stopped with sa0 2 and M1 in sa1 at 0x005d1000, sa1's page, not at page 0: after two
fills twice (LFF2 E1239, LFF3 E1241) and after three (LF3F E1243), the PAGE0 outcome FAILED against
its prediction (held) each time **[HW]**. So the stop does not fault at page 0 whenever sa0 holds a
word below one page, and the two readings row Q left (the lowest faulting page kept; sa0 read first
with 0x005d2000 mapped) both predicted page 0 there **[HW against the frozen predictions]**. The
earlier page-0 stops ran on modules 83FBFD86 and 079DD0D1, and the two with the bank (2, M1), LF and
LF2, after one fill: the module and the number of fills changed together, and no row splits them
**[infer]**. Row Q's stop at sa1's page with 0x005d2000 in sa0 repeated on 10BBF3BF (Q2, E1245)
**[HW]**. This record's "the stop faults at page 0 when sa0 holds a word below one page and at sa1's
page when sa0 is V0 [HW, two rows of this round]" holds for the rows it names, not as a rule: its
own bank, (2, M1), stopped at sa1's page in LFF2, LFF3 and LF3F. The 2026-11-25 correction's "the
lowest faulting page fits every stop read so far" no longer fits. This record's frozen verdict and
readings stand.
