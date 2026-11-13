+++
id = "E1034"
claim = "r13-flag stage f2 (4 jobs, E383's probe --tri form; planned faults): the frozen control failed, so every row is cannot tell ('controls FAILED: f2-ctl: FAILED'): E383's bit-12 mode 0 job (sideband 0x1200) completed with 3900 of its 4096 words in E383's set (frozen >= 4055); post hoc, its high 16 bits are E383's pixel for pixel (4096 of 4096, as in r13-tex's replicate of the same job) and its low 16 bits differ on 813 pixels (122 between the two round 13 runs), so the control's word-set rule could fail on a variation E383's two equal runs could not show; ungated, the three bit-11 rows (0x0a00, 0x0a04, 0x0a08) each faulted with BIF_INT_STAT 0x91000 at page 0x37001000, E383's status and page, at addresses 0x37001021, 0x37001011 and 0x37001011"
unit = "pbe"
method = "r13-flag (render/closing-r13-flag), stage f2 of the question-closing pass (round 13, the flagged session: decisions R13-3 (a) (f1, f2) and R13-4 (a) (f3) of closing13/DECISIONS-R13.md with the user's OK for planned faults and recovered hangs only, plan closing13/plan/rank-round13.md sections 2 and 3), dataset render-closing-r13-flag; attempt out/20261113-220930 (f2 22:10:25 Mac time; driver log run.log; its freeze FROZEN.sha256 3fe98f0a30f0c91240269673f835201a7469a158610d66a885138137775ecc59; scores score-f2.txt); on the laptop (host cedar, kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (linux fork 2a650d74, installed and loaded alike), stock firmware, tool ~/sgxfive-test-t10 (t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, built from resgx545 a581c06), every job one process of the kit runner (kit/run_stage.sh at resgx545 0493e36), a debugfs reset before every row without noreset, a reset and the strict health fill and triangle after every fault or hang, no debugfs knob written, every output and kernel slice kept gzipped; the rows are tables/STAGE.txt, the frozen predictions predictions/STAGE.tsv (gen/make.py)); freezes: FROZEN.sha256 3fe98f0a30f0c91240269673f835201a7469a158610d66a885138137775ecc59 (78 files), PREDICTIONS.sha256 fc5833e71af828d4e8c31114d7073631ba5ea710b169c5be2aad9ba340d22615 (11 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 0493e36a, resgx545:tools/closing/kit/lib_kit.sh at 0493e36a, resgx545:tools/closing/kit/run_stage.sh at 0493e36a, resgx545:tools/closing/kit/kitscore.py at 0493e36a, resgx545:tools/closing/kit/fake/sudo at 0493e36a, resgx545:tools/closing/kit/fake/timeout at 0493e36a, resgx545:tools/closing/kit/fake/df at 0493e36a, resgx545:tools/closing/kit/fake/modinfo at 0493e36a, resgx545:tools/closing/kit/fake/sha256sum at 0493e36a, resgx545:tools/closing/kit/fake/tool.sh at 0493e36a, resgx545:tools/closing/kit/fake/tool.py at 0493e36a, resgx545:tools/closing/kit/fake/ssh.py at 0493e36a, resgx545:tools/closing/scorekit.py at 0493e36a, resgx545:tools/closing/sessioncheck.py at 0493e36a, data:texture/p1141/templates/tx_map.s at 75d01ee2, data:texture/p1141/support/build.py at 75d01ee2, data:texture/p1141/support/texmodel.py at 75d01ee2, data:texture/p1141/support/specs.json at 75d01ee2, data:texture/p1132/tx-t3/tw32-ctl.txt.gz at 75d01ee2, data:texture/p1132-recomp/raw/tx-t3bits/bins/tx-t3bits__33.bin at 75d01ee2, data:render/closing-r10-tex/gen/pins.py at 75d01ee2, data:render/closing-r10-tex/gen/tex.py at 75d01ee2, data:render/closing-r10-tex/gen/addr.py at 75d01ee2, data:pbe/sideband-channels/pbe-sideband-channels-0208/bins/eot_plain.bin at 75d01ee2, data:pbe/sideband-channels/pbe-sideband-channels-0208/bins/pbe-sideband-channels-0208__0.bin at 75d01ee2, data:pbe/sideband-channels/pbe-sideband-channels-bit12-1200/raw.txt at 75d01ee2, data:pbe/sideband-channels/kernel.log at 75d01ee2, data:render/closing-r6-render4x/bins/p1131-green__0.bin at 75d01ee2, resgx545:probes/ta/templates/pix_green.s at 0493e36a, resgx545:probes/ta/templates/pix_op.s at 0493e36a, resgx545:probes/ta/p1131-progs.toml at 0493e36a, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=B60AB0B475DD1E8972419B5; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["render-closing-r13-flag:out/20261113-220930/f2/", "render-closing-r13-flag:fold/"]
terms = ["SIDEBAND.PACKMODE", "SIDEBAND.BIT9", "CR_BIF_INT_STAT"]
+++
**What ran.** E383's form (`probe --tri pixel --pixels`, the eot slot eot_plain, the pixel shader
writing 0xc0804020, E383's published bins), in run order: f2-ctl (control, sideband 0x1200: bit 12
in
pack mode 0 with E383's bit 9), then f2-b11-m0, -m4 and -m8 (sideband 0x0a00 | mode: bit 11 with bit
9), the stage's planned rows (`expectfault`, `#limit 3`). Frozen: the control completes with at
least
4055 of 4096 words in E383's mode 0 set (r13-tex sb12's H-FIXED); H-E383 (each bit-11 row faults),
H-E383-PAGE (BIF_INT_STAT 0x91000 at page 0x37001000 [infer: the same heap layout]), H-NOFAULT.

**Frozen verdict (as printed).** attempt 20261113-220930, stage f2 (run.log): `SUMMARY: f2: controls
FAILED: f2-ctl: FAILED`; attempt 20261113-220930, stage f2 (run.log): `SUMMARY: f2: controls FAILED:
f2-ctl: FAILED`; attempt 20261113-220930, stage f2 (run.log): `SUMMARY: f2: controls FAILED: f2-ctl:
FAILED`.

**Results [HW].** f2-ctl completed with 4096 words, 3900 of them in E383's set: the control FAILED
and
gates every row (cannot tell). The three bit-11 rows faulted (`job faulted, context lost`), each
with
one kernel line: `BIF fault 0x91000 at 0x37001021` (mode 0), `0x37001011` (mode 4) and `0x37001011`
(mode 8), all at page 0x37001000 (E383's: 0x3700103b, 0x37001003, 0x37001013 [infer: its log's
order]); the strict health drew after each, no recovery failed, and the runner's snapshot after each
job held no latched fault (the kernel's recovery had cleared it).

**Post hoc (fold/look.py, not frozen).** f2-ctl's high 16 bits equal E383's kept image pixel for
pixel (4096 of 4096); the 813 pixels that differ differ only in the low 16 bits. r13-tex's
sb12-rep-m0-c0, the same job earlier in the sitting, gives the same split (inset 3924; 799 pixels,
low 16 bits only), and the two round 13 runs differ on 122 pixels, again only in the low half.
E383's
two runs were equal on all 4096, which is why the frozen rule took the whole word as fixed.

**What it shows.** Nothing frozen: the gate is shut. [post hoc] Bit 12 in mode 0 stores a fixed high
half (the 0x0066 and 0x00ff pattern of E383, pixel for pixel) and a low half that varies run to run.
[HW, ungated] Bit 11 faults the job in modes 0, 4 and 8 on B60AB0B4 too, at E383's status and page
0x37001000, with low address bits that are not E383's.

**What it does not show.** What lies at 0x37001000 (which heap and buffer the PBE writes there),
what
bit 11 selects, and whether the low address bits follow the mode; the bit-12 low half's source (a
value left in memory, a counter) [infer]. No held-out reading of bit 11 is scored.
