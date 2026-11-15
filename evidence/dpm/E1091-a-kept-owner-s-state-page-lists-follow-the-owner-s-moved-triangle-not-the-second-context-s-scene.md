+++
id = "E1091"
claim = "r20-own stages ow and owt (6 jobs, t18b under regtimeline, render_keep armed, a 1024x768 owner at P 0x422 closed early, the second context drawing the library's default triangle): with the owner's triangle moved, the lists in the kept owner's state page after the second context's render are the owner's moved cover, not the second context's scene: macrotiles 0, 1, 2, 3, 4, 5, 6, 8, 9 and 12 at the move -112,-80 (2 of 2) and 0, 1, 4, 5, 6, 7, 9, 10, 11, 13 and 14 at 64,64 (1 of 1), exactly gen/cover.py's covers, counts summing to the owner's own peak less 1 (20 and 21; regtimeline 0x0724 under the owner's state base 0x20006000 peaks at 0x15 and 0x16, the second context's at 0x13); frozen 'ow: H-SECOND ... is not supported: 0 held, 3 FAILED' with the rival H-OWNER fitting 3 of 3; the unmoved control repeated E1087's pages 4 to 6 dword for dword; which kick stores is not decided ('owt: cannot tell: no row decided'): 0x0694 and 0x0698 read 0 in every sample of every row, and the state base the scorer took for the owner's (words.101 rtds:11, 0x20406000) is the one 0x062c holds during the second context's run"
unit = "dpm"
method = "r20-own (render/closing-r20-own), stages ow, owt of the question-closing pass (round 20, closing20/plan/rank-round20.md section 4, S2, user decisions R20-1 to R20-7 (a, R20-3 b), run over the travel cable, folded with the lead's confirmation), dataset render-closing-r20-own; attempt out/20261115-080117 (scores score-ow.txt, score-owt.txt); on the laptop host cedar over the direct cable, kernel 7.3.0-resgx545, module srcversion E0CC40275493F8AEAD8180B (linux fork 456404fcffe5, installed and loaded alike), stock firmware, tool ~/sgxfive-test-t18b (t18b, sha256 58e7985504d0d3311155d94627da8b8473335d9a843f5610e44731864315b21e, built from resgx545 ec50498, recipe data:render/closing-r19-own/lead/build_tool18b.sh) under ~/regtimeline (sha256 079f63590ce87ff2a1ac5499291e52340ff448d9c5e41942a9420264764de803, read only, `0 0.3 REGS --`) for the rows and t10 for the health pair, every row `tri --width 1024 --height 768 -n 1 --keep-overflow --wait-ms 20000 --ctx2 --close-first-early --kept-copy DIR --words DIR --kpoke-render 1:ta:7^=0xc [--move 1:DX,DY]` with debugfs render_keep armed and render_pb_pages P (tables/ow.txt/owt.txt, frozen predictions from gen/make.py, the moves from gen/cover.py), a debugfs reset and the health pair around every row; freezes: FROZEN.sha256 f9058c19fe87f72b3f03a6e21236d54fd937d773460edf3fbe60d761df424c3c (47 files), PREDICTIONS.sha256 efd2cffd3090994e241c64af738ef5ddc598e164f460bcb82e70ab67bd8fbc0c (3 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at c0f8c41f, resgx545:tools/closing/kit/lib_kit.sh at c0f8c41f, resgx545:tools/closing/kit/run_stage.sh at c0f8c41f, resgx545:tools/closing/kit/kitscore.py at c0f8c41f, resgx545:tools/closing/kit/fake/sudo at c0f8c41f, resgx545:tools/closing/kit/fake/timeout at c0f8c41f, resgx545:tools/closing/kit/fake/df at c0f8c41f, resgx545:tools/closing/kit/fake/modinfo at c0f8c41f, resgx545:tools/closing/kit/fake/sha256sum at c0f8c41f, resgx545:tools/closing/kit/fake/tool.sh at c0f8c41f, resgx545:tools/closing/kit/fake/tool.py at c0f8c41f, resgx545:tools/closing/kit/fake/ssh.py at c0f8c41f, resgx545:tools/closing/scorekit.py at c0f8c41f, resgx545:tools/closing/sessioncheck.py at c0f8c41f, data:render/closing-r19-own1b/out/20261114-230658/own1/o1-big-a.kept.1.bin.gz at ba3990f0, data:render/closing-r19-own1b/out/20261114-230658/own1/o1-big-a.kept.closed.1.bin.gz at ba3990f0, data:render/closing-r19-own1b/out/20261114-230658/own1/o1-big-a.ta3d.101.bin.gz at ba3990f0, data:render/closing-r19-own1b/out/20261114-230658/own1/o1-big-a.words.101.txt.gz at ba3990f0, data:render/closing-r19-own/out/20261114-223625/own2/o2-p30.kept.1.bin.gz at ba3990f0, data:render/closing-r19-own/out/20261114-223625/own2/o2-p30.kept.closed.1.bin.gz at ba3990f0, data:render/closing-r19-own/out/20261114-223625/own2/o2-p30.ta3d.101.bin.gz at ba3990f0, data:render/closing-r19-own/out/20261114-223625/own2/o2-c-a.kept.1.bin.gz at ba3990f0, data:render/closing-r19-own/out/20261114-223625/own2/o2-c-a.kept.closed.1.bin.gz at ba3990f0, data:render/closing-r19-own/out/20261114-223625/own2/o2-c-a.ta3d.101.bin.gz at ba3990f0, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built, ec50498e6b5cbf3ebff07233da508023dd28f4a2 at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; TOOLSRC.sha256: 70aa910e14ae8040072b8c2cde5991830c4dcfe6bcd35ccf722c080ee9f38e29 ec50498e6b5cbf3ebff07233da508023dd28f4a2:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=E0CC40275493F8AEAD8180B; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW", "infer"]
date = "2026-11-15"
data = ["render-closing-r20-own:out/20261115-080117/ow/", "render-closing-r20-own:out/20261115-080117/owt/", "render-closing-r20-own:fold/"]
terms = ["CR_DPM_STATE_BASE0", "CR_DPM_TASK_STATE", "CR_DPM_TASK_CONTROL"]
+++
**What ran.** Stage ow, 4 rows in order: `ow-c` (control, unmoved), `ow-m1-a` and `ow-m1-b` (fit,
the owner moved by `--move 1:-112,-80`) and `ow-m2` (held out, `--move 1:64,64`), regtimeline on
0x0620-0x0634, 0x0658, 0x065c, 0x0674, 0x0694, 0x0698 and 0x0700-0x0728. Stage owt, 2 unmoved rows
(`owt-a` control and fit, `owt-b` held out) with regtimeline on 0x062c, 0x0634, 0x0694 and 0x0698
only. `--move 1:` moves the first context's triangle only; the second context draws the default.
The plan's move -128,-96 was replaced by -112,-80 because its vertices sit on macrotile edges, where
a pixel-centre cover and a conservative tile cover differ; at -112,-80 and 64,64 they agree
(gen/cover.py). The pages are located by the fork's layout (control, OTPM and state pages 4, 5 and
6) and compared by dword. No copy right after the close read empty (22 of 22 copies made).

**Frozen verdict (as printed).** attempt 20261115-080117 (run.log): `SUMMARY: ow: H-SECOND: the
kept owner's lists after the second render are the second context's scene, not the owner's (Q191)
is not supported: 0 held, 3 FAILED, 0 cannot tell of 3` with `FITS: H-OWNER 3`; `SUMMARY: owt:
cannot tell: no row decided`. The controls ow-c and owt-a passed (no overflow, 2 copies of 69632
bytes, the closed copy's pages 4 to 6 zero, the after copy's E1087's dword for dword).

**Results [HW].** Every job ended rc 0 and exact. After the second render the kept owner's state
page lists macrotiles 0, 1, 2, 3, 4, 5, 6, 8, 9, 12 (ow-m1-a, ow-m1-b; counts sum 20) and 0, 1, 4,
5, 6, 7, 9, 10, 11, 13, 14 (ow-m2; sum 21), with the global entry 16 0x00010001, 1, against
E1087's 0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 13 (sum 18) unmoved. regtimeline shows two runs per job:
0x062c = 0x20006000 while 0x0724's high half climbs to 0x13 (unmoved), 0x15 (-112,-80) or 0x16
(64,64), then 0x062c = 0x20406000 while it climbs to 0x13 in every row
(fold/timeline-stretches.txt).
0x0694 and 0x0698 are 0 in every sample of all 6 jobs; 0x062c does not return to 0x20006000 after
the second run starts. The frozen scorer re-run on the kept files is byte for byte
(fold/reproduce-ow.txt, fold/reproduce-owt.txt).

**What it shows.** [HW] The lists stored in the kept owner's state page follow the owner's
triangle, not the second context's: the macrotile set is the owner's moved cover and the counts sum
to the owner's peak less 1, as E1087's unmoved lists summed to U - 1. [infer] The first run, under
state base 0x20006000, is the owner's (its peak follows the move) and the second, under 0x20406000,
the second context's, so the base words.101 reports (rtds:11 0x20406000) is not the owner's GPU
state base as 0x062c sees it; owt's frozen rule looked for the wrong base. Q191's "whose scene" is
decided: the owner's.

**What it does not show.** Which event writes the lists (no task write was visible in 0x0694 or
0x0698 at any sample, and 0x062c never shows the owner's base again during the second run), why
they appear only after the second context's run (E1087: the closed copy is zero), and whether any
task reads them back.
