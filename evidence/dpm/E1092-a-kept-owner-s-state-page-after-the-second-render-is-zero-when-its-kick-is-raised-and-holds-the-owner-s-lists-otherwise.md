+++
id = "E1092"
claim = "r20-own stage owp (5 jobs, t18b under regtimeline, render_keep armed, a 1024x768 owner closed early after its overflowing render, the second context drawing the default triangle): the kept owner's state page after the second context's render is zero when the owner's kick is raised and holds E627 lists when it is not, by the regime read per row (TA3DCtl dword 38): raised at P 0x2c zero; not raised at 0x30 E1084's ten dwords exactly (3 of 3 with the control), at 0x34 one list (macrotile 7) and the global list; frozen 'owp: H-REGIME ... (5 of 5 rows decided)'; with the owner moved -112,-80 at 0x30 the lists are 1, 2, 3, 5, 6 and 9, within the owner's moved cover and not E1084's (frozen 'owpw: H-SECOND ... is not supported: 0 held, 1 FAILED', H-OWNER fitting), so they are the owner's; post hoc, not raised, the lists of the copy made right after the close and those after the second render together make the owner's cover in each of the 4 not-raised rows"
unit = "dpm"
method = "r20-own (render/closing-r20-own), stage owp of the question-closing pass (round 20, closing20/plan/rank-round20.md section 4, S2, user decisions R20-1 to R20-7 (a, R20-3 b), run over the travel cable, folded with the lead's confirmation), dataset render-closing-r20-own; attempt out/20261115-080117 (scores score-owp.txt); on the laptop host cedar over the direct cable, kernel 7.3.0-resgx545, module srcversion E0CC40275493F8AEAD8180B (linux fork 456404fcffe5, installed and loaded alike), stock firmware, tool ~/sgxfive-test-t18b (t18b, sha256 58e7985504d0d3311155d94627da8b8473335d9a843f5610e44731864315b21e, built from resgx545 ec50498, recipe data:render/closing-r19-own/lead/build_tool18b.sh) under ~/regtimeline (sha256 079f63590ce87ff2a1ac5499291e52340ff448d9c5e41942a9420264764de803, read only, `0 0.3 REGS --`) for the rows and t10 for the health pair, every row `tri --width 1024 --height 768 -n 1 --keep-overflow --wait-ms 20000 --ctx2 --close-first-early --kept-copy DIR --words DIR --kpoke-render 1:ta:7^=0xc [--move 1:DX,DY]` with debugfs render_keep armed and render_pb_pages P (tables/owp.txt, frozen predictions from gen/make.py, the moves from gen/cover.py), a debugfs reset and the health pair around every row; freezes: FROZEN.sha256 f9058c19fe87f72b3f03a6e21236d54fd937d773460edf3fbe60d761df424c3c (47 files), PREDICTIONS.sha256 efd2cffd3090994e241c64af738ef5ddc598e164f460bcb82e70ab67bd8fbc0c (3 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at c0f8c41f, resgx545:tools/closing/kit/lib_kit.sh at c0f8c41f, resgx545:tools/closing/kit/run_stage.sh at c0f8c41f, resgx545:tools/closing/kit/kitscore.py at c0f8c41f, resgx545:tools/closing/kit/fake/sudo at c0f8c41f, resgx545:tools/closing/kit/fake/timeout at c0f8c41f, resgx545:tools/closing/kit/fake/df at c0f8c41f, resgx545:tools/closing/kit/fake/modinfo at c0f8c41f, resgx545:tools/closing/kit/fake/sha256sum at c0f8c41f, resgx545:tools/closing/kit/fake/tool.sh at c0f8c41f, resgx545:tools/closing/kit/fake/tool.py at c0f8c41f, resgx545:tools/closing/kit/fake/ssh.py at c0f8c41f, resgx545:tools/closing/scorekit.py at c0f8c41f, resgx545:tools/closing/sessioncheck.py at c0f8c41f, data:render/closing-r19-own1b/out/20261114-230658/own1/o1-big-a.kept.1.bin.gz at ba3990f0, data:render/closing-r19-own1b/out/20261114-230658/own1/o1-big-a.kept.closed.1.bin.gz at ba3990f0, data:render/closing-r19-own1b/out/20261114-230658/own1/o1-big-a.ta3d.101.bin.gz at ba3990f0, data:render/closing-r19-own1b/out/20261114-230658/own1/o1-big-a.words.101.txt.gz at ba3990f0, data:render/closing-r19-own/out/20261114-223625/own2/o2-p30.kept.1.bin.gz at ba3990f0, data:render/closing-r19-own/out/20261114-223625/own2/o2-p30.kept.closed.1.bin.gz at ba3990f0, data:render/closing-r19-own/out/20261114-223625/own2/o2-p30.ta3d.101.bin.gz at ba3990f0, data:render/closing-r19-own/out/20261114-223625/own2/o2-c-a.kept.1.bin.gz at ba3990f0, data:render/closing-r19-own/out/20261114-223625/own2/o2-c-a.kept.closed.1.bin.gz at ba3990f0, data:render/closing-r19-own/out/20261114-223625/own2/o2-c-a.ta3d.101.bin.gz at ba3990f0, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built, ec50498e6b5cbf3ebff07233da508023dd28f4a2 at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; TOOLSRC.sha256: 70aa910e14ae8040072b8c2cde5991830c4dcfe6bcd35ccf722c080ee9f38e29 ec50498e6b5cbf3ebff07233da508023dd28f4a2:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=E0CC40275493F8AEAD8180B; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW", "infer"]
date = "2026-11-15"
data = ["render-closing-r20-own:out/20261115-080117/owp/", "render-closing-r20-own:fold/"]
terms = ["CR_DPM_STATE_BASE0", "ta3d_ctl"]
+++
**What ran.** Stage owp, 5 rows in order: `owp-30-a` (control and fit, P 0x30: E1084's o2-p30
again), `owp-30-b` (fit, the same), `owp-30m` (held out, P 0x30, the owner moved by `--move
1:-112,-80`), `owp-2c` and `owp-34` (held out, P 0x2c and 0x34), regtimeline as E1091's ow. Both
contexts take P from render_pb_pages; the owner's regime is read from its `ta3d.101.bin` dword 38
(raised iff non-zero, E625), and a row is scored under the regime read. Pages by the fork's layout
(state page 6), compared by dword.

**Frozen verdict (as printed).** attempt 20261115-080117 (run.log): `SUMMARY: owp: H-REGIME: the
owner's state page after the second render is zero iff its kick is raised, E627 lists otherwise, a
repeat at 0x30 (Q192) (5 of 5 rows decided)`; `SUMMARY: owpw: H-SECOND: a moved owner at 0x30 keeps
the second context's lists (Q192) is not supported: 0 held, 1 FAILED, 0 cannot tell of 1` with
`FITS: H-OWNER 1, H-REGIME 5`. The control owp-30-a passed (overflow 1, 2 copies of 69632 bytes,
page 6 E1084's o2-p30 dword for dword).

**Results [HW].** Every job ended rc 0 (both contexts' first renders overflowed, as E1084's).
Regimes: 0x2c raised, 0x30 and 0x34 not raised. After the second render page 6 holds: 0x30 (2 rows
and the control) 0x00010010, 0x10; 0x00020011, 0x13; 0x00010014, 0x14; 0x0002000f, 0x12 at pairs
2, 6, 7 and 10 and 0x00010001, 1 at entry 16, as E1084; 0x30 moved: lists at 1, 2, 3, 5, 6 and 9
and entry 16; 0x34: 0x00010013, 0x13 at pair 7 and entry 16; 0x2c: zero. The copy right after the
close holds the owner's abort lists at 0, 1, 2, 4, 5, 6, 8, 9, 13 (0x30), 0, 1, 4, 5, 8, 9, 12
(0x30 moved), 0, 1, 2, 4, 5, 6, 8, 9, 10, 13 (0x34) and 2, 5, 6, 7, 9, 10, 13 (0x2c, raised).
regtimeline's 0x0724 peaks at 0xe, 0xe, 0xe, 0xb and 0x12 under both state bases. The frozen
scorer re-run on the kept files is byte for byte (fold/reproduce-owp.txt).

**What it shows.** [HW] E1084's 0x30 lists repeat (3 of 3), and the state page left after the
second context's run follows E627's two regimes: zero when the owner's kick was raised, lists when
it was not (0x2c against 0x30 and 0x34). The lists of a moved owner are inside its own cover and
differ from the unmoved owner's, so they are the owner's, not the second context's (E1091's ow
too). [infer] Not raised, the after lists hold every macrotile of the owner's cover that the abort's
lists left out, and some listed again (0x30:
{0, 1, 2, 4, 5, 6, 8, 9, 13} and {2, 6, 7, 10}; moved: {0, 1, 4, 5, 8, 9, 12} and {1, 2, 3,
5, 6, 9}; 0x34: ten and {7}), their union the owner's cover: the lists the owner's TA built
after its abort, as E627's raised reading (2 and 6 at 0x30, 1, 5 and 9 moved, are in both).

**What it does not show.** Which event of the second context's run stores (Q191: no task write
seen, E1091), why a raised owner's page ends zero, and whether a load reads these lists back.
