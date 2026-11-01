+++
id = "E059"
claim = "Setting either half of the terminate word to 0 leaves part of the 64x64 target unwritten: the high half 2048 pixels (x 32-63), the low half 1024 pixels (y 48-63); the other 28 values of the two halves change nothing, and all three repeats agree"
unit = "vdm"
method = "sweep table probes/vdm/terminate.toml on the laptop, linux fork with the debug option on: the 64x64 triangle job, every value of both halves of the end-of-scene terminate word (eos:1) by XOR against the job's value, three repeats each"
tiers = ["HW"]
date = "2026-11-01"
data = ["vdm-terminate"]
terms = ["VDM_BLOCK.TERMINATE", "terminate bounding box"]
+++

**What runs.** The triangle job (`sgxfive-test tri`, 64x64 target pre-filled with the sentinel
0xdeadbeef) writes 1 in each half of the terminate word of its vertex stream (word `eos:1`). The
table XORs the word with 0x1-0xf (low half) and 0x10000-0xf0000 (high half), 30 values, and runs
each value three times on a fresh context, after a baseline run without a poke. The kernel log
and the visibility counters were recorded with every case.

**Results.** The baseline writes 1062 triangle pixels and 3034 background pixels (hash
0x99385a04ee01c585). 28 of the 30 values, in both halves, give that image three times out of
three. The two flips that clear a half, which is a value of 0 there, do not:

| word | half | value | unwritten pixels | first one | hash |
|---|---|---|---|---|---|
| `eos:1` ^= 0x1 | low | 0 | 1024 | (0, 48) | 0xaa090dae7af4a745 |
| `eos:1` ^= 0x10000 | high | 0 | 2048 | (32, 0) | 0x09214d2af62ec245 |

Both jobs complete (`job: ok`), the unwritten pixels keep the sentinel, and each of the six runs
gives the same count and the same hash. 1024 pixels is a 64x16 band, 2048 a 32x64 band. The
first unwritten pixels are the band's corners: the high half at 0 leaves x 32-63 unwritten, the
low half at 0 leaves y 48-63 unwritten (not y 32-63). The visibility counters stayed at 0 in
all 93 runs, so no run differs by them.

**Not shown.** The table only moves the halves one value away from the job's 1 and to 0; which
values above 15 do what is not tried. Why the low half's band is 16 rows and the high half's 32
columns is not visible on a target this small.
