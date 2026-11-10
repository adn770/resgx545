+++
id = "E816"
claim = "R3k stages k0c and k0h (K0, tasks of ours unchanged from L3 and S2b on the new module): alias2 read its registers as E791 found them (C0: pclink 0x98, p1 1, sa64 0x2, sa65 0x02000000, sa63 0; C1, sa65 written with bit 23 set, kept the tick and the next entry read sa65 0x02000000 again) and ring_hold read idle with no task (H0: signatures idle-empty twice) and busy in every element sampled inside a 90.5 ms hold (H1: hold 2262434 units, as wanted, signatures busy twice, all elements as a running task); G0, one ordinary miscinfo kick, was answered, logged one kick entry carrying the count 2 and moved the kicker file and the CCB offsets from 2 to 3 (kicker 3 ccbctl 3 3 kicks 3), the ticks on the 25000 grid; one row (ticks_K_after, the count byte of the ticks after the kick) is void because the 16-rung ring ended at the kick entry: 7 held, 1 void"
unit = "edm"
method = "R3k session K0 (stages k0c, k0h), dataset edm-closing-r3k-events, 2026-11-10, kernel 7.3.0-resgx545, the new module of round 3 (fork resgx545 8fc748b0, srcversion 230E0EF50FFFD606C53AE3C, installed = loaded, checked at each preflight; gma500_gfx.ko sha256 06bf58db6e1c78f2bd9858bcc7b9e63d752786e098e50b5c67345ce69f2ceb78 as recorded in env.json), stock firmware sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a, the laptop (host cedar) on the home LAN, not the direct cable, rebooted into the new module at 18:48 (boot-test-kernel.sh then test-session.sh, health ok); the final run in one driver call from 19:12:08 Mac time (out/r3-k0.log: k0c 19:12:24, k0h 19:12:33); k0c with alias2 (sha256 c41bd078cd42eb33..., L3's bytes) armed in slot 0 at the stage start, jobs C0 (reader) and C1 (sa65 | 1 << 23); k0h with ring_hold (sha256 fa0f79dbb5864187..., S2b's bytes), one reset and arm per job, H0 (idle, two signatures 20 and 60 ms after, status at 40 ms), H1 (a hold of n = 1508279, about 90.5 ms, two signatures and the status inside it) and G0 (window 2, one miscinfo through the kicker op: the kicker file before and after, the ring, the CCB offsets, kick_no_bump read back); scored by the frozen score/score_r3.py k0c and k0h (out/score-k0c.txt, out/score-k0h.txt); health ok after each stage; tools as E815. Freeze history of the session (FROZEN.sha256 over every generator, scorer, runner, table, blob and prediction; PREDICTIONS.sha256 1f32e767... throughout): 1527b62e... (FROZEN.pre-logfix.sha256) until K0's second attempt, 463c251b... (FROZEN.pre-armlog.sha256; K0's four stages and K1's first attempt ran under it) until K1's first attempt, 1d6a3ad2... (FROZEN.sha256; K1 ran under it); each refreeze was made after a failed attempt and before the next one, with the mock test first, and changed no prediction file. Failed attempts of K0's first stage: E815. The G0 row ticks_K_after was read from the ring after the run: the ring (16 rungs) holds 15 ticks at 6.33 to 20.33 ms after the window opened and the kick entry at 20.35 ms, none after (scratch reading with the session's own reader, scorelib.ring)"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["edm-closing-r3k-events:out/k0c/", "edm-closing-r3k-events:out/k0h/"]
terms = ["Event Data Master (EDM)", "CR_EVENT_KICK", "CR_EVENT_KICKER"]
+++
**What ran.** K0 reruns three rows of earlier sessions on the new module with their tasks
unchanged: alias2's reader (E791 A0) and its kept sa65 write (A7, kept in L3), ring_hold's idle
and 90-tick-hold signatures (E811 H0, S2b), and one ordinary miscinfo kick in the ring (E768's G0
shape, K = 2 after the arm, +1 by a kick). It is the gate of K1: a failed control here would have
stopped everything.

**Frozen verdicts (as printed).** `SUMMARY: k0c: C0 held; C1 kept 1 of 1; stops 0 []; Q152 rows:
control: 11 held, 0 FAILED, 0 cannot tell/void` and `SUMMARY: k0h: H0 idle; H1 as L3's; k0h G0:
control: 7 held, 0 FAILED, 1 cannot tell/void; cannot tell ['E768 (ring_e1: K = 2 after the arm,
+1 a kick)']`.

**Results [HW].**

| job | read |
|---|---|
| c0 | reader: pclink 0x98, p1 1, sa64 0x2, sa65 0x2000000, sa63 0x0; CCB write 2 read 2, HostCtl dword 14 0 |
| c1 | next entry: pclink 0x98, sa65 0x2000000 (K << 24); CCB 2 and 2, dword 14 0; the tick kept |
| h0 | signatures idle-empty and idle-empty |
| h1 | hold 2262434 units (wanted 2262434, band held); signatures busy and busy, every element as a running task |
| g0 | 15 ticks and 1 kick entry in the ring, kicker file before `kicker 2 ccbctl 2 2 kicks 2`, after `kicker 3 ccbctl 3 3 kicks 3`; ticks_K_before 2, kick_entries 1, grid yes, miscinfo answered (3.4 ms), kick_no_bump N |

**G0's void row.** The prediction ticks_K_after = 3 could not be read: the ring has 16 rungs, the
15 ticks fill it up to 20.33 ms and the kick entry (pa1 0x02000100: count 2, bit 8 set, the value
before the bump as in E768) is the sixteenth, so no tick after the kick was recorded and the
scorer marks the row void (ticks_K_after None). The kicker file does show the +1 (2 to 3, and the
CCB offsets and the kicks counter with it). The same ring limit voids rows of stage kb (E819).

**What it shows and does not.** alias2 and ring_hold behave on the new module as they did on the
old one in every row compared; the kicker file's format and counters are as designed. It does not
read the count byte after a kick (void), so E768's second half is not repeated here.
