+++
id = "E1033"
claim = "r13-flag stage f1 (4 probe fills on a twiddled 32 x 32 32-bit texture in E566's tx_map form, the default 16-page scratch; planned faults): T3 bit 14 faulted both twiddled rows, E566's own tw32-t3b14 (u in (1, 2)) and a held-out row with u = x / 4096 (E1003's move 0 to 63 texels), BIF fault 0x90002 at the scratch's page + 0x21000 and + 0x40000, past every mapping of the job; frozen 'H-FAULTANY (2 of 2 rows decided)', 'H-E566 (1 of 1 rows decided)', the three move models (the move in the twiddled index, in the column unwrapped, in the column wrapped) 'not supported: 0 held, 2 FAILED'; both bit-clear references (E566's tw32-ctl byte for byte, the tile law's column 0) passed"
unit = "texture"
method = "r13-flag (render/closing-r13-flag), stage f1 of the question-closing pass (round 13, the flagged session: decisions R13-3 (a) (f1, f2) and R13-4 (a) (f3) of closing13/DECISIONS-R13.md with the user's OK for planned faults and recovered hangs only, plan closing13/plan/rank-round13.md sections 2 and 3), dataset render-closing-r13-flag; attempt out/20261113-220930 (f1 22:09:32 Mac time; driver log run.log; its freeze FROZEN.sha256 3fe98f0a30f0c91240269673f835201a7469a158610d66a885138137775ecc59; scores score-f1.txt); on the laptop (host cedar, kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (linux fork 2a650d74, installed and loaded alike), stock firmware, tool ~/sgxfive-test-t10 (t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, built from resgx545 a581c06), every job one process of the kit runner (kit/run_stage.sh at resgx545 0493e36), a debugfs reset before every row without noreset, a reset and the strict health fill and triangle after every fault or hang, no debugfs knob written, every output and kernel slice kept gzipped; the rows are tables/STAGE.txt, the frozen predictions predictions/STAGE.tsv (gen/make.py)); freezes: FROZEN.sha256 3fe98f0a30f0c91240269673f835201a7469a158610d66a885138137775ecc59 (78 files), PREDICTIONS.sha256 fc5833e71af828d4e8c31114d7073631ba5ea710b169c5be2aad9ba340d22615 (11 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 0493e36a, resgx545:tools/closing/kit/lib_kit.sh at 0493e36a, resgx545:tools/closing/kit/run_stage.sh at 0493e36a, resgx545:tools/closing/kit/kitscore.py at 0493e36a, resgx545:tools/closing/kit/fake/sudo at 0493e36a, resgx545:tools/closing/kit/fake/timeout at 0493e36a, resgx545:tools/closing/kit/fake/df at 0493e36a, resgx545:tools/closing/kit/fake/modinfo at 0493e36a, resgx545:tools/closing/kit/fake/sha256sum at 0493e36a, resgx545:tools/closing/kit/fake/tool.sh at 0493e36a, resgx545:tools/closing/kit/fake/tool.py at 0493e36a, resgx545:tools/closing/kit/fake/ssh.py at 0493e36a, resgx545:tools/closing/scorekit.py at 0493e36a, resgx545:tools/closing/sessioncheck.py at 0493e36a, data:texture/p1141/templates/tx_map.s at 75d01ee2, data:texture/p1141/support/build.py at 75d01ee2, data:texture/p1141/support/texmodel.py at 75d01ee2, data:texture/p1141/support/specs.json at 75d01ee2, data:texture/p1132/tx-t3/tw32-ctl.txt.gz at 75d01ee2, data:texture/p1132-recomp/raw/tx-t3bits/bins/tx-t3bits__33.bin at 75d01ee2, data:render/closing-r10-tex/gen/pins.py at 75d01ee2, data:render/closing-r10-tex/gen/tex.py at 75d01ee2, data:render/closing-r10-tex/gen/addr.py at 75d01ee2, data:pbe/sideband-channels/pbe-sideband-channels-0208/bins/eot_plain.bin at 75d01ee2, data:pbe/sideband-channels/pbe-sideband-channels-0208/bins/pbe-sideband-channels-0208__0.bin at 75d01ee2, data:pbe/sideband-channels/pbe-sideband-channels-bit12-1200/raw.txt at 75d01ee2, data:pbe/sideband-channels/kernel.log at 75d01ee2, data:render/closing-r6-render4x/bins/p1131-green__0.bin at 75d01ee2, resgx545:probes/ta/templates/pix_green.s at 0493e36a, resgx545:probes/ta/templates/pix_op.s at 0493e36a, resgx545:probes/ta/p1131-progs.toml at 0493e36a, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=B60AB0B475DD1E8972419B5; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["render-closing-r13-flag:out/20261113-220930/f1/", "render-closing-r13-flag:fold/"]
terms = ["T3.BIT14", "CR_BIF_INT_STAT"]
+++
**What ran.** E566's tx_map form (scratch dword i = 0xD0000000 | i), a twiddled 32 x 32 texture (T1
0x0C01F01F) at the scratch's first dword, `probe --temps 32 --coords --pixels` with the default
16-page scratch at 0x3e003000 (the coordinates' 3 pages after it, to 0x3e016000). Rows in run order:
f1-ref-a (control: E566's tw32-ctl program, byte for byte the published one), f1-tw32 (E566's
tw32-t3b14: the same with T3 bit 14, u in (1, 2), so E1003's move floor(4096 clamp(u, 0, 1)) is
4096),
f1-ref-b (control: u = x / 4096, v on row y's centre, bit 14 clear) and f1-small (held out: the same
with bit 14, a move of x = 0 to 63 texels). The two bit-14 rows were the stage's planned rows
(`expectfault`, `#limit 2`).

**Frozen verdict (as printed).** attempt 20261113-220930, stage f1 (run.log): `SUMMARY: f1: H-E566:
T3 bit 14 on a twiddled 32 x 32 texture (1 of 1 rows decided)`; attempt 20261113-220930, stage f1
(run.log): `SUMMARY: f1: H-FAULTANY: T3 bit 14 on a twiddled 32 x 32 texture (2 of 2 rows decided)`;
attempt 20261113-220930, stage f1 (run.log): `SUMMARY: f1: H-TWIDX: T3 bit 14 on a twiddled 32 x 32
texture is not supported: 0 held, 2 FAILED, 0 cannot tell of 2`; attempt 20261113-220930, stage f1
(run.log): `SUMMARY: f1: H-TWX: T3 bit 14 on a twiddled 32 x 32 texture is not supported: 0 held, 2
FAILED, 0 cannot tell of 2`; attempt 20261113-220930, stage f1 (run.log): `SUMMARY: f1: H-TWX-WRAP:
T3 bit 14 on a twiddled 32 x 32 texture is not supported: 0 held, 2 FAILED, 0 cannot tell of 2`.

**Results [HW].** Both controls passed: f1-ref-a drew E566's kept tw32-ctl image and f1-ref-b the
tile
law's column 0 (E561's law, 2048 of 2048 each). Both bit-14 rows faulted (`job faulted, context
lost`), each with one kernel line: f1-tw32 `BIF fault 0x90002 at 0x3e024001` (page scratch +
0x21000,
14 pages past the coordinates' end), f1-small `BIF fault 0x90002 at 0x3e043001` (page scratch +
0x40000, 45 pages past it); the scratch was unchanged, the strict health drew after each, and no
recovery failed (fold/look.out). H-TWX's page (+ 0x40000) was frozen for f1-tw32, where the fault
landed at + 0x21000; on f1-small it froze an image.

**What it shows.** [HW] T3 bit 14 on a twiddled texture faults the job: E566's fault replicates, and
a
held-out row whose strided reading (E1003) would move every read by at most 63 texels faults too, at
a page 256 KiB past the scratch. So the move E1003 measured on strided textures is not what bit 14
does to a twiddled read: the move in the twiddled index (the plan's H-TWMOVE), in the texel column
and in the wrapped column each predicted an image there. [infer] On a twiddled texture the bit sends
the read far outside the texture (the two fault pages are each the first faulting page only, so they
bound nothing below them).

**What it does not show.** Where the reads go: only the first faulting page of each job is read, and
no row with a scratch large enough to hold them ran (the 1 MiB heap past the scratch is unmapped).
Whether pixels with u = 0 (no move on a strided texture) fault too, or whether any twiddled read
with
bit 14 faults whatever u; other twiddled sizes, a filtered sample (Q078's other clause). The fault
status 0x90002 differs from f2's 0x91000 in its low bits [infer: the requestor].
