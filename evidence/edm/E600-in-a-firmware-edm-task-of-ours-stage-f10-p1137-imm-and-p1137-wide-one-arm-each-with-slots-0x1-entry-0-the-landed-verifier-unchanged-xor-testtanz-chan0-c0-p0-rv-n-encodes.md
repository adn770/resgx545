+++
id = "E600"
claim = "In a firmware (EDM) task of ours (stage f10, p1137_imm and p1137_wide, one arm each with slots=0x1 entry=0, the landed verifier unchanged), `xor.testtanz.chan0 !c0, p0, rV, #n` encodes every n from 0 to 127 exactly and zero-extended, and a value of 128 and up reaches the test exactly through `mov rK, #W` (limm) and `xor.testtanz.chan0 !c0, p0, rV, rK`: 7 of 7 jobs with 128 and 64 tests each, every p0 as predicted; with V = n all 128 p0 false, with V = n xor one bit (two jobs, the bit 1 << (n mod 32) and 1 << ((n + 16) mod 32)) all 128 true, and with V = n or 0xffffff80 all 128 true (the 7-bit field is not sign-extended: n = 64 to 127 would read false if it were), and for 64 wide values W from 128 to 0xffffffff, the limm field boundaries 20/21 and 25/26 and the powers of two included, V = W gives p0 false 64 of 64 and V = W with one bit flipped gives p0 true 64 of 64 in two jobs [HW]; every job was done within 0.78 ms, the tick advanced after each arm (991.2 and 998.0 Hz) and the gate was exact after each reset"
unit = "edm"
method = "on the laptop (direct cable), linux fork tip 1dd291a61499, module srcversion B21FDA82BD5E5CB5A627E3B (installed and loaded, recorded in env.toml), stock firmware, our firmware tasks armed in the general slot (own_arm 'slots=0x1 entry=0 (stock temporaries)', one arm per task), the landed verifier unchanged, the landed tools/fwtask runner (fwtask_run.py, run_stage.py) driven by probes/p1136/run_1137.py through probes/p1136/run_1137_logged.py (which also keeps every job's record and whole results page), sources probes/p1136/asm/p1137_imm.s and p1137_wide.s made by probes/p1136/gen_1137.py (blob sha256 in env.toml), jobs and expected readbacks by probes/p1136/judge1137.py with markers of their own in every job (never the page's initial fill 0xdeadc0de), results pre-filled with sentinels of their own; the predictions (probes/p1136/predictions-1137.toml, sha256 17f6cc521ce8e58c3a995aa395641a5cba09d6627ef7578705400a7fc2af45b2, row P37_F10a and P37_F10b) were written and hashed before the first run; a reset to stock and the gate (fill and triangle exact) after each arm. Run p1137-f10 (one run of 7 jobs in two arms). Firmware (EDM) tasks, not client pixel tasks"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["firmware-tasks-p1137-f10", "vectors-firmware-tasks-p1137"]
terms = ["Event Data Master (EDM)"]
+++
**What ran.** Two arms of one of our firmware tasks each: `p1137_imm` (680 instructions, accepted by
the verifier) tests n = 0 to 127 in blocks of eight (`ldad.bypassl1` of eight values V_n from the
page, one `wdf`, then eight `xor.testtanz.chan0 !c0, p0, r, #n` each followed by `mov r, #0` and `p0
mov r, #1`, the results stored to the page), and `p1137_wide` (416 instructions) tests 64 values W
of 128 up to 0xffffffff, each loaded into a register by a limm `mov` and tested against V from the
page. Four jobs of the first (V = n; V = n xor 1 << (n mod 32); V = n or 0xffffff80; V = n xor 1 <<
((n + 16) mod 32)) and three of the second (V = W, two jobs with one bit flipped). Each job's V, the
128 or 64 result dwords' sentinels and the run id are the host's own, every value distinct over the
whole plan and never the page's initial fill.

**Results.** [HW] 7 of 7 jobs as predicted, with 128 + 128 + 128 + 128 and 64 + 64 + 64 results
checked (704 p0 values, 4 x 128 + 3 x 64, read as the model, 0 not; the V = n jobs alone would also
read all false if p0 were stuck false, and the one-bit jobs all true if it were stuck true, so
together they exclude both): V = n gave all false, the one-bit jobs and V = n or 0xffffff80 all
true. Job times 0.16 to 0.78 ms. The arms: tick 991.2 Hz (`p1137_imm`) and 998.0 Hz (`p1137_wide`),
the verifier accepted both, no log line of the kernel's own-task path; after each reset the gate was
exact (fill and triangle) and the tick rate 995.3 and 972.9 Hz. The kernel log of the stage (150
lines) shows the two debugfs resets at BIF_FAULT 0x0, EVENT_STATUS 0x20000000/0x400 and no fault.

**Against the predictions.** P37_F10a held (4 of 4 jobs), P37_F10b held (3 of 3 jobs).

**What it shows.** [HW] In a firmware task the 7-bit test immediate is exact for 0 to 127 and
zero-extended, so a backend can emit `#n` for n <= 127 and a limm `mov` plus the register test for
any 32-bit n; the limm is exact for the 64 values tried, the field boundaries included [infer] The
same for other n above 127. A host check, not a hardware result and not part of any dataset: the
assembler's word for the limm of 2128 values (64 wide W, 2000 random, every power of two and every
low mask) is read back equal by the loader's limm decoder, and the test form assembles for n = 0 to
127 only (0 to 1099 swept); the script and its output are probes/p1136/imm_encode.py and
imm-encode.txt.

**What it does not show.** n = 128 and up as an immediate (the assembler refuses it, `#128`, so no
raw word was run); the non-test rotated 16-bit immediate (`and r, r, #n`: the landed verifier's
verdict function says unknown form for `and r12, r5, #5`, which verifier-matrix.txt does not list);
the other test channels.
