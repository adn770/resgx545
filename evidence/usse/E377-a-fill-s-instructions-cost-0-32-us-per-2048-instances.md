+++
id = "E377"
claim = "Below 65536 iterations a fill's loop time is linear in its count: 3.020 µs an iteration for 8 instructions and 5.582 µs for 16 (1000 to 32000 iterations, 5 runs each, rms 0.4 and 1.2 ms), so 0.3203 µs per instruction over the fill's 2048 instances, 127.8 cycles of the 399.0 MHz reference or 16.03 instances a cycle; at 60000 iterations (180 ms and more) our kernel declared 9 of 10 jobs hung"
unit = "usse"
method = "on the laptop, linux fork b5a86838ae59 with the debug option on: probes/usse/loop-short.toml: loop_count.s (8 instructions an iteration) and loop_count16.s (16) at 1000, 4000, 16000, 32000 and 60000 iterations, 5 runs each, timed by regtimeline's end (host clock from the run's start); least-squares lines per loop length over the runs that completed; one run"
tiers = ["HW", "infer"]
date = "2026-11-03"
data = ["usse-loop-short"]
terms = []
+++

**Results.** Every job of 1000 to 32000 iterations completed with o0 = 0. The two lines meet at
0.100 s for no iterations (the run's own start-up). The difference between them, 2.562 µs for 8
nops, gives 0.3203 µs per instruction; the counter decrement and the branch add 0.458 µs an
iteration beyond their two instructions' share. At 60000 iterations one 8-instruction job
completed (0.18 s) and the other four and all five 16-instruction ones were declared hung after
about a second, then recovered.

**Reading [infer].** 0.3203 µs x 399.0 MHz = 127.8 cycles for 2048 instances, 16.03 instances an
instruction a cycle: within 0.2 percent of a whole number, as the 399.0 MHz reference being the
USSE's clock with 16 instances issued a cycle would give. The fit cannot tell 399 MHz from 400
(15.99 a cycle), and with the issue rate not measured a clock of k x 399 MHz issuing 16/k
instances a cycle fits as well.

**Not shown.** The issue rate; why 60000-iteration jobs hang at about a second.
