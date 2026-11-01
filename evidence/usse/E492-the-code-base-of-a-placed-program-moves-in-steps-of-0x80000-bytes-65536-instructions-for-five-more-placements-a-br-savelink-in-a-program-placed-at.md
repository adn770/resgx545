+++
id = "E492"
claim = "The code base of a placed program moves in steps of 0x80000 bytes (65536 instructions) at five more placements: a br.savelink in a program placed at 0x2ff000 reads its link as 0xfe02, at 0x1a0000 as 0x4002, at 0x3a8000 as 0x5002, at 0x4ff000 as 0xfe02 and at 0x300008 as 0x3 (the offset inside the step divided by 8, plus 2), and a lapc to the link plus 8 computed at run time lands in each (5 offsets, a read and a jump program at each, 2 jobs of each program: 20 of 20 jobs, o0 = the link, never 0xFA11); with E476's five placements, 0x80000 is the only power of two from 0x1000 to 0x1000000 that fits all ten links (0x40000 fits 7, 0x20000 and 0x100000 fit 5, the others 4 or fewer), and seven of the ten placements are not multiples of it (0x10000, 0x1ff000 and the five of this table)"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1124 (sha256 58907b06a8e9030472a809cd669d2c3823946fd67aaf4775f942704a90f6a5ae): probes/usse/place-more.toml (10 of its 17 probes: a read and a jump probe at each of five offsets, placed with sgxfive-test's `--place OFFSET=FILE --place-form cbase` as E476, 2 jobs per probe, each job the same program, 20 jobs); the campaign runner once, no probe.py first run; no job failed, kernel.log holds only the marks. The fit of the step is computed from the link values read here and in E476, with the model link = (X mod u) / 8 + 2 for X the placement and u the step, for u = 2^12 to 2^24"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["usse-place-more"]
terms = ["Universal Scalable Shader Engine (USSE)"]
+++

**What runs.** The two templates of E476's place-link: `br.savelink #1; mov r10, pclink; o0 = r10`
(read) and the same followed by `r5 = r10 + 8; mov pclink, r5; lapc` to the last word, with
`mov.skipinv.end o0, #0xFA11` as the fall-through (jump). The offsets are 0x2ff000, 0x1a0000,
0x3a8000, 0x4ff000 and 0x300008 (a multiple of 8 up to 0x4ff000 is accepted by `place`; larger
offsets and offsets that are not multiples of 8 were not tried).

**Results.** Read and jump each gave 0xfe02 (0x2ff000), 0x4002 (0x1a0000), 0x5002 (0x3a8000), 0xfe02
(0x4ff000) and 0x3 (0x300008) in both jobs, and o0 = the link in every jump job. The model with u =
0x80000 fits 20 of 20 jobs. With u = 0x100000 it fits 4 of the 20 (the two programs at 0x300008, 2
jobs each: one of the five offsets), and with u = 0x40000 12 of 20 (three offsets; it fails at
0x2ff000 and at 0x4ff000, 8 jobs). Over all ten placements (E476's 0x10000, 0x100000, 0x1ff000,
0x200000, 0x400000 and these five), u = 0x80000 fits 10 of 10 offsets, 0x40000 7, 0x20000 and
0x100000 5 each, 0x200000 3, 0x400000 2 and 0x800000 and 0x1000000 1; the powers of two up to
0x10000 fit 4.

**What it shows.** [HW] The link a placed program reads moves in steps of 0x80000 bytes at five more
offsets, seven of them in all not multiples of the step, so the step cannot be 0x40000 or 0x100000
and, among powers of two, no other value fits: the second and further non-aligned placements that
Q123 asked for. The counts are offsets (10) and jobs (the two jobs of a probe are one program
twice), not independent cases. [infer] A step that is not a power of two was not excluded by a fit;
the rule "code base = the placement rounded down to the step" is the model that the ten links fit.
That a task started by the firmware counts from the code base the firmware gives it is still a
guess.

**What it does not show.** A jump across a 65536-word step (bits 16 and 17 of the counter) and
indices 256 to 8191 in a fill: the tool refuses programs of over 256 words. Narrows Q123: its second
non-aligned placement is answered, the rest stays open.
