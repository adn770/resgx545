+++
id = "E834"
claim = "R4 stage kb2 (r4-events, 10 jobs of ring_hold.s, each a reset and an arm, the writes made before the logging window and one miscinfo 1 ms after it opened, no stop; Q290): the ordinary kicks (g0p x2, the timing control) gave one kick entry with K 2 6.45 and 6.46 ms after the call's stamp, 8 ticks before it and 7 after, the ticks after K 3 and pa2 0x01061a70, answered; with the kicker word W written to 0x42 before one ordinary kick (q2p x3) the kernel's bump made W 0x43 (67), the kick was served (one entry, K 2, answered, CCB offsets 3 and 3) and the 6 ticks after it carried K 3 in 3 of 3, so the count is not W as latched (H-LATCH refuted); a kick without the bump (q3p x3, q4 x2) raised no kick entry in 5 of 5 (the ring reached 5 to 6 ticks past the call's stamp + 8 ms), the ticks after it kept K 2 (H-HWC, a count of CR_EVENT_KICK writes, refuted), carried pa2 0x01061a74 (E751's latched mark) from the first tick 6.75 to 7.94 ms after the stamp on, and USE0_SERV_EVENT bit 16 read set in both samples after the 504 ms timeout; an ordinary kick sent after it in a second window (q4 x2) was served at once (one entry with K 2, answered in 3.5 ms) and read one command (CCB 4 and 3, W 3), and its ticks still read 0x01061a74; frozen verdict 'count byte: H-LATCH REFUTED, H-CNT consistent (3 row groups), H-HWC REFUTED; unbumped kick: H-PEND REFUTED, H-NOEVENT REFUTED, H-LATE REFUTED'"
unit = "edm"
method = "R4 session r4-events stage kb2 (round 4, decision 9; plan closing4/events/exp-events-r4.md section 4), dataset edm-closing-r4-events, attempt out/a1 (run 2026-11-11 20:55:40 Mac time, one attempt, stage exit 0, 10 jobs run and 0 void, no stop, reset, gate and health ok at the end), the laptop (host cedar), kernel 7.3.0-resgx545, module of the linux fork's branch resgx545 at a2788bd8 (srcversion 99CD90DA26E3AFF9C450517, installed = loaded, checked at the preflight), stock firmware sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a, the session's load step (health fill and triangle through ~/sgxfive-test-s1b, sha256 46a2d063...) before the stage; the task ring_hold.s of S2b byte for byte (sha256 fa0f79db...), which logs every entry of slot 0 in a 16-rung ring in window 2; each job a debugfs reset and the arm (K 2 after it), the ring cleared, the writes (q2p: the debugfs kicker file =0x42; q3p and q4: the one-shot kick_no_bump Y, read back N after), the window opened, one miscinfo through the debugfs 1 ms later, then 5 ms; after a call that timed out the register signature twice 30 ms apart; q4: the ring cleared, a second window and one ordinary miscinfo 1 ms after it, the kicker file read after; 'after the kick' frozen as the ticks after the kick entry (g0p, q2p) or after the call's start stamp + 8.0 ms (q3p, q4), 'before' as before the entry or the stamp + 5.0 ms; g0p x2 the stage's timing control (the runner ends the stage after a g0p without one kick entry and 3 ticks after it); q2p, q3p and q4 held out, their -r2 and -r3 replicates; predictions frozen in predictions/kb2.tsv before the run (PREDICTIONS.sha256); scored by the frozen score/score_r4e.py kb2 (out/a1/score-kb2.txt, one SUMMARY line, scorekit from resgx545 5a13042), re-run on the kept files on 2026-11-11 with byte-identical output; the per-entry times, the pa2 switch and the q4 second window's entries read after the run with the session's own reader (score/r4common.py read_page) by a scratch script, not in the copy"
tiers = ["HW", "infer"]
date = "2026-11-11"
data = ["edm-closing-r4-events:out/a1/kb2/"]
terms = ["Event Data Master (EDM)", "CR_EVENT_KICK", "CR_EVENT_KICKER", "CR_USE0_SERV_EVENT", "CR_CLKGATESTATUS"]
+++
**What ran.** E819 refuted H-KW (the hardware reads the kernel's kicker word W at each event) and
left the count byte (`pa1` bits 31:24) between H-LATCH (W as latched when a kick is served) and a
hardware count, with its Q2 ring full 11 ms before the kick; and it found that a kick without the
bump is not answered, its ring ending at the kick (round 4 reading 0a, E819's correction). Stage
kb2 makes the writes before the logging window opens and the call 1 ms after it, so that the kick
falls about 6.5 ms into the ring with about 7 ticks after it. Q290's hypotheses: H-LATCH (Q2P's
ticks after the kick carry 0x43), H-CNT (a count of served kicks or consumed commands: 3), H-HWC
(a count of `CR_EVENT_KICK` writes: 3, and 3 after an unbumped write); for the unbumped kick
H-PEND (an event left pending: no kick entry, ticks 0x01061a74, `USE0_SERV_EVENT` bit 16 clear,
delivered with the next kick: two entries, CCB 4 and 4), H-NOEVENT (nothing raised: ticks
0x01061a70, bit 16 set, one entry and CCB 4 and 3 at the next kick), H-LATE (a kick entry inside
the ring).

**Frozen verdict (as printed).** `SUMMARY: kb2: G0P timing held; count byte: H-LATCH REFUTED,
H-CNT consistent (3 row groups), H-HWC REFUTED; unbumped kick: H-PEND REFUTED, H-NOEVENT REFUTED,
H-LATE REFUTED; stops 0 []; every control PASS (66); 77 of 77 non-control rows decided; Q290
rows: fit: 10 held, 0 FAILED, 0 cannot tell/void; held out: 16 held, 11 FAILED, 0 cannot
tell/void; ... replicate: 24 held, 16 FAILED, 0 cannot tell/void; ... control: 66 held, 0 FAILED,
0 cannot tell/void` (the refuted lists elided; out/a1/score-kb2.txt).

**Results [HW].** Times are from the call's start stamp (`CR_TIMER`, 24.94 units a microsecond).

| job | class | kick entries (K, ms) | ticks before / after, K after | `pa2` of the ticks after | kicker file after | bit 16 after the timeout |
|---|---|---|---|---|---|---|
| g0p, g0p-r2 | ok | 1 (2, 6.45), 1 (2, 6.46) | 8 / 7, 3 | 0x01061a70 | `kicker 3 ccbctl 3 3 kicks 3` | - |
| q2p, -r2, -r3 | ok | 1 each (2; 6.52, 6.74, 6.48) | 9 / 6, 3 | 0x01061a70 | `kicker 67 ccbctl 3 3 kicks 3` | - |
| q3p, -r2, -r3 | kick-timeout | 0 | 7, 7, 8 / 6, 6, 5; 2 | 0x01061a74 | `kicker 2 ccbctl 3 2 kicks 3` | set, set (each) |
| q4, q4-r2 | kick-timeout | 0 | 7 / 6, 2 | 0x01061a74 | `kicker 2 ccbctl 3 2 kicks 3` | set, set (each) |

Q4's second window: one kick entry with K 2 (6.55 and 6.40 ms after its call's stamp), the
miscinfo answered in 3.49 and 3.46 ms, the kicker file `kicker 3 ccbctl 4 3 kicks 4` in both, the
ticks before the entry K 2 and after it K 3. Every job kept the tick (the runner's alive check
after the job), and `kick_no_bump` read back N after each unbumped write.

**Read after the run [HW, post hoc, not frozen].**
- The latched mark starts at the write. In each of the five unbumped jobs every tick up to 5.75
  to 6.94 ms after the stamp reads 0x01061a70 and every one from 6.75 to 7.94 ms on reads
  0x01061a74 (7, 7, 6, 8 and 7 latched ticks); the served kicks' entries came 6.40 to 6.74 ms
  after the stamp. No tick of g0p and q2p reads 0x01061a74.
- The EDM was not stopped: in the two signature samples after each timeout `USE0_SERV_EVENT`
  counted on (0x105a0 to 0x105cd in q3p, 40 to 45 counts in 40 to 55 ms), HostCtl dword 12
  advanced, the event timer counted and `CR_EVENT_STATUS` read 0x20000000, while
  `CR_CLKGATESTATUS` read 0x000ccfa0, the value of a stop's signature (E537), in 10 of 10 samples;
  the kick pass of stage kp, which also left a command unread (E835), read 0x20 there.
- The mark outlasts a served kick. In q4's second window, 500 ms after the unbumped write, the
  ticks before and after the served kick all read 0x01061a74 (9 and 6, 8 and 7); the next job,
  after the reset and the arm, starts at 0x01061a70.

**What it shows.** The count byte is not W (H-LATCH refuted: W 0x43 and the count 3 after the
same served kick, 3 of 3, held out and replicated) and not a count of `CR_EVENT_KICK` writes
(H-HWC refuted: an unbumped write left it 2 in 5 of 5, and after q4's second write, the fourth
since the load, it read 3). It counts served kicks (H-CNT); whether those are kick events
delivered or commands read is not separated by kb2's rows (they agree in every one), but E835's
kick pass, whose command stayed unread, was followed by ticks with K 3: [infer] the count is the
kick events delivered to the EDM, and a kick's own entry carries the count of the kicks before
it. A kick written without the bump raises no event, before or after the 504 ms timeout, and is
not delivered by the next served kick (H-LATE and H-PEND's delivery refuted: one entry, one
command read, CCB 4 and 3, as H-NOEVENT said). It is not inert either (H-NOEVENT's plain ticks
refuted): [infer, post hoc] from the write on, every tick arrives while something reads busy in
`CR_CLKGATESTATUS` (E751's latched mark, the stop's clock-gate value) though the EDM serves the
ticks and kicks and its queue reads empty (bit 16 set), and that state lasts at least 500 ms and
through a served kick, until the debugfs reset. None of the frozen hypotheses held whole: H-PEND
was right about the marks and wrong about the queue and the delivery, H-NOEVENT the other way.

**What it does not show.** Which unit reads busy (only the whole `CR_CLKGATESTATUS` word was
sampled) and what the write without the bump starts in it; whether the latched state ends by
itself after more than 500 ms or by anything short of a reset; which of the two unread
commands q4's second kick read (both were GETMISCINFO); a count of delivered kicks against
read commands in a frozen row (KP's K 3 is post hoc). The count after 256 served kicks without
the bump rule was not run. One firmware and one module.
