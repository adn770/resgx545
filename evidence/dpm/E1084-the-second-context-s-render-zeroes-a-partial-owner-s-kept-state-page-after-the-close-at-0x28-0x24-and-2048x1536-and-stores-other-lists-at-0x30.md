+++
id = "E1084"
claim = "r19-own stage own2 (6 jobs, t18b, render_keep armed, 1024x768 owners kept by the first context's early close; t18b copied the kept TA data after the close and after the second context's render): the owner's state page (page 6; 0x12000 at 2048x1536) held its lists after the close (18 non-zero dwords at P 0x28 in 3 of 3 rows, flags 0xc and 0x4; 24 at 0x24; 10 at 2048x1536 and 0x28; 20 at 0x30) and was zero after the second context's render in 5 of 6 rows (P 0x28 x3, 0x24, 2048x1536), so the zero E631 read after the tool exits is made between the close and the end of that render, not by the close or the second context's creation; at P 0x30 (held out) the render left 10 other non-zero dwords there instead (lists of other pages and the global list 0x00010001, 1) and 4 words 0x002002xx in the control page; frozen: 'H-RSTORE ... is not supported: 5 held, 1 FAILED, 0 cannot tell of 6' (o2-p30 the FAILED row, H-LATE's '>0' by count); the control o2-c-a passed (overflow 1, 2 copies, 69632 bytes)"
unit = "dpm"
method = "r19-own (render/closing-r19-own), stage own2 of the question-closing pass (round 19, closing19/DECISIONS-R19.md (R19-1 to R19-6 (a); S3 r19-own, safe), plan closing19/plan/rank-round19.md section 4; run over the travel cable after r19-k0 stopped at its own gate (2 jobs had touched the module), folded with the lead's confirmation), dataset render-closing-r19-own; attempt out/20261114-223625 (scores score-own2.txt); on the laptop (host cedar over the direct cable, kernel 7.3.0-resgx545, module srcversion E0CC40275493F8AEAD8180B (linux fork 456404fcffe5, installed and loaded alike), stock firmware, tool ~/sgxfive-test-t18b (t18b, sha256 58e7985504d0d3311155d94627da8b8473335d9a843f5610e44731864315b21e, built from resgx545 ec50498, recipe data:render/closing-r19-own/lead/build_tool18b.sh) for the rows and t10 for the health pair, every row `tri --width W --height H -n 1 --keep-overflow --wait-ms 20000 --ctx2 --close-first-early --kept-copy DIR --words DIR --kpoke-render 1:ta:7^=F` with debugfs render_keep armed and render_pb_pages P (tables/STAGE.txt, frozen predictions/STAGE.tsv from gen/make.py), a debugfs reset and the health pair around every row); freezes: FROZEN.sha256 daf8d12997815f3b012ed7181b70328eb3e94fe1236d1711aab1ffe0b181f901 (40 files), PREDICTIONS.sha256 105109b9bd8dd6696e6eab8ba0666c860739578d136fc923acf7175bf32b5510 (2 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 6809cddd, resgx545:tools/closing/kit/lib_kit.sh at 6809cddd, resgx545:tools/closing/kit/run_stage.sh at 6809cddd, resgx545:tools/closing/kit/kitscore.py at 6809cddd, resgx545:tools/closing/kit/fake/sudo at 6809cddd, resgx545:tools/closing/kit/fake/timeout at 6809cddd, resgx545:tools/closing/kit/fake/df at 6809cddd, resgx545:tools/closing/kit/fake/modinfo at 6809cddd, resgx545:tools/closing/kit/fake/sha256sum at 6809cddd, resgx545:tools/closing/kit/fake/tool.sh at 6809cddd, resgx545:tools/closing/kit/fake/tool.py at 6809cddd, resgx545:tools/closing/kit/fake/ssh.py at 6809cddd, resgx545:tools/closing/scorekit.py at 6809cddd, resgx545:tools/closing/sessioncheck.py at 6809cddd, data:dpm/partial-model-batch/dumps/owner-safe.c1/ow-part-solo.kept.bin.gz at 95df71e9, data:dpm/partial-model-batch/dumps/owner-safe.c1/ow-part-c-k.kept.bin.gz at 95df71e9, data:dpm/partial-model-batch/dumps/owner-safe.c1/ow-kcopy-c.kept.1.bin.gz at 95df71e9, data:dpm/partial-model-batch/dumps/owner-safe.c1/ow-kcopy-4.kept.1.bin.gz at 95df71e9, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built, ec50498e6b5cbf3ebff07233da508023dd28f4a2 at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; TOOLSRC.sha256: 70aa910e14ae8040072b8c2cde5991830c4dcfe6bcd35ccf722c080ee9f38e29 ec50498e6b5cbf3ebff07233da508023dd28f4a2:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=E0CC40275493F8AEAD8180B; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW", "infer"]
date = "2026-11-14"
data = ["render-closing-r19-own:out/20261114-223625/own2/", "render-closing-r19-own:fold/"]
terms = ["CR_DPM_STATE_BASE0", "CR_DPM_CONTROL_BASE", "ta3d_ctl"]
+++
**What ran.** Stage own2 (closing19/plan/rank-round19.md section 4), 6 rows in order: `o2-c-a`
(control and E631's case), `o2-c-b` (flag 0xc) and `o2-4` (flag 0x4) at P 0x28, fit; `o2-p30` and
`o2-p24` at P 0x30 and 0x24, and `o2-2k` (2048x1536 at 0x28), held out; all with flag 0xc but
`o2-4`. Every row ran a 1024x768 (or 2048x1536) first context whose render overflowed the
parameter buffer (partial renders), closed it early with render_keep armed, and had t18b copy
debugfs render_kept to `kept.closed.1.bin` right after the close and to `kept.1.bin` after the
second context's render (which overflowed too), before any other close. The DPM pages are located
by the fork's layout (score.py `layout`, tested against the fork's KUnit table): control, OTPM and
state at 0x4000, 0x5000 and 0x6000 for 1024x768 and at 0x10000, 0x11000 and 0x12000 for 2048x1536.

**Frozen verdict (as printed).** attempt 20261114-223625, stage own2 (run.log): `SUMMARY: own2:
H-RSTORE: the partial owner's state page holds its lists after the close and is zero after the
second context's render (Q192) is not supported: 5 held, 1 FAILED, 0 cannot tell of 6`.

**Results [HW].** Every job ended rc 0, both copies made, sizes 69632 (225280 at 2048x1536).
Non-zero
dwords of the state page, after the close / after the second render: `o2-c-a` 18 / 0, `o2-c-b`
18 / 0, `o2-4` 18 / 0, `o2-p24` 24 / 0, `o2-2k` 10 / 0, `o2-p30` 20 / 10. The pages that differ
between the copies are the state page alone, except `o2-4` (page 4, the control page: the 5 words
0x00200057, 0x002000ad, 0x0020007e, 0x002000c0, 0x00200087 at dwords 0, 1, 4, 5, 8 appear after the
render, E631's 5 words) and `o2-p30` (pages 1, 4 and 6: after the render the state page holds
pairs 0x00010010, 0x10; 0x00020011, 0x13; 0x00010014, 0x14; 0x0002000f, 0x12 and entry 16
0x00010001,
1, and the control page 0x00200203, 0x0020027f, 0x0020029b, 0x00200245 at dwords 2, 6, 7, 10; page
1's two dwords 0x80400243, 0x80400244 at 512 and 513 are gone). The control o2-c-a passed. The
frozen scorer re-run on the kept files is byte for byte (fold/reproduce-own2.txt).

**What it shows.** [HW] For a partial-render owner the lists stay in its kept state page through
the close, and the second context's run (between that close and the end of its render) replaces
them: with zero at P 0x28 (both flags), 0x24 and at 2048x1536, and at 0x30 with a different set of
lists, also in the control page. So the store that follows the next context's render does replace
a partial owner's state page (Q192), and what it writes depends on that run. [infer] The 0x30 lists
look like a state page written for the second context's own scene (E627: at 0x2d to 0x34 the
abort's threshold is not raised and the state page keeps the abort's lists), the zero like the
raised regime's page after its last partial render; this is post hoc and not tested.

**What it does not show.** Which event of the second context's run stores (its TA kick, a partial
render, or its render's end), why 0x30 differs (one row), whether the 0x30 lists are the second
context's own, and whether a load task reads the page back.
