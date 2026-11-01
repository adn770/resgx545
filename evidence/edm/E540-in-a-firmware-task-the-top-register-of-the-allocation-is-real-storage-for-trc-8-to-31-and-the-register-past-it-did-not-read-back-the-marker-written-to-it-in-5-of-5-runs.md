+++
id = "E540"
claim = "In a firmware task of ours started with TRC T = 8, 9, 12, 16, 24 and 31 (32 to 124 temporaries) a marker written to r(4T - 1) (r31, r35, r47, r63, r95 and r123) read back as written in 6 of 6 runs, with the closed task called after it (the tail call), the tick advancing and the status registers healthy after each (arming rates 965.8 to 999.4 Hz), and the marker written to the register past the allocation (r32, r36, r48, r64 and r96 for T = 8, 9, 12, 16 and 24; none for T = 31, whose next register r124 cannot be named) was not read back in any of the 5 runs (0 of 5; one job and one read per T, so \"never\" is not shown): it read 0 (T = 8 and 9), 0xb8b9babb (T = 12), 0xd0000e00 (T = 16) and 0xd00009c0 (T = 24); r0 read 0 in all 6; TRC 32 and above have no result: the arm of T = 32 failed (its saved error is cut off and kernel.log holds no refusal line; [infer] the fork's arm gate refuses a TRC above its free maximum unless trc_hazard=1 is given, which the tool as it ran gave only from 49), and arming with the hazard word was not made"
unit = "edm"
method = "as E531: asm/fwtask/trc_08.s to trc_31.s (31 instructions each, 30 for T = 31; blob sha256 trc_08 cbb1de22af31...2f0f, trc_09 4ae3305e793c...ae, trc_12 4060637c3208...f9e3, trc_16 e6072dd9564c...8fec, trc_24 008953fa3be2...89c0d and trc_31 0fbf908f392d...fa0b), one reload and boot per T with own_arm slots=0x1 entry=0 trc=T; the task writes 0x7a110000 + T to r(4T - 1), 0x7b220000 + T to r(4T) when that is 123 or below, reads both back and r0, and stores them; the closed task follows; run by tools/fwtask/run_stage.py stage s13, tool sha256 54eb8909...e56e, predictions I13_T08 to I13_T31 and I13_P09 to I13_P24 frozen before stage B (predictions-1130.toml sha256 d8c677cd...27197). Run p1130-e-trc: T = 8, 9, 12, 16, 24 and 31 ran (one job each); the arm of T = 32 failed in the tool (s13-T32-armfail.txt holds a python traceback cut off at the arm's `wr(\"own_arm\",{` call, so the error text is not saved, and kernel.log ends with the T = 31 arm's `own_code: 282 bytes accepted` and no refusal line; the tool as it ran added the hazard word only from T = 49 up) and the stage stopped; arming 32, 40 and 48 with trc_hazard=1 was not made (the session's permission system did not allow it), so T = 32, 40, 48 (predicted to run) and 49 and 64 (predicted to hang) were not run and have no result. The tool file of this tree (not the one that ran, tool sha256 above) now refuses a T of 32 or more unless `--trc-hazard` is given, which is off by default; nothing here arms or runs it. No fill or triangle gate ran in this run; the stock check after the session is p1130-post-stock. A firmware task, not a client pixel task. The module and its verifier as E536 (the fixed verifier was not used; it accepts trc_08 to trc_64)"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["firmware-tasks-trc-ladder", "firmware-tasks-final-stock-check", "vectors-usse-fwtask-p1130"]
terms = ["Event Data Master (EDM)"]
+++

**Results.** [HW] Top register: 0x7a110008, 0x7a110009, 0x7a11000c, 0x7a110010, 0x7a110018 and
0x7a11001f for T = 8, 9, 12, 16, 24 and 31: as written (6 of 6; T = 31 is r123, the highest
register that can be named). Past the allocation: r32 = 0 (T = 8, written 0x7b220008), r36 = 0 (T =
9), r48 = 0xb8b9babb (T = 12), r64 = 0xd0000e00 (T = 16) and r96 = 0xd00009c0 (T = 24): the marker
in none of the five (0 of 5; the rows I13_P09, I13_P12, I13_P16 and I13_P24 held, 4 of 4, and T = 8
had no row). r0 was 0 in all six. The non-zero values are leftovers [infer: another instance's or
an earlier job's registers, as for pixel tasks, E486 and E484; the two 0xd0000... values have the
form of the probe fill's per-instance value]. The write to the register past the allocation was
not seen by the read of it (5 of 5, one job and one read per T), as in a client fill (E535).

**Predictions.** I13_T08 to I13_T31 held (6 of 6) and I13_P09 to I13_P24 held (4 of 4). T = 32, 40
and 48 (predicted to run) and 49 and 64 (predicted to hang) have **no result**: they were not
run.

**What ran.** Six reloads and boots, one per T, in about two seconds each; the arm of T = 32
followed the sixth and was the stage's last act. What the data show of the arm of 32 is only that it
failed: the saved error is cut off and kernel.log has no refusal line. [infer] That the fork's arm
gate refuses a TRC of 32 or more without the hazard word rests on the host tool, which sets
`trc_hazard` when the TRC is above the fork's free maximum (tools/fwtask/host/own_host.c, the
constant `SGX_OWN_TRC_FREE_MAX`, whose value is in the fork's header, not in the data or in this
tree), and on T = 31 having armed; the fork's source was not re-read for this record. The tool gave
the word from 49 up. The session's final debugfs reset and stock check (job, fill and triangle
exact) is recorded apart.

**Not shown.** TRC 32 and above, the hang predicted for 49 and up, any use of registers above
r123, and the cost of a large TRC.
