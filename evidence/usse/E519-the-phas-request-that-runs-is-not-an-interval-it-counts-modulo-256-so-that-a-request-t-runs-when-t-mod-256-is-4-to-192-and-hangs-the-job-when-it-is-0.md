+++
id = "E519"
claim = "The phas request that runs is not an interval: it counts modulo 256, so that a request T runs when T mod 256 is 4 to 192 and hangs the job when it is 0 or 196 to 252, in every request run: 100 to 120 and 148 to 156, 164 to 188 and 260 to 448 (all multiples of four there) ran (6 + 10 + 45 + 3 = 64 requests, o0 = the marker written to the last register of the request, or r123), 228 to 248 and 452 to 504 hung (6 + 14 = 20), and the 15 requests 512 to 1016 chosen by the rule (8 predicted to run, 7 to hang) all did as predicted (15 of 15, 8 ran, 7 hung)"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1126 (sha256 751f7223c8c731a08d75cfc3920a5d1050488ca3bdc426be45b7c431e600f82e): probes/usse/phas-low2.toml (6 requests), phas-low.toml (the second probe, 10 requests; the first probe, 100 to 120, wrote r123 past the allocation: a table error of mine, NONE with mixed pixels, kept), phas-high-a to phas-high-e.toml (6 + 15 + 15 + 15 + 17 requests), phas-mod.toml (15 requests), campaign runner, one run each, the 6 + 14 + 7 hangs recovered with no reload, the baseline triangle clean after every probe; start allocation --temps 8; phas-high-b to phas-high-d ran all 45 and phas-high-e ran 440, 444, 448 and hung from 452, found after the table was written; the modulo-256 prediction of phas-mod was written after those runs and tested on 512 to 1016, not on a fit of them"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["usse-phas-low", "usse-phas-low2", "usse-phas-high-a", "usse-phas-high-b", "usse-phas-high-c", "usse-phas-high-d", "usse-phas-high-e", "usse-phas-mod"]
terms = []
+++

**What runs.** The two-phase fill of E487 (`phas #2, #T`, the phase writes the marker 0x7E57007B to
r(min(123, T - 1)) for every request up to 504 (r123 from 124 up) and, in the 15 requests from 512
up, to r(T mod 256 - 1) for the 8 predicted to run (r123 when that is above 123: 640, 704, 896, 960;
r63 for 576 and 832; r3 for 516 and 772) and to r3 for the 7 predicted to hang, reads it back and
stores it; start with 8 temporaries), T in multiples of four: 100 to 120 (writes r(T - 1)), 148,
152, 156, 164 to 188, 228 to 248, 260 to 504, and 512, 516, 576, 640, 704, 708, 764, 768, 772, 832,
896, 960, 964, 1000, 1016.

**Results.** Ran with the marker back: 100, 104, 108, 112, 116, 120; 148, 152, 156, 164 to 188; 260
to 316, 320 to 376, 380 to 436 and 440, 444, 448; of 512 to 1016: 516, 576, 640, 704, 772, 832, 896,
960 ran; 512, 708, 764, 768, 964, 1000, 1016 hung. With E487 (12 values ran, 12 hung): ran = 8 to
192 and 260 to 448 and the mod rule's, hung = 196 to 256, 452 to 512, 708, 764, 768, 964, 1000,
1016, 1020.

**What it shows.** [HW] 72 requests ran and 27 hung in this phase (E487's 12 values that ran and 12
that hung fit the same rule): a request is accepted when its value modulo 256 is 4 to 192 and hangs
when it is 0 or 196 to 252, for every multiple of four 100 to 1016 run (the 15 chosen from 512 up:
15 of 15). What a request allocates is not shown. The jobs of phas-high-b and phas-high-c (260 to
376) read r123 back as the marker in 2048 of 2048 pixels, but every E519 job wrote the same marker,
0x7E57007B, to r123, earlier jobs wrote it there too, and E484 shows that temporaries persist from
job to job, so the read-back does not show that the write landed: E519 does not show whether a write
reaches a register under a small allocation (E486 wrote distinct markers, Q132), and the allocation
of a request above 256 is not measured (Q144). [HW] None of the 16 requests from 100 to 188 run here
hung (one job each). All of this was measured in client pixel tasks (fills), not in firmware tasks.

**What it does not show.** Requests not multiples of four (not encodable), the request that gives 4,
8 or 16 to a phase compared with a request of 4, 8 or 16 (their effect on E485's storage: the marker
read back, not the register count), a start allocation other than 8 for the new ranges, 1024 and up
(the field takes 1020).
