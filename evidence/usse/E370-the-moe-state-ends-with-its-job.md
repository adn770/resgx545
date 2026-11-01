+++
id = "E370"
claim = "MOE state set in one job is not in force in the next: after a job whose program runs smbo #1, #0, #0, #0 (or smlsi with increments 2), the next job's mov r10, r1 (mov.repeat2 r10, r1) writes r10 (r10 and r11) as with no MOE instruction, in three runs of three; within its own job smbo's destination offset moves the final mov.end o0, r10 to o1, so the pixels keep the job before's o0"
unit = "usse"
method = "on the laptop, linux fork b5a86838ae59 with the debug option on: probes/usse/moe-state.toml (dump.s, r1-r8 = 0x11 to 0x88): a job with smbo #1, #0, #0, #0 then mov r10, r1, the next job mov r10, r1 alone; a job with smlsi #2 x4 increments then mov.repeat2 r10, r1, the next job mov.repeat2 r10, r1 alone; three runs; one run"
tiers = ["HW", "infer"]
date = "2026-11-03"
data = ["usse-moe-state"]
terms = []
+++

**Results.** After `smbo #1, #0, #0, #0`, `mov r10, r1` writes r11 (0x11; r10 keeps its preset);
the next job's `mov r10, r1` writes r10. After `smlsi #2` x4, `mov.repeat2 r10, r1` writes r10 =
r1 and r12 = r3; the next job's writes r10 = r1 and r11 = r2. Three runs of each pair agree.

The smbo job's pixel is mixed: 0x11 on 1940 and 1908 pixels in runs 2 and 3, the preset
0xa0a1a2a3 on 108 and 140, and in run 1 the baseline triangle's two colours and the preset; the
job before each wrote 0x11 or nothing to o0.

**Reading [infer].** smbo's destination offset applies to the template's final `mov.end o0, r10`,
which then writes o1: o0 keeps what the job before left in each instance's output register
(E373). That is the "offset that does not reach every instance's final mov.end alike" of E087.
The state is reset, or not carried, from one job to the next; whether it survives from one task
to the next of the same job is not shown.
