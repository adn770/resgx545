+++
id = "E921"
claim = "R7 session r7-faults stage L (Q111's lockup stop, read by R-6 as two `lock #0` and no release; E088's counter fill, 64 x 32, each pixel instance adding 1 to one scratch dword): with `lock #0` ... `release #0` the counter ended at 512 and with `lock #0`, `lock #1` ... `release #1`, `release #0` at 512 too (controls), with `lock #0` twice and then two releases or one the fill hung with the counter at 0 (no quad's update stored) and the kernel's reset recovered it, and with `lock #0` and no release it hung after one update (E088's case, replicated); frozen verdict 'H-SELF consistent (4 held, 0 FAILED, 0 cannot tell of 4); H-REFLAG REFUTED (0 held, 4 FAILED, 0 cannot tell of 4); H-RECOUNT REFUTED (1 held, 3 FAILED, 0 cannot tell of 4); L-REP consistent (2 held, 0 FAILED, 0 cannot tell of 2)', 9 controls passing; so in a pixel program a second `lock` of a mutex its holder still holds blocks the holder itself, neither passing as a flag nor counting; that the EDM's lockup routine stops at its second `lock #0` the same way is an inference from the pixel pipeline, not measured in the EDM"
unit = "usse"
method = "R7 session r7-faults (E919's session, attempt out/20261112-222800, module, tool, freeze and s0), stage L after s0 (22:28:37 Mac time), the first stage with jobs: five probe fills (sgxfive-test probe --temps 32 --pixels FILE), each the counter program of probes/usse/templates/counter.s (pinned in FROZEN.commits) with the plan's lock lines, assembled by gen/asm_l.py with usse-asm (sha256 ed323826..., pinned by hash) into bins/ (listing bins/LISTING.txt): l0 `lock #0`, the load, add and store, `release #0` (E088's case 1, byte for byte); l1 `lock #0`, `lock #1`, the update, `release #1`, `release #0`; l2 `lock #0`, `lock #0`, the update, `release #0`, `release #0`; l3 `lock #0`, `lock #0`, the update, `release #0`; l4 `lock #0`, the update, no release (E088's case 3, byte for byte); in that order, the scratch dword starting at 0xd0000000; a hang ('job hung' from the tool and the kernel's 'job N hung, recovering') is a reading, followed by strict health; the stage stops on a failed health, a probe that faults, or the third hang with rows left (l4, the third, was the last row). Frozen [infer]: H-SELF (a second lock of a held mutex blocks its holder: l2 and l3 hang with 0, l4 hangs with 1) against H-REFLAG (a re-lock passes and one release frees the mutex: l2 and l3 512) and H-RECOUNT (a re-lock passes and the locks are counted: l2 512, l3 hangs after one update); L-REP (l4 replicates E088 case 3: hang, 0xd0000001); controls L-CTL (l0 and l1 ok, 512; they gate l2, l3, l4). Scored by the frozen score/score_f.py (out/20261112-222800/score-l.txt), re-run on the kept files at the fold, byte-identical. The firmware reading R-6 and the edm_dataflow listing were read after the run, as E890 states them, to say what this bears on"
tiers = ["HW", "RE", "infer"]
date = "2026-11-12"
data = ["render-closing-r7-faults:out/20261112-222800/l/", "render-closing-r7-faults:bins/"]
terms = ["Universal Scalable Shader Engine (USSE)", "Event Data Master (EDM)"]
+++
**What ran.** E088 measured that `lock #n` ... `release #n` serialises the quads of a fill and that
a `lock` never released hangs the next quad. The EDM's lockup routine, as the firmware reading R-6
gives it (E890), takes `lock #0` twice and never releases, then stores 2 to `CR_DPM_TASK_STATE` and
polls `CR_EVENT_STATUS` bit 6; E890 and E902 showed a host read of 0x0694 cannot tell whether that
store is reached. Stage L asks the instruction itself, in a pixel program: does a second `lock` of
a mutex block the instance that holds it?

**Frozen verdict (as printed).** `SUMMARY: l: H-SELF consistent (4 held, 0 FAILED, 0 cannot tell of
4); H-REFLAG REFUTED (0 held, 4 FAILED, 0 cannot tell of 4); H-RECOUNT REFUTED (1 held, 3 FAILED, 0
cannot tell of 4); L-REP consistent (2 held, 0 FAILED, 0 cannot tell of 2)`; `SUMMARY: Q111 lock
(l): H-SELF: a second lock #0 of a held mutex blocks its own holder (a pixel program) (4 of 4 rows
decided)`; `SUMMARY: l controls: 9 PASS, 0 FAIL, 0 NODATA` (with s0's five).

**Results [HW].**

| case | program | class | scratch at the end |
|---|---|---|---|
| l0 | lock #0, update, release #0 | ok | 512 (0xd0000200) |
| l1 | lock #0, lock #1, update, release #1, release #0 | ok | 512 |
| l2 | lock #0, lock #0, update, release #0, release #0 | hang | 0 (unchanged) |
| l3 | lock #0, lock #0, update, release #0 | hang | 0 (unchanged) |
| l4 | lock #0, update (no release) | hang | 1 (0xd0000001) |

Each hang was the tool's 'job hung, context lost' and the kernel's 'job N hung, recovering', then a
reset whose boot came up; the strict health after each passed, and so did the stage's.

**What it shows.** In a pixel program on the USSE a second `lock #0` by the instance (quad) that
holds mutex 0 never returns: the quad that took the mutex first blocks on its own second `lock`
before its update, so no update is stored and every other quad waits on the first `lock` (l2, l3:
0, as H-SELF froze). The lock is not a flag a re-lock passes (H-REFLAG would give 512) nor a count
(H-RECOUNT would let l2 finish), and the release count after it makes no difference, since the
releases are never reached. Two different mutexes taken in a row do not hang (l1), and E088's
unreleased lock replicates (l4). The simulator now stops a pixel program at a second `lock` of a
mutex it holds, as a hang (`crates/sgx-sim`, with this record).

**What it does not show (the EDM's lockup stop).** Nothing ran in the EDM. Read with R-6 [RE], the
lockup routine's two `lock #0` would, if `lock` behaves in an EDM task as in a pixel program, stop
the EDM at its second `lock` before the store to `CR_DPM_TASK_STATE` and before the poll of bit 6: a
self-deadlock, which fits every reading of the stop (bit 6 clear, no DPM state clear started, 0x0694
reading 0, the tick stopped) [infer]. That transfer is not shown: whether an EDM task's `lock` uses
the same eight mutexes and blocks the same way, whether mutex 0 is free when the routine is entered
(if not, the first `lock` already blocks, still before the store), and whether anything outside the
task releases it, are open; the simulator refuses a second `lock` of a held mutex in an EDM task
rather than modelling it. The direct test is an own EDM task with `lock #0` twice and a mark between
them (the plan's kernel option K2, `lock` and `release` in the own-task verifier), not run.
