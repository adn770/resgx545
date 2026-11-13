+++
id = "E1011"
claim = "Round 11 offline (Q139; no run): on r7-rp stage q139's 21 poked TA dumps (E907's run on module 41E2F5C7, 10 fit, 10 held-out and 1 replicate row, never read for the flag) and its poked control, frozen by hash before any of their dumps was opened, every dump holds exactly one header with flag bit 7, at H-EVEN's slot of the last target tile in block order (H-FLAGSLOT 21 of 21 and the control), and a target tile draws iff a stream header naming it lies at or before that slot (H-LAST 21 of 21, every one of the 128 or 600 tiles); H-EVEN's (here R7-BLK's) slots are exact on 24 of 24 dumps; the rival 'the flag is on the highest header slot written' fails 17 of 21 (flag 95 to 743, highest 141 to 1183: non-target headers written past the target), while 'the highest slot of a target tile's header' is never parted from H-FLAGSLOT [HW, held out offline on a second module build; infer: no kept dump has its last block-order target tile below another target tile's slot]"
unit = "ta"
method = "Offline, no run (round 11, decisions R11-2 a of closing11/DECISIONS-R11.md and closing11/plan/rank-round11.md, finding 1). Data: r7-rp's kept stage q139 (render-closing-r7-rp out/20261112-205431/q139/: 3 controls, 10 fit, 10 held-out, 1 replicate; all 24 jobs 'job: ok' with whole images and both dumps; rc 1 is the expectdiff line only), E907's run on module srcversion 41E2F5C756F96D20F7109A4 (fork 3f0b3e74), where E1007's q139c ran on B60AB0B4. Check closing11/plan/c1-q139flag/: the rules (H-LAST, H-FLAGSLOT, the rival H-HIGHEST in three forms: (a) the highest non-zero header slot of the dump, (b) the highest slot a predicted header takes, (c) the highest slot of a stream header naming a target tile) frozen in hflag_rule.json (sha256 291ef61dbabdfc46b13aea65c3b3989c3831af2a500b7dbc17ca48b9d9864d53, FREEZE.log 2026-11-13T11:03:57Z: read before were E907, E944, E959, E1007, r10-geo's scorer code and q139c dumps, r7-rp's cases.tsv and one job text, no r7-rp .tri.tadata.bin or .tri.param.bin), the scorer hflag_score.py (13d60577...) over byte copies of r10-geo's readers in lib/ (lib_dump.py, pbdump_dump.py, region_tiles_dump.py, q139_fit.py, q139model.py, q139even.py), output hflag_score.out, notes NOTE.md; pass strict, every decided row. This fold re-ran hflag_score.py with python -I on the kept directory and got a byte-identical output; sgx-pipe's `ta::macrotile_slots` gives every row's wrong-tile count and flag slot (the test r7_rp_s_poked_dumps_end_the_list_at_the_last_target_tile_in_block_order_e1011)"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["render-closing-r7-rp:out/20261112-205431/q139/", "cited-scratch:closing11/plan/c1-q139flag/", "cited-scratch:closing11/plan/rank-round11.md"]
terms = ["CR_TE_MTILE1", "CR_TE_MTILE2", "CR_TE_MACROTILE_STRIDE"]
+++
**What was done.** E959 read post hoc that each kept TA dump holds one region header with flag bit
7, on the last target tile in block order, and that a tile draws iff its header lies at or before
it; E1007 held both out on four new dumps of module B60AB0B4 at macrotile words 4 and 8 regions
wide. r7-rp's stage q139 (E907) had dumped 21 poked cases of E877's datasets and a poked control on
an earlier module build (41E2F5C7): E907 scored their slots and wrong tiles, never the flag. The
round 11 planner froze H-LAST, H-FLAGSLOT and the rival H-HIGHEST by hash before opening any of
those dumps, then scored all 24 rows; this fold re-ran the scorer byte for byte.

**Results [HW, held out offline]** (hflag_score.out):

| set | rows | one bit-7 header | H-LAST | H-FLAGSLOT | H-HIGHEST a / b / c |
| --- | --- | --- | --- | --- | --- |
| fit | 10 | 10 | 10 | 10 | 2 / 2 / 10 |
| held out | 10 | 10 | 10 | 10 | 2 / 2 / 10 |
| replicate | 1 | 1 | 1 | 1 | 0 / 0 / 1 |
| poked control m1-B1-5 | 1 | 1 | 1 | 1 | 1 / 1 / 1 |

The two unpoked baselines flag slot 127 (256 x 256) and 743 (640 x 480). The poked rows flag 43 to
127 at 256 x 256 and 343 to 743 at 640 x 480; H-LAST is right on every tile (128 or 600 a row).
H-EVEN's and R7-BLK's slots are exact on 24 of 24 rows: every first macrotile here is 0 or 1 mod 4
tiles wide (4, 5, 8, 12, 16, 20, 28), where the two agree; the stride-4 row is H-EVEN in block order
(E944), the order E907's row-order reading missed.

**Where the rivals part.** On 17 of 21 poked rows headers lie past the flag (dump highest 141 to
1183 against flags 95 to 743, e.g. m1-B1-28 flag 375 against 1183, m2-B1-20 743 against 1119):
the TA writes whole macrotiles past the target, and those non-target headers sit above the flag.
"The highest slot written" (forms a and b) fails there; it holds only on the four rows with nothing
written past the flag (strides 4, 8, 16 and 24) and on the control. Form (c), the highest slot of a
header naming a target tile, equals H-FLAGSLOT on all 24 rows: no kept dump has its last block-order
target tile below another target tile's slot [infer], so these data do not part the two.

**What it shows.** [HW, held out offline] Flag bit 7 ends the region list the 3D reads, on the
header of the last target tile the TA writes in block order, on a second module build and at 21
poked words and strides that E1007 did not run, among them MTILE1 words with bit 31 set and clear
and
four strides. E1007's own reading stands; its sentence that "the highest slot" is not parted holds
only for the form restricted to target tiles (an appended note there). sgx-pipe's
`ta::macrotile_slots` now admits r7-rp's ten MTILE1 and five more MTILE2 words and gives each row's
wrong-tile count and flag slot.

**What it does not show.** H-EVEN at fx 2 or 3 mod 4 (every kept job there faulted: not safe
class), the flag against the highest target tile's slot (a dump whose last block-order target tile
is not the highest target slot is needed, which may need such words), the stride's relation to the
RT data and why E509's words fault. Refuted by: a readable dump with zero or two flagged headers,
or a drawn tile whose only header lies past the flag.
