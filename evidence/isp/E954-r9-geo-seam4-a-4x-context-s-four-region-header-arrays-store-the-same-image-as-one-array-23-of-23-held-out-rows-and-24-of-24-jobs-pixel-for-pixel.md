+++
id = "E954"
claim = "R9-geo stage seam4 (the seam holes, E953's question; the same 24 renders with --aa4 alone, the 4x context's automatic four region-header arrays, never run before in modes 0 and 1, and E828's j1r as a control): four arrays store the region model's image as one array does: H-SAME4 (the O8 table's H-REGION set) exact on 23 of 23 held-out rows (E502's control configuration held out here), H-FULL4 [infer: no hole] 2 of 17 (the two zero-hole twins), H-UNION 8 of 23; both controls passed (j1r hash 0x4a61860dcb4ab325 with no background pixel, as E828; TE 0x20000000 no hole); frozen verdicts 'H-SAME4 exact on every held-out set (23 of 23 rows decided)', H-FULL4 '2 held, 15 FAILED', H-UNION '8 held, 15 FAILED'; post hoc, all 24 shared jobs stored the same image pixel for pixel with four arrays as with one (stage seam1, E953)"
unit = "isp"
method = "R9-geo stage seam4 of the question-closing pass, round 9 (S9-geo, decisions R9-3 a and S-1 a of the seeds plan closing9/seeds/exp-seeds-r9.md section 1), on the laptop (host cedar), 2026-11-13, attempt out/20261113-081038 (dataset render-closing-r9-geo; the only attempt, 77 jobs in four stages, every job class ok, no stop, no lead decision), kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (fork 2a650d74, the one-shot test boot; installed = loaded, knobs at their defaults at every stage start), tool ~/sgxfive-test-rgn4 (t4, sha256 e6951558..., bound by FROZEN.commits' built line to resgx545 4623753 userspace/libsgxfive/tools/sgxfive-test.c, sha256 703cbcea...), the session kit of resgx545 f32dfacc (kit/run_stage.sh with run/hooks.sh, a debugfs reset before each job; every row replayed before the freeze on the library mock built from the tool's source, none refused); frozen before the first job: FROZEN.sha256 ce1fd939..., PREDICTIONS.sha256 2693875c..., FROZEN.commits; scored by the frozen score/score.py (out/ATT/score-STAGE.txt), re-run at the fold on the kept files with byte-identical output, every kept file decompressing to the raw sha256 the laptop logged (out/fold/reproduce.sh, reproduce.out). Jobs: stage seam1's 24 command lines (E953) with --aa4 and no knob (render_rgn_arrays at its default 0, so the context gets four arrays, sgx_render_rgn_arrays(0, true) = 4), named f4-NAME, and E828's j1r (`tri --tri-full --keep-going --wait-ms 20000 --width 288 --height 144 --max-width 288 --max-height 144 --aa4 --pixels` with E824's pokes, cmd:1 0xe0000000, cmd:13 0x80000002), expectdiff with `job: ok`. Frozen (predictions/seam4.tsv, from the O8 R8-1 table): per job H-SAME4 (the table's H-REGION set), H-UNION (its halves-off set) and, on the 17 tri-full rows, H-FULL4 (no hole); E502's 64 x 64 mode 1 TE 0x60000000 row is held out here because H-FULL4 parts it; controls j1r (its hash and 0 background, E828) and 64 x 64 mode 2 TE 0x20000000 (no hole under every rival). Post hoc at the fold: out/fold/post_read.py compares each job's pixels with stage seam1's"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["render-closing-r9-geo:out/20261113-081038/seam4/", "render-closing-r9-geo:out/fold/"]
terms = ["CR_TE_AA", "CR_ISP_MSAA", "region header"]
+++
**What ran.** Since fork a2788bd8 a context made for 4x targets gets four arrays of region
headers (E828, E824); E502, E504 and E727 ran on one. Whether the four arrays change the seam holes
in modes 0 and 1 had never been run (seeds plan finding 2: 51 kept four-array jobs, all mode 2 at
TE 0xe0000000, where every rival predicts no hole). Stage seam4 ran stage seam1's rows with --aa4
alone, with E828's 288 x 144 four-array render as a control.

**Frozen verdict (as printed).** `H-SAME4 exact on every held-out set (23 of 23 rows decided)`;
`H-FULL4 exact on every held-out set is not supported: 2 held, 15 FAILED, 0 cannot tell of 17`;
`H-UNION exact on every held-out set is not supported: 8 held, 15 FAILED, 0 cannot tell of 23`.
Controls: f4-ctl-j1r-288x144 hash 0x4a61860dcb4ab325, no pixel but the triangle's (PASS);
f4-ctl-tf-64x64-m2-2 no hole (PASS).

**Results [HW].** Every job printed `job: ok`. The holes and stored sets are those of E953 row for
row (64 holes at E502's 64 x 64 configuration, 20 to 514 at the new sizes); post hoc, the 24 jobs
the stages share stored the same image pixel for pixel (out/fold/reproduce.out).

**What it shows.** [HW] The number of region-header arrays (one or four) does not change what a
multisampled render stores in modes 0 to 2 at these sizes: the region model holds for the 4x
context's own layout too, and the 'complete list per half' reading of four arrays (H-FULL4) is
refuted. [infer] The four arrays matter for the TA's writes (E824's fault sizes), not for which
list a half tile reads.

**What it does not show.** Sizes above 128 x 96 with four arrays in modes 0 and 1, and the role of
each of the four arrays.
