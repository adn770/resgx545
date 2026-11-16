+++
id = "E1119"
claim = "r30-pde stage f67 (Q109, a size field the BIF does not take; every s0 control passed): a client directory entry with the unnamed size codes 6 and 7 is walked as 4 KiB entries like codes 0 to 5: four copies (each code twice) completed and read region pages 4 to 7 through table entries 4 to 7, as frozen H-ALIAS predicts (4 of 4), with no fault, no hang, BIF_INT_STAT 0x80000 and BIF_FAULT 0 after each; the frozen H-FAULT and H-ALIAS16 were refuted (0 held, 4 FAILED each)"
unit = "bif"
method = "r30-pde (render/closing-r30-pde), stage f67 of the question-closing pass (round 30, the round 29 kernel plan's N1 session (decision N-4 a): the full flagged session approved by the user 2026-11-16, at most 20 planned faults), dataset render-closing-r30-pde; attempt out/20261116-131809 (scores score-f67.txt); on the laptop (host cedar over the travel cable, kernel 7.3.0-resgx545, module srcversion 7CE8E38EDB97FC5EA4F6C90 (linux fork r30-kernel 8bc0877e8603: debugfs vm_pde_addr, vm_pde_size, vm_pde_layout and vm_large; installed and loaded alike, booted once with the user's OK; its KUnit suites passed in the fork's series check on the laptop, 222 of 222 with the debug option), stock firmware, tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7, built on the laptop by lead/build_tool30_laptop.sh), health ~/sgxfive-test-t10; every job a debugfs reset, the row's dbg: knobs written and read back (vm_pde_addr 0x60000000, vm_pde_size, vm_pde_layout), `sgxfive-test-t30 copy --src-addr A --height H --large-copy W` or `fill --dst-addr A --height H --large-copy W` (64 pixels wide, stride 256), the knobs restored; the rows tables/STAGE.txt from gen/make.py, the frozen predictions predictions/STAGE.tsv from gen/pde.py, a port of the fork's sgx_mmu_large.c held to its KUnit values); freezes: FROZEN.sha256 9050a555c5997e08fa476c53e34ac06ac71929a50b5d03cca77aa202778d3830 (47 files), PREDICTIONS.sha256 d8ee143980226f0b0e0092b6946349c79611bf0b5cb41abd1993cb740fdc1d97 (5 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 42c4de78, resgx545:tools/closing/kit/lib_kit.sh at 42c4de78, resgx545:tools/closing/kit/run_stage.sh at 42c4de78, resgx545:tools/closing/kit/kitscore.py at 42c4de78, resgx545:tools/closing/kit/fake/sudo at 42c4de78, resgx545:tools/closing/kit/fake/timeout at 42c4de78, resgx545:tools/closing/kit/fake/df at 42c4de78, resgx545:tools/closing/kit/fake/modinfo at 42c4de78, resgx545:tools/closing/kit/fake/sha256sum at 42c4de78, resgx545:tools/closing/kit/fake/tool.sh at 42c4de78, resgx545:tools/closing/kit/fake/tool.py at 42c4de78, resgx545:tools/closing/kit/fake/ssh.py at 42c4de78, resgx545:tools/closing/scorekit.py at 42c4de78, resgx545:tools/closing/sessioncheck.py at 42c4de78, resgx545:userspace/libsgxfive/tools/sgxfive-test.c at 42c4de78, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built, 42c4de7855d6f310321cc03fa0780b698a735e4d at built; tools: TOOLSRC.sha256: 253fd15bcb6a0a6381d20aacbb635af1c99d764388f394f9a24dc61266b6418d 42c4de7855d6f310321cc03fa0780b698a735e4d:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=7CE8E38EDB97FC5EA4F6C90; pinned commits named by the session: resgx545 main 42c4de7855d6; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW", "infer"]
date = "2026-11-16"
data = ["render-closing-r30-pde:out/20261116-131809/f67/", "render-closing-r30-pde:fold/"]
terms = ["CR_BIF_DIR_LIST_BASE0", "CR_BIF_FAULT", "CR_BIF_INT_STAT"]
+++
**What ran.** f67, last: `copy --src-addr 0x60004000 --height 64` (VA [16K, 32K) of the slot)
with vm_pde_size 6, 7, 6, 7, the table of one 4 MiB region whose entry i names its own page i
(entry 0 page 1), so the reading names the size taken: 4 KiB entries or any size from 64 KiB give
pages 4 to 7, 16 KiB gives pages 0 to 3 with the table page first (README, pre-run; same attempt
and module as E1117).

**Frozen verdict (as printed).** `H-ALIAS: the unnamed code is taken as a size (any but 16 KiB, or
4 KiB entries) (4 of 4 rows decided)`; `H-ALIAS16 ... is not supported: 0 held, 4 FAILED`;
`H-FAULT: the BIF does not take the entry: the job faults (or hangs, recovered) is not supported:
0 held, 4 FAILED`. The frozen rule: `Q109 CLAUSE 3 code 6: taken as a size (not 16 KiB)`, the same
for code 7, and `Q109 RULE: RETIRE (every clause has its reading)`.

**Results [HW].** Each copy read `0:4,0:5,0:6,0:7` (job: ok, 409 to 411 us), the table intact,
nothing changed; BIF_INT_STAT 0x80000 and BIF_FAULT 0 in the runner's snapshot after each job,
and no kernel BIF line.

**What it shows.** With E1117: the BIF reports nothing for size codes 6 and 7, because it does
not read the size field at all; every code 0 to 7 walks 4 KiB entries [infer: from codes 1 to 5
walking 4 KiB entries, the reading H-ALIAS shares with the 4 KiB walk].

**What it does not show.** These rows cannot tell 4 KiB entries from a size of 64 KiB or more for
codes 6 and 7 (the table was built so that those give the same pages); E1117's codes 1 to 5,
whose rows do tell them apart, are the reason to read it as the 4 KiB walk [infer].
