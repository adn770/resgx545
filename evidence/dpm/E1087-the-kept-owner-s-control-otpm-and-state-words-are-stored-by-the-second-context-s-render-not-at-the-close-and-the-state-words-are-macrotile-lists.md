+++
id = "E1087"
claim = "r19-own1b stage own1 (8 jobs, t18b, render_keep armed, the first context closed early; t18b copied the kept TA data right after the close and after the second context's render, every copy made): the 64x64 owner's words 0x00200047, 0x04000417, 0x00020001 and 2 (control, OTPM and state pages, pages 1 to 3) were in no copy made right after the close and in every copy after the second render, flag 0xc, 5 of 5 rows (4 at P 0x422, 1 at 0x200), and in neither copy with flag 0x4 (the control), so they are stored by the second context's run between the close and its render's end, not at the close; frozen 'own1a: H-RENDER ... (5 of 5 rows decided)'; for a 1024x768 owner at P 0x422 (no partial render) the state page after the second render begins 0x00010002, 2, not the owner's page count (H-COUNT 'is not supported: 0 held, 2 FAILED'), nor 0x00020001, 2 (H-CONST) nor 0 (H-NONE): post hoc it holds 11 macrotile list pairs (count << 16 | head, tail) whose counts sum to 18, U - 1 for the scene's 19 pages, with 11 words 0x002000xx to 0x002002xx in the control page and 0x04000417 at the OTPM page's dword 16, all three pages zero right after the close (2 of 2, identical)"
unit = "dpm"
method = "r19-own1b (render/closing-r19-own1b), stage own1 of the question-closing pass (round 19, the lead's decision after r19-own's attempt 20261114-223625 stopped its own1 at o1-c-a on an empty copy right after the close (E1085): own1 of closing19/plan/rank-round19.md section 4 again with two more 64x64 flag-0xc repeats, an empty copy a row's cannot tell; run over the travel cable, folded with the lead's confirmation), dataset render-closing-r19-own1b; attempt out/20261114-230658 (scores score-own1.txt); on the laptop (host cedar over the direct cable, kernel 7.3.0-resgx545, module srcversion E0CC40275493F8AEAD8180B (linux fork 456404fcffe5, installed and loaded alike), stock firmware, tool ~/sgxfive-test-t18b (t18b, sha256 58e7985504d0d3311155d94627da8b8473335d9a843f5610e44731864315b21e, built from resgx545 ec50498, recipe data:render/closing-r19-own/lead/build_tool18b.sh) for the rows and t10 for the health pair, every row `tri --width W --height H -n 1 --keep-overflow --wait-ms 20000 --ctx2 --close-first-early --kept-copy DIR --words DIR --kpoke-render 1:ta:7^=F` with debugfs render_keep armed and render_pb_pages P (tables/own1.txt, frozen predictions/own1.tsv from gen/make.py), a debugfs reset and the health pair around every row); freezes: FROZEN.sha256 4953d37af5b85fdc177afb9b9be3d743c44041e97f45ee95db144fe0f9f929ce (35 files), PREDICTIONS.sha256 9ce2db54ba4fae9fd1b798decbaf221e618ced2c1162e7f072028a7f85ce7697 (1 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 50606dc1, resgx545:tools/closing/kit/lib_kit.sh at 50606dc1, resgx545:tools/closing/kit/run_stage.sh at 50606dc1, resgx545:tools/closing/kit/kitscore.py at 50606dc1, resgx545:tools/closing/kit/fake/sudo at 50606dc1, resgx545:tools/closing/kit/fake/timeout at 50606dc1, resgx545:tools/closing/kit/fake/df at 50606dc1, resgx545:tools/closing/kit/fake/modinfo at 50606dc1, resgx545:tools/closing/kit/fake/sha256sum at 50606dc1, resgx545:tools/closing/kit/fake/tool.sh at 50606dc1, resgx545:tools/closing/kit/fake/tool.py at 50606dc1, resgx545:tools/closing/kit/fake/ssh.py at 50606dc1, resgx545:tools/closing/scorekit.py at 50606dc1, resgx545:tools/closing/sessioncheck.py at 50606dc1, data:dpm/partial-model-batch/dumps/owner-safe.c1/ow-kcopy-c.kept.1.bin.gz at 95df71e9, data:dpm/partial-model-batch/dumps/owner-safe.c1/ow-kcopy-4.kept.1.bin.gz at 95df71e9, data:dpm/partial-model-batch/dumps/owner-safe.c1/ow-part-c-k.kept.bin.gz at 95df71e9, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built, ec50498e6b5cbf3ebff07233da508023dd28f4a2 at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; TOOLSRC.sha256: 70aa910e14ae8040072b8c2cde5991830c4dcfe6bcd35ccf722c080ee9f38e29 ec50498e6b5cbf3ebff07233da508023dd28f4a2:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=E0CC40275493F8AEAD8180B; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW", "infer"]
date = "2026-11-14"
data = ["render-closing-r19-own1b:out/20261114-230658/own1/", "render-closing-r19-own1b:fold/"]
terms = ["CR_DPM_STATE_BASE0", "CR_DPM_CONTROL_BASE", "ta3d_ctl"]
+++
**What ran.** Stage own1, 8 rows in order: `o1-4` (control, 64x64, flag 0x4), `o1-c-a` to
`o1-c-d` (64x64, flag 0xc, fit: E1085's own1 rows and two repeats), `o1-big-a` and `o1-big-b`
(1024x768 at P 0x422, held out) and `o1-p200` (64x64 at P 0x200, held out). The form and the
hypotheses are E1084's and E1085's: the DPM pages are located by the fork's layout (64x64 pages 1, 2
and 3; 1024x768 pages 4, 5 and 6). A copy right after the close that read empty, as E1085's
o1-c-a did, would have made its row cannot tell; none did (16 of 16 copies made).

**Frozen verdict (as printed).** attempt 20261114-230658, stage own1 (run.log): `SUMMARY: own1a:
H-RENDER: the 64x64 owner's words are stored by the second context's render, not at the first
context's close (Q191 a, c) (5 of 5 rows decided)`; `SUMMARY: own1b: H-COUNT: the 1024x768 owner's
state words count its pages (Q191 b) is not supported: 0 held, 2 FAILED, 0 cannot tell of 2`. The
control o1-4 passed (no overflow, 2 copies of 24576 bytes, no owner word in either).

**Results [HW].** Every job ended rc 0 and exact. 64x64, flag 0xc: right after the close the
control, OTPM and state pages are zero; after the second render they hold 0x00200047, 0x04000417
and 0x00020001, 2 (5 of 5, P 0x422 and 0x200). 1024x768 at P 0x422 (both rows byte for byte the
same in the pages read): right after the close pages 4 to 6 are zero; after the second render the
state page holds the pairs 0x00010002, 2; 0x00010005, 5; 0x0001000d, 0xd; 0x00010003, 3;
0x00030006, 0xb; 0x0003000e, 0x12; 0x00010013, 0x13; 0x00010004, 4; 0x00030007, 0xc; 0x0002000f,
0x11; 0x00010008, 8 at dword pairs 0, 1, 2, 4, 5, 6, 7, 8, 9, 10 and 13; the control page
0x00200057,
0x002000a0, 0x002001a8, 0x0020007e, 0x00200160, 0x0020025f, 0x0020027b, 0x00200087, 0x0020019e,
0x00200225, 0x0020011a at dwords 0, 1, 2, 4, 5, 6, 7, 8, 9, 10 and 13; the OTPM page 0x04000417 at
dword 16; page 1 changes in 2 dwords. The frozen scorer re-run on the kept files is byte for byte
(fold/reproduce-own1.txt).

**What it shows.** [HW] The kept owner's control, OTPM and state words are not there after its
close and are there after the second context's render, so they are stored by that context's run,
by its render's end (Q191 a); the flag-0xc dependence holds (flag 0x4: none). [infer] The state
words are not a count of the owner's pages: they are macrotile lists in E627's format (count << 16
| head, tail), at 64x64 one list of 2 pages, at 1024x768 eleven lists whose counts sum to U - 1, and
the control page holds one word per listed macrotile at the same dword index (0x0020xxxx, the low
half different per macrotile; at 64x64 the one 0x00200047), the OTPM word 0x04000417 sitting at
dword 16 for 1024x768 and at 0 for 64x64. Both contexts draw the same scene at the same size, so
whose lists these are (the owner's or the second context's) is not separated.

**What it does not show.** Which event of the second context's run stores (its TA kick or its
render's end), whose scene the lists describe, and whether any task reads them back.
