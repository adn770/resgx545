+++
id = "E1085"
claim = "r19-own stage own1 (Q191) decided nothing: on its first flag-0xc row (o1-c-a, 64x64, P 0x422) t18b's copy of render_kept right after the first context's early close read 0 bytes although the kernel logged the context closed and kept (slot 0, TA data 0x20000000), and the copy after the second context's render read 24576 bytes with the four owner words 0x00200047, 0x04000417, 0x00020001, 2 (75 non-zero dwords, as E631's ow-kcopy-c); hook_check stopped the stage (1 of 2 copies) and the 4 other rows did not run; the control o1-4 (flag 0x4) passed: both copies 24576 bytes and no owner word in either; frozen: 'own1a: cannot tell: no row decided', 'own1b: cannot tell: no row decided'"
unit = "dpm"
method = "r19-own (render/closing-r19-own), stage own1 of the question-closing pass (round 19, closing19/DECISIONS-R19.md (R19-1 to R19-6 (a); S3 r19-own, safe), plan closing19/plan/rank-round19.md section 4; run over the travel cable after r19-k0 stopped at its own gate (2 jobs had touched the module), folded with the lead's confirmation), dataset render-closing-r19-own; attempt out/20261114-223625 (scores score-own1.txt); on the laptop (host cedar over the direct cable, kernel 7.3.0-resgx545, module srcversion E0CC40275493F8AEAD8180B (linux fork 456404fcffe5, installed and loaded alike), stock firmware, tool ~/sgxfive-test-t18b (t18b, sha256 58e7985504d0d3311155d94627da8b8473335d9a843f5610e44731864315b21e, built from resgx545 ec50498, recipe data:render/closing-r19-own/lead/build_tool18b.sh) for the rows and t10 for the health pair, every row `tri --width W --height H -n 1 --keep-overflow --wait-ms 20000 --ctx2 --close-first-early --kept-copy DIR --words DIR --kpoke-render 1:ta:7^=F` with debugfs render_keep armed and render_pb_pages P (tables/STAGE.txt, frozen predictions/STAGE.tsv from gen/make.py), a debugfs reset and the health pair around every row); freezes: FROZEN.sha256 daf8d12997815f3b012ed7181b70328eb3e94fe1236d1711aab1ffe0b181f901 (40 files), PREDICTIONS.sha256 105109b9bd8dd6696e6eab8ba0666c860739578d136fc923acf7175bf32b5510 (2 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 6809cddd, resgx545:tools/closing/kit/lib_kit.sh at 6809cddd, resgx545:tools/closing/kit/run_stage.sh at 6809cddd, resgx545:tools/closing/kit/kitscore.py at 6809cddd, resgx545:tools/closing/kit/fake/sudo at 6809cddd, resgx545:tools/closing/kit/fake/timeout at 6809cddd, resgx545:tools/closing/kit/fake/df at 6809cddd, resgx545:tools/closing/kit/fake/modinfo at 6809cddd, resgx545:tools/closing/kit/fake/sha256sum at 6809cddd, resgx545:tools/closing/kit/fake/tool.sh at 6809cddd, resgx545:tools/closing/kit/fake/tool.py at 6809cddd, resgx545:tools/closing/kit/fake/ssh.py at 6809cddd, resgx545:tools/closing/scorekit.py at 6809cddd, resgx545:tools/closing/sessioncheck.py at 6809cddd, data:dpm/partial-model-batch/dumps/owner-safe.c1/ow-part-solo.kept.bin.gz at 95df71e9, data:dpm/partial-model-batch/dumps/owner-safe.c1/ow-part-c-k.kept.bin.gz at 95df71e9, data:dpm/partial-model-batch/dumps/owner-safe.c1/ow-kcopy-c.kept.1.bin.gz at 95df71e9, data:dpm/partial-model-batch/dumps/owner-safe.c1/ow-kcopy-4.kept.1.bin.gz at 95df71e9, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built, ec50498e6b5cbf3ebff07233da508023dd28f4a2 at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; TOOLSRC.sha256: 70aa910e14ae8040072b8c2cde5991830c4dcfe6bcd35ccf722c080ee9f38e29 ec50498e6b5cbf3ebff07233da508023dd28f4a2:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=E0CC40275493F8AEAD8180B; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW", "infer"]
date = "2026-11-14"
data = ["render-closing-r19-own:out/20261114-223625/own1/", "render-closing-r19-own:fold/"]
terms = ["CR_DPM_STATE_BASE0", "CR_DPM_CONTROL_BASE", "ta3d_ctl"]
+++
**What ran.** Stage own1 (closing19/plan/rank-round19.md section 4), after own2: `o1-4` (the
control, 64x64, flag 0x4), then `o1-c-a` (64x64, flag 0xc, fit); `o1-c-b`, `o1-big-a`, `o1-big-b`
(1024x768 at P 0x422) and `o1-p200` did not run. The form is E1084's.

**Frozen verdict (as printed).** attempt 20261114-223625, stage own1 (run.log): `SUMMARY: own1a:
cannot tell: no row decided`; `SUMMARY: own1b: cannot tell: no row decided`. The runner: `## STOP
(stage own1): o1-c-a: 1 of 2 kept copies made (render_keep not taken or render_kept unreadable),
after o1-c-a`.

**Results [HW].** `o1-4`: both copies 24576 bytes, the control, OTPM and state pages (pages 1 to 3)
zero in both, 71 non-zero dwords after the render (E631's ow-kcopy-4). `o1-c-a`: `job: ok` twice,
exact; `tri: render_kept after closing the first context, before the second context's render 1:
... (0 bytes)`; the kernel slice holds `render context 0x32411000 closed and kept: slot 0, TA data
0x20000000`; the copy after the second render is 24576 bytes with the four owner words in pages 1
to 3 and 75 non-zero dwords, as E631's ow-kcopy-c. The frozen scorer re-run on the kept files is
byte for byte (fold/reproduce-own1.txt).

**What it shows.** [HW] The flag-0xc words of E631 are repeated after the second render on this
module (1 of 1). [infer] The empty copy is a race of the tool against the kernel: render_kept reads
0 bytes while no context is parked (each job starts after a reset, which releases the parked
ones), and the context is parked when its last reference goes (`sgxfive_ctx_release`, which calls
`sgxfive_render_fini`, at fork 456404fcffe5), which can be after the close ioctl returns if a
finished job still holds one; t18b copies at once. The 7 other copies after an early close in
this session (own2's 6, o1-4) were made in time.

**What it does not show.** Whether the words are in the 64x64 owner's pages before the second
render (Q191's kick against close), and the 1024x768 owner's state words (H-COUNT).
