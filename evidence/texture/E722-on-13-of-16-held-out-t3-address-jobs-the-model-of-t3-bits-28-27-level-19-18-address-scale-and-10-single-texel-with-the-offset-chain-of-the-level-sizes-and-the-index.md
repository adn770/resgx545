+++
id = "E722"
claim = "On 13 of 16 held-out T3 address jobs the model of T3 bits 28:27 (level), 19:18 (address scale) and 10 (single texel) with the offset chain of the level sizes and the index scaled after the sum is exact over 2048 pixels (13 of 13 that completed), against 12 of 13 for the strided chain by stride x height and 10 of 13 for the scale applied to the index only; the 3 jobs with the largest address extent (86016, 87040 and 174080 bytes against at most 65536 for the 13 that ran) faulted the job with a BIF fault"
unit = "texture"
method = "on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed and loaded), firmware /lib/firmware/sgx545_ukernel.fw sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a, tool ~/sgxfive-test-1138b sha256 ba6baa62fe33a5aa510c05ea1aa9a04c25798c60c4954655882682f05a5b8291, the 13 scripts of p1141/tex run in one pass by run-all-1141tex.sh on 2026-11-09 (14:25 to 14:31; 140 jobs, one process per job, a marker per job in the kernel log, every raw output gzipped and kept); declared.tsv, predictions-declared.tsv (380 rows) and manifest-1141tex.sha256 written before the first job (file times 14:16 to 14:20, first job 14:25:01) and verified here by sha256 (5dae7939..., f4187d25..., 144da32e...; 27 of 28 manifest lines by sha256sum -c, the 28th, the 74 staged programs, by the sha256 of sha256sum stage-bins/*.bin); recompute/recompute_p1141tex.py (numpy, scratch, shares no code with the run scripts) run on the dumps, its output in recompute-output.txt. Post hoc and not frozen: post/post_1141tex.py with post-output.txt"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["texture-isp-msaa-verification-1141"]
terms = ["T3.BIT10", "T3.BITS19_18", "T3.BITS28_27"]
+++
**What ran.** tex-c-addr: 16 fills, all declared held-out and "safe": levels L = 0 to 3 with
scales e = 0 to 3 and both together on a twiddled 64 x 64 (7 jobs), 32 x 64 (2), 128 x 32 (2) and
a strided 128 x 32 (4) and 32 x 64 (1); bit 10 on two. Names ad-<tw|st>WxH-L<level>e<scale>. A
fill, the index tag of the map texture in every dword.

**Hypotheses (frozen).** A4: texel read at base + ((off + idx) << e) dwords, off = sum over k < L
of max(1, w >> k) max(1, h >> k), idx the tile-law index of (X >> L, Y >> L) (E561) or, strided, X
>> L + stride (Y >> L); bit 10 reads the base dword; offset bits 7:0 before the address mode. "A4
stride chain": off with the stride times the height on a strided texture. "A4 shift idx only": the
index shifted, not the offset. The plan expected A4 at 16 of 16, the index-only form to differ
from A4 on 6 jobs and the stride chain on 1.

**Results.** [HW] 13 jobs completed (rc 0, 2048 pixels): A4 exact on 13 of 13 (all pixels), the
stride chain on 12 of 13 (ad-st128x32-L2e1 reads 0 of 2048), the index-only form on 10 of 13 (0 of
2048 on ad-tw64x64-L1e1, ad-tw32x64-L2e1 and ad-st128x32-L2e1). 3 jobs faulted, rc 3, "job
faulted, context lost": ad-tw64x64-L2e2, ad-tw64x64-L3e3, ad-st128x32-L3e2 (BIF fault 0x90002 at
0x3e017007, 0x3e02d002 and 0x3e018004; one devcoredump line). No pixel was read, so the frozen
prediction of each of the 3 fails as a prediction (the plan said low risk, 16 of 16): as run, A4
is 13 of 16. Each of the 3 jobs was followed by a reset and a health triangle that drew (health:
ok).

**Post hoc, not frozen (post/post_1141tex.py, section addr).** [infer] The last dword A4 reads, in
bytes: 20480, 21504, 21760, 40960, 10240, 21504, 20480, 65536, 20480, 43008 and 10240 on the 11
completed jobs that are not bit-10 jobs (the largest, ad-tw128x32-L0e2, is exactly 0x10000) and
86016 (0x15000), 174080 (0x2a800) and 87040 (0x15400) on the three that faulted. So the faults are
exactly the jobs whose A4 extent exceeds 64 KiB, consistent with a texture buffer of 64 KiB the
sampler read past, and the order of the fault addresses follows the extents. One buffer size
explains the three faults; whether the buffer is 64 KiB was not measured (answered by E787: the
probe's layout).

**Population.** The model A4 was fitted on the 12 jobs of E566 (in sample); the 13 jobs here are
held out and confirm it at 100% of the jobs that returned an image. The three extreme jobs are not
evidence for or against A4's pixels.

**What it shows.** [HW] The level offset is the sum of the level sizes below L (the width times
the height of each level, not the stride) and the address scale shifts the sum of offset and
index, on twiddled textures up to 64 x 64 (to L = 1, e = 1; and L = 3, e = 0) and a strided 128 x
32 (to L = 2, e = 1). [infer] The scale is a shift of the dword address, not of the index alone (3
jobs refute the index-only form).

**Limits of the run.** Only a 32-bit format and widths up to 128 were run. The 64 KiB cause is
the probe's scratch size (the probe prints "scratch ... (64 KiB)"), [infer]
until a run with a larger buffer (done: E743, E787). The strided chain is separated from A4 by one
job (12 of 13
against 13 of 13).

**What it does not show.** The three largest combinations (no image); level 3 with a scale on a
strided texture; sizes above 128 wide; T3 bits 11 and 12; other formats (the fill is a 32-bit
format); the "10 of 13" index-only form fails only where both L > 0 and e > 0.
