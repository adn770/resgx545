+++
id = "E822"
claim = "R3k stage e3a (K1, 3 rounds, Q166, no stop): the same five steps as E821 with the CLEAR2 write made by a task of ours (strclr.s, `str #69`, the verifier's new row for 0x0114) in slot 0 instead of the host: CR_EVENT_STATUS2 0x440 after the loop fill and after 1 s, 0x440 after bit 15, 0x400 after bit 6, 0x440 after the next loop fill, in 3 of 3 rounds: frozen verdict 'CLEAR2 reads [H-W] in 3 rounds; the host route (e3h) ran: exit 0', H-ALL and H-NONE refuted; the firmware route and the host route agree"
unit = "platform"
method = "R3k session K1 (stage e3a; decisions R3-K1 and R3-K2, Q166, firmware route; the first str of a clear register by a task of ours), dataset edm-closing-r3k-events, 2026-11-10, kernel 7.3.0-resgx545, the new module of round 3 (fork resgx545 8fc748b0, srcversion 230E0EF50FFFD606C53AE3C, installed = loaded, checked at each preflight; gma500_gfx.ko sha256 06bf58db6e1c78f2bd9858bcc7b9e63d752786e098e50b5c67345ce69f2ceb78 as recorded in env.json), stock firmware sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a, the laptop (host cedar) on the home LAN, not the direct cable, rebooted into the new module at 18:48 (boot-test-kernel.sh then test-session.sh, health ok); the final run of session K1 in one driver call from 19:29:52 Mac time (out/r3-kev.log: f 19:29:52, t 19:30:07, kb 19:30:19, e2b 19:30:56, e3h 19:31:10, e3a 19:31:23, e3b 19:31:39), each stage gated on the previous stage's kept stage.json, gated on e3h's kept stage.json; the task strclr (sha256 7259a198104657e0..., 33 instructions, our own source) armed in slots 0xf at each of the 3 jobs (after a reset), commands taking the value to store (the task answered each: control); the same five steps as E821 with the loop fill loop-b16-i56 (our own source, a 16-instruction body, 56 iterations: E431 and E769 found that this length latches CR_EVENT_STATUS2 bit 6 until a reset) through the pinned tool ~/sgxfive-test-s1b (sha256 46a2d06380814fdb07e7d711376f41fee4af8e6b3f75698d3e2ce52acfd6cc71) as the latch and `str #69` of 0x8000 (step 3) and 0x40 (step 4) in place of the host's kregnow; stop budget 0; exit 0, 3 jobs, health ok; scored by the frozen score/score_r3.py e3a (out/score-e3a.txt). Freeze history of the session (FROZEN.sha256 over every generator, scorer, runner, table, blob and prediction; PREDICTIONS.sha256 1f32e767... throughout): 1527b62e... (FROZEN.pre-logfix.sha256) until K0's second attempt, 463c251b... (FROZEN.pre-armlog.sha256; K0's four stages and K1's first attempt ran under it) until K1's first attempt, 1d6a3ad2... (FROZEN.sha256; K1 ran under it); each refreeze was made after a failed attempt and before the next one, with the mock test first, and changed no prediction file"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["edm-closing-r3k-events:out/e3a/"]
terms = ["CR_EVENT_HOST_CLEAR2", "CR_EVENT_STATUS2", "Event Data Master (EDM)"]
+++
**What ran.** E821's rounds with the write made from inside the firmware: a task of ours stores
the value to `CR_EVENT_HOST_CLEAR2` (0x0114, `str #69`) instead of the host writing it. The
verifier accepted the store only for this register in this blob.

**Frozen verdict (as printed).** `SUMMARY: e3a: CLEAR2 reads ['H-W'] in 3 rounds; the host route
(e3h) ran: exit 0; Q166 rows: fit: 18 held, 0 FAILED, 0 cannot tell/void; held out: 7 held, 2
FAILED, 0 cannot tell/void; refuted ['H-ALL', 'H-NONE']; replicate: 14 held, 4 FAILED, 0 cannot
tell/void; refuted ['H-ALL', 'H-NONE']; control: 9 held, 0 FAILED, 0 cannot tell/void`.

**Results [HW].** CR_EVENT_STATUS2 after steps 1 to 5 of each round: 0x440, 0x440, 0x440, 0x400,
0x440 (before: 0x400); route fw in all three. The task took the commands in every round (the 3
extra control rows over E821's 6).

**What it shows and does not.** A firmware task's `str` of bit 6 to `CR_EVENT_HOST_CLEAR2` clears
the latched STATUS2 bit 6 as the host's write does, and a store of bit 15 does not: the two routes
agree, so the effect belongs to the register and not to who writes it. It does not show anything
for `CR_EVENT_HOST_CLEAR` (0x0134, `str #77`), which was to run only if stage e3b's B1 kept the
tick and did not run (E823). The firmware `str` rows used so far are 0x0acc (E818) and 0x0114
(this record).
