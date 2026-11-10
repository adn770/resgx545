+++
id = "E748"
claim = "In a firmware task of ours in the general slot (slot 0), run on the 1 kHz tick, pa0 to pa4 read the same words as sa64 to sa68 in 3 of 3 read passes (sa64 = 2, sa65 = pa1 = 0x02000000, sa66 = pa2 = 0x01061a70, sa67 = pa3 = 0x04000004, sa68 = pa4 = 0x00030001), with sa0 = 0x32004000 and not pa0; the frozen held-out prediction sa66 = 0x01061a70 (from E537 and E532, never read before) held in 3 of 3 read passes, and a write of a marker to sa67 or to sa68 by the allowed mov to sa was read back through pa3 or pa4 in the same pass and through both banks in the next task, for 3 of 3 markers each (0xb2a06701 to 0xb2a06703, 0xb2a06801 to 0xb2a06803), the tick staying alive and the values the control read written back and read back (restore67, restore68) in the same stage"
unit = "edm"
method = "S2 stages e2r and e2w of the question-closing pass, paths relative to edm/closing-s2/ of the dataset. e2r (run 1794265160-18705, 2026-11-09 23:59): asm/pa_read.s (71 instructions, blob sha256 2f16ef614d06...), one arm with slots=0x1 entry=0; on host command 1 the task stores pa0 to pa4, sa64 to sa68, sa0 and CR_TIMER to the results page, then arms command 9 for the next pass, which stores pa3, pa4, sa67 and sa68 again; no sa write; 3 read passes. e2w (run 1794265168-18785), which the runner starts only behind the e2r gate (sa66 = 0x01061a70 in 3 of 3 valid read passes): asm/pa_write.s (135 instructions, blob sha256 1fe6ccb60ad2...), a control read pass, three writes of sa67 (command 2, M = 0xb2a06701 to 03), three of sa68 (command 3, M = 0xb2a06801 to 03), then restore67 and restore68 with the values the control read; the writer reaches its tail call with p0, p1, p2, p3 = 0, 0, 1, 1 as E536's writer; the closed tick handler runs after every pass (tail call); kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B, stock firmware (sha256 6a00268e9d4c...), tool ~/sgxfive-test-s1 as the other S2 stages; predictions frozen before the run, scored by the frozen score/score_s2.py e2r and e2w; the health after every job (class ok, tick advancing) and the end-of-stage reset and gate are in the stage logs"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["edm-closing-s2:out/e2r/", "edm-closing-s2:out/e2w/"]
terms = ["Event Data Master (EDM)"]
+++
**What ran.** Q098 asks whether pa_n of an EDM task is sa_(64+n): PDS #13 would pass the three
words of an event and the task's attribute store would hold them from sa64. E537's writer, which
wrote sa65 and was not followed by its reader, would then have written what the closed task reads
as pa1. The proposal's two stages read sa64 to sa68 and, only if sa66 read E532's pa2, wrote sa67
and sa68, two registers whose closed-task use was not measured.

**Frozen verdicts.** e2r: `H-D read side held (sa64..66 = pa0..pa2); sa66 prediction 3 of 3 valid`,
gate open. e2w: `cmd 2: H-D (pa3 follows in 3/3); cmd 3: H-D (pa4 follows in 3/3); ctl ok;
restores ['restore67 ok', 'restore68 ok']` (out/score-e2r.txt, out/score-e2w.txt). Both controls
(pa0 = 2 on the read pass, the control read pass of e2w) passed.

**Results [HW].** Each read pass: pa0 0x2, pa1 0x02000000, pa2 0x01061a70, pa3 0x04000004, pa4
0x00030001 and sa64 to sa68 the same five words; sa0 0x32004000. The next pass (command 9) read
pa3, pa4, sa67 and sa68 as before. After `mov sa67, M` the same pass read M in pa3, and the next
task (the next tick) read M in both pa3 and sa67; the same for sa68 and pa4. Every marker's
neighbour register kept its value (sa68 and pa4 while sa67 was written, 0x00030001). The markers
persisted from job to job inside the arm (the control read of w67-2 saw w67-1's marker in pa3 and
sa67), until restore67 and restore68 wrote 0x04000004 and 0x00030001 back; all 9 jobs of e2w were
class ok, the tick advanced after each, health was ok, and the end reset and gate were exact. The
writer's p0 to p3 at its tail call were 0, 0, 1, 1 in every write job.

**Reading [infer].** In an EDM task pa_n names sa_(64+n), at least for n = 0 to 4: the three
words PDS #13 hands the task land in sa64 to sa66, and the next read of pa_n returns what an sa
write left, for pa3 and pa4 in these jobs. E537's writer wrote sa65, which the closed task reads
as pa1 (Q152 asks what the closed task does with it). A fill has the same read side, where a write
to sa_n is read through pa_n (E380) and a `mov` to pa_n is lost; the alias seen here therefore does
not say that a write to pa_n lands in an EDM task. Whether the PDS rewrites sa64 to sa66 for every
event (the reads here were ticks, whose words do not change) is not shown; pa2 does change per
event (E746, E747).

**Not shown.** The direction pa to sa (a `mov` to a pa register: the verifier of the firmware
tasks refuses it), pa5 and above and sa69 and above, sa64 to sa66 written (not run: sa65 is the
event word), the alias in slots 1 to 3, whether an sa write survives a reset (E536 saw sa100 and
sa127 survive one; these registers were put back before the reset), and the alias for an event
that is not a tick.
