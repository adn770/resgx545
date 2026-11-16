+++
id = "E1126"
claim = "r32-misc on module 7CE8E38E (Q111, a served kick without INVAL_DATA), stage m1 (the kit word pre:miscinfo: one debugfs miscinfo read, a GETMISCINFO command with no cache control pending, after the reset and before snap0), every control passed, every non-control row held out: CR_CACHE_CTRL reads 0x0000ffff in snap0 after the served read in 7 of 7 rows (H-CC-FW held 7 of 7, H-CC-HW refuted 7 of 7), so a served kick whose command carries no INVAL_DATA does not set bit 28; the triangle after the read still leaves 0x1000ffff (H-CC-ONE 7 of 7); the read is answered in 154 to 161 us (H-MI-LAT 6 of 6), as the boot's own GETMISCINFO after each reset (the controls: one logged answer before snap0 without the word, two with it); whether bit 28 is the firmware's write or the hardware's response to the firmware's INVAL_DATA work is not decided"
unit = "platform"
method = "r32-misc (render/closing-r32-misc), stage m1 of the question-closing pass (round 32: the user's decision of 2026-11-16 to add the kit word pre:miscinfo, safe stages only, a debugfs miscinfo read with no data invalidation after the kit's reset and before snap0, never a register write; the direct test of closing29/r31-cc/fold/next-miscinfo.md (E1123); session built on the kit of resgx545 80d9f2a, safe class, records E1126 and E1127 reserved by the frozen README), dataset render-closing-r32-misc; attempt out/20261116-185655 (scores score-m1.txt); on the laptop (host cedar over the travel cable, kernel 7.3.0-resgx545, module srcversion 7CE8E38EDB97FC5EA4F6C90 (N1; installed and loaded alike, fork 8bc0877e8603), stock firmware, tool ~/sgxfive-test-t10 (t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, resgx545 a581c06); t10 `tri --width 64 --height 64` after the kit's reset, 9 rows: controls m1-c1 and m1-c3 without the word, m1-c2 and m1-01..06 with pre:miscinfo; no knob, no kreg, no register write); freezes: FROZEN.sha256 1ec181964674e1ba1634249180bd6e7ae8de1a7eb5cca295a7e327949d2c177b (37 files), PREDICTIONS.sha256 0aafe6876128d7b94dc7dd3404f3cb186d8fbe014be54b88c0598dec9af03bf8 (2 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 80d9f2a1, resgx545:tools/closing/kit/lib_kit.sh at 80d9f2a1, resgx545:tools/closing/kit/run_stage.sh at 80d9f2a1, resgx545:tools/closing/kit/kitscore.py at 80d9f2a1, resgx545:tools/closing/kit/fake/sudo at 80d9f2a1, resgx545:tools/closing/kit/fake/timeout at 80d9f2a1, resgx545:tools/closing/kit/fake/df at 80d9f2a1, resgx545:tools/closing/kit/fake/modinfo at 80d9f2a1, resgx545:tools/closing/kit/fake/sha256sum at 80d9f2a1, resgx545:tools/closing/kit/fake/tool.sh at 80d9f2a1, resgx545:tools/closing/kit/fake/tool.py at 80d9f2a1, resgx545:tools/closing/kit/fake/ssh.py at 80d9f2a1, resgx545:tools/closing/scorekit.py at 80d9f2a1, resgx545:tools/closing/sessioncheck.py at 80d9f2a1, data:render/closing-r31-cc/out/20261116-144402/c1/kernel.log at 6b5c5112, data:render/closing-r31-cc/out/20261116-144402/c1/c1-01.snap0.regs.gz at 6b5c5112, data:render/closing-r31-cc/out/20261116-144402/c1/c1-01.snap9.regs.gz at 6b5c5112, data:render/closing-r31-cc/out/20261116-144402/c1/c1-01.txt.gz at 6b5c5112, data:render/closing-r31-cc/out/20261116-144402/c2/c2-01.txt.gz at 6b5c5112, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=7CE8E38EDB97FC5EA4F6C90; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW", "infer"]
date = "2026-11-16"
data = ["render-closing-r32-misc:out/20261116-185655/m1/", "render-closing-r32-misc:fold/"]
terms = ["CR_CACHE_CTRL"]
+++
**What ran.** r32-misc's stage m1 (closing29/r32-misc README, pre-run): 9 plain 64x64 triangles
of t10 after the kit's reset, m1-01 to m1-06 and the control m1-c2 with the kit word
`pre:miscinfo` (resgx545 45bbaaa): the runner reads debugfs `miscinfo` once after the reset and
before `snap0`, which sends one GETMISCINFO command with the pending cache control, and stops
before the job unless the kernel's answer was served (`GETMISCINFO answered after N us`, `all
values match`). The boot's own GETMISCINFO after each reset (`sgxfive_ident_ask`) carries the
firmware file's cache control (INVAL_BIF_PD 0x2, doc/specs/boot_sequence.md) and `sgxfive_command`
clears it once sent (fork 8bc0877e8603), so the word's command carries none; neither has
INVAL_DATA (bit 3). Frozen: H-CC-FW (snap0 0x0804 0x0000ffff after the read) against H-CC-HW
(0x1000ffff: any served kick sets bit 28), counted only where the read was served and the
triangle after it set bit 28; H-CC-ONE (snap9 0x1000ffff); H-MI-LAT (100 to 400 us, from r31-cc's
boot answers, post hoc). Controls: m1-c1, m1-c3 (no word) diff 0, cache 0x0000ffff, cache9
0x1000ffff, kicks 1 (the kernel's logged answers after the last boot kick before snap0); m1-c2 diff
0, mi 1, kicks 2.

**Frozen verdict (as printed).** Every control PASS (m1-c1, m1-c3: `diff=0 cache=0x0000ffff
cache9=0x1000ffff kicks=1`; m1-c2: `diff=0 mi=1 kicks=2`). `m1 H-CC-FW [held]: ... (7 of 7 rows
decided)`, `m1 H-CC-HW [held]: ... is not supported: 0 held, 7 FAILED, 0 cannot tell of 7`, `m1
H-CC-ONE [held]: ... (7 of 7 rows decided)`, `m1 H-MI-LAT [held]: ... (6 of 6 rows decided)`.
fold/reproduce.out reproduces every score byte for byte.

**Results [HW].** snap0 0x0804 0x0000ffff in all 9 rows, snap9 0x1000ffff in all 9; every job drew
exactly. The word's answers 154 to 161 us (NAME.miscinfo, every one `all values match`). Post hoc
(fold/posthoc.txt, the stage's kernel.log): one `SGX firmware: core 545 ... answered after N us`
after each boot kick and one for each word read, so every word row had two served GETMISCINFO
commands before its snap0 and every other row one; snap0 comes 3 s after the last.

**What it shows.** A served kick without INVAL_DATA, with no cache control at all (the word's)
or with INVAL_BIF_PD only (the boot's, here and in r31-cc's 52 snap0 after it, post hoc), leaves
CR_CACHE_CTRL at the reset word: the hardware does not set bit 28 at a kick (H-CC-HW refuted).
With E1123 (the change follows the kick pass's BIF write) and E1120 to E1123 (every kick with
INVAL_DATA, a triangle's or a fill's, sets it) bit 28 goes with the command's INVAL_DATA [infer:
the cache-control word is the one difference between the two kinds of kick here]. The read does
not change the triangle's own change (H-CC-ONE). For sgx-sim: a read after a served kick whose
run never writes the register answers the reset word, as the model's E1122 rule already does.

**What it does not show.** Whether bit 28 is the firmware's literal `| 0x10000000` (E013) or a
hardware response to the work the firmware does for INVAL_DATA: both need bit 3, and the kit has
no kick that carries INVAL_DATA alone; what the firmware's own read after a TA kick returns
(inside one sample, E1123); a kick with BIF bits other than INVAL_BIF_PD; the other
CR_EVENT_STATUS bits Q111 names.
