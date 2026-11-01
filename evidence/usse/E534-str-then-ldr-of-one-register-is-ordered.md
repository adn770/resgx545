+++
id = "E534"
claim = "In a firmware (EDM) task of our own, a str to CR_REG_0814 (0x0814, 17 bits) or CR_PDS_REG_0A78 (0x0a78, 6 bits) is seen by the next ldr of the same register and lands in the register the host reads, with nothing between them and at every distance run: in 318 of 318 runs the predicted (L, H) came out; 228 of the 306 matrix runs could tell a str that landed from one that did not (the value finally stored differs from the one the register held), 138 on 0x0814 and 90 on 0x0a78, and those 228 are the ones that show it. Per case: str then ldr with 0, 1, 2, 4 and 16 nops between, with a wdf, with an idf and a wdf, with an idf alone, or with a second str read B (or C) and left the host reading B (or C); an ldr of the other register read that register's own value, which kept it (X8); an ldr before a str is not changed by it (X6, 30 of 30 that could tell); a stad of the result, then a load of the run id, a wdf and two more stores, then the state flag with no idf, landed in 18 of 18 (X9)"
unit = "usse"
method = "as E531 (srcversion 7ED723C25D78D7FCB3C08C1, own_arm slots=0x1 entry=0 trc=8), stages 5 and 6 of tools/fwtask/run_stage.py. Only the two registers 0x0814 and 0x0a78 were written by a str or read in a matrix: asm/fwtask/x9b_r1.s and x9b_r2.s (2738 bytes each, 17 commands X0 to X11), predictions frozen in tools/fwtask/predictions.toml (sha256 38e364de9a46535b82cf9f045eab84d19d2b112f7907ffd2cd38bf4514f67183) before the first str; the host wrote the start value A with kreg, the parameters B and C and the command, read the results page and the register back with kreg, restored it and read it again; 17 cases x 2 value pairs x 3 repeats in a seeded shuffled order (seed 1129) per matrix, with the tool as the watchdog (no done in 100 ms, ticks, EVENT_STATUS2, the log, at most 3 resets; none was needed) and a check every 10 runs. Populations: p1129-s5c-x0x1-r1 (12 runs, X0 and X1 on 0x0814: no str, or a str of the held value, so none can tell a landed str), p1129-s6r1 (102 runs on 0x0814; its second value pair was B xor mask, which is A for this register, so 51 runs stored the held value), p1129-s6r1b (102 runs on 0x0814, the second pair swaps B and C) and p1129-s6r2 (102 runs on 0x0a78): 318 runs in all, 306 of the matrix. The tool changed between s5c and s6r1 (tool hash 370f89f7) and s6r1b (40b17a1f): the second-pair rule is not the same, so the landed tools do not reproduce s6r1 or s5c. The first attempts of the stage failed in the tool and are kept: p1129-s5-x0x1-r1 and p1129-s5b-x0x1-r1 (arm record and kernel log only, no records, so whether a str ran in them cannot be told; the name p1129-s5-x0x1-r1 was used by two runs and its files are those of the last one, which cannot be checked further). The kernel.log of p1129-s6r2 holds two boots, lines 1 to 447 those of p1129-s6r1b and its own from line 448 on, so a count of boots or errors per directory must not use it. Per run the stage took 0.07 to 1.1 ms (the tool's timer). The 318 runs are also the 318 vectors of vectors-usse-fwtask-9b (tools/fwtask/make_vectors.py, one per run, the wrapper as the kernel patched it); the simulator replays them exactly (sgx_sim::fwtask::FwBus). A firmware task, not a client pixel task"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["firmware-tasks-str-then-ldr", "vectors-usse-fwtask-9b"]
terms = ["Universal Scalable Shader Engine (USSE)", "Event Data Master (EDM)"]
+++

**Matrix.** Cases and counts per register and pair (6 runs a case in each matrix, 3 per pair; A the
start value, B and C the task's values; L the value the `ldr` returned, H what the host read after):
X0 (`ldr` only: L = A, H = A), X1 (`str` of the value just read, then `ldr`: A, A), X2 at d = 0, 1,
2, 4 and 16 nops (L = B, H = B), X3 (a `wdf` between), X4 (`idf`, `wdf`), X5 (`idf` only), all L =
B, H = B, X6 at d = 0 and 4 (`ldr`, nops, `str`: L = A, H = B), X7 (two `str`: L = C, H = C), X8
(`str` on one register, `ldr` of the other: the other read its own start value and kept it, so the
two do not alias), X9 (X2 at 0, the result `stad` followed by a `br`, a load of the run id, `wdf
drc0`, two more `stad` and then the state flag with no `idf`: every result landed with the flag, 18
of 18), X10 (a first `ldr` and `wdf`, 64 `nop`s, then a second `ldr`: B, B), X11 (`CR_TIMER` read
before and after a `str`, `ldr` and `wdf`: the two counts differed by 3 in 6 runs and by 4 in 12, an
upper bound in counts of a timer whose unit is not established, not a latency).

**Counts.** 318 of 318 runs finished (done flag, command cleared, register restored, no overlap) and
matched their row of the predictions: 12 + 102 + 102 + 102. A run can tell a landed `str` from one
that did not only if the value finally stored differs from the one the register held: that is 228 of
the 306 matrix runs, 138 on 0x0814 (48 of s6r1 and 90 of s6r1b) and 90 on 0x0a78. 255 of the 306
matrix runs have B different from A (the first matrix's 51 runs of its second pair stored the held
value), but that still counts the 30 runs of X0 and X1, which have no `str` or a `str` of the held
value; without them 225 stored a different value with a `str`, and 3 runs of X7 in the first
matrix stored the held value first and a different one second: 228 in all. By case the same holds:
X3, X4, X5 and X10 had 18 runs each and 15 could tell, X2 had 90 and 75 could, X6 36 and 30, and X9
18 of 18 (its test is the results page filled beforehand with 0xdeadc0de, not the register). The
`reading` strings in the verdict files are the classifier's generic labels (X0 and X1 read "the str
did not land" and X7 and X8 "other" there, X6 "(A,B)"): the verdict is `predicted_ok`, the match to
the row of the frozen predictions, which every run has.

**Reading.** [HW] Row one of the predictions for both registers: (L, H) = (B, B) at every distance
run (0, 1, 2, 4 and 16 `nop`s, and a second `ldr` 64 `nop`s later in X10) and with every fence
variant, so for 0x0814 and 0x0a78 only, while the EDM is idle and no job runs, a `str` was seen by
the later `ldr` of the same register and by the host with no fence in 318 of 318 runs. 0x0814 is
shown by 138 runs that could tell and 0x0a78 by 90 (6 at each distance 0, 1, 2, 4 and 16 on
0x0a78, 9 on 0x0814). The 318 are four fresh loads of the firmware (s5c, s6r1, s6r1b, s6r2), and
the replicates within a load are not independent of one another. [infer] That the two are plain
storage that neither the closed task nor the PDS reads or writes while the EDM is idle: the only
evidence is the host's read-back width (17 and 6 bits), and the ordering is shown against the host's
timing, not against the time of the `str` (X11 is an upper bound).

**Not shown.** A register whose write starts work, a job running, the hardware's or the closed
task's own writes of a register, registers 0x0810, 0x0818 and 0x0520 (not used in this phase), the
register-index forms and an index of more than 14 bits (never run), the time of a `str` (X11 is a
bound), and anything of the closed task (Q154, Q134).