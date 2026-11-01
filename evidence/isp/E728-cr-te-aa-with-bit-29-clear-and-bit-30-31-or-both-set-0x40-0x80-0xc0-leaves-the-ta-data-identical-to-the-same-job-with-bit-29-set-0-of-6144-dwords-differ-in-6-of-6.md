+++
id = "E728"
claim = "CR_TE_AA with bit 29 clear and bit 30, 31 or both set (0x40, 0x80, 0xc0) leaves the TA data identical to the same job with bit 29 set (0 of 6144 dwords differ in 6 of 6 comparable jobs) and the parameter buffer identical except a one-dword shift of the 16 dwords 11 to 26 (13 dwords differ in 6 of 6), and stores an empty image in 9 of 9 jobs; the same words differ from TE 0x00 in 89 to 818 parameter and 132 to 367 TA dwords"
unit = "isp"
method = "on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed and loaded), firmware /lib/firmware/sgx545_ukernel.fw sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a, tool ~/sgxfive-test-1138b sha256 ba6baa62fe33a5aa510c05ea1aa9a04c25798c60c4954655882682f05a5b8291, the 13 scripts of p1141/tex run in one pass by run-all-1141tex.sh on 2026-11-09 (14:25 to 14:31; 140 jobs, one process per job, a marker per job in the kernel log, every raw output gzipped and kept); declared.tsv, predictions-declared.tsv (380 rows) and manifest-1141tex.sha256 written before the first job (file times 14:16 to 14:20, first job 14:25:01) and verified here by sha256 (5dae7939..., f4187d25..., 144da32e...; 27 of 28 manifest lines by sha256sum -c, the 28th, the 74 staged programs, by the sha256 of sha256sum stage-bins/*.bin); recompute/recompute_p1141tex.py (numpy, scratch, shares no code with the run scripts) run on the dumps, its output in recompute-output.txt. Post hoc and not frozen: post/post_1141tex.py with post-output.txt"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["texture-isp-msaa-verification-1141"]
terms = ["CR_TE_AA"]
+++
**What ran.** msaa-b-te29: 11 jobs, `tri --keep-going --dump-render`, one triangle (0,0), (192,0),
(0,192) on 64 x 64 and 128 x 128 targets: TE 0x40000000, 0x80000000 and 0xc0000000 at mode 0 (64 x
64) and mode 2 (64 x 64 and 128 x 128), 9 jobs, plus controls t29-m2-20-64x64-ctl (TE 0x20) and
t29-m2-e0-64x64-ctl (TE 0xe0) which landed already. Dumps: the param buffer (1150976 dwords, 1216
to 2112 non-zero) and the TA data (6144 dwords, 144 to 384 non-zero), compared with the landed
dumps of te 0x00 and of the job with bit 29 added (isp/msaa-te-dumps).

**Hypotheses (frozen).** H gate: bit 29 gates the image only, so the dumps equal those of TE 0x00.
H bits: the bits act in the stream, so the dumps equal those of the job with bit 29 set.

**Results.** [HW] Against TE 0x00: param 89 dwords differ (0x40 and 0x80 at 64 x 64), 217 (0xc0),
291, 300, 818 at 128 x 128; TA data 132, 132, 279, 172, 172, 367: H gate equal on 0 of 9. Against
the bit-29-set landed job (6 of the 9 have one): TA data 0 dwords differ on 6 of 6; param 13
differ on 6 of 6 (dwords 11 to 26, and a[i+1] = b[i] on all 15 positions of that stretch: our
stream is the landed one delayed by one dword; the other 1150963 dwords equal). E504 reports,
against TE 0x20000000, 76 parameter and 132 TA dwords for 0x60000000 and 0xa0000000 (mode 0 and
mode 2, 64 x 64), and a clear word byte for byte equal to 0x20000000: the 89 and 132 here are 76 +
13 and 132, so the effect of bit 30 or 31 is the same with bit 29 clear plus the 13-dword shift.
The two controls differ from the landed jobs in 0 dwords of both buffers (2 of 2). The image is
empty (0 triangle pixels, the tool: 3969 of 4096 or 16129 of 16384 wrong inside) in 9 of 9, the
E281 observation now for bits 30 and 31 alone and at 128 x 128. Frozen scoring: H bits is exact on
the TA data (6 of 6) and not on the parameter buffer (0 of 6 equal): partially met.

**Return code.** The 9 jobs are rc 1 with the tool's image check failing: the empty image is the
result, not an error. The two controls are rc 0.

**Population.** All 9 held out; the shift is not a measurement of a modelled quantity.

**What it shows.** [HW] H gate is refuted: the dumps of TE 0x40, 0x80 and 0xc0 differ from those
of TE 0x00 in every job (9 of 9), so bits 30 and 31 act in the TA's output. The TA data do not
depend on bit 29 (equal with and without it in 6 of 6), and the parameter buffer depends on it
only by a one-dword displacement of a 16-dword stretch (Q285), the rest of the 89 differing dwords
at 64 x 64 being E504's 76 of bit 30; the image, however, is empty without bit 29 whatever else is
set (9 of 9). [infer] The 13 dwords are a packet, perhaps a region header, moved by one dword.

**Interaction with bit 30 and 31.** Landed te 0x20 equals te 0x00 in the parameter buffer and the
TA data (0 dwords differ, reviewer's check), so bit 29 alone changes nothing and has an effect
only when bit 30 or 31 is set. post/post-output.txt prints all 6 pairs with a landed bit-29 twin
(0x40 and 0x80 at mode 0 and mode 2 64 x 64, 0xc0 at mode 2 at 64 x 64 and 128 x 128): TA data 0
of 6144 differing on 6 of 6, parameter buffer 13 dwords differing at 11 to 26 on 6 of 6, the two
controls 0.

**What it does not show.** What the shifted stretch is; why an empty image follows; the 128 x 128
bit-29 comparisons (no landed job); the jobs at 0xc0 mode 0 against bit 29 (none landed).
