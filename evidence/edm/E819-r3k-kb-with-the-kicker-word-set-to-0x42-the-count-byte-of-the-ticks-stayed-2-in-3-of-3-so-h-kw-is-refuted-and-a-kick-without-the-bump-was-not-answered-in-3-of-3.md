+++
id = "E819"
claim = "R3k stage kb (K1, 12 jobs of ring_hold.s, Q290, no stop): with the kicker word W written to 0x42 (the debugfs kicker file; Q1, 3 jobs) the count byte pa1 bits 31:24 of the ticks after the write stayed 2 (3 to 4 ticks a job), so H-KW (the hardware reads the kernel's kicker word at each event) is REFUTED, 3 of 3; with the write followed by one ordinary miscinfo (Q2) the kicker file read 0x43 (67), the CCB offsets and the kicks counter 3, the miscinfo was answered, and the count after the kick is void because the 16-rung ring held 16 ticks and ended 11 ms before the kick (H-LATCH and H-HWC cannot tell); with the one-shot kick_no_bump (Q3, the command written and kicked, W not bumped) the miscinfo was NOT answered in 3 of 3 jobs (no answer in 504 ms), the CCB write offset moved to 3 and the read offset stayed 2, the kicks counter rose by 1 and W stayed 2, and the 3 controls that predicted an answer FAILED; frozen verdict 'Q0 held (ticks K = 2); consistent with [H-LATCH, H-HWC], refuted [H-KW]'"
unit = "edm"
method = "R3k session K1 (stage kb; decision R3-K5, Q290), dataset edm-closing-r3k-events, 2026-11-10, kernel 7.3.0-resgx545, the new module of round 3 (fork resgx545 8fc748b0, srcversion 230E0EF50FFFD606C53AE3C, installed = loaded, checked at each preflight; gma500_gfx.ko sha256 06bf58db6e1c78f2bd9858bcc7b9e63d752786e098e50b5c67345ce69f2ceb78 as recorded in env.json), stock firmware sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a, the laptop (host cedar) on the home LAN, not the direct cable, rebooted into the new module at 18:48 (boot-test-kernel.sh then test-session.sh, health ok); the final run of session K1 in one driver call from 19:29:52 Mac time (out/r3-kev.log: f 19:29:52, t 19:30:07, kb 19:30:19, e2b 19:30:56, e3h 19:31:10, e3a 19:31:23, e3b 19:31:39), each stage gated on the previous stage's kept stage.json; the task ring_hold (sha256 fa0f79dbb5864187..., S2b's bytes) armed in slot 0 after a debugfs reset and the arm at each of the 12 jobs (K = 2 after the arm, E768), window 2 open, then per row, 1 ms after the window: Q0 nothing (3 jobs, the fit rows), Q1 `kicker =0x42` (3), Q2 Q1 then one miscinfo through the kernel (3), Q3 `kick_no_bump` then one miscinfo (3), 5 ms of ticks and 5 ms after; the kicker file (W, ccbctl[0], ccbctl[1], kicks) read before and after, the CCB offsets and kick_no_bump read back, stop budget 0 (a tick stop ends the stage); stage exit 0, 12 jobs run, no stop, health ok; scored by the frozen score/score_r3.py kb (out/score-kb.txt). Freeze history of the session (FROZEN.sha256 over every generator, scorer, runner, table, blob and prediction; PREDICTIONS.sha256 1f32e767... throughout): 1527b62e... (FROZEN.pre-logfix.sha256) until K0's second attempt, 463c251b... (FROZEN.pre-armlog.sha256; K0's four stages and K1's first attempt ran under it) until K1's first attempt, 1d6a3ad2... (FROZEN.sha256; K1 ran under it); each refreeze was made after a failed attempt and before the next one, with the mock test first, and changed no prediction file. The ring times below (when the ring ended, when the kick was made, the ticks after the kick call began in Q3) were read from the kept page records after the run with the session's own reader (scorelib.ring), scratch arithmetic not in the dataset; the frozen scorer reads the kick entry, which Q3 never had"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["edm-closing-r3k-events:out/kb/"]
terms = ["Event Data Master (EDM)", "CR_EVENT_KICK", "CR_EVENT_KICKER"]
+++
**What ran.** E768 found that the count byte of every event handed to an EDM task equals the
commands the kernel has sent through the CCB (mod 256) and ccbctl[0], and that two readings fit
every row: the hardware reads the kicker word the kernel bumps before each `CR_EVENT_KICK` write
(H-KW), or it counts the writes (H-HWC); a third, H-LATCH, takes the word as it was at the last
kick. The new module lets the host set the word (`kicker =N`, live only, no job unfinished) and
send one command without the bump (`kick_no_bump`), so each reading can be separated: Q1 changes W
with no kick, Q2 adds one ordinary kick, Q3 kicks without the bump. Frozen K of the ticks after
the action: H-KW 0x42, 0x43, 2 (Q1, Q2, Q3); H-LATCH 2, 0x43, 2; H-HWC 2, 3, 3.

**Frozen verdict (as printed).** `SUMMARY: kb: Q0 held (ticks K = 2); consistent with ['H-LATCH',
'H-HWC'], refuted ['H-KW']; stops 0 []; Q290 rows: fit: 9 held, 0 FAILED, 0 cannot tell/void; held
out: 2 held, 1 FAILED, 9 cannot tell/void; refuted ['H-KW']; cannot tell ['H-HWC', 'H-LATCH'];
replicate: 4 held, 2 FAILED, 18 cannot tell/void; refuted ['H-KW']; cannot tell ['H-HWC',
'H-LATCH']; control: 39 held, 3 FAILED, 0 cannot tell/void; refuted ['control']`.

**Results [HW].**

| job | action | ticks in the ring | kicker file after | CCB write, read after | miscinfo | count byte of the ticks |
|---|---|---|---|---|---|---|
| q0, q0-r2, q0-r3 | none | 13, 13, 12 | `kicker 2 ccbctl 2 2 kicks 2` | 2, 2 | - | 2 |
| q1, q1-r2, q1-r3 | `kicker =0x42` at 19.0, 18.0, 18.4 ms | 16, 16, 16 | `kicker 66 ccbctl 2 2 kicks 2` | 2, 2 | - | 2 after the write (3, 4, 4 ticks) |
| q2, q2-r2, q2-r3 | the write, then a miscinfo at 32.9, 32.5, 32.3 ms | 16, 16, 16 (no kick entry) | `kicker 67 ccbctl 3 3 kicks 3` | 3, 3 | answered | void: the ring ended at 21.4, 22.0, 21.3 ms |
| q3, q3-r2, q3-r3 | `kick_no_bump`, a miscinfo at 14.3, 14.4, 14.4 ms | 16, 16, 16 (no kick entry) | `kicker 2 ccbctl 3 2 kicks 3` | 3, 2 | NOT answered (errno 110, 504 ms) | void by the frozen reader |

Every job read kick_no_bump back as N; the tick went on after each Q3 job (the after-window check
advancing at 943 to 1051 Hz) and health was ok after the stage; the class of the Q3 jobs is
kick-timeout, not stop.

**The failed controls.** The 3 controls that FAILED are miscinfo_answered of q3, q3-r2 and q3-r3,
predicted yes in every world (the design: every miscinfo answered) and observed no: with the kick
made without the bump the firmware did not answer; the CCB write offset moved (3) and the read
offset did not (2). [infer] The firmware's CCB reader needs the kicker word to change to see a
command (the kick by itself, the `CR_EVENT_KICK` write, was made: the kicks counter rose), a
reading of the one observation, not tested. A kick the firmware does not read is what E537's stop
looked like, but the tick went on here.

**Void rows.** Q2 and Q3 predict the count after a kick, which needs the kick's entry or ticks
after it in the 16-rung ring. In Q2 the ring was full of ticks (16, ending at 21 to 22 ms) before
the kick was made (32 to 33 ms; the ring's first entry came 6 ms after the window opened; the
design assumed 1 + 5 + 5 ms and about 12 entries, PREFLIGHT.md section 3), and in Q3 no kick entry
exists because the firmware never read the command, so 9 held-out and 18 replicate rows cannot
tell, by the frozen rule.

**Post hoc, not frozen and not scored.** The ticks in Q3's ring after the kick call began (8, 8
and 7 ticks) all carry the count 2, the same as before the kick. The kernel's kicks counter says
the `CR_EVENT_KICK` write was made. [infer] If the hardware counted `CR_EVENT_KICK` writes
(H-HWC), the count after the write would be 3; it stayed 2, as W and the CCB read offset did, so
H-HWC does not fit this reading, and H-KW is refuted by Q1; what remains is that the count follows
what the firmware has consumed or the word as latched at a kick (H-LATCH), which Q2 would have
separated and could not.

**What it shows and does not.** H-KW is refuted (Q1, 3 of 3). The rows that separate H-LATCH from
H-HWC could not be read. A kick written without the bump is not answered by the firmware, which
the design had not expected. Not shown: the count byte after a bumped kick with W set (Q2),
whether the firmware reads W at all, and what it means that pa2 read 0x01061a74 instead of
0x01061a70 in the last 2 ring entries of q3 and the last one of q3-r2.
