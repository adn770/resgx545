+++
id = "E1127"
claim = "r32-misc on module 7CE8E38E (Q111), stage m2 (pre:miscinfo, then t10's 64x64 triangle under regtimeline on CR_CACHE_CTRL and CR_USE0_SERV_EVENT at 852 to 856 ns a sample), every control passed, the non-control row held out: the first sample after the served read reads 0x0000ffff and snap0 too (H-CC-FW held 3 of 3, H-CC-HW refuted 3 of 3); the triangle's change comes once, to 0x1000ffff (H-CC-ONE 3 of 3), 24.41 and 25.15 ms after the tool starts (H-CC-LAT 2 of 2, inside E1122's 18.3 to 25.2 ms); the read answered in 148 us (H-MI-LAT 1 of 1)"
unit = "platform"
method = "r32-misc (render/closing-r32-misc), stage m2 of the question-closing pass (round 32: the user's decision of 2026-11-16 to add the kit word pre:miscinfo, safe stages only, a debugfs miscinfo read with no data invalidation after the kit's reset and before snap0, never a register write; the direct test of closing29/r31-cc/fold/next-miscinfo.md (E1123); session built on the kit of resgx545 80d9f2a, safe class, records E1126 and E1127 reserved by the frozen README), dataset render-closing-r32-misc; attempt out/20261116-185655 (scores score-m2.txt); on the laptop (host cedar over the travel cable, kernel 7.3.0-resgx545, module srcversion 7CE8E38EDB97FC5EA4F6C90 (N1; installed and loaded alike, fork 8bc0877e8603), stock firmware, tool ~/sgxfive-test-t10 (t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, resgx545 a581c06); pre:miscinfo then `regtimeline 1.5 0.5 0x0804,0x0b14 -- ~/sgxfive-test-t10 tri --width 64 --height 64` after the kit's reset, 2 rows: control m2-c1 and m2-01; regtimeline ~/regtimeline sha256 079f63590ce87ff2a1ac5499291e52340ff448d9c5e41942a9420264764de803, tools/sweep/regtimeline.c, read only through /dev/mem; no knob, no kreg, no register write); freezes: FROZEN.sha256 1ec181964674e1ba1634249180bd6e7ae8de1a7eb5cca295a7e327949d2c177b (37 files), PREDICTIONS.sha256 0aafe6876128d7b94dc7dd3404f3cb186d8fbe014be54b88c0598dec9af03bf8 (2 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 80d9f2a1, resgx545:tools/closing/kit/lib_kit.sh at 80d9f2a1, resgx545:tools/closing/kit/run_stage.sh at 80d9f2a1, resgx545:tools/closing/kit/kitscore.py at 80d9f2a1, resgx545:tools/closing/kit/fake/sudo at 80d9f2a1, resgx545:tools/closing/kit/fake/timeout at 80d9f2a1, resgx545:tools/closing/kit/fake/df at 80d9f2a1, resgx545:tools/closing/kit/fake/modinfo at 80d9f2a1, resgx545:tools/closing/kit/fake/sha256sum at 80d9f2a1, resgx545:tools/closing/kit/fake/tool.sh at 80d9f2a1, resgx545:tools/closing/kit/fake/tool.py at 80d9f2a1, resgx545:tools/closing/kit/fake/ssh.py at 80d9f2a1, resgx545:tools/closing/scorekit.py at 80d9f2a1, resgx545:tools/closing/sessioncheck.py at 80d9f2a1, data:render/closing-r31-cc/out/20261116-144402/c1/kernel.log at 6b5c5112, data:render/closing-r31-cc/out/20261116-144402/c1/c1-01.snap0.regs.gz at 6b5c5112, data:render/closing-r31-cc/out/20261116-144402/c1/c1-01.snap9.regs.gz at 6b5c5112, data:render/closing-r31-cc/out/20261116-144402/c1/c1-01.txt.gz at 6b5c5112, data:render/closing-r31-cc/out/20261116-144402/c2/c2-01.txt.gz at 6b5c5112, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=7CE8E38EDB97FC5EA4F6C90; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW"]
date = "2026-11-16"
data = ["render-closing-r32-misc:out/20261116-185655/m2/", "render-closing-r32-misc:fold/"]
terms = ["CR_CACHE_CTRL"]
+++
**What ran.** r32-misc's stage m2 (closing29/r32-misc README, pre-run): 2 rows, the control m2-c1
and m2-01, each `pre:miscinfo` (as E1126) then `regtimeline 1.5 0.5 0x0804,0x0b14 --
~/sgxfive-test-t10 tri --width 64 --height 64` after the kit's reset. Frozen: H-CC-FW (snap0 and
the timeline's first sample 0x0000ffff) against H-CC-HW (0x1000ffff), H-CC-ONE (one change, to
0x1000ffff), H-CC-LAT (10 to 40 ms after the tool starts; E1122 18.3 to 25.2, post hoc), H-MI-LAT.
Control m2-c1: diff 0, ivl 400 to 3000 ns, mi 1, kicks 2. The sampling starts 0.5 s before t10,
after snap0, so it does not time the read itself.

**Frozen verdict (as printed).** Control m2-c1 PASS. `m2 H-CC-FW [held]: ... (3 of 3 rows
decided)`, `m2 H-CC-HW [held]: ... is not supported: 0 held, 3 FAILED, 0 cannot tell of 3`, `m2
H-CC-LAT [held]: ... (2 of 2 rows decided)`, `m2 H-CC-ONE [held]: ... (3 of 3 rows decided)`, `m2
H-MI-LAT [held]: ... (1 of 1 rows decided)`. fold/reproduce.out reproduces every score byte for
byte.

**Results [HW].** Both rows: snap0 and the first sample 0x0000ffff, one change to 0x1000ffff held to
the end, at 24.41 (m2-c1) and 25.15 ms (m2-01) after the tool starts, snap9 0x1000ffff, 856 and
852 ns a sample; the word's answers 155 and 148 us, two logged answers before each snap0
(fold/posthoc.txt). Both jobs drew exactly.

**What it shows.** The reset word holds from the served read through the 0.5 s lead to the
triangle's own kick, and that kick changes it once, at the time E1122 measured without the read:
the earlier GETMISCINFO neither sets bit 28 nor moves the triangle's change.

**What it does not show.** The read's own moment (the timeline starts after snap0); whether bit 28
is the firmware's write or a hardware response to its INVAL_DATA work (E1126); two rows only, so
the latency is consistent with E1122, not a new distribution.
