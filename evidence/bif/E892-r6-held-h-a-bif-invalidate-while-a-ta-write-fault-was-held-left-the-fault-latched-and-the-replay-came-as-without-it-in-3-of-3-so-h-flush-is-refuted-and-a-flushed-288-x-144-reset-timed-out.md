+++
id = "E892"
claim = "R6 session r6-held part H stage q, the flush rows (Q003; the cells of E891 with the r6 kernel's debugfs bif_flush, CR_BIF_CTRL.INVAL_DC set and cleared with the other bits kept, written while E848's TA write fault 0x90004 was held, before the debugfs reset): the flush was taken in 3 of 3 (status 0, BIF_CTRL 0x00000000 before and after) and BIF_INT_STAT 0x90004 and BIF_FAULT stayed latched after it (H-LATCH, 3 of 3); after the reset the first triangle faulted at the replay's word as without the flush, 0x2000a061 at 640 x 480 (b0), 0x2000a062 after a fill (b1) and 0x20006061 at 288 x 144 (b2), each cell ending with a triangle that drew at the third; the boot after b2's flushed held reset timed out ('SGX recovery failed: -110', BIF_INT_STAT 0x000d0004 in the dump before it) as did the unflushed a2's; frozen verdict 'H-FLUSH REFUTED (0 held, 3 FAILED, 0 cannot tell of 3); H-PEND consistent (6 held of 6); H-BOOT REFUTED (2 held, 1 FAILED of 3); H-LATCH consistent (6 held of 6)', every control passing (the flush's two H-KEEP controls in 3 of 3, n0's refusal with nothing held); so a BIF invalidate while the fault is held does not drop the pending write, and does not prevent the -110"
unit = "bif"
method = "R6 session r6-held part H stage q (E891's session, attempt, boot, module, firmware, tool and cell sequence), the cells b0 (640 x 480, no follow-up), b1 (640 x 480, a fill) and b2 (288 x 144, no follow-up), run between the a cells; in each, after the registers at 2.8 s and 1 s later and with the hold still set, `echo 1 > bif_flush` (fork r6-kernel 3f0b3e74: refused with EBUSY unless a recovery is held; BIF_CTRL read, INVAL_DC, bit 3, set and cleared with the other bits as read; the kernel logs BIF_CTRL before and after, BIF_INT_STAT, BIF_FAULT and MEM_REQ_STAT), its status kept, the registers again, then the debugfs reset and the rest of the cell as in E891; s0's n0 wrote bif_flush with nothing held first (refused with EBUSY, BIF_CTRL unchanged: the control that the knob refuses outside a hold); the stage's stop after b2's health (rc 22, the -110 of a2 and b2 in a row) and the lead's decision not to resume are E891's; predictions frozen before the run: H-FLUSH [infer] (the invalidate drops the pending write: the first triangle draws) against H-PEND (the replay as without the flush, with H-LIST's list), H-LATCH (E826: the fault still latched right after the flush), H-BOOT [infer] (no -110 after a flushed held reset, from E848's -110 dumps read as a TA write in the boot); the H-KEEP controls (the flush's status 0 and BIF_CTRL the same before and after) gate the flush rows and a0's H-REPLAY control gates them too; scored by the frozen score/score_h.py on the kept files at the fold (postrun/score-q.txt), E891's"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r6-held:out/20261112-154536/q/", "render-closing-r6-held:postrun/"]
terms = [
    "CR_BIF_CTRL", "CR_BIF_CTRL.INVAL_DC", "CR_BIF_FAULT", "CR_BIF_INT_STAT",
    "Tile Accelerator (TA)",
]
+++
**What ran.** E848's -110 boots and replays read as a TA region-header write that the reset does not
drop. The planning asked whether the BIF's directory cache holds it: the r6 kernel's `bif_flush`
invalidates the cache (`CR_BIF_CTRL.INVAL_DC` set and cleared, the boot sequence's invalidate, the
other bits kept) while a fault is held. H-FLUSH: the invalidate drops the pending write and the
first triangle after the reset draws; H-PEND: the replay comes as without it. H-LATCH asks whether
the latched fault survives the flush (E826: only the reset cleared it), H-BOOT whether a flushed
reset avoids the -110.

**Frozen verdict (as printed, the stage's lines).** `SUMMARY: q: H-LIST consistent (...); H-WORD
REFUTED (...); H-FLUSH REFUTED (0 held, 3 FAILED, 0 cannot tell of 3); H-PEND consistent (6 held, 0
FAILED, 0 cannot tell of 6); H-BOOT REFUTED (2 held, 1 FAILED, 0 cannot tell of 3); H-LATCH
consistent (6 held, 0 FAILED, 0 cannot tell of 6); H-REPLAY consistent (...)`, `SUMMARY: Q003
flush (q): H-FLUSH: a BIF invalidate while the fault is held drops the pending write (no replay) is
not supported: 0 held, 3 FAILED, 0 cannot tell of 3`, `SUMMARY: q controls: 40 PASS, 0 FAIL, 0
NODATA`; s0: `SUMMARY: s0: controls all PASS (4)` (out/20261112-154536/score-s0.txt, postrun/).

**Results [HW].**

| cell | job's BIF_FAULT | flush | after it: INT_STAT, FAULT | steps after the reset | -110 |
|---|---|---|---|---|---|
| b0 | 0x2000a061 | 0, CTRL 0 -> 0 | 0x90004, 0x2000a061 | fault a061, fault a061, ok | none |
| b1 | 0x2000a061 | 0, CTRL 0 -> 0 | 0x90004, 0x2000a061 | fill, fault a062, fault a061, ok | none |
| b2 | 0x20006061 | 0, CTRL 0 -> 0 | 0x90004, 0x20006061 | fault 6061, fault 6061, ok | reset, t2 |

The kernel's `bif_flush:` lines read `MEM_REQ_STAT` 0 and the fault words as latched. Every reset
read `BIF_INT_STAT` 0x80000 and `BIF_FAULT` 0 in its first line, as in E767 and E826. The -110s of
the stage, each after the 500 ms wait for the EDM's boot and with the kernel's second reset then
booting: a2's held reset (dump `BIF_INT_STAT` 0x000d0004, `BIF_FAULT` 0x20006060) and its first
replay (0x20004060), b2's flushed held reset (0x1000b050) and its second replay (0x10002050); none
in the four 640 x 480 cells (4 held resets, 8 replays), 4 of 5 recoveries at 288 x 144.

**Read after the run [HW, post hoc].** The dumps' words are E848's (0x1000b050, 0x10002050,
0x20004060) and one new, 0x20006060: the held job's own page and `SB` with `CID` 0, inside the boot.
In b2 the kernel's line for the first replay names the held job's directory (PD 0x725d000, the job's
own), the second another.

**What it shows.** A BIF directory-cache invalidate while a TA write fault is held leaves the fault
latched (H-LATCH, 3 of 3, with E826's other writes) and does not drop the pending write: after the
reset the replay came as in the unflushed cells, with H-LIST's list (H-PEND 3 of 3 held out, H-FLUSH
refuted in 3 of 3). A flushed held reset can still time out at the boot (b2, H-BOOT refuted 1 of 3),
and the timeouts followed the 288 x 144 cells, flushed or not.

**What it does not show.** Where the write is kept (the invalidate reached the directory cache only;
`CR_BIF_CTRL.FLUSH` and the other caches were not touched), why the -110 follows the 288 x 144 job
and not the 640 x 480 one on this boot (E848's h2 at 640 x 480 had none either; its h1, h3, h4 at
288 x 144 had them), and whether the dump's fault is the replay itself. One run of each cell.
