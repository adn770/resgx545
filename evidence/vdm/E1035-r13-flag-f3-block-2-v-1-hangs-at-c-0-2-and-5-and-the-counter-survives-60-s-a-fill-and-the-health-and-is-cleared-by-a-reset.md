+++
id = "E1035"
claim = "r13-flag stage f3 (19 jobs, 8 recovered hangs, the kit's noreset and idle:S): E700's counter held on every clause row at v = 7 and failed below 2: a v = 7 job after a completed one hung on a 128 x 128 one-block target, after 60 s idle, after a fill job and after the kit's health fill and triangle, and completed after a reset that followed no hang (M1 and M3 held 5 of 5 there; H-SHAPE, H-DECAY, H-FILLCLR, H-HEALTHCLR and H-RESETKEEP each 0 of 1); block-2 v = 1 (grid bits 7:0 = 5) hung at c = 0, 2 and 5 (3 of 3), so 'M1 ... not supported: 5 held, 3 FAILED', 'M3 ... 6 held, 2 FAILED', 'H-C05 ... 2 held, 1 FAILED'; the control (E413's v = 7 pair) passed"
unit = "vdm"
method = "r13-flag (render/closing-r13-flag), stage f3 of the question-closing pass (round 13, the flagged session: decisions R13-3 (a) (f1, f2) and R13-4 (a) (f3) of closing13/DECISIONS-R13.md with the user's OK for planned faults and recovered hangs only, plan closing13/plan/rank-round13.md sections 2 and 3), dataset render-closing-r13-flag; attempt out/20261113-220930 (f3 22:11:24 Mac time; driver log run.log; its freeze FROZEN.sha256 3fe98f0a30f0c91240269673f835201a7469a158610d66a885138137775ecc59; scores score-f3.txt); on the laptop (host cedar, kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (linux fork 2a650d74, installed and loaded alike), stock firmware, tool ~/sgxfive-test-t10 (t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, built from resgx545 a581c06), every job one process of the kit runner (kit/run_stage.sh at resgx545 0493e36), a debugfs reset before every row without noreset, a reset and the strict health fill and triangle after every fault or hang, no debugfs knob written, every output and kernel slice kept gzipped; the rows are tables/STAGE.txt, the frozen predictions predictions/STAGE.tsv (gen/make.py)); freezes: FROZEN.sha256 3fe98f0a30f0c91240269673f835201a7469a158610d66a885138137775ecc59 (78 files), PREDICTIONS.sha256 fc5833e71af828d4e8c31114d7073631ba5ea710b169c5be2aad9ba340d22615 (11 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 0493e36a, resgx545:tools/closing/kit/lib_kit.sh at 0493e36a, resgx545:tools/closing/kit/run_stage.sh at 0493e36a, resgx545:tools/closing/kit/kitscore.py at 0493e36a, resgx545:tools/closing/kit/fake/sudo at 0493e36a, resgx545:tools/closing/kit/fake/timeout at 0493e36a, resgx545:tools/closing/kit/fake/df at 0493e36a, resgx545:tools/closing/kit/fake/modinfo at 0493e36a, resgx545:tools/closing/kit/fake/sha256sum at 0493e36a, resgx545:tools/closing/kit/fake/tool.sh at 0493e36a, resgx545:tools/closing/kit/fake/tool.py at 0493e36a, resgx545:tools/closing/kit/fake/ssh.py at 0493e36a, resgx545:tools/closing/scorekit.py at 0493e36a, resgx545:tools/closing/sessioncheck.py at 0493e36a, data:texture/p1141/templates/tx_map.s at 75d01ee2, data:texture/p1141/support/build.py at 75d01ee2, data:texture/p1141/support/texmodel.py at 75d01ee2, data:texture/p1141/support/specs.json at 75d01ee2, data:texture/p1132/tx-t3/tw32-ctl.txt.gz at 75d01ee2, data:texture/p1132-recomp/raw/tx-t3bits/bins/tx-t3bits__33.bin at 75d01ee2, data:render/closing-r10-tex/gen/pins.py at 75d01ee2, data:render/closing-r10-tex/gen/tex.py at 75d01ee2, data:render/closing-r10-tex/gen/addr.py at 75d01ee2, data:pbe/sideband-channels/pbe-sideband-channels-0208/bins/eot_plain.bin at 75d01ee2, data:pbe/sideband-channels/pbe-sideband-channels-0208/bins/pbe-sideband-channels-0208__0.bin at 75d01ee2, data:pbe/sideband-channels/pbe-sideband-channels-bit12-1200/raw.txt at 75d01ee2, data:pbe/sideband-channels/kernel.log at 75d01ee2, data:render/closing-r6-render4x/bins/p1131-green__0.bin at 75d01ee2, resgx545:probes/ta/templates/pix_green.s at 0493e36a, resgx545:probes/ta/templates/pix_op.s at 0493e36a, resgx545:probes/ta/p1131-progs.toml at 0493e36a, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=B60AB0B475DD1E8972419B5; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["render-closing-r13-flag:out/20261113-220930/f3/", "render-closing-r13-flag:fold/"]
terms = ["VDM_STATE1.BITS11_9"]
+++
**What ran.** Two forms: E700's two-block stream (`probe --tri pixel`, 12 vertices, two objects,
p1131-blue and p1131-green, block 1's bits 11:9 set by `--vdm 1^=`, block 2's by `--vdm 9^=`, block
2's
bits 7:0 at 5) and E413's one-triangle job (`tri --poke vdm:1^=0xa00`, v = 7). Each sequence opened
with a normal (reset) row; its later rows carried `noreset`. Rows: the control f3-c-a, f3-c-b
(E413's
pair: the second must hang); f3-v1c0 (block-2 v = 1 after a reset, c = 0); (4, 2) then v = 1 (c =
2);
(7, 2) then v = 1 (c = 5); a v = 7 pair at 128 x 128; a v = 7 pair with `idle:60` before the second;
a pair with a `fill` between (noreset); a pair with a plain triangle between, itself after a reset;
a pair with the kit's strict health (`after`) between. Eight planned rows (`expectfault`, `#limit
8`).

**Frozen verdict (as printed).** attempt 20261113-220930, stage f3 (run.log): `SUMMARY: f3: H-C05:
VDM_STATE1 bits 11:9 counter (Q163) is not supported: 2 held, 1 FAILED, 0 cannot tell of 3`; attempt
20261113-220930, stage f3 (run.log): `SUMMARY: f3: H-DECAY: VDM_STATE1 bits 11:9 counter (Q163) is
not supported: 0 held, 1 FAILED, 0 cannot tell of 1`; attempt 20261113-220930, stage f3 (run.log):
`SUMMARY: f3: H-FILLCLR: VDM_STATE1 bits 11:9 counter (Q163) is not supported: 0 held, 1 FAILED, 0
cannot tell of 1`; attempt 20261113-220930, stage f3 (run.log): `SUMMARY: f3: H-HEALTHCLR:
VDM_STATE1 bits 11:9 counter (Q163) is not supported: 0 held, 1 FAILED, 0 cannot tell of 1`; attempt
20261113-220930, stage f3 (run.log): `SUMMARY: f3: H-RESETKEEP: VDM_STATE1 bits 11:9 counter (Q163)
is not supported: 0 held, 1 FAILED, 0 cannot tell of 1`; attempt 20261113-220930, stage f3
(run.log): `SUMMARY: f3: H-SHAPE: VDM_STATE1 bits 11:9 counter (Q163) is not supported: 0 held, 1
FAILED, 0 cannot tell of 1`; attempt 20261113-220930, stage f3 (run.log): `SUMMARY: f3: M1:
VDM_STATE1 bits 11:9 counter (Q163) is not supported: 5 held, 3 FAILED, 0 cannot tell of 8`; attempt
20261113-220930, stage f3 (run.log): `SUMMARY: f3: M3: VDM_STATE1 bits 11:9 counter (Q163) is not
supported: 6 held, 2 FAILED, 0 cannot tell of 8`.

**Results [HW].** Every opening row, the fill and the plain triangle completed. Hangs (`job hung,
context lost`, one kernel `job N hung, recovering` line each, the strict health drawing after each,
no recovery failed): f3-c-b, f3-v1c0, f3-v1c2, f3-v1c5, f3-shape-b, f3-idle-b, f3-fill-b and
f3-hl-b, 8
of the 8 the kernel log names. f3-rst-b completed. With E700's c before each row (fold/look.out): v
=
7 at c = 5 hung 5 of 5 (64 x 64 after the control's first, 128 x 128, after 60 s, after a fill,
after
the health) and completed at c = 0 after the reset; block-2 v = 1 hung at c = 0, 2 and 5.

**What it shows.** [HW, held out] The counter's state is not cleared by 60 s of idle, by a fill job
or by the health fill and triangle between two jobs, and a debugfs reset that follows no hang clears
it (E700's single observation, held out). It holds for a one-block job on a 128 x 128 target. Below
2,
none of the frozen clauses holds: block-2 v = 1 with bits 7:0 at 5 hung at every c run (0, 2, 5),
where M1 (g(1) = -1) predicted three completions, M3 (a hang at c = 0 only) two, H-C05 one.
[post hoc] Against E1021's grid row sg-v1-r5 (the same word, completed at c = 3) and E701's c = 8
completion, neither c alone nor the word decides v = 1: [infer] the job before (here always a reset
or
a v 2 to 7 job of the same stream) is a candidate.

**What it does not show.** What the counter is; v = 1 in block 1 or v = 0; other stream shapes (24
or
48 vertices, three objects, other temporaries); idles longer than 60 s; a job of a second context
between.
