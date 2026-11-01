+++
id = "E545"
claim = "In a two-object stream, of the fields of one block's VDM_STATE1 flipped (bit 8, bits 11:9, bits 15:13, bit 17, bit 25 and the closed driver's two word forms; the grid set bits 11:9 and 7:0), each moves all that block's marks (viewport x, ISP word 1 in the object, own pixel shader) together or none: of 86 completed jobs 77 show all the control's marks, 8 the marked block's object absent (bits 11:9 = 0) and 1 neither (sg-v6-r0, the other block's object absent); bit 8, bit 25 and bits 15:13 = 2, 3, 4 change nothing (20 of 20), and the one word 0x0a022205 hung in 2 of 2 runs and completed in 1 of 1, so the marks of a block move together under every field flipped and a hang is not a function of the word"
unit = "vdm"
method = "script tables vdm-state-units (36 jobs), vdm-state-risky (78) and vdm-state-grid (19), on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion 7ED723C25D78D7FCB3C08C1 (installed equal to loaded), stock firmware (own_arm off), tool sgxfive-test-1126 (sha256 751f7223c8c731a08d75cfc3920a5d1050488ca3bdc426be45b7c431e600f82e, unchanged), no kernel or module change, no reboot, no clock-gate register written, a 64 x 64 triangle drawing exactly before and after every script: `probe --tri pixel --vertices 12 --obj2 6` (two objects of 6 vertices, each with its own state block, the first blue and the second green by `--obj2-pixel`), the marks of the block under test (viewport x offset 48 against 32 in `--obj2-blk 6`, ISP word 1 0x20f0 against 0x10f0, its own pixel shader) and one field of the block's VDM state word flipped by `--vdm 1^=` (block 1) or `--vdm 9^=` (block 2), two runs each, a control per variant; marks read from the pixels (counts and left edge of each colour) and from the dump (the words 0x20f0 and 0x10f0); H47-N+17 and H47-G1, G2 and N declared before the runs (plan.md sections 1, 6, 9)"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["vdm-state-units"]
terms = ["VDM_STATE1.BIT8", "VDM_STATE1.BITS11_9", "VDM_STATE1.BITS15_13", "VDM_STATE1.BIT25"]
+++

**Outcomes.** [HW] 133 jobs: 86 completed (vdm-state-units 34 of 36, vdm-state-risky 38 of 78,
vdm-state-grid 14 of 19) and 47 hung (2, 40 and 5). Of the 86, 77 show all three marks of the block
under test as the control's (green 1054 pixels from x = 24 and blue 638 from x = 8 with the second
block marked, the words 0x20f0 and 0x10f0 in the object; mirrored for the first block), 8 the marked
block's object absent (all its marks with it: bits 11:9 = 0, 4 jobs of vdm-state-units and 4 of the
grid) and 1 neither (sg-v6-r0, below).

**Fields that change nothing.** [HW] Bit 8 flipped (4 of 4), bits 15:13 at 2, 3, 4 (12 of 12) and
bit 25 (4 of 4) give the control's marks in 20 of 20 jobs; bits 11:9 at 3, 4 and 5 in 10 of 12 (the
other two hung, one run each, bits 11:9 = 4 in block 1 and 5 in block 2); bits 11:9 = 6 completes in
both blocks with the control's marks (4 of 4); in the grids the same value 6 hung at rows 1, 2, 3, 8
(vdm-state-risky) and at rows 6 and 16 and in one of three runs at rows 5 (vdm-state-grid): 7 of the
14 jobs at v = 6 hung.

**Fields that hang.** [HW] Bits 15:13 at 0, 5, 6, 7 hang in both blocks and both runs (16 of 16, as
E060 and E427); bit 17 flipped hangs (4 of 4); the closed driver's two state-word forms 0x0800e105
and 0x08002505 set hang (8 of 8); bits 11:9 = 1 hang in block 2 (2 of 2) and complete in block 1 (2
of 2); bits 11:9 = 7 hang in 2 of 4 jobs (one run of each block, E413's alternation). In
vdm-state-risky's grid (word 9 set to the base 0x0a022405 with bits 11:9 = v and bits 7:0 = rows,
rows 1, 2, 3, 8 and v = 0 to 7, 32 jobs): v = 0 removes the object (4 of 4), v = 1 and v = 6 hang (4
of 4 each), v = 2 to 5 and 7 complete with all marks (20 of 20), at every rows.

**The marks move together, and the word does not decide.** [HW] vdm-state-grid (19 jobs, declared
after that grid, plan.md section 9) tested two readings of the grid's v = 6 hang: H47-G1 (completes
only at rows = 5) was right in 4 of 10 v = 6 jobs and H47-G2 (4 <= rows <= 7) in 5 of 10: v = 6
completed at rows 4, 7, 9, 255 and 0 and hung at 6 and 16, and at one of three runs at 5. H47-N (v =
1 hangs at every rows) was right in 0 of 4: v = 1 completed at rows 4, 5, 6, 7. The word 0x0a022205
(v = 1, rows 5) hung in both runs of vdm-state-risky (block 2) and completed in vdm-state-grid's set
word of the same value (sg-v1-r5); the base word set explicitly (sg-v2-r5) completes with all marks,
as the unflipped control does, so the base is the base. So a job's completion is not a function of
its VDM state word [HW]; E413's alternation (a job hangs exactly when the previous one completed)
fits the four v = 7 jobs of the grid (complete, hang, complete, hang) and does not fit v = 1, 6 and
the single hangs of 4 and 5 [infer]: Q163. The one job that is neither all marks nor an absent
object is sg-v6-r0, with the attribute count (bits 7:0) at 0: the first object is absent and the
second shows its marks.

**Against the declared predictions.** H47-N+17 (marks all present, all absent, or a hang, by the
fields' E060 and E427 values): 6 of 6 controls and 54 of 72 held out; the 18 misses: two single
hangs at bits 11:9 = 4 and 5 (declared complete), bits 11:9 = 6 completing (4 jobs; declared a
hang), bit 17 and the two closed forms hanging (12 jobs; declared an absent object).

**What it does not show.** Fields never flipped (bits 0 to 7 outside the grid, 12, 16, 18 to 24 and
26 to 31); whether a block that sets MTE state or loads constants to every pixel separates the units
(not built; E440, Q020); what a hang's state does beyond the plain triangle after each script (drawn
exactly).
