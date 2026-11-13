+++
id = "E953"
claim = "R9-geo stage seam1 (Q141; 24 tri renders with E504's pokes, each with --aa4 and debugfs render_rgn_arrays 1, a context made for 4x targets whose region headers are forced to one array, E502's, E504's and E727's condition): the stored image of every held-out job is the landed region model's (E727's msaa_model.py, E922's in-sample reading frozen as the O8 R8-1 table): H-REGION exact on 22 of 22 held-out sets (14 tri-full renders at sizes never run, 64 x 96 to 128 x 96 in modes 0 to 2 with TE 0x6, 0xa or 0xe, 6 single triangles of new slopes and 2 zero-hole twins; 20 to 514 holes, 211 to 5564 stored pixels, no other colour), its halves-off rival H-UNION 8 of 22; both controls passed (E502's A-m1-te60-64x64 64 holes as its set, E504's TE 0x20000000 no hole); frozen verdicts 'H-REGION exact on every held-out set (22 of 22 rows decided)' and 'H-UNION ... is not supported: 8 held, 14 FAILED'; Q141 retires"
unit = "isp"
method = "R9-geo stage seam1 of the question-closing pass, round 9 (S9-geo, decisions R9-3 a and S-1 a of the seeds plan closing9/seeds/exp-seeds-r9.md section 1), on the laptop (host cedar), 2026-11-13, attempt out/20261113-081038 (dataset render-closing-r9-geo; the only attempt, 77 jobs in four stages, every job class ok, no stop, no lead decision), kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (fork 2a650d74, the one-shot test boot; installed = loaded, knobs at their defaults at every stage start), tool ~/sgxfive-test-rgn4 (t4, sha256 e6951558..., bound by FROZEN.commits' built line to resgx545 4623753 userspace/libsgxfive/tools/sgxfive-test.c, sha256 703cbcea...), the session kit of resgx545 f32dfacc (kit/run_stage.sh with run/hooks.sh, a debugfs reset before each job; every row replayed before the freeze on the library mock built from the tool's source, none refused); frozen before the first job: FROZEN.sha256 ce1fd939..., PREDICTIONS.sha256 2693875c..., FROZEN.commits; scored by the frozen score/score.py (out/ATT/score-STAGE.txt), re-run at the fold on the kept files with byte-identical output, every kept file decompressing to the raw sha256 the laptop logged (out/fold/reproduce.sh, reproduce.out). Jobs: r8-geo's 24 seam rows (E934) with the flag their premise needs: `tri [--tri-full] --keep-going --wait-ms 20000 --width W --height H --max-width W --max-height H --aa4 --pixels --poke cmd:1=TE --poke cmd:10=0xeaa26e26 --poke cmd:13=0x8000000M --poke cmd:16=0xeaa26e26` (single triangles with --tri-v, --tri-z 0.5,0.5,0.5 and --poke blk:2^=0x8), each with the row knob dbg:render_rgn_arrays=1, which the runner wrote before the job, read back and restored to 0 after it; the knob makes the context's arrays sgx_render_rgn_arrays(1, aa4) = 1 and lets it take a TE_AA with bit 31 or 30 (fork 2a650d74 sgxfive_render.c sgxfive_render_init, ctx->aa_ms = aa4 || setting); the tail room is the 4x one. Rows expectdiff with `job: ok` (a hole is the tool's diff; a rejected job would have stopped the stage). Frozen: predictions/seam1.tsv, the O8 R8-1 table (render/closing-r8-geo gen/o8/q141_r8pred.tsv) byte for byte: per job the holes (tri-full) or stored pixels (a single triangle) as a count and the sha256 of the set under H-REGION and H-UNION (halves=False); the session's tests checked the control's set against E502's kept dump (isp/msaa-ident A-m1-te60-64x64-x, 64 background pixels) before the freeze"
tiers = ["HW"]
date = "2026-11-13"
data = ["render-closing-r9-geo:out/20261113-081038/seam1/", "render-closing-r8-geo:gen/o8/"]
terms = ["CR_TE_AA", "CR_ISP_MSAA", "region header"]
+++
**What ran.** E922 found the landed region model (a stored half tile takes only its
half-region's primitive list) to give every background pixel of E502 and E504 in sample, and froze
a held-out table for round 8's seam stage; E934 showed those rows never ran (the module refuses a
multisampled TE_AA from a context not made for 4x targets, and the rows lacked --aa4). Stage seam1
ran the same 24 rows with --aa4 and the debug knob render_rgn_arrays at 1, so that the 4x context
keeps one array of region headers, as E502, E504 and E727 had.

**Frozen verdict (as printed).** `H-REGION exact on every held-out set (22 of 22 rows decided)`;
`H-UNION exact on every held-out set is not supported: 8 held, 14 FAILED, 0 cannot tell of 22`.
Controls: ctl-a-m1-6-64x64 64 holes, the frozen set (PASS); ctl-tf-64x64-m2-2 no hole (PASS).

**Results [HW].** Every job printed `job: ok`; no pixel held a colour other than the triangle's
or the background.

| rows | sets | H-REGION | H-UNION |
|---|---|---|---|
| 14 tri-full, 64 x 96 to 128 x 96, modes 0, 1, 2 | holes 20 to 514 | 14 of 14 | 4 of 14 |
| 2 twins (mode 2, TE 0xa0000000) | no hole | 2 of 2 | 2 of 2 |
| 6 single triangles, 64 x 64 and 128 x 64 | 211 to 5564 stored | 6 of 6 | 2 of 6 |

**What it shows.** [HW] The background pixels under the full triangle, and the stored pixels of a
single triangle, of a multisampled render on one array of region headers are the region model's
with its two halves, at sizes, modes and slopes never used to set it: the seam holes are the
halves' lists, not a clip or a region left without a primitive. Q141 retires (decision R8-3 a,
S-1 a).

**What it does not show.** Sizes above 128 x 96 on one array (E828's 288 x 144 faulted there),
other primitives than the tool's triangle and its full quad, and why the hardware walks the halves
so (the model states it, it does not explain it). Four arrays: E954.
