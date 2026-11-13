+++
id = "E934"
claim = "R8-geo stage seam (Q141; 24 tri renders with E504's pokes, CR_TE_AA in cmd:1): every job whose CR_TE_AA had bit 31 or 30 set (0x60000000, 0xa0000000, 0xe0000000: 23 of 24) was rejected at submission (the tool's 'job: rejected (Invalid argument)', 0xdeadbeef in every pixel), so no held-out row ran and the control ctl-a-m1-6-64x64 read no hole set (FAILED); the one job with 0x20000000 ran and stored no hole as frozen; frozen verdicts 'controls FAILED: ctl-a-m1-6-64x64: FAILED' for H-REGION and H-UNION; the cause, read after the run: the rows did not pass the tool's --aa4, and the module (since fork a2788bd8, round 4) refuses a multisampled TE_AA from a render context not created for 4x targets (sgxfive_render_check) [infer from the source]; Q141 is not answered"
unit = "isp"
method = "R8-geo stage seam of the question-closing pass, round 8 (decisions R8-2 a and R8-3 a; plan closing8/rank/rank-round8.md R8-1), on the laptop (host cedar), 2026-11-13, attempt out/20261113-015842 (dataset render-closing-r8-geo; the first attempt, out/20261113-015816, ran nothing: the lead passed SGX_TARGET_SSH_OPTS where the kit reads SGX_TARGET_HOST_KEY_ALIAS, so staging failed, and the lead's run log inside the session directory was a new file the freeze refused), kernel 7.3.0-resgx545, module srcversion 37EC97AB0CB37213C42FCCC (fork 664fd0d0, installed = loaded, knobs at their defaults at the stage start), tool ~/sgxfive-test-rgn4 (t4, sha256 e6951558..., resgx545 4623753), the session kit of resgx545 d97c4739 (kit/run_stage.sh with run/hooks.sh, a debugfs reset before each job, every job class ok, no stop, no lead decision); frozen before the first job: FROZEN.sha256 2687abf3..., PREDICTIONS.sha256, FROZEN.commits; scored by the frozen score/score.py (out/ATT/score-STAGE.txt), re-run at the fold on the kept files with byte-identical output, every kept file decompressing to the raw sha256 the laptop logged (out/fold/reproduce.sh, reproduce.out). Jobs: `tri [--tri-full] --keep-going --wait-ms 20000 --width W --height H --max-width W --max-height H --pixels --poke cmd:1=TE --poke cmd:10=0xeaa26e26 --poke cmd:13=0x8000000M --poke cmd:16=0xeaa26e26` (single triangles with --tri-v, --tri-z 0.5,0.5,0.5, --poke blk:2^=0x8: E727's form), the rows of E504 and E727, which ran on module B21FDA82 with tool 1138b; rows marked expectdiff (a hole is the tool's diff). Frozen: the O8 R8-1 table (render/closing-r8-geo gen/o8/q141_r8pred.tsv, predictions/seam.tsv byte for byte): holes or stored sets under the landed region model and its halves-off rival. The runner took the rejected jobs as readings: each printed a diff line with rc 1, which expectdiff accepts. Read after the run (post hoc): each job's job line and error (out/fold/post_read.py) and, read only, the linux fork at 664fd0d0 (drivers/gpu/drm/gma500/sgxfive/sgxfive_cmd.c sgxfive_render_check, sgx_render.h sgx_render_te_aa_ms, sgxfive_render.c ctx->aa_ms), and the tool's --aa4 option (sgxfive-test.c, 4623753)"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["render-closing-r8-geo:out/20261113-015842/seam/", "render-closing-r8-geo:out/fold/"]
terms = ["CR_TE_AA", "CR_ISP_MSAA"]
+++
**What ran.** E922 found the landed region model to give every background pixel of E502 and E504
in sample; R8-1 was to hold it out: 14 tri-full renders at sizes never run, 2 zero-hole twins and 3
single triangles of other slopes in modes 1 and 2, with two controls (64 x 64 mode 1 TE 0x60000000,
64 holes frozen; mode 2 TE 0x20000000, no hole). Stage seam ran all 24 jobs; none faulted.

**Frozen verdict (as printed).** `Q141 seam holes, H-REGION: controls FAILED:
ctl-a-m1-6-64x64: FAILED`, H-UNION the same. Every held-out row printed FAILED for both rivals
(4096 to 12288 'other' pixels): none of them ran.

**Results [HW].** 23 jobs, every one with CR_TE_AA bit 31 or 30 set, printed `job: rejected
(Invalid argument)` and `sgxfive-test: render: Invalid argument`, the target untouched
(0xdeadbeef); ctl-tf-64x64-m2-2 (0x20000000) printed `job: ok` and stored the triangle in all
4096 pixels, as frozen. No kernel message, fault or reset.

**Read after the run.** The module's render check refuses a TE_AA with bit 31 or 30 (a
multisampled render) unless the context was created for 4x targets or its region-header arrays are
forced by debugfs (`sgxfive_render_check`, since fork a2788bd8, which gave 4x contexts four
region-header arrays, after E504 and E727 ran on B21FDA82). The tool creates such a context with
--aa4; the rows, copied from E504's and E727's command lines, did not carry it. The mock answered
from the argv alone and modelled no kernel check; the dry runs against the library's mock printed
the same rejection before the freeze, unread. [infer] A rerun with --aa4 is the row Q141 still
needs.

**What it shows.** [HW] On module 37EC97AB a tri render whose CR_TE_AA sets bit 31 or 30 without
--aa4 is refused at submission, every one of the 23 run. Nothing about the seam holes.

**What it does not show.** Q141's held-out row, or whether --aa4's context (four region-header
arrays) changes the stored image E502, E504 and E727 saw with one.
