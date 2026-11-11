+++
id = "Q290"
question = "does the hardware count the writes to CR_EVENT_KICK or read the kernel's kicker word for the count byte pa1 bits 31:24 that every event handed to an EDM task carries (E768: it equalled the GETMISCINFO commands since the load mod 256 in 15 of 15 jobs, the two readings agreeing whenever the kernel bumps the word before each write), and why does a kick's own entry carry the value from before its bump"
unit = "edm"
kind = "hw"
value = "low"
phase = 11
evidence = ["E746", "E747", "E768", "E794", "E819"]
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
