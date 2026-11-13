+++
id = "E1020"
claim = "Round 12 offline (Q107, Q038; no run): predicting each G = 1 depth dump of the 11.38 batch's overflowed 1024x768 jobs (dpm/partial-model-batch depth-safe.c1 and .c26: z = 0.5 at 0x23, 0x28 and 0x30 pages and the ramp at 0x28 and 0x30, runs 1 and 2, 10 dumps) from the same cell's G = 33 dump by E996's overlay (each slot holds, whole, the tile visited last in region header order), frozen by hash before any G = 1 dump's bytes were read, holds 0 of 10 (32201 or 51968 of 61440 decidable dwords, 60 or 101 of 120 slots), and so do the rivals (first visited, last in raster order, the zero region fixed in slot space, 0 of 10 each); the sign is not the cause (sign-masked counts equal). The same overlay predicts E489's 1024x768 ramps in x and y at G 0, 1 and 2 from their G = 33 dumps, jobs without a partial render, 6 of 6, every dword (held out for E996, whose targets were 64x32 to 256x64). Read after the score: every G = 1 dump begins with 15104 zero dwords (slots 0 to 28 and 256 dwords of slot 29, the same in every cell and run) and its later slots mostly repeat one tile's content rather than each slot's owner [HW, held out offline for the overlay; the zero prefix and the repeated tile post hoc; infer: the final store after partial renders is not the plain store overlaid]"
unit = "zls"
method = "Offline, no run (round 12, decision R12-4 a of closing12/DECISIONS-R12.md and closing12/plan/rank-round12.md, finding 4). Data: the 20 depth dumps dp-<scene>-g{1,33}-<P>-r{1,2}.depth.1.bin.gz of dpm-partial-model-batch dumps/depth-safe.c1 and dumps/depth-safe.c26 (E628's and E629's jobs; the ramp at 0x30 has its G = 33 run 1 in c1 and run 2 in c26) and, for the control, zls-store-layout-dumps dumps/fit-1024x768-G{0,1,2,33}-ramp{x,y}.bin.gz (E489). Check closing12/plan/c3-q107/: q107_rule.py (sha256 8863d62163db7c9fc0f5907cfe19629be96a1b3b38d2de8b7721a49e9d19ca0d, FREEZE.log 2026-11-13T12:19:45Z: read before were the cases.tsv of the two directories, one G = 33 dump's length and first 16 bytes and its G = 1 twin's length, and E996, E628, E629 and E489) freezes RULE (G = 1 slot 2 ty + tx holds the G = 33 dump's tile at slot 34 ty + tx of the tile last in r10-x gen/z.py's header rank, four macrotiles a side of 8 x 12 regions, zero and half-zero tiles included, the sign as stored), R-FIRST, R-RASTER and R-ZEROFIX; pass: every scored dword equal. Tiles in G = 33 slots past the 1568 a dump holds (tile rows 46 and 47) are 'cannot tell', their slots left out (scorer side, no rule change). Scorer q107_score.py (q107_score.out); after the score q107_posthoc.py (q107_posthoc.out) located the zero prefix and the repeated tiles; notes NOTE.md. G = 33 runs 1 and 2 of a cell agree at 766976 of 802816 dwords, so the G = 33 source is not run-exact; RULE's misses (up to 29239 dwords) exceed that in four cells and the G = 1 runs score alike. This fold re-ran q107_score.py and q107_posthoc.py with python -I on resgx545-data ffd076572 and got byte-identical outputs; sgx-pipe's `zls::final_store` refuses the store after a partial render under Q107 (the_final_store_of_an_overflowed_job_is_refused_e628_e629_e1020)"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["dpm-partial-model-batch", "zls-store-layout-dumps", "cited-scratch:closing12/plan/c3-q107/", "cited-scratch:closing12/plan/rank-round12.md"]
terms = ["CR_ISP_ZLSCTL"]
+++
**What was done.** E996 held on hardware that a ZLS slot shared by overlapping tiles keeps the tile
the 3D visits last in region header order, at five pitches of targets of two macrotiles a side.
E628 and E629 read the stores of jobs that overflow at 1024x768 (a zero region in the first
macrotile row, the sign set by the raise) and left the tile order of the store open (Q107). The
11.38 batch kept the same overflowed cells at G = 1 (overlapping) and G = 33 (no overlap); no record
had compared them. The round 12 planner froze E996's rule and three rivals by hash, scored all ten
G = 1 dumps, and as a control scored E489's six 1024x768 ramps of jobs without a partial render.

**Results [HW, held out offline]** (q107_score.out), dwords equal of the decidable ones per G = 1
dump:

| cell | RULE | slots | verdict |
| --- | --- | --- | --- |
| z05 0x23, runs 1 and 2 | 32201 / 61440 | 60 / 120 | failed |
| z05 0x28, runs 1 and 2 | 32201 / 61440 | 60 / 120 | failed |
| z05 0x30, runs 1 and 2 | 51968 / 61440 | 101 / 120 | failed |
| ramp 0x28, runs 1 and 2 | 51968 / 61440 | 101 / 120 | failed |
| ramp 0x30, runs 1 and 2 | 51968 / 61440 | 101 / 120 | failed |

R-FIRST, R-RASTER and R-ZEROFIX hold 0 of 10 as well (R-ZEROFIX 16341 to 17408 of 64256 dwords).
Masking the sign bit changes no count. The control: RULE holds E489's ramps x and y at G 0, 1 and
2 (40448, 64512 and 88576 dwords each, every one), 6 of 6; R-FIRST and R-RASTER 0 of 6; R-ZEROFIX 6
of 6 (a null rival there, the control has no zero).

**Read after the score (post hoc)** (q107_posthoc.out): every G = 1 dump starts with 15104 zero
dwords, slots 0 to 28 and the first 256 dwords of slot 29, in every cell and run; the slots after
that hold content equal to one common G = 33 tile, (3, 46) or (10, 39), not each slot's owner (2 of
120 slots hold the owner's content, in z05 at 0x30).

**What it shows.** [HW, held out offline] E996's overlay holds at 1024x768 at three overlapping
pitches for jobs without a partial render, a target of four macrotiles a side that E996 did not run
(an appended note there). It does not give the final store of a job that overflows: there the G = 1
store is not the G = 33 store overlaid in any of the four orders tried. [infer] The partial renders
and the final render's load and store make another sequence of writes; the zero prefix is a prefix
of the window, not E628's zero tiles moved by the overlay. sgx-pipe's `zls::final_store` refuses
the store after a partial render (Q107).

**What it does not show.** Where the zero prefix and the repeated tile come from (a job over a load
buffer of ascending indices with a marked G = 33 twin would name the tiles), the order of the tile
stores in such jobs, and pitches, sizes and formats other than these. Refuted by: an overflowed G =
1 dump that equals the overlay of its G = 33 twin. Q107's tile-order clause stays open for jobs
with partial renders; E628's "tile order of the store not shown" stands.
