+++
id = "E846"
claim = "R4-render4x stage o (7 of 8 jobs run, o6 skipped by its condition): the frozen verdict is cannot tell for Q292 and for H-SPM4 because the control o2 (1x 1024 x 768 at render_pb_pages 0x82, frozen to overflow) completed with 0 wrong pixels; read after the run, its row ran the tool's default triangle, whose dumps hold 19 scene pages (o1, o2 and E845's s0), while its frozen need of 97 was the model of the full-screen triangle, so the control's prediction was made for another scene; post hoc and not rescored, the 4x full triangle on four arrays completed at 1024 x 768 with P 0xe3 (193 pages) and ended in -ENOSPC without a fault one page lower (0xe2), as did 288 x 144 at P 0x23 (need 12), while 4096 x 1152 at 0x422 (need 1153) faulted with E828 j4's word (BIF_FAULT 0x10000011) and the 1x full triangle at 4096 x 4096 ended in -ENOSPC: an overflowing 4x scene ends as a 1x one does, and the 4x fault is not the overflow"
unit = "dpm"
method = "R4-render4x (R4-G) stage o (8 rows, fault limit 5) of the question-closing pass, round 4, dataset render-closing-r4-render4x, second attempt out/20261111-211649 (stage o 21:16:50 Mac time; driver log run2.log), the lead's decision after stage p's stop in the first attempt (E845): `run/k.sh --from o`, budgets unchanged, s0's controls read from the first attempt by the gate; laptop host cedar, 2026-11-11, the boot, kernel, module (srcversion 99CD90DA26E3AFF9C450517), firmware and tool (sha256 e6951558...) of E845; render_pb_pages written per row after the row's reset and read back (0x83, 0x82, 0xe3, 0xe2, 0x23, then 0x422), 0x422 restored after each job; o1 and o2 `tri --width 1024 --height 768 -n 1 --keep-going --keep-overflow --wait-ms 20000` (E827's ctl-u-1024-n1), o3, o4, o5 and o7 the 4x full triangle of E845 (o5 held: hold_recovery Y, the registers read at 2.8 s and 1 s later, the kernel's reset, `--pixels`, the held dumps through debugfs), o8 `tri --tri-full` at 4096 x 4096 with the default CR_TE_AA, each with --dump-render and --regs 0x0700-0x072c except o5; o6 (o5 plus a tadata_fill of page 7) only if o5 faulted: skipped; the outcome, the fault word and the page rule frozen in predictions/o.tsv before the first job (FROZEN.sha256 80a16d2b..., PREDICTIONS.sha256 7ceff7ba...); scored by the frozen score/score_r.py o (out/20261111-211649/score-o.txt; its s0 lines read NODATA because s0 is in the first attempt, the verdict over both attempts reads them PASS), re-run on the kept files on 2026-11-11 with byte-identical output; why o2 failed, the dumps' non-zero pages and the outcomes of the gated rows were read after the run from the kept files (post hoc), not rescored"
tiers = ["HW", "infer"]
date = "2026-11-11"
data = ["render-closing-r4-render4x:out/20261111-211649/o/", "render-closing-r4-render4x:postrun/"]
terms = ["CR_TE_AA", "Parameter Buffer (PB)", "CR_BIF_FAULT", "CR_BIF_INT_STAT", "region header"]
+++
**What ran.** Stage o tested H-SPM4, the planning's reading of Q292: a 4x scene that overflows
the parameter buffer faults on the 3D side (E828 j4's word) where the same overflow at 1x ends in
-ENOSPC. The page rule (a scene completes iff P - 0x22 >= its need; E625, E735, E773) was the
control, two boundary pairs one page apart: o1 and o2 at 1x 1024 x 768 (frozen need 97), o3 and
o4 at 4x 1024 x 768 (U4 193). o4, o5 (288 x 144 at P 0x23) and o7 (4096 x 1152, U4 1153) were
predicted to fault, o8 (the 1x full triangle at 4096 x 4096, j4's control) to end in -ENOSPC.

**Frozen verdict (as printed).** `Q292 (o): cannot tell: controls: o2-1x-1024x768-p82: FAILED`;
`H-SPM4 (o): controls FAILED: o2-1x-1024x768-p82: FAILED` (`score_r.py verdict` over both
attempts; the stage's own score-o.txt lists s0's three controls as NODATA as well, since s0 ran in
the first attempt).

**Results [HW].**

| job | size, mode | P | frozen | outcome | pixels |
|---|---|---|---|---|---|
| o1 | 1024 x 768, 1x, default | 0x83 | complete (ctl) | complete, PASS | 0 wrong, E827's hash |
| o2 | 1024 x 768, 1x, default | 0x82 | overflow (ctl) | complete, FAIL | 0 wrong, E827's hash |
| o3 | 1024 x 768, 4x | 0xe3 | complete (ctl) | complete, PASS | 0 wrong, E824 h8's hash |
| o4 | 1024 x 768, 4x | 0xe2 | fault | -ENOSPC, no fault | 4096 triangle, 780545 wrong |
| o5 | 288 x 144, 4x, held | 0x23 | fault | -ENOSPC, no fault | 0 wrong, the completed hash |
| o6 | o5 + tadata_fill page 7 | 0x23 | either/or | skipped (o5 did not fault) | - |
| o7 | 4096 x 1152, 4x | 0x422 | fault | fault 0x90100 at 0x10000011 | 756800 of 4718592 right |
| o8 | 4096 x 4096, 1x | 0x422 | -ENOSPC | -ENOSPC, no fault | 16384 triangle, 2832421 wrong |

The -ENOSPC rows are the tool's `scene overflowed the parameter buffer, context kept (No space
left on device)` with no BIF line in the kernel log; o5's snapshots read BIF_INT_STAT 0x80000 at
2.8 s and 3.8 s, and its held dumps are the 62- and 63-byte error of a debugfs read with no
context (`No such device`). o7's first wrong pixel is (1024, 0), as in E828's j4, and the health
triangle after it passed and the stage ran to its end.

**Read after the run [HW, post hoc; not rescored].** Why o2 failed: its row is E827's
ctl-u-1024-n1, the tool's default triangle (207456 triangle pixels of 786432), not the
`--tri-full` triangle; the frozen need 97 is the model of the full triangle (predictions/o.tsv:
"need U1 97 [model]"). The default triangle's dumps in o1, o2 and E845's s0 hold the scene pages 0
to 0x12, 19 pages, so at P 0x82 (96 usable) it fits by 77 pages and completed as o1 did. The
control was frozen for another scene than its row runs; it says nothing against the page rule,
and o1's PASS does not test the rule at a boundary either. The dumps of o3 and o4 both hold the
scene pages 0 to 0xc0 (193, U4); o8's hold 0 to 0x400 (1025 pages, the buffer filled).

So, read without the gate: the 4x boundary pair o3 and o4 split exactly as the page rule says at
U4 193 (complete at 193 usable pages, overflow at 192), and the overflow ended in -ENOSPC with no
fault, at 1024 x 768 (o4) and at 288 x 144 (o5): the refuting reading of H-SPM4 frozen in the
table ("-ENOSPC like 1x"). o7 overflows and is larger than 1280 x 1024 at once, so it cannot tell
the two apart; o8 confirms that the full triangle at j4's size ends in -ENOSPC at 1x.

**What it shows.** [HW, post hoc] At 4x on four arrays the page rule holds at its boundary (one
pair) and an overflowing scene ends in -ENOSPC without a fault, as at 1x; the fault of E828's j4,
of E845's two sizes and of o7 is not the overflow. With E845 that leaves Q292 as a size fault
whose onset lies past 1024 x 768 and at or before 1280 x 1024. [infer] The PB fit U4 holds at 193
pages in a third and fourth dump.

**What it does not show.** The frozen verdict decides nothing: the control's prediction was wrong
for its own row, so every row is gated. Why an overflow at 288 x 144 with one usable page gives
the completed image while at 1024 x 768 it gives 4096 triangle pixels, under the fork's rule that
an overflowed image is undefined; o6's question (whether the 3D reads ext-Z region headers) did
not run. One run each.

**Correction 2026-11-12:** (after R5-render4x, E866) The sentence "the frozen need 97 is the model
of the full triangle" above is wrong for 1x: 97 was the model, and the model was wrong. The 1x full
triangle at 1024 x 768 needs 49 scene pages: it completed at P 0x53 with 49 pages in its dump and
ended in -ENOSPC at 0x52 (E866, exploratory, at the need a per-macrotile model gave before the run).
So had o2 run the full triangle at P 0x82 (96 usable) it would have completed as well; the record's
reading that the control said nothing against the page rule stands. The post hoc reading of this
record (a 4x overflow ends in -ENOSPC without a fault) now holds under a frozen verdict, held out at
640 x 480 and 512 x 384 (E866, H-ENOSPC4, 6 of 6 rows decided).
