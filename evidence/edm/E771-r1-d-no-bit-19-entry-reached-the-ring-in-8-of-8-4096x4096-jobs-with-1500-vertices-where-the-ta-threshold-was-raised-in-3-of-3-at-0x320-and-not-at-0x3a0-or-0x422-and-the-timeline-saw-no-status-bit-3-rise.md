+++
id = "E771"
claim = "In 8 jobs of a 4096x4096 render of 1500 vertices under our event ring (ring_e1 with 12 rungs in slot 3, window 1) no entry of the ring carried pa1 bit 19 (22, 22, 22, 17, 17, 17, 17 and 17 entries, no drops in any slot), whether the TA's threshold was raised (render_pb_pages 0x320: the job's own register 0x0624 read 0x2fe and TA3DCtl dword 38 0x20, 3 partial renders, 3 of 3 jobs) or not (0x3a0: 0x37e, dword 38 0, 2 partial renders, 3 of 3; 0x422: 0x400, dword 38 0, 2 partial renders, 2 of 2), and the parallel register timeline of CR_EVENT_STATUS (1064 to 1411 samples a job, about 5.2 us apart at the median) showed no rising edge of status bit 3, which the reversed order of E155 maps to pa1 bit 19, in any of the 8 jobs; the controls of the stage reproduced E747 (a 64x64 triangle: its 9 entries in E747's order, 2 of 2 runs; a 1024x768 partial render: slot 2 bits 21 and 10, no bit 19, 1 of 1, the dispatch of every entry 100%); so the raise rule (H-RAISE: bit 19 only in raise jobs) and the threshold rule (H-THRESH: whenever the TA reaches its threshold) are refuted on these jobs and what stands is that bit 19 does not arrive here at all (H-NEVER), or arrives in a way neither the ring nor a sampled register shows; the frozen held-out rows read 12 held and 10 FAILED, the 10 being the three H-RAISE rows of the raise jobs and the order comparison of the timeline with the ring (D5) in 7 of 8 jobs"
unit = "edm"
method = "R1-events stages d0 and d1 of the question-closing pass, round 2, runs 1794299708-1672 (d0, the run whose gate opened d1) and 1794299717-1745 (d1) of the dataset edm-closing-r1-events, on the laptop (host cedar), 2026-11-10 09:35 laptop time (08:35 UTC), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), stock firmware (sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a), tool ~/sgxfive-test-s1b (sha256 46a2d06380814fdb07e7d711376f41fee4af8e6b3f75698d3e2ce52acfd6cc71, S1b's, with its regtimeline, sha256 prefix 079f63590ce87ff2); blob ring_e1 (692 instructions, sha256 6e5fd452660c4ff4c99e3251c3b1ec09ce4417a0b604b70c3274a92aae61aa90, armed with own_arm slots=0xf entry=0,1,2,3; window 1 logs every pass but a plain tick, 16 rungs in slot 0, 8 in slots 1 and 2, 12 in slot 3); d0 (one arm): d0-tri64 and its replicate (tool tri, 64x64) and d1-partial (tool tri --width 1024 --height 768 -n 2 --keep-overflow with render_pb_pages 0x30 written, read back and restored); d1 (a debugfs reset and an arm before every job, as S1b isolated them): d2-0x320, d3-0x3a0 (three runs each) and d4-0x422 (two), each the tool's probe --tri pixel --width 4096 --height 4096 --vertices (the green pixel program) with render_pb_pages 0x320, 0x3a0 or the default 0x422 written, read back and restored, under regtimeline reading 0x012c (CR_EVENT_STATUS), 0x0118 (CR_EVENT_STATUS2), 0x0624, 0x0658 and 0x0724 and the ring read after the job; the raise read from dword 38 of the results page's TA3DCtl copy; the stage's d0 gate (D0 and D1 reproduce E747 with dispatch 100%) computed by the frozen scorer and checked before d1; tables, predictions (predictions/d0.tsv, d1.tsv) and scorer frozen before the first job (FROZEN.sha256, PREDICTIONS.sha256); scored by the frozen score/score_r1.py d0 and d1 (out/score-d0.txt, out/score-d1.txt); out/d0-try1 (run 1794299374-1402) is the first run of d0, identical in result (out/score-d0-try1.txt), and out/d1-try1 (run 1794299383-1475) the first try of d1, stopped after its first job, d2-0x320, which the runner classed trigfail because its ringtool check looked for 'overflowed' in the last 4000 characters of the tool output that the timeline's samples fill; the probe's 'scene overflowed' line was in the full output (rc 3, the tick advancing, the health check ok), the runner was changed to read the whole output and the files refrozen with PREDICTIONS.sha256 byte-identical, and d0 and d1 were run again from their starts (the gate had been reset by the stop); the scored d1 is the rerun"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["edm-closing-r1-events:out/d0/", "edm-closing-r1-events:out/d1/", "edm-closing-r1-events:out/d0-try1/", "edm-closing-r1-events:out/d1-try1/"]
terms = ["Event Data Master (EDM)", "CR_EVENT_STATUS"]
+++
**What ran.** Q033's open part is which hardware event sets bit 19 of the event word. E747 found
none of the 138 events of 14 jobs carrying it, the two overflowing partial renders included. The
reading offered for the round (note on Q033) was that bit 19 is status bit 3, a threshold event of
the dynamic parameter manager, that the init scripts enable, and that it comes with the TA raising
its first abort's threshold (H-RAISE) or whenever the TA reaches the threshold (H-THRESH); the
alternative was that it never arrives (H-NEVER). D2 is a job where the raise reproduced in S1b
(E753), D3 and D4 jobs where it does not and the TA still reaches its threshold.

**Frozen verdict.** d0: `controls held (D0 and D1: E747 reproduced, dispatch 100%); rows: fit: 3
held, 0 FAILED, 0 cannot tell/void; control: 6 held, 0 FAILED` (the same in both runs), the gate
open. d1: `H-NEVER (or the ring lost it): no bit-19 entry in any raise job; rows: held out: 12
held, 10 FAILED, 0 cannot tell/void; refuted ['D5 (reversed order, E155/E747)', 'H-RAISE (bit 19
only in raise jobs); H-THRESH (the TA reaches thr0 here too)']; control: 10 held, 0 FAILED`. The
raise reproduced in the three D2 jobs (a held-out row, held; the job's own 0x0624 read the written
knob in 8 of 8 jobs, a control), so H-RAISE's row failed in each of them and the stage was not
'cannot tell'; the
D3 alternative row of H-THRESH (at least one bit-19 entry whenever the TA reaches thr0, here 2
partial renders a job) failed in 3 of 3.

**Results [HW].** Every job: bit-19 entries 0, drops [0, 0, 0, 0], slot 0 not full, status bit-3
rising edges 0. The rows:

- d2-0x320, -r2, -r3: 0x0624 0x2fe, dword 38 0x20 (raise), 3 partial renders, 22 entries.
- d3-0x3a0, -r2, -r3: 0x0624 0x37e, dword 38 0 (no raise), 2 partial renders, 17 entries.
- d4-0x422, -r2: 0x0624 0x400, dword 38 0 (no raise), 2 partial renders, 17 entries.
- d0-tri64 and -r2: 9 entries (0:8, 1:9, 3:4, 3:22 and five 0:8, slot:bit), as E747; d1-partial: 21
  entries with slot 2 bits 21 and 10 and no bit 19.

The timeline's rising edges of status bits over the jobs were bits 0, 1, 6, 12, 13, 14, 18, 20, 26
and 31 (some in some jobs), never 3.

**Post hoc [infer; read after the run, not held out].** The sampling limit of the timeline: the
timeline read about 1064 to 1411 samples a job over 1.3 to 2.8 s; the median spacing was 5.2 us,
the 90th percentile 20 to 62 us and the 99th percentile 9 to 12 ms (the first interval of every
timeline, 0.83 to 1.4 s, and gaps of 0.24 to 4.8 ms in the 20 ms after it are in the long tail). A
status bit that rose and fell between two samples, or inside one of those gaps, would not be seen;
a bit set for only a few microseconds is below what this timeline resolves. So 'no bit-3 edge' is
the timeline's reading and H-NEVER is not shown by it alone. The ring did not lose the event by
overflow: no slot dropped an entry and slot 0 never filled, but an event that the PDS merged with
another one or that never reached it is not excluded. The D5 row (the timeline's order of rising
bits equals the ring's, within one bit) failed in 7 of 8 jobs, all but d4-0x422: the bits that
rise within a few microseconds (statuses 1, 12, 18 and 0) came in another order in the samples than
in the ring (for example the ring's 1, 12, 18, 0 against the timeline's 1, 12, 0, 18), which is
the timeline's resolution again, not a fact about bit 19, and E747's ring order is not touched by
it. The partial-render counts (3 at 0x320 and 2 at 0x3a0 and 0x422) are the scorer's count of the
stretches of the timeline where register 0x0658 has bit 0 set, an instrument reading that no
frozen row expected.

**Not shown.** The event that sets bit 19, if one does: a longer or finer timeline (an in-task
sample of `CR_EVENT_STATUS` would need a task that reads it, not tried), a job that reaches the
threshold with the parameter buffer exhausted in another way, and any event that the PDS does not
hand to the task. The two E155 handlers that test bit 19 post nothing; whether the hardware
delivers it at all stays open (Q033).
