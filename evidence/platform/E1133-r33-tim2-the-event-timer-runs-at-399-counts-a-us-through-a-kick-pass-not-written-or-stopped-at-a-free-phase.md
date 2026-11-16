+++
id = "E1133"
claim = "r33-tim2 on module 7CE8E38E (fwsim's tim, E1130; the rerun of E1131), stages t1 (CR_EVENT_STATUS, CR_CACHE_CTRL and CR_EVENT_TIMER) and t1d (CR_EVENT_TIMER alone), regtimeline over plain 64x64 triangles, every control passed, every row held out: CR_EVENT_TIMER counts down 398.9 to 399.1 a us with a period of 1002.40 to 1002.65 us (H-TIM-399 30 of 30 clauses, H-TIM-400 refuted), keeps bit 24 alone in 31:24 and bits 23:0 at most 400000 (H-TIM-EN, H-TIM-RANGE, H-TIM-RELOAD 15 of 15 rows; H-TIM-24 refuted), sits at a phase spread over the period at the kick pass's CR_CACHE_CTRL write (H-TIM-ASYNC held, H-TIM-SYNC refuted) and is not written or stopped through the pass (H-TIM-WRITE refuted 11 of 11: 120 to 300 us after the change within 345 counts of its pre-change line); H-TIM-LINE is not supported (19 held, 3 FAILED of 22: the window's median |residual| 69442.7, 72830.1 and 1049.6 against at most 800 in t1-01, t1-07 and t1-08); with E1133's running count fwsim's M2 kick under replay passes PDS #14's tim read and stops on a memory fault at 0x0002007c in the task PDS #14 starts"
unit = "platform"
method = "r33-tim2 (render/closing-r33-tim2), stages t1, t1d of the question-closing pass (round 33: the rerun of r33-tim, E1131, whose controls failed on the sample interval, with the interval premise and the held-out values from E1131's post-hoc readings; safe class; record E1133 reserved by the frozen README), dataset render-closing-r33-tim2; attempt out/20261116-213803 (scores score-t1.txt, score-t1d.txt); on the laptop host cedar over the travel cable, kernel 7.3.0-resgx545, module srcversion 7CE8E38EDB97FC5EA4F6C90 (N1; installed and loaded alike, fork 8bc0877e8603), stock firmware, tool ~/sgxfive-test-t10 (t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, resgx545 a581c06) under ~/regtimeline (sha256 079f63590ce87ff2a1ac5499291e52340ff448d9c5e41942a9420264764de803, tools/sweep/regtimeline.c, read only through /dev/mem), every job `regtimeline TOTAL 0.005 REGS -- ~/sgxfive-test-t10 tri --width 64 --height 64` after a debugfs reset (t1: 0.06 and 0x012c,0x0804,0x0acc, 11 rows with controls t1-c1, t1-c2, t1-c3; t1d: 0.04 and 0x0acc, 4 rows with control t1d-c1), no knob and no register write; the rows tables/STAGE.txt from gen/make.py, every row held out, the frozen predictions predictions/STAGE.tsv; the post-hoc readings fold/posthoc.py and posthoc.txt, not frozen; the fwsim run of the fold (resgx545 branch r33-fold-tim2: tools/fwsim with seeds.toml [events] emit_tim, crates/pysgx/tests/test_fwsim_m2.py) offline; freezes: FROZEN.sha256 2dd944444d38f03265f66806bf7a3e0ad5c9b141764de1a99f9cb64499ab1499 (37 files), PREDICTIONS.sha256 485df3679c567bcdf2c32ca18cbb08c27ce7851321fe3ff8b9e7a1fb7b27ba64 (2 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 7dba6bd1, resgx545:tools/closing/kit/lib_kit.sh at 7dba6bd1, resgx545:tools/closing/kit/run_stage.sh at 7dba6bd1, resgx545:tools/closing/kit/kitscore.py at 7dba6bd1, resgx545:tools/closing/kit/fake/sudo at 7dba6bd1, resgx545:tools/closing/kit/fake/timeout at 7dba6bd1, resgx545:tools/closing/kit/fake/df at 7dba6bd1, resgx545:tools/closing/kit/fake/modinfo at 7dba6bd1, resgx545:tools/closing/kit/fake/sha256sum at 7dba6bd1, resgx545:tools/closing/kit/fake/tool.sh at 7dba6bd1, resgx545:tools/closing/kit/fake/tool.py at 7dba6bd1, resgx545:tools/closing/kit/fake/ssh.py at 7dba6bd1, resgx545:tools/closing/scorekit.py at 7dba6bd1, resgx545:tools/closing/sessioncheck.py at 7dba6bd1, data:render/closing-r30-evst2/out/20261116-132348/e2/e2-01.txt.gz at 052c0a8b, data:render/closing-r30-evst2/out/20261116-132348/e2/e2-02.txt.gz at 052c0a8b, data:render/closing-r32-misc/out/20261116-185655/m2/m2-01.snap0.regs.gz at 052c0a8b, data:render/closing-r32-misc/out/20261116-185655/m2/m2-01.snap9.regs.gz at 052c0a8b, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=7CE8E38EDB97FC5EA4F6C90; pinned commits named by the session: resgx545 main 7dba6bd, resgx545 main 7dba6bd12e84; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW", "RE", "infer"]
date = "2026-11-16"
data = ["tools/fwsim/seeds.toml", "crates/pysgx/tests/test_fwsim_m2.py", "render-closing-r33-tim2:out/20261116-213803/t1/", "render-closing-r33-tim2:out/20261116-213803/t1d/", "render-closing-r33-tim2:fold/"]
terms = ["CR_EVENT_TIMER", "CR_CACHE_CTRL", "CR_EVENT_STATUS", "CR_EVENT_STATUS.MADD_CACHE_INVAL_COMPLETE"]
+++
**What ran.** r33-tim2 (closing29/r33-tim2 README, pre-run), the rerun of r33-tim (E1131): 15
plain 64x64 triangles of t10 under regtimeline, sampling from 5 ms before t10 starts for 60 ms (t1:
CR_EVENT_STATUS 0x012c, CR_CACHE_CTRL 0x0804, CR_EVENT_TIMER 0x0acc) or 40 ms (t1d: 0x0acc alone).
The interval premise and every held-out value come from E1131's post-hoc readings: controls diff
0, ivl (t1 3500 to 6500 ns, t1d 2500 to 5000), every 0x0acc sample a running count; hypotheses
H-SPACING, H-TIM-EN, H-TIM-RANGE (at most 400000) against H-TIM-24, H-TIM-RELOAD, H-TIM-399
against H-TIM-400, H-CC-ONE, H-CC-LAT, H-TIM-LINE against H-TIM-WRITE (the count against its line
fitted on the 1 ms before the change), H-TIM-ASYNC against H-TIM-SYNC.

**Frozen verdict (as printed).** Controls t1-c1, t1-c2, t1-c3 (ivl 4875, 4779, 4812) and t1d-c1
(3094) PASS. `H-TIM-399 ... (22 of 22 rows decided)` in t1 and `(8 of 8 rows decided)` in t1d,
H-TIM-400 `not supported: 0 held, 22 FAILED` and `0 held, 8 FAILED`; H-TIM-EN, H-TIM-RANGE,
H-TIM-RELOAD 11 of 11 and 4 of 4, H-TIM-24 `not supported: 0 held, 11 FAILED` and `0 held, 4
FAILED`; H-SPACING 22 of 22 and 8 of 8; H-CC-ONE 22 of 22, H-CC-LAT 11 of 11; H-TIM-ASYNC 1 of 1,
H-TIM-SYNC `not supported: 0 held, 1 FAILED`; H-TIM-WRITE `not supported: 0 held, 11 FAILED`;
**H-TIM-LINE `not supported: 19 held, 3 FAILED, 0 cannot tell of 22`**. fold/reproduce.out
reproduces both scores byte for byte.

**Results [HW].** Rate 398.98 to 399.01 counts a us and period 1002.482 to 1002.538 us over the
15 rows; the largest count 399892 to 400000. The change comes 22.75 to 25.67 ms after the tool
starts; the line's count there 10066 to 335084 over the rows. 120 to 300 us after the change the
median residual from the pre-change line is 5.7 to 345.0 counts (11 of 11). H-TIM-LINE's failed
clause is the window's median |residual| (at most 800): t1-01 69442.7 and t1-07 72830.1 (the
window holds one sample, the change sample), t1-08 1049.6 (three samples, the change sample at
-74329); 1049.6 lies between the 800 bound and H-TIM-WRITE's 2000, the other two above 2000. In
those three rows the sample after the change sample comes 181.5, 190.5 and 193.8 us later, in the
other 8 rows 6.5 to 62.0 us later (fold/posthoc.txt).

**fwsim [RE, infer].** sgx-sim takes a caller's running count for a program a task emits
(refusing a value outside E1133's rule; a stopped timer is read from the register) and fwsim
seeds 0x01061a70 (tools/fwsim/seeds.toml [events] emit_tim, a [time] input). Under replay
(E1130) the M2 kick then passes PDS #14's tim read: PDS #14 starts one task, the kick's second
entry, and the run stops on a memory fault at 0x0002007c, an address no placed page holds, with
no register read refused; the stop and the firmware register writes are the same for the counts
0x01000000, 0x01030d40, 0x01061a70 and 0x01061a80 (crates/pysgx/tests/test_fwsim_m2.py).

**What it shows.** The timer through a plain triangle is a running down-counter of 399 counts a
us (399.0 MHz) with a 1002.5 us period that reloads to 400000 and is neither written nor stopped
by the kick pass, at a phase a kick does not fix: the rule fwsim needs for an emitted program's
tim, up to its phase, which stays a [time] input. Post hoc, not frozen: the three failed rows'
change-sample residuals equal the gap that follows them at 399 a us (174, 183, 186 us) [infer:
the sample's 0x0acc read came that long after its timestamp; E1131 had one such row, -29478];
E1131's +568 to +633 count steps 18 to 40 us after the change (E1131 [infer: host read timing])
recur in t1-02, t1-05 and t1-c2 (window medians 600.6 to 633.9) inside the bound.

**What it does not show.** That the count stays on its line inside the window (H-TIM-LINE not
supported); the count PDS #14 itself reads (inside the pass); where an emitted program's douta
land (the sim puts them in the secondary bank; no row tests it); the cause of the fault at
0x0002007c in the run.
