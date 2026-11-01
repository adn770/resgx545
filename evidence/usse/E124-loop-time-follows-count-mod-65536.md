+++
id = "E124"
claim = "A fill whose shader runs a counted loop of 8 instructions takes a host-measured time linear in the iteration count taken modulo 65536 (3.03 µs an iteration over the 64x32 fill, 100 ms at zero, 0.95 ms rms), not in the count itself, although every run ends with the counter at 0"
unit = "usse"
method = "probes/usse/loop-timing.toml on the laptop, linux fork with the debug option on: a 64x32 fill whose pixel program loads a count, then runs six nops, a decrement with a test of the result and a branch back until the counter is 0; counts 12500, 37500, 125000, 375000 and 1250000, 20 runs each, each run timed by the regtimeline wrapper from the tool's start to its exit"
tiers = ["HW"]
date = "2026-11-01"
data = ["usse-loop-timing"]
terms = []
+++

**What runs.** Each case is one `sgxfive-test probe` process: it builds the fill, submits it,
waits and reads back. The program moves the count into r1 and -1 into r2, then loops over six
nops, `iadd32.testtanz` r1 = r1 + r2 and a branch back while the result is not zero, and ends
with o0 = r1. The time is the whole process, from start to exit, so it includes the job's
setup and readback.

**Results.** All 100 runs complete with o0 = 0 on all 2048 pixels. The median times are 137.6
ms (12500 iterations), 213.1 ms (37500), 279.9 ms (125000), 243.8 ms (375000) and 114.9 ms
(1250000); within a count the 20 runs spread by 1 to 8 ms. The time does not grow with the
count: the largest count is the fastest. Against the count modulo 65536 (12500, 37500, 59464,
47320 and 4816) a straight line fits all 100 runs: 3.03 µs an iteration, 100.0 ms at zero,
0.95 ms rms. The line has five distinct x values and the residual is the scatter of the runs;
no other modulus and no non-linear dependence on the count was tried.

The full 32-bit count is in the program: the assembler encodes all of it, and a `mov` of a
32-bit value reads back intact in the other USSE tables (the preset `0xa4a5a6a7` of r11 in 15752
dumps, wherever the instruction under test leaves r11 alone).

**Not shown.** Why the time follows the count modulo 65536 while the loop ends with the counter
at 0: whether the loop runs fewer iterations than the count, or runs them at a rate that
depends on the count, is not separated by a whole-process time. What this means for the core
clock is open (Q002).
