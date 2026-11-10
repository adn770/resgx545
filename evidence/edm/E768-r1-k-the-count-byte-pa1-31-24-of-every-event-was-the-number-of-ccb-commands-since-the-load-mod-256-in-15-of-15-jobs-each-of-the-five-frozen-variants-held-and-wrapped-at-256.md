+++
id = "E768"
claim = "The count byte of the event word (pa1 bits 31:24) that a firmware task of ours (ring_e1) read on every tick and kick equalled the number of commands (kicks) the kernel had sent through the CCB since the firmware load, mod 256 (GETMISCINFO, fill and copy alike), in all 15 jobs of the frozen stage: 2 after the arm (the boot's GETMISCINFO and the runner's own: 2 of 2 jobs, and 1 of 1 after a debugfs reset and an arm), 1 when the runner's own read was left out of the arm (2 of 2) and 4 when two more were added (2 of 2), the kick's own entry 2 and the ticks after it 3 after one kick (2 of 2), 254 kicks after the arm wrapped it to 0 (the four logged kicks read 0, 1, 2 and 3 and the ticks after them 4, 2 of 2, against 255 for a saturating byte), and in a 64x64 fill and a copy it rose by one after each of the job's two (slot 0, pa0 0, pa1 bit 8) entries and after no other entry (4 of 4); the CCB write offset ccbctl[0] equalled the count in every row; held out 31 of 31, fit 13 of 13, replicate 3 of 3 rows as the frozen scorer printed, and none of the frozen predictions failed; whether the hardware counts the writes to CR_EVENT_KICK or reads the kernel's kicker word is not separated"
unit = "edm"
method = "R1-events stage k of the question-closing pass, round 2 (15 jobs: k0, k1, k2, k3, k4 and k5 each with a replicate except k1, k6-fill and k6-copy with a replicate each), run 1794299244-949 of the dataset edm-closing-r1-events, on the laptop (host cedar), 2026-11-10 09:27 laptop time (08:27 UTC), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), stock firmware (sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a), tool ~/sgxfive-test-s1b (sha256 46a2d06380814fdb07e7d711376f41fee4af8e6b3f75698d3e2ce52acfd6cc71); blob ring_e1 (S2's event ring with 12 rungs in slot 3, 692 instructions, sha256 6e5fd452660c4ff4c99e3251c3b1ec09ce4417a0b604b70c3274a92aae61aa90, accepted by the landed tools/fwtask verifier, armed with own_arm slots=0xf entry=0,1,2,3); each job its own arm: the standard arm path (own_arm, own_code, load, boot, then the runner's miscinfo read), nomisc (the runner's read left out) or extra2 (two more reads after the health check), made by the session's runner (run/r1_run.py), not by the landed cmd_arm; the trigger none (window 2: ticks), one GETMISCINFO kick (window 2), 254 kicks in window 0 (nothing logged) then four logged kicks in window 1 and the ticks in window 2, or a 64x64 fill or copy (window 1); the page read twice (the second read must equal the first); the arm path's GETMISCINFO calls counted from the kernel log's 'answered after' lines (15 of 15 jobs showed their variant) and ccbctl read from the kernel log; the frozen predictions (predictions/k.tsv, PREDICTIONS.sha256) came from the offline reading of the kernel source of the f0f8720 note and from E746 and E747 (the fit rows); scored by the frozen score/score_r1.py k (out/score-k.txt)"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["edm-closing-r1-events:out/k/"]
terms = ["Event Data Master (EDM)", "CR_EVENT_KICK", "CR_EVENT_KICKER"]
+++
**What ran.** E746 and E747 read the count byte as something every event carries that a host kick
advances, and left open what advances it and why it reads 2 after an arm. The offline reading of the
kernel source (note on Q290, before the runs) offered H-KW, the hardware reading the kicker word
the kernel bumps before each kick, and H-HWC, a hardware count of writes to `CR_EVENT_KICK`, which
predict the same numbers whenever the kernel bumps the word before each write. This stage varies
how many GETMISCINFO commands the arm path sends and how many kicks follow, and reads the byte on
ticks and on kick entries.

**Frozen verdict.** Every frozen row held in both runs of each condition (`out/score-k.txt`):
`controls held; Q290 rows: fit: 13 held, 0 FAILED, 0 cannot tell/void; held out: 31 held, 0 FAILED,
0 cannot tell/void; replicate: 3 held, 0 FAILED, 0 cannot tell/void`. The controls: the window's
ticks on the 25000-unit grid in 11 of 11 windows with four or more ticks, the kernel log's
GETMISCINFO answers after the arm equal to the arm path's calls in 15 of 15 jobs, no drops in any
ring.

**Results [HW].**

- k0 and k0-r2 (standard arm, 2 GETMISCINFO answers in the log): 8 and 9 entries, all ticks, K
  2, ccbctl[0] 2.
- k1 (a debugfs reset, then the arm): K 2, ccbctl[0] 2.
- k2 and k2-r2 (the runner's own read left out, 1 answer): K 1, ccbctl[0] 1.
- k3 and k3-r2 (two extra reads, 4 answers): K 4, ccbctl[0] 4.
- k4 and k4-r2 (one kick): 11 entries, one of them not a tick (the kick's, K 2), the ticks after
  it K 3, ccbctl[0] 3.
- k5 and k5-r2 (254 kicks in window 0, then four logged kicks and the ticks): ccbctl[0] 0 after
  the 254 and 4 after the four, the kicks' K 0, 1, 2, 3, the ticks after them 4, 260 answers in
  the kernel log.
- k6-fill, k6-copy and their replicates: three entries each, K and kind (2, (0,8)), (3, other),
  (3, (0,8)), ccbctl[0] 4: the count rose after each (0,8) entry only.

The unfrozen alternatives of the table did not hold: a firmware that starts the byte at 2 whatever
the arm path sends (H-FW) is contradicted by 1 and 4 in k2 and k3, and a byte that saturates at 255
(H-SAT) by the wrap to 0 in k5.

**Post hoc [infer; read after the run, not held out].** The count is the number of commands the
kernel sent through the CCB, each with one write to `CR_EVENT_KICK`, since the load: the boot's
GETMISCINFO one, the arm's own read a second, a client job's commands one each. A kick's own entry carries the value
from before its own bump (k4: 2, then 3 on the next tick), which is the order the frozen rows
state and the stage measured; why the latch falls before the bump is not shown. The first entry of
a fill or copy being a (0, 8) entry with K = 2 and the job's last entry K = 3 fits the two kicks
that the job causes (ccbctl 2 then 4).

**Not shown.** H-KW against H-HWC: every row has the kernel bump the kicker word and write
`CR_EVENT_KICK` once each, so the two agree; separating them needs a kernel or debugfs change that
writes `CR_EVENT_KICK` without a bump, or bumps without a write (not run, not planned here). The
byte's meaning for an event that arrives while a task of ours holds the EDM (K7 of the proposal,
two kicks in a hold) and for kicks of the other-event path (`CR_EVENT_KICK2` does not bump).
