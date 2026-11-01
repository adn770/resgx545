+++
id = "E404"
claim = "With 0x0818 holding bit 8 and not bit 10 (0x100, 0x1ff, 0x3ff), a triangle render draws wrong pixels when the render before it ran under the same value with a target of another size, deterministically, the job reporting ok; with the init value 0x7ff, with any other of 32 values tried, with the register written between the two jobs, with one job after the write and with two of the same size, it draws exactly"
unit = "platform"
method = "probes/platform/register-limits.toml (first seen, 0x0818 = 0x3ff, three runs of three loads), register-limits-scan.toml (1078 runs, one job a write), register-limits-pairs.toml (200 runs: every ordered pair of triangle sizes 64, 96, 128, 160, 256, the value 0x3ff and 0x7ff, written before the pair and between the jobs, twice) and register-limits-values.toml (128 runs: 32 values, pairs 96 then 128 and 128 then 96, twice); on the laptop, linux fork f1fad0ed9d0e with the debug option on"
tiers = ["HW"]
date = "2026-11-07"
data = ["platform-register-limits", "platform-register-limits-scan", "platform-register-limits-pairs",
        "platform-register-limits-values"]
terms = []
+++

**First seen.** In register-limits, with 0x0818 = 0x3ff held through the jobs of a case, the
triangle at 1024x1024, at 2048x2048 and the eight renders at 256x256 each drew wrong pixels in
all three repeats (the job ok, no fault, the time unchanged: E403); the 64x64 triangle, run first,
did not, and nor did any copy or fill.

**One job a write.** The scan (platform-register-limits-scan, 1078 runs; its kernel.log is the
journal's copy, the campaign's fallback when the ring buffer had lost the mark) wrote the value
before each job and restored 0x7ff after it: the triangle at 32 to 512 in steps of 16 (twice,
with 0x3ff and with 0x7ff: 124 runs); 0x0818 at every fourth value from 0 to 0x7ff and at every
value with bit 8 set and bit 10 clear, 896 of the 2048 values, at 256x256; and the single bits and
complements of the three registers at 256x256 (58 runs). All 1078 draw exactly; no value of the
first part drew wrong, so the second part's repeat of those (none) did not run. So the value alone
does not break a render. A first scan of every value (2048 runs) lost its kernel-log mark to the
ring buffer and was run again in this shorter form.

**Pairs.** With 0x3ff written before two jobs, the second of every one of the 20 ordered pairs of
different sizes draws wrong, in both repeats, the same count of wrong pixels each time (96 then
128: 2439 of 16384; 128 then 96: 2155 of 9216; 64 then 256: 59427 of 65536) and the
first and every second job of two equal sizes draw exactly. With 0x7ff none of the 50 pairs
does. With the register written between the jobs (the first at 0x7ff, the second at 0x3ff) none
of the 50 does. So it is the first job's run under the value that matters, not the write before
the second [infer: state a render leaves while 0x0818 has these bits that the next render of
another layout reads].

**Which values.** Of 32 values (0x7ff with each bit cleared, each bit alone, the masks 2^n - 1,
0x7ff), exactly 0x100, 0x1ff and 0x3ff draw the second render wrong (pairs 96 then 128 and 128
then 96, twice each, all four runs); 0x5ff, 0x6ff, 0x200, 0x7ff and the others draw it exactly.
With the single bits and the three masks that fail, bit 8 set and bit 10 clear is the one
condition the 32 satisfy exactly; the combinations 0x300, 0x500 and the like were run afterwards
(E405).

**Which jobs.** A copy or fill after a job under these values draws exactly (E403's workloads
ran with 0x3ff; only triangles failed). The wrong pixels are of two kinds: the triangle's colour
where the background belongs (small targets) and the tool's sentinel where nothing was written
(from 224x224 up, whole tiles from x = 160 [infer: tiles that were not rendered]).

This does not say what bit 8 or bit 10 does; it shows 0x0818 reaches the render path (a render's
tile or region state kept from one context to the next [infer]) while the transfer path and a
render's time do not depend on it.
