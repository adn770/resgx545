+++
id = "E821"
claim = "R3k stage e3h (K1, 3 rounds, Q166, no stop): after a loop fill latched CR_EVENT_STATUS2 at 0x440 (bit 6, TRIG_3D, and the idle bit 10; still 0x440 after 1 s), a host write of bit 15 (0x8000, a bit that was not set) to CR_EVENT_HOST_CLEAR2 through debugfs kregnow 0x0114 left it at 0x440, a host write of bit 6 (0x40) cleared it to 0x400, and a further loop fill latched it again to 0x440, in 3 of 3 rounds: frozen verdict 'CLEAR2 reads [H-W] in 3 rounds', H-W (the bits written clear), H-ALL (any non-zero write clears all) and H-NONE (no write clears) tested, H-ALL and H-NONE refuted"
unit = "platform"
method = "R3k session K1 (stage e3h; decision R3-K1, Q166, host route), dataset edm-closing-r3k-events, 2026-11-10, kernel 7.3.0-resgx545, the new module of round 3 (fork resgx545 8fc748b0, srcversion 230E0EF50FFFD606C53AE3C, installed = loaded, checked at each preflight; gma500_gfx.ko sha256 06bf58db6e1c78f2bd9858bcc7b9e63d752786e098e50b5c67345ce69f2ceb78 as recorded in env.json), stock firmware sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a, the laptop (host cedar) on the home LAN, not the direct cable, rebooted into the new module at 18:48 (boot-test-kernel.sh then test-session.sh, health ok); the final run of session K1 in one driver call from 19:29:52 Mac time (out/r3-kev.log: f 19:29:52, t 19:30:07, kb 19:30:19, e2b 19:30:56, e3h 19:31:10, e3a 19:31:23, e3b 19:31:39), each stage gated on the previous stage's kept stage.json; per round (3 jobs hr, hr-r2, hr-r3, each after a debugfs reset and the arm; no task of ours needed, the stage has no blob) the five steps (1) the loop fill loop-b16-i56 (our own source, a 16-instruction body, 56 iterations: E431 and E769 found that this length latches CR_EVENT_STATUS2 bit 6 until a reset) through the pinned tool ~/sgxfive-test-s1b (sha256 46a2d06380814fdb07e7d711376f41fee4af8e6b3f75698d3e2ce52acfd6cc71) then CR_EVENT_STATUS2 read, (2) a wait of 1 s then read, (3) `kregnow 0x0114=0x8000` then read, (4) `kregnow 0x0114=0x40` then read, (5) the loop fill again then read; the kregnow row of 0x0114 is write-only (no read of the old value, no read-back); stop budget 0; exit 0, 3 jobs, health ok; scored by the frozen score/score_r3.py e3h (out/score-e3h.txt). Freeze history of the session (FROZEN.sha256 over every generator, scorer, runner, table, blob and prediction; PREDICTIONS.sha256 1f32e767... throughout): 1527b62e... (FROZEN.pre-logfix.sha256) until K0's second attempt, 463c251b... (FROZEN.pre-armlog.sha256; K0's four stages and K1's first attempt ran under it) until K1's first attempt, 1d6a3ad2... (FROZEN.sha256; K1 ran under it); each refreeze was made after a failed attempt and before the next one, with the mock test first, and changed no prediction file"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["edm-closing-r3k-events:out/e3h/"]
terms = ["CR_EVENT_HOST_CLEAR2", "CR_EVENT_STATUS2", "CR_EVENT_STATUS2.TRIG_3D"]
+++
**What ran.** Q166 asks what a write to `CR_EVENT_HOST_CLEAR2` clears: the bits written, others,
or the bits that stay set until acknowledged. The host already writes `HOST_CLEAR2 = 0` on every
SW_EVENT (the kernel's interrupt handler) and STATUS2 bit 6 survives later jobs (E357), so a write
of 0 clears nothing; a non-zero write was untested because no debugfs file wrote the register. The
new `kregnow` row does. The latch is a loop fill that sets `CR_EVENT_STATUS2` bit 6 and holds it
until a reset (E431, E769).

| step | action | H-W | H-ALL | H-NONE |
|---|---|---|---|---|
| 1 | reset, loop fill | 0x440 | 0x440 | 0x440 |
| 2 | wait 1 s | 0x440 | 0x440 | 0x440 |
| 3 | CLEAR2 = bit 15 | 0x440 | 0x400 | 0x440 |
| 4 | CLEAR2 = bit 6 | 0x400 | 0x400 | 0x440 |
| 5 | loop fill again | 0x440 | 0x440 | 0x440 |

**Frozen verdict (as printed).** `SUMMARY: e3h: CLEAR2 reads ['H-W'] in 3 rounds; Q166 rows: fit:
18 held, 0 FAILED, 0 cannot tell/void; held out: 7 held, 2 FAILED, 0 cannot tell/void; refuted
['H-ALL', 'H-NONE']; replicate: 14 held, 4 FAILED, 0 cannot tell/void; refuted ['H-ALL',
'H-NONE']; control: 6 held, 0 FAILED, 0 cannot tell/void`. Steps 1 and 2 are the fit rows, steps 3
to 5 the held out (round 1) and the replicates (rounds 2 and 3); the FAILED rows are H-ALL's step
3 (0x400 predicted, 0x440 read) and H-NONE's step 4 (0x440 predicted, 0x400 read) in each round.

**Results [HW].** CR_EVENT_STATUS2 after the steps, in every round: 0x440, 0x440, 0x440, 0x400,
0x440 (before step 1, after the reset: 0x400). Bit 10 (DCU_INVAL_COMPLETE, the idle level) read 1
at every step. The loop fills returned rc 0 with o0 0x00000000 (2048 of 2048 pixels).

**What it shows and does not.** A host write of bit 6 to `CR_EVENT_HOST_CLEAR2` clears the latched
STATUS2 bit 6 and nothing else (bit 10 stays), a write of another bit (15, not set) does not clear
it, and the latch can be set again by a job afterwards (3 of 3 rounds). So for this register the
bits written are the bits cleared, and a latch that stays until a reset (E357, E431) is cleared by
a host write. Not shown: a write of a bit that is set other than bit 6, CR_EVENT_HOST_CLEAR (stage
e3b), whether the write clears bits that a handler would otherwise acknowledge.
