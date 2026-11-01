+++
id = "E598"
claim = "In client pixel tasks (fills), with a GPU reset and 3 seconds before each job, `ldab` and `ldaw` with an immediate offset read the byte at base + n and the halfword at base + 2n, zero-extended (the offset counts elements of the access size, not dwords and not bytes for the halfword): 16 of 16 jobs (8 offsets each, from the dwords 0x9c8db6a7 and 0x7e6d5c4b, every byte of the first with bit 7 set, so a sign extension would show: ldab #0 to #3 read 0xa7, 0xb6, 0x8d and 0x9c), and `ldaw` and `ldad` at an address that is not a multiple of their size read the bytes at that address, across the dword boundary too (`ldaw` at base + 1, + 2 and + 3 read 0x8db6, 0x9c8d and 0x4b9c, `ldad` at base + 1, + 2 and + 3 read 0x4b9c8db6, 0x5c4b9c8d and 0x6d5c4b9c): 6 of 6 jobs; no job faulted or hung [HW]; client pixel jobs: the firmware-task verifier refuses `ldab` and `ldaw` (unknown form), so a narrow load was not run in a firmware task"
unit = "usse"
method = "on the laptop (direct cable), linux fork tip 1dd291a61499, module srcversion B21FDA82BD5E5CB5A627E3B (installed and loaded, recorded in env.toml), stock firmware, tool sgxfive-test-1135 (sha256 7732b94538cd221f25be85f307d93168413ef57cfae81065a268a73f08902687, built on the laptop from tools/sgxfive-test.c of the 11.35 tree, sha256 f5cdccb15a73de6584e33e43c5a2eb1ba5e37de7e43a07c39cb9a8d386c6e74b) with the 11.35 probe.py and campaign runner; table probes/usse/fw37-narrow.toml (frozen file in probes/p1136/manifest-1137.sha256; run with each probe name prefixed usse-fw37-narrow-, sha256 d7d480e06d9acda1bedf1d15c49d7dfa47ec875f666f6bdb2dcd8efa8726543f), made by probes/p1136/gen_client.py, 6 probes, 48 jobs, template narrow.s (scratch dwords 16 and 17 preset to 0x9c8db6a7 and 0x7e6d5c4b, bytes a7 b6 8d 9c 4b 5c 6d 7e; r28 the base, r5 = 0xaabbccdd the store source), SGX_PROBE_BETWEEN a debugfs reset and 3 s before every job; the baseline triangle drew 0 of 4096 pixels wrong before and after each of the 6 probes; the predictions (probes/p1136/predictions-1137.toml, sha256 17f6cc521ce8e58c3a995aa395641a5cba09d6627ef7578705400a7fc2af45b2, rows P37_C13a and P37_C13b) were written and hashed before the first run. Run usse-fw37-narrow (one run, shared with E598 and E599). Client pixel jobs, not firmware tasks"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["usse-fw37-narrow", "vectors-usse-fw37"]
terms = []
+++
**What ran.** The first run of any narrow memory form: `usse_isa` 7.10 listed the word and byte
forms as undecided. Three probes of the table: `ldab r10, [r28,+#n], drc0` and `ldaw r10, [r28,+#n],
drc0` for n = 0 to 7 from an aligned base, and `ldaw`, `ldad` with offset 0 from a base 1, 2 and 3
bytes past the aligned one. r28 is the scratch address (0x5CAF0040 patched by the tool); the pixel
is r10.

**Results.** [HW] 22 of 22 jobs read the model. `ldab` #0 to #7: 0xa7, 0xb6, 0x8d, 0x9c, 0x4b, 0x5c,
0x6d, 0x7e, one byte, zero in the upper 24 bits (a sign extension would have read 0xffffffa7 and so
on for four of the eight). `ldaw` #0 to #3: 0xb6a7, 0x9c8d, 0x5c4b, 0x7e6d (halfword n, not byte n
and not dword n: of the eight jobs the sign-extension rival differs from the model in 4, the "counts
dwords" rival in 7 and the "counts bytes" rival in 7, and none of them reads as the hardware did),
#4 to #7 read 0x0012, 0xd000, 0x0013 and 0xd000, the halves of the fill's next two dwords
(0xd0000012 and 0xd0000013 by the fill's pattern `0xd0000000|i`, as the vectors record it; this run
dumps only the scratch dwords 16 and 17), so the offset units carry past the two preset dwords.
Unaligned: `ldaw` at base + 1 reads 0x8db6 (bytes 1 and 2), at + 2 0x9c8d, at + 3 0x4b9c (bytes 3
and 4: across the dword boundary); `ldad` at + 1, + 2, + 3 reads 0x4b9c8db6, 0x5c4b9c8d, 0x6d5c4b9c,
the documented read of those bytes, here for the first time with the halfword as well. No job failed
or hung; job times 778 to 1705 microseconds (the 48 jobs of the table); the kernel log (1682 lines)
shows the 48 debugfs resets at BIF_FAULT 0x0 and no fault; the baseline drew exactly before and
after each of the 6 probes.

**Against the predictions.** P37_C13a 16 of 16 and P37_C13b 6 of 6 held.

**What it shows.** [HW] A narrow load is zero-extended, its offset counts elements of its own size,
and an unaligned address reads the bytes there (no alignment down, no zero, no fault), for the byte
and halfword forms as for the dword one. [infer] The same holds for offsets beyond those run and for
the other registers and banks.

**What it does not show.** A firmware (EDM) task: the verifier says "unknown form" for `ldab` and
`ldaw`, so the backend's `u8` and `u16` loads need a verifier row before this can be repeated there;
a register offset, a negative offset, the increment forms, `.fetchN` and `.repeatN` on a narrow
load; `ldab` on the other banks; the effect of `.bpcache` or `.bypassl1` on a narrow load (Q195).
