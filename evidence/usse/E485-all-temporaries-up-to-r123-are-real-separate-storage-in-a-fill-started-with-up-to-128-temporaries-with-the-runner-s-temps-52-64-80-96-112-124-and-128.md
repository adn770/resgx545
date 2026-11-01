+++
id = "E485"
claim = "In a client pixel task (a fill, not a firmware task) started with up to 128 temporaries every register sampled up to r123 is real, separate storage: with the runner's --temps 52 and 64 the registers r2, r4 ... and the top one (26 and 32 registers, 4 of 4 cases, ascending and descending) and with --temps 80, 96, 112, 124 and 128 the registers r2, r6 ... and the top one (21, 25, 29, 32 and 32 registers, 10 of 10 cases) read back their own markers (14 of 14 cases), so the file does not wrap at 32, 48 or 64, and r123 reads back at --temps 124 and 128 (8 of 8 cases); the registers between the sampled ones (r3, r5, r7 and so on) were not read; r124-r127 are not named by an ALU instruction (usse-asm refuses r124 and up as an ALU operand [infer]: no raw word was run) but are destinations of a load, and after ldad.fetch4 r124 in a job started with 128 temporaries i0, i1 and i2 keep their markers (1 case, 3 of 3 registers) and i3 reads the marker of i0 (the reading of E075)"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1122 (sha256 ec423efc3d9aa34576553da70916be4ceb715a729cbc02cc4bd89fa052511244): probes/usse/temps-max.toml (7 probes, 15 cases, every second register from r2: the readback tool shows 32 changed dwords, so the cases with --temps 80, 96, 112, 124 and 128 (10 cases) were cut off after the first 32 dwords, r2 to r64 (all correct), and the verdict was \"none of the hypotheses fits\" for those five probes, a table error; two runs: probe.py one probe at a time, then the campaign, the same readbacks in 15 of 15 cases), redone as probes/usse/temps-sparse.toml (5 probes, 10 cases, every fourth register, at most 32 dwords, under a new name; the campaign, the dataset, and a second probe.py run, identical in 10 of 10) and the case i0-i3 of temps-max t128 (the third case of that probe, 1 case)"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["usse-temps-max", "usse-temps-sparse"]
terms = []
+++

**What runs.** A fill run with `--temps T` writes a marker 0x7E570000 | n to registers r2, r4 ...
(temps-max) or r2, r6 ... (temps-sparse) and the top register min(T - 1, 123), ascending in one
case and descending in another, then stores each to a scratch dword and the top one as the pixel. T
= 52, 64 (26 and 32 registers in temps-max); 80, 96, 112, 124, 128 (21, 25, 29, 32, 32 registers in
temps-sparse; 40, 48, 56, 62 and 62 in the cut-off temps-max cases). The wrap hypotheses (r(n) is
r(n mod 64)) predict a different marker for r2 or r66.

**Results.** temps-max T = 52, 64: 4 of 4 cases read their own markers (SETTLED); T = 80 to 128:
the first 32 dwords (r2 to r64) correct, the other dwords not shown (cut off), the pixel (the top
register) its own marker 0x7E57004F, 5F, 6F, 7B and 7B (the verdict "none fits" is from the
cut-off, not a disagreement). temps-sparse: 10 of 10 cases read every sampled register's own
marker, ascending and descending; the 64-wrap hypothesis is false for the 5 probes. The T = 128
i0-i3 case: i0, i1, i2 read back 0x1E570000, 1, 2 after `ldad.fetch4 r124` (the load did not
overwrite them) and i3 read 0x1E570000 (not its marker 0x1E570003).

**What it shows.** [HW] The sampled temporaries, up to r123 (usse-asm's limit for an ALU operand),
hold separate values: no aliasing at 32 or 48 (T = 52, 64) or at 64 (T = 80, 96, 112, 124, 128,
temps-sparse). [HW] r124-r127 as the destinations of a load are not i0-i2 (the load into r124 left
them alone, one case). i3 reading i0 agrees with E075 (i3 reads i0 of the next instance of the
quad), every instance holding the same marker here; the table expected four separate registers.

**What it does not show.** r124-r127 as storage (no load destination was read back, so that the load
landed in r124-r127 is not shown); the registers between the sampled ones (r3, r5, r7 ... at every
size, and every register not r2 + 4n above r64); whether a larger request costs time (E487). All of
this was measured in client pixel tasks (fills), not in firmware tasks.
