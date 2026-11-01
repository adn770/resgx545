+++
id = "E513"
claim = "A branch over code that a test of pa0 selects is taken by a whole 2x2 quad, from the test of its top-left lane: with `xor.testtaz.chan0 !c0, p0, r7, #0` and `!p0 br` over the code, the four lanes (the pixels 0, 1, 64 and 65) ran it for pa0 == 0 and the four lanes 2, 3, 66 and 67 for pa0 == 2, and no lane for pa0 == 1, 3 and 64 (a value no instance has); in the quads that ran the code each lane saw its own stad, unfenced in 2 of the 3 cases that load (8 of 8 lanes; the third has an idf and its wait between: 4 of 4 lanes) and the four stores of a quad reached the host in each of the 5 jobs that stored (cases 0, 2, 3, 4 and 6 of the table, three of them, 0, 4 and 6, with no fence at all)"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1126 (sha256 751f7223c8c731a08d75cfc3920a5d1050488ca3bdc426be45b7c431e600f82e): probes/usse/store-own2.toml probe usse-store-own2-quad (9 cases, one run, SETTLED by the quad hypothesis) and the first run of the table as I first wrote it, usse-store-own-one of the dataset usse-store-own (NONE: the hypotheses assumed one lane runs the code; the data show four lanes, a table error of mine, kept; the second table repeated the first run's cases (K = 0, 1 and 2, K = 64 and the mov control, with the same programs and the same pixels) and added K = 3; its quad predictions were written knowing the first run's four lanes at K = 0 and 2 and none at K = 1, so the top-left reading is a replication on K = 0, 1 and 2 and a prediction only for K = 3, which ran nothing as predicted); coordinates and every pixel as in E512; the selected quad's pixels are 0xC0DE0001 in the other 2044 and V1 or 0xBBBB0002 in the four"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["usse-store-own2", "usse-store-own"]
terms = []
+++

**What runs.** The program of E512 with the stad and the load (or one `mov r10, #0xBBBB0002`, the
skip-count control) after `xor.testtaz.chan0 !c0, p0, r7, #K` and `!p0 br #m`, where m is one more
than the instructions skipped (K = 0, 1, 2, 3 and 64, and none: K = 64 never holds), r10 =
0xC0DE0001 for the instances that skip.

**Results.** K = 0: the pixels 0, 1, 64, 65 hold their own V1 (cases: stad, ldad, wdf; the same with
an idf and its wait between) and four scratch dwords changed (0x8000, 0x8004, 0x8100, 0x8104 as
bytes) in the cases with the stad alone, with an idf and its wait at the end or with no fence at
all; K = 2: the pixels 2, 3, 66, 67; K = 1, K = 3 and K = 64: no pixel differs from 0xC0DE0001 and
no dword changed; control `mov`: 0xBBBB0002 in the four pixels of K = 0's quad and 0xC0DE0001 in
2044. The branch skips exactly the instructions between (m - 1 of them).

**What it shows.** [HW] The branch of a client pixel task is decided per quad: an instance whose own
lane's test is false still runs the code when the top-left lane of its quad has it true, and a
selected odd (top-right) lane runs nothing, so "one instance selected by a test of pa0" (the emitpds
probe, E488) selected a quad of four instances (and the emit was executed by four lanes). [HW]
Within the quad that ran, each lane saw its own stad (unfenced in 2 of the 3 cases that load, with
an idf between in the third) and its own store reached the host with no fence. [infer] The decision
is the top-left lane's (K = 1 and 3 do nothing, K = 0 and 2 run the quad: a replication for K = 0, 1
and 2, a prediction for K = 3); whether the other three lanes' tests would matter if they differed
from it is not separated (all four values of the quad were tested in one program only through pa0
itself). All of this was measured in client pixel tasks (fills), not in firmware tasks.

**What it does not show.** A test whose result differs across the lanes of a quad other than by pa0
== K; instances selected by a test in a 3D or larger target; a quad on a wider target.
