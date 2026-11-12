+++
id = "E870"
claim = "Round 6 offline reading of E869's held dump and of the 26 four-array 4x outcomes on record (Q292; post hoc, one dump, nothing held out): H-TPM, the tail pointers of a 4x job are one dword per tile of the doubled grid (16 x 8 pixel tiles) at TA-data offset 4 x Z(x, y), Z the bit interleave with y on the even bits and x on the odd bits (Z-order), fits the dump exactly: the 1023 region headers that lost their stream offset (word 1) against the completed twin m1 are the 1023 headers whose word-1 dword is the entry of an in-target tile (0 extra, 0 missing; with x on the even bits 426 of 1708 predicted are lost); the check not used for the fit, 'a job faults iff the entries of its target's tiles pass the td.rgn of its context's maximum', gives 26 of 26 recorded outcomes (E824, E828, E845, E846, E867, E868 incl. its eight rows no frozen rule fitted, E869), but every one of them was known when the rule was written, so it is an offline check, not a held-out one; other interleaves and limits miss 3 to 8; left unexplained: 189 word-0 losses (all at header-grid entries outside the target), bit 27 set on 914 headers (never in a completed dump), and the 4096-wide right block of E828 and E846"
unit = "dpm"
method = "Offline, no run (round 6, area render4x, decision R6-1 a: the plan's offline results land before any session; plan closing6/render4x/exp-render4x-r6.md sections 1.1 to 1.4). The planner's scripts closing6/render4x/d_map.py, d_cmp.py, d_cmp2.py, morton.py, sep.py, residue.py and cells.py (standard library only, no firmware-derived input) read the published session render-closing-r5-render4x, attempt out/20261112-100112, read-only: row d's held TA data (d1-1280x1024-held.heldtadata.bin.gz, E869) against the completed twins m1 (1280 x 1024 on a 1280 x 1040 maximum) and m2 (on 2048 x 2048) of E867, header by header with the layout model of the rgn4 kernel (morton.py lay(): the maximum's 4 side^2 bytes of tail-pointer room, then the control, OTPM and state pages, then td.rgn); a dword is lost where d holds zero and m1 a non-zero value. morton.py part 1 states H-TPM against the lost dwords, part 2 scores 16 variants (y or x on the even bits, the tiles of the target or of the header grid, the limit at the room's end, OTPM, state page or td.rgn) over 26 cells: the 24 four-array 4x cells below 4096 wide on record and the two 4096-wide faults. In the fold (2026-11-12) cells.py was run without arguments to write cells.out (its part 1, the flag bytes of the six completed four-array dumps; the planner kept no output of it). Every script was re-run from its published copy (resgx545-data cited/closing6/render4x/) and printed output byte-identical to the kept .out files (d_map.py without -v). No frozen verdict and no prediction: the interleave and the limit were read from d's dump after E869 had reported it, and the 26 outcomes had all been recorded (E824 to E869) before the rule was written"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r5-render4x:out/20261112-100112/d/", "render-closing-r5-render4x:out/20261112-100112/m/", "render-closing-r5-render4x:out/20261112-100112/l/", "render-closing-r5-render4x:out/20261112-100112/x/", "cited-scratch:cited/closing6/render4x/"]
terms = ["CR_TE_AA", "CR_TE_TPC_ADDR", "Parameter Buffer (PB)", "CR_BIF_FAULT", "region header"]
+++
**What was done.** E869 held E845's 1280 x 1024 fault and found 1212 of 12288 region headers off
the doubled-grid rule, from `td.rgn` 0x7000 to 0xd804, most with word 0 intact and a zero stream
offset; what cleared them was not read from one dump. The round 6 planner compared that dump with
E867's completed twin m1 header by header (`closing6/render4x/d_cmp.py`, `d_cmp2.py`, `d_map.py`),
named the pattern H-TPM and checked it (`morton.py`), looked for sizes that separate its two
tile sets (`sep.py`), applied it to the 4096-wide faults (`residue.py`) and read the flag bytes of
the completed dumps (`cells.py`). All re-run from their published copies: byte-identical.

**Results [HW, read post hoc].** m1 and m2 differ in 0 headers, so a completed job's headers are
reproducible. Row d against m1 (`d_cmp2.out`, `morton.out` part 1):

| class | headers | what |
|---|---|---|
| same | 10160 | all three words equal m1's |
| A | 1023 | word 1 (the stream offset) zero, word 0's x, y and macrotile intact |
| C | 189 | word 0 zero, word 1 intact |
| B | 914 + 2 | word 0 bit 27 (0x08000000) set, clear in m1; 2 with flags 0x04, 0x10 off |

Three of the A headers also lost flag 0x04 or 0x10; header 0 lost its whole word 0, whose x, y and
macrotile are 0. B's word 1 equals m1's.

The A dwords fill aligned blocks of the TA data and nothing else: [0x7000, 0x8800), [0x9000,
0x9800), [0xc000, 0xc800), [0xd000, 0xd800), E869's runs within 4 bytes of a 2 KiB boundary.

- *The fit (part 1).* With Z putting y on the even bits, the headers whose word-1 dword is
  4 x Z(x, y) for a tile (x, y) of the target's doubled grid (80 x 128 tiles of 16 x 8 pixels)
  are 1023, and they are exactly the 1023 that lost word 1: both 1023, lost only 0, predicted
  only 0. With x on the even bits: 1708 predicted, 426 of them lost.
- *Word 0.* The 189 C dwords all lie at entries of the header grid outside the target (x 80 to
  95, the macrotile span past the target's edge): 189 of the 682 word-0 dwords at such entries.
  Of the 1025 word-0 dwords at in-target entries one is lost (header 0).
- *Bit 27.* The 914 headers are all headers whose own tile's entry lies inside the region headers;
  3072 in-target tiles have their entry there (4096 in the tail room, 3072 over the control, OTPM
  and state pages). No completed four-array dump of the session (l2, m0, m1, m2, m4, x1) has bit
  27 in any header, and each is zero below `td.rgn` (`cells.out`).
- *The check (part 2).* Rule: a four-array 4x job faults iff 4 x (Z(2tx - 1, 2ty - 1) + 1), the
  end of the target's entries (tx, ty the single-sampled 32 x 16 tile counts), passes the
  `td.rgn` of its context's maximum. 26 of 26:

| cells (record) | entries end | `td.rgn` | rule, measured |
|---|---|---|---|
| eight own sizes, 64 x 64 to 640 x 480 (E824, E828 j1r) | 0x80 to 0x35c0 | 0x4000 | complete |
| 1024 x 768 own (E824 h8) | 0x7000 | 0x7000 | complete |
| 1024 x 512 own (E868 x1) | 0x4000 | 0x4000 | complete |
| 2048 x 240, 1280 x 768 (E868 l1, l4) | 0xaff0, 0xc800 | 0x7000 | fault |
| 1024 x 1024, 1184 x 768, 1024 x 800 (E868 l5, x2, x3) | 0x8000, 0xc760, 0x7ac0 | 0x7000 | fault |
| 256 x 1536 own (E868 l2) | 0x11800 | 0x13000 | complete |
| 768 x 2048 own (E868 l3) | 0x17800 | 0x13000 | fault |
| 1280 x 1024 own (E845, E869) and on 2048 x 1024 (E867 m3) | 0xd800 | 0x7000 | fault |
| 2048 x 1536 own (E845) | 0x1c000 | 0x13000 | fault |
| 1024 x 768, 1280 x 1024 on larger maxima (E867 m0, m1, m2) | 0x7000, 0xd800 | 0x13000 | complete |
| 2048 x 1536 on 4096 x 4096 (E867 m4) | 0x1c000 | 0x43000 | complete |
| 4096 x 1152 own (E846 o7, overflows) | 0x3ac00 | 0x13000 | fault |
| 4096 x 4096 own (E828 j4, overflows) | 0x80000 | 0x43000 | fault |

  The other variants: y even with the limit at the room's end, OTPM or state page 8, 4 and 3
  misses; x even 8, 8, 5 and 3. The tiles of the target and of the header grid give the same
  outcomes in every variant, and no own-maximum size up to 2048 each way within the buffer gives
  them different ones (`sep.out`: 0 sizes); only the dump separates them (only in-target entries
  lost word 1).
- *The 4096-wide faults (`residue.out`).* H-TPM loses offsets from header 0 at 4096 x 4096
  (macrotiles 0, 1 and 2) and from header 1707 in macrotile 0 at 4096 x 1152 (macrotiles 0 to 5).

**What was seen before.** The planner wrote H-TPM after reading E869's dump against m1; the
interleave came from which dwords were lost and the limit, `td.rgn`, from where the losses start
(0x7000), so neither number was fitted on the 26 outcomes. But the 26 outcomes were all on record
(E824, E828, E845, E846, E867, E868, E869) and known to the planner, including the eight rows of
E868 that killed its eleven frozen rules and the 192 post hoc extents, and 16 variants were scored
on them, of which 2 fit (y even, `td.rgn`, the target's or the grid's tiles, indistinguishable on
outcomes). The fit is one held dump; the 26 of 26 is an offline check on seen data, not a
held-out test.

**What it shows [infer].** The TA keeps its tail pointers Z-ordered from `CR_TE_TPC_ADDR`, at 4x
indexed by the doubled grid, one dword per 16 x 8 pixel tile; where the target's entries pass
`td.rgn` the end of the TA's run zeroes them over the region headers and takes the stream offsets
that lie at in-target entries with them; a zero offset sends the 3D to the request base, the
fault's page (E869). The fault's onset is then where the far corner's entry passes `td.rgn`: a wide
target faults early because x 64 sets bit 13 of the index (0x8000 bytes), a tall one late because
y sits on the lower bit of each pair. Entries over the control, OTPM and state pages do not fault a
job that completes (1024 x 768 reaches 0x7000 with a room of 0x4000), so the limit is the headers,
not the room. The room a 4x context needs for a maximum of tx x ty tiles is 4 x (Z(2tx - 1, 2ty -
1) + 1) bytes, at most 4 x (2 side)^2: Q292's planned room (side doubled, four times the bytes) is
a bound at every size (at 4096 x 4096 the need is 0x80000, the bound 0x100000).

**What it does not show.** Whether a second held fault loses exactly the frozen set (one dump, no
replicate); whether H-TPM predicts outcomes it was not written over (the plan's stage A rows, not
run). Unexplained: the 189 word-0 losses at grid-only entries, while word 0 survives at in-target
entries (whether word 0 is written again later or the entry write keeps it is not decided by one
dump); bit 27 on 914 headers whose own entry lies in the headers [infer, weak: the TA read the entry
back from header memory]; the 4096-wide residue, since H-TPM loses offsets from macrotile 0 at both
4096-wide sizes and so does not give E828's right 1024 x 1024 block (1048576 pixels, first wrong at
(1024, 0)) or E846's 756800 right pixels, both scenes also overflowing; whether 1x tail pointers
are Z-ordered the same way (no 1x dump can show it, the entries are zero afterwards); whether
entries over the control, OTPM and state pages disturb a job that overflows (E866's overflows at
640 x 480 and 512 x 384 ended cleanly with such an overlap, not examined further).
