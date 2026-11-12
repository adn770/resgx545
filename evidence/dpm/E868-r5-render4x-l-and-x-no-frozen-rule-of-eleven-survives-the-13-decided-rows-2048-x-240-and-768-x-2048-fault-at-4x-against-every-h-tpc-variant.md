+++
id = "E868"
claim = "R5-render4x stages l and x (8 jobs on their own maximum, 6 faults): the 4x full triangle on four arrays faulted with E845's word (BIF_INT_STAT 0x90100, BIF_FAULT 0x10000011) at 2048 x 240, 768 x 2048, 1280 x 768, 1024 x 1024, 1184 x 768 and 1024 x 800 and completed with 0 wrong pixels at 256 x 1536 (97 scene pages) and 1024 x 512 (129), health ok after every fault; 2048 x 240 and 768 x 2048 fault where all four frozen H-TPC variants predicted completion, and 1024 x 512 completes where TPC-d-state predicted a fault; the frozen verdict over the 13 decided rows of m, l and x: no frozen rule survives, Q292's cause is none of the eleven (stage l alone leaves none; stage x alone leaves TPC-rb-rgn, K-OR, K-P and K-AREA)"
unit = "dpm"
method = "R5-render4x stages l (5 rows, fault limit 5) and x (3 rows, fault limit 3; gated on stage m holding H-TPC, which it did, E867) of the question-closing pass, round 5 (decisions R5-3 a, R5-4 a, R5-6 a), dataset render-closing-r5-render4x, attempt out/20261112-100112 (l 10:05:58, x 10:07:07 Mac time; driver log run-r5x.log), laptop host cedar, 2026-11-12, the boot, kernel, module (srcversion 99CD90DA26E3AFF9C450517), firmware and tool (sha256 e6951558...) of E865; each row the 4x command of E867 on its own maximum (--max-width W --max-height H), --dump-render and --regs 0x0700-0x072c, render_rgn_arrays 0 and render_pb_pages 0x422 read back, a debugfs reset before each job, the fill and the strict health triangle after each fault; neither stage reached its limit (l took 4 fault-class events of 5, x 2 of 3), so every row ran and no stop needed a decision; the eleven rules' predictions computed from each row's argv (gen/rules.py) and frozen in predictions/l.tsv and x.tsv before the first job (FROZEN.sha256 e24977b3..., PREDICTIONS.sha256 6c700fa8...; the plan: closing5/render4x/exp-render4x-r5.md sections 1.4, 3.3 and 3.4); scored by the frozen score/score_r.py l and x in the run (score-l.txt, score-x.txt) and by `score_r.py verdict out/20261112-100112` (postrun/verdict.txt), all re-run on the kept files on 2026-11-12, score-l.txt and score-x.txt byte-identical; the search over extents of the layout's spans against its limits was made at the fold (postrun/posthoc_rules.py and .out, post hoc)"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r5-render4x:out/20261112-100112/l/", "render-closing-r5-render4x:out/20261112-100112/x/", "render-closing-r5-render4x:postrun/"]
terms = ["CR_TE_AA", "Parameter Buffer (PB)", "CR_BIF_FAULT", "CR_BIF_INT_STAT", "region header"]
+++
**What ran.** Stage l separated width, height and count: five sizes chosen so that each of the
eleven rules has its own column of outcomes (2048 x 240 and 256 x 1536 past one limit alone, 768 x
2048 larger than 1280 x 1024 in pixels, pages and height, 1280 x 768 and 1024 x 1024 one step past
1024 x 768 in one dimension). Stage x, gated on m, placed H-TPC's variant (d, rs or rb extents of
the doubled grid against the region headers or the state page) with three sizes near 1024 x 768.
Every row on its own maximum, as E845's.

**Frozen verdict (as printed).** l: `survivors none of the 11 rules over 5 decided rows`. x:
`survivors ['TPC-rb-rgn', 'K-OR', 'K-P', 'K-AREA'] of the 11 rules over 3 decided rows`. Over the
session (`score_r.py verdict`): `Q292 (m, l, x): no frozen rule survives the 13 decided rows: Q292's
cause is none of the eleven`.

**Results [HW].**

| job | size | outcome | H-TPC frozen | rules the row contradicts (as printed) |
|---|---|---|---|---|
| l1 | 2048 x 240 | fault | complete | the four TPC, K-H, K-AND, K-TPM, K-P, K-AREA |
| l2 | 256 x 1536 | complete, 97 pages | complete | K-H, K-OR |
| l3 | 768 x 2048 | fault | complete | the four TPC, K-W, K-AND |
| l4 | 1280 x 768 | fault | fault | K-H, K-AND |
| l5 | 1024 x 1024 | fault | fault | K-W, K-AND, K-TPM |
| x1 | 1024 x 512 | complete, 129 pages | split | TPC-d-state |
| x2 | 1184 x 768 | fault | split | TPC-d-rgn, K-H, K-AND |
| x3 | 1024 x 800 | fault | split | TPC-d-rgn, TPC-rs-rgn, K-W, K-AND, K-TPM |

Every fault: the kernel's `BIF fault 0x90100 at 0x10000011 ... recovering`, the tool's `job
faulted, context lost`, the fill and the health triangle after it passed; no `recovery failed`
line. The two completed rows had 0 wrong pixels and 0 region headers off the rule.

**Read after the run [post hoc].** None of 192 extents 4 k A B (A and B the doubled tile count,
the doubled macrotile span, the doubled side or the doubled larger span, across and down; k from a
quarter to two), against the maximum's tail room, state page or region offset, splits the 24
four-array cells below 4096 wide on record (11 earlier, 13 here) as measured
(`postrun/posthoc_rules.out`). On their own maximum 1024 x
768 completes and 1024 x 800, 1184 x 768, 1280 x 768 and 1024 x 1024 fault with the same tail room
(0x4000), and 256 x 1536 completes where 768 x 2048 faults with the same room (0x10000).

**What it shows.** [HW] On their own maximum the fault starts past 1024 x 768 in either dimension
alone (1184 x 768 and 1024 x 800 fault), and narrow targets fault too, wide or tall (2048 x 240,
768 x 2048), while 256 x 1536 and 1024 x 512 complete: no fixed width, height, count, page or area
limit fits, and none of H-TPC's four frozen extents does. With E867 the cause depends on the
context's maximum, and the size at which a context's room runs out is not any extent frozen here
[infer].

**What it does not show.** The rule of the onset, or what the 3D reads at the request base; whether
these sizes complete on a larger maximum (only E867's three targets ran so). One run each, one boot.
