+++
id = "Q290"
question = "what does a write to CR_EVENT_KICK with the kicker word unchanged start in the EDM (E834: no event and no command read, before or after a 504 ms timeout or a later served kick, yet every tick after it arrives latched, pa2 0x01061a74, with CR_CLKGATESTATUS reading 0x000ccfa0 and the event queue empty, for at least 500 ms and through a served kick, until a reset), and is the count byte pa1 bits 31:24 the kick events delivered to the EDM or the commands read (E834: neither W nor a count of CR_EVENT_KICK writes; they agree in every frozen row, E835's unread kick pass was followed by K 3 post hoc)"
unit = "edm"
kind = "hw"
value = "low"
phase = 11
evidence = ["E746", "E747", "E768", "E794", "E819", "E834", "E835"]
terms = ["Event Data Master (EDM)"]
+++
Split off 2026-11-10 from the questions on bits 24 and 25 of pa1 (answered by E746, which read them as
bits of a count byte). The count is 2 on every tick of a freshly armed firmware, 2, 3 and 4 on the
three host kicks of E746 (+1 after each), and rose by one after each (slot 0, pa1 bit 8, pa0 = 0)
entry of 14 client jobs, the kernel's command buffer kicks that a job causes (E747, read after the
run, not a frozen rule); it carried unchanged from the last entry of a job to the first of the next
(13 of 13 boundaries). Open: whether it counts kicks of the kernel's command buffer or something
those kicks also cause, why it is 2 after the arm (the arm's own GETMISCINFO read is one guess,
not tested), whether it wraps at 256 and whether any other event advances it.

To settle it: a stage that reads the byte at the arm, after a reset and after more than 256 kicks,
and a job type whose kernel-buffer kicks are known (a transfer, a render with a partial render),
logged in window 2 of the ring of E746.

Note 2026-11-10 (an offline reading of the kernel fork's source on branch resgx545, made before the
round 2 runs; the source was not re-read for this note, and nothing here is a measurement). The
kernel's `sgx_ccb_submit` bumps `BUF_KICKER` (modulo 256) before each `EVENT_KICK`; the boot's KICK2
does not; the counter is zeroed at boot (sgxfive.c:326), and `CR_EVENT_KICKER` (0x0ac4) is
programmed with that word's address [source]. The boot ends with a GETMISCINFO (one bump) and the
arm's own miscinfo is a second, which would make the count 2 after an arm [infer: H-KW, the hardware
reads the kicker word modulo 256, one candidate beside a hardware count of the writes to
`EVENT_KICK`]. H-KW then predicts 2, 1 or 3 if the arm's post-GETMISCINFO is skipped or doubled,
and the CCB offset (`ccbctl[0]`) advancing in lockstep would be a free instrument [infer]. An
oddity that H-KW leaves open: the kick's own entry carries the value from before the bump.

Narrowed 2026-11-10 (R1-events stage k, E768; not retired). The count is the number of commands
(kicks) the kernel has sent through the CCB since the firmware load, mod 256, equal to ccbctl[0]
in every row (GETMISCINFO, fill and copy alike): 2 after the arm path (the boot's
and the runner's own), 1 with the runner's left out and 4 with two more, 2 after a reset and an
arm, the kick's own entry 2 and the ticks after it 3, 254 more kicks wrapped it to 0 (the logged
kicks read 0, 1, 2, 3, the ticks after 4, against 255 for a saturating byte), a fill's and a
copy's two kicks each advanced it after their (0, 8) entries only, and `ccbctl[0]` equalled it in
every row (15 of 15 jobs, 47 rows held, none failed). What advances it and why it reads 2 after a
load are answered. Open, and the reason the question stays: whether the hardware counts the writes
to `CR_EVENT_KICK` (H-HWC) or reads the kicker word the kernel bumps before each write (H-KW) is
not separated, because every kick of every row had both; telling them apart needs a kernel or
debugfs change that writes `CR_EVENT_KICK` without a bump or bumps without a write (not run).
Also open: why the kick's own entry carries the value from before its bump. The simulator takes
the host kicks mod 256 (sgx-sim `event_count`, which is H-HWC's reading and H-KW's too for every
kick the kernel makes). Value stays low: the simulator loses nothing the two readings differ on
until a kick is made that the kernel does not make.

Narrowed 2026-11-10 (R3-events stage k7, E794; not retired). Two kicks that arrive while a task
holds the EDM for 90 ticks are delivered as two entries, not merged: K 2 and 3, the ticks after
them 4 and ccbctl[0] 4, in 3 of 3 jobs, each kick's read answered, the controls (no kick: burst
4; one kick: one entry, ticks K + 1) reproducing S2b; H-MERGE is refuted. The count byte of a
queued kick's entry is the value at its arrival (2, then 3), although both were served after the
hold, when both bumps had happened [infer]. That answers the sub-question of the second note's
oddity only in part: the pre-bump value is the value when the event is formed, not when it is
served; why the latch falls before the bump is still not shown, and H-KW against H-HWC is not
separated either (the kernel bumped the word before each of these writes). The simulator already
queues each kick as its own event with its count (a test pins it).

Narrowed 2026-11-10 (K1 stage kb, E819; not retired). H-KW is refuted: with the kicker word written
to 0x42 (3 jobs) the count byte of the ticks after the write stayed 2. A kick sent without the bump
(`kick_no_bump`) was not answered by the firmware in 3 of 3 (ccbctl write offset 3, read offset 2,
kicks counter +1, word unchanged, ticks kept), which failed the design's control. The rows that
separate H-LATCH from H-HWC could not be read (the 16-rung ring was full before the Q2 kick, Q3 has
no kick entry); post hoc the ticks after Q3's unbumped kick carry 2, which does not fit H-HWC
[infer]. Open: H-LATCH against a count of consumed commands, why a kick without the bump is not
read.

Note 2026-11-11 (round 4, two offline readings of the kept rings of E819, made before the next
session's rows are frozen because they change what row Q3' predicts; [data] for the counts, [infer]
for the readings, no new measurement).
- E819's Q3 ring ends at the kick, not 7 ticks after it. The stamps of E819 are taken before the
  `miscinfo` call starts; in the one kept job of the same op with a logged kick entry (K0's G0, E816)
  the entry came 6.70 ms after that stamp. Q3's calls started at 14.30, 14.36 and 14.42 ms and its
  rings (16 rungs, full) ended at 22.00, 22.16 and 21.38 ms, so the `CR_EVENT_KICK` write fell at
  about 21.0 to 21.1 ms [one latency sample] and the ring holds 2, 1 and 0 to 1 ticks after it, not
  the 8, 8 and 7 "after the call began". The post hoc reading that the count stayed 2 and the absence
  of a kick entry rest on at most 3 ticks and about 1 ms. Refuted by: a Q3 job whose ring covers 5
  ms after the write.
- Those last ticks carry E751's "latched while busy" mark. Of 635 tick entries in the kept rings of
  r3k-events (f, t, kb, k0h) and R4-B, `pa2` reads 0x01061a70 in 628 and 0x01061a74 in 6 (plus one
  mid-period sample): the three ticks of the post-hold burst of K0's H1 (as E749, E751, E752 and
  r3x-events H1: 12 of 12 burst entries) and the last 2, 1 and 0 entries of q3, q3-r2 and q3-r3, all
  on the 25000 grid. E751 reads 0x74 as a tick latched on arrival while the EDM is not idle. So
  from about the time of the unbumped kick's write the EDM was not idle when ticks arrived, with no
  kick entry logged: the unbumped kick may have left an event pending or in service that never
  reached our slot 0 task (3 entries in 2 of 3 jobs, post hoc, a candidate).

Narrowed 2026-11-11 (round 4 session r4-events, stage kb2, E834; not retired, and the question
line is reworded to what is left). With the writes made before the logging window and the kick
about 6.5 ms into it, the ring covered 5 to 7 ticks after every kick. The count byte is not the
kicker word as latched at a served kick: with W written to 0x42 and bumped to 0x43 by the kernel's
kick, the ticks after the served kick carried 3 (H-LATCH refuted, 3 of 3, held out and
replicated); and it is not a count of `CR_EVENT_KICK` writes: a write without the bump left it 2
(5 of 5) and the next served kick, the fourth write since the load, made it 3 (H-HWC refuted). It
counts served kicks (H-CNT consistent). A kick without the bump raised no kick entry and was not
delivered by the next served kick (one entry, one command read, CCB 4 and 3: H-PEND and H-LATE
refuted), but it was not inert (H-NOEVENT's plain ticks refuted): read after the run, every tick
from the write on carried 0x01061a74, `CR_CLKGATESTATUS` read the stop's 0x000ccfa0 while the EDM
served ticks with its queue empty (`USE0_SERV_EVENT` bit 16 set, counting), and the marks lasted
500 ms and through the served kick until the reset [post hoc, 5 of 5 jobs]. E835's kick pass of
ours, which left its command unread (read = write - 1), was followed by ticks with K 3: the count
is the kick events delivered rather than the commands read [infer, post hoc, 2 of 2]. The old
line's second clause (why a kick's own entry carries the value from before its bump) reads, with
H-CNT, as the count of the kicks served before it [infer]. Open: what the unbumped write starts
(which unit reads busy, and whether anything short of a reset ends it), and delivered against
read in a frozen row.
