+++
id = "Q290"
question = "what advances the count byte pa1 bits 31:24 that every event handed to an EDM task carries (in E747's 14 client jobs it rose by one after each entry with pa0 = 0 and pa1 bit 8 and after nothing else, 124 of 124 successive pairs; E746: after each host kick), and why does it read 2 on the first tick after a firmware load"
unit = "edm"
kind = "hw"
value = "low"
phase = 11
evidence = ["E746", "E747"]
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
