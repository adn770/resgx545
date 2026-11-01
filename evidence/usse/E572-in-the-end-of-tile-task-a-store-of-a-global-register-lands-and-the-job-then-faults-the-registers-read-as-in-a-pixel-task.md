+++
id = "E572"
claim = "In the end-of-tile task of the triangle job a stad of a global register to the scratch lands the register's value in 44 of 44 jobs that stored (37 of q053-eot2, the 4 of the second form of q053-eot, 3 of q053-eotst) and the job then faults: BIF fault 0xd0400 at 0x340042 in 39 of the 44, at 0x340043 in 1 and at 0x740012 in 4 (the cases g23 at 64x64 and 128x128, g18 and g25 at 32x16: no pattern with the register or the size), the health triangle drew exactly after every recovery (no health failure line in any of the 5 scripts); the 4 jobs of the first form (a store through r8) faulted at 0x42; 5 programs of 7 to 10 instructions without a store complete 5 of 5; and the registers read as in a pixel task (g16, g26-g31, g40 = 0, g20 and g41 = 1, g42 = 0x3f800000, g43 = 0xff000000; 12 of the 13 declared constants), with g19 reading 0x1a through a store, as in E372; g17 reads 0, g18 0x16 at 32x16, 64x64 and 128x128, g21 0x12, 0x16, 0x15 and g23 0, 0x10, 0x10 by target size"
unit = "usse"
method = "script tables q053-eot (4 jobs, r8 as the address: 4 of 4 faulted at 0x42, kept as q053-eot-first; its programs were overwritten and are not kept), q053-eot (4 jobs, r1 as the address between the two emits, the address 0x5CAF0000 + 256 * job number: 4 of 4 faulted at 0x340042), q053-eotcap (4 jobs: 0 to 3 extra nops), q053-eotst (4 jobs: a mov alone, a store of r2, of g43 with and without the fence) and q053-eot2 (37 jobs, one register a job, declared after those; the address 0x5CAF0000 + 16 * job number is the marker), 5 scripts and 6 runs, on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion 5AD04F33F6BCDA7B880E238 (installed equal to loaded at the start of every script, never reloaded), stock firmware (own_arm off), tool sgxfive-test-1126 (sha256 751f7223c8c731a08d75cfc3920a5d1050488ca3bdc426be45b7c431e600f82e, unchanged), no kernel or module change, no reboot, no clock-gate register written: the end-of-tile slot (--slot eot) holds the plain program of the tool with the stores added; the scratch is read after the job as the tool prints it, the fault addresses from each script's kernel.log"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["usse-globals-vertex-eot"]
terms = []
+++

**Declared and hashed.** The first form ran at 03:28:42, before the base declared files and the
q053-eot table were written (03:29:58); the second form ran at 03:30:11. The q053-eotcap and
q053-eotst tables (staged 03:31:21 and 03:31:54, runs 03:31:25 and 03:31:57) are not in hashes.txt,
so nothing records them before their runs. q053-eot2 was declared at 03:33:07 and hashed, and ran
at 03:33:11; its declaration follows the eot, eotcap and eotst results.

**What ran.** 53 jobs in 6 runs. The first form of the program (4 jobs, a store through r8 as the
address) faulted in 4 of 4 at 0x42, the dword at +0 of the scratch reading 0, and its programs were
overwritten by the second form and are not kept; the second (4 jobs: 11 and 10 stores between the
two emits, r1 the address) faulted at 0x340042 in 4 of 4 and only the first store's dword changed
(to 0, the value of its register); q053-eotcap (a program of the plain end-of-tile task with 0, 1,
2 and 3 extra nops, 7 to 10 instructions, no store) completed in 4 of 4 and so did the mov alone of
q053-eotst, 5 of 5 in all, so the slot is not limited to 8 instructions. q053-eotst: `stad [r1,+#0],
r2` (stored 0x001f8000), `stad [r1,+#0], g43` with and without `idf`/`wdf` (stored 0xff000000
both) each stored the value and the job then faulted (3 of 3). The recoveries (a debugfs reset and
a drawing triangle) never failed.

**Faults.** [HW] The fault addresses of each script's kernel.log, one fault line a failed job:

| script | jobs that stored | fault 0xd0400 at |
|---|---|---|
| q053-eot, first form | 4 (r8, no value read) | 0x42 in 4 |
| q053-eot, second form | 4 | 0x340042 in 4 |
| q053-eotst | 3 | 0x340042 in 2, 0x340043 in 1 |
| q053-eot2 | 37 | 0x340042 in 33, 0x740012 in 4 |

The "44 of 44" is the second form, eotst and eot2 together (4 + 3 + 37): in each the scratch
dword of the first store holds the value stored and the job then faulted; 39 at 0x340042, 1 at
0x340043, 4 at 0x740012. The four at 0x740012 are the cases g23 at 64x64, g18 at 32x16, g23 at
128x128 and g25 at 32x16 (jobs 8, 24, 31 and 34 of the table): another address with other
registers and sizes, no pattern with the value. The address is not the scratch's.

**Values.** [HW] In q053-eot2 (37 jobs, 37 with a store and 37 faults after it, one register a
job, the scratch dword at the job's own offset, 16 * job number, holds the register): g16 0, g20 1,
g26 to g31 0, g40 0, g41 1, g42 0x3f800000, g43 0xff000000 at 64x64, the same as the pixel task
(E374); g19 reads 0x1a through the store, as E372 found for a store's source (it reads 0 through a
mov in the pixel task, E372): the instruction's read decides [infer, from E372 and this]. g17 0,
g18 0x16, g21 0x16, g22 0, g23 0x10, g24 0, g25 0, g39 0 at 64x64; at 32x16 and 128x128 g21 0x12
and 0x15, g22 1 and 0, g23 0 and 0x10, g24 0 and 8, g17 and g18 and g25 and g39 as at 64x64: the
value of whichever tile stored last [infer: the tiles store to the same dword and the last one's
value is what is read], so it differs with the target. Declared before the run: H53-pix (the pixel
task's constants) 11 of 12 held-out values and the fit g43, the miss g19; H53-vtx (the vertex
task's values, E571) 10 of 12 held out, missing g19 and g41, and the fit g43.

**The programs.** The 49 programs of the three scripts after the first form are in the dataset
(programs/<script>/*.bin, the copies staged on the machine that drove the laptop, not read back from
it): the 37 of q053-eot2 reassemble byte for byte from the text of the generator kept in
analysis/gen.

**Not shown.** [infer] Why a store in the end-of-tile task faults the job after the value has
landed (the fault address 0x340042 looks like a code or table address, not the scratch, so the
fault may be the next store's, the emit's or the task's end; only the first of the second form's
stores landed); the g values per tile (only the last tile's store survives).
