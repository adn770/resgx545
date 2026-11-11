+++
id = "E807"
claim = "R3-pixel stage q-v (88 jobs frozen, 74 run and 14 skipped by the frozen sweep stops: a vertex program on the tool's triangle that loops N times on a relative br, every vertex's stored depth word 0x3f200000 + N the loop proof, as E784): the five controls passed (no loop, N = 1 and N = 3 with STATUS2 0x400 after the job; N = 880 clear and 1760 set, E784's points), every run job's depth word proved the loop on every decoded vertex and STATUS2 read 0x400 after every reset; with E784's eight-instruction body on 3 vertices bit 7 was clear at N = 1045 and set at 1100 in both orders (ladders of 935 to 1705 in steps of 55, up and down, monotone), so the frozen bracket of width 55 is (1045, 1100]; with a 16-instruction body it was clear at 601 and set at 649, with a 4-instruction body set at 1760, the lowest point of its ladder (5 more run, 9 skipped), with 12 vertices clear at 554 and set at 698 and with 48 vertices (15 decoded) clear at 329 and set at 538; HV-INSTR (a fixed count of instructions a vertex) was REFUTED for the 16-instruction body and for 12 and 48 vertices and consistent for the 4-instruction body, HV-MA (a count of multiply-adds a vertex) REFUTED for all four, and HV-JOB (a count a job) REFUTED for 12 and 48 vertices; bit 7 showed 184 to 195 us after the burst began in every set job"
unit = "edm"
method = "R3-pixel stage q-v of the question-closing pass, round 3 (session L2, decision R3-P4; the sixth stage, started 16:28:35 Mac time, out-l2.log), dataset render-closing-r3-pixel, on the laptop (host cedar, direct cable), 2026-11-10, attempt out/20261110-160415, kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), the stock firmware (core 545 rev 0x1000d, DDK 1.7.17 build 862890 in every health line), tool ~/sgxfive-test-r1 (sha256 bf4f8be2d8a8fe50034559450928e05695dc96d396d4892f9b00ea6bc0d4f053) and ~/regtimeline (sha256 079f63590ce87ff2a1ac5499291e52340ff448d9c5e41942a9420264764de803), R1's builds, not rebuilt; every job after a debugfs reset, CR_EVENT_STATUS2 read from the debugfs registers after the reset and after the job, the job under regtimeline 0 0.3 0x0008,0x0118,0x012c (the burst B is the run of CR_CLKGATESTATUS 0x0008 not idle, t6 and t7 the time of the first sample with bit 6 or 7 of 0x0118 from the burst's start); freeze FROZEN.sha256 8a0fa9aa... and PREDICTIONS.sha256 d1cdc86b... before the first job; health ok after every stage; each job `probe --temps 16 --pixels --tri vtxuse --width 64 --height 64 --vtx-coords 2 --dump-render DIR --slot pixel=pix_green.bin PROGRAM` (--vertices 12 or 48 for those rows) with vloop-BODY-iN.bin from bins/ (vtx_loop.s, the body a parameter; imae write r4 to r8 in turn, DEVIATION 9); the frozen sweep stops skipped the rest of a sweep group after its first set bit 7; the depth words decoded from the kept dumps (pbdump first_object); scored by the frozen score/score_r3.py q-v (out/score-q-v.txt)"
tiers = ["HW"]
date = "2026-11-10"
data = ["render-closing-r3-pixel:out/20261110-160415/q-v/"]
terms = ["CR_EVENT_STATUS2", "CR_CLKGATESTATUS", "Universal Scalable Shader Engine (USSE)"]
+++
**What ran.** E784 placed the first set of bit 7 between 880 and 1760 iterations of an
eight-instruction vertex loop on the tool's three vertices. Q-v narrows that point in both orders
and runs two more bodies and two more vertex counts, which separate a count of instructions a
vertex (HV-INSTR), of multiply-adds a vertex (HV-MA) and a count a job (HV-JOB).

**Frozen verdict (as printed).** `controls pass; b8v bracket (last clear, first set] up (1045,
1100] down (1045, 1100] (orders agree, width 55); b16v HV-INSTR REFUTED; b16v HV-MA REFUTED; b4v
HV-INSTR consistent; b4v HV-MA REFUTED; v12 HV-INSTR REFUTED; v12 HV-MA REFUTED; v12 HV-JOB REFUTED;
v48 HV-INSTR REFUTED; v48 HV-MA REFUTED; v48 HV-JOB REFUTED`.

**Results [HW].**

| ladder | points run | (last clear, first set] | frozen HV-INSTR / HV-MA / HV-JOB |
|---|---|---|---|
| b8v up, 3 vertices | 935 to 1705, 15 | (1045, 1100] | the bracket's own row |
| b8v down, 3 vertices | 1705 to 935, 15 | (1045, 1100] | |
| b16v, 3 vertices | 280 to 950, 17 | (601, 649] | 522..550 MISS / 402..424 MISS / - |
| b4v, 3 vertices | 1760 to 3152, 6 (9 skipped) | (none, 1760] | 2090..2200 ok / 5225..5500 MISS / - |
| b8v, 12 vertices | 110 to 698, 9 (4 skipped) | (554, 698] | 1045..1100 MISS / 1045..1100 MISS / 261..275 MISS |
| b8v, 48 vertices (15 decoded) | 28 to 538, 7 (1 skipped) | (329, 538] | 1045..1100 MISS / 1045..1100 MISS / 65..69 MISS |

The bursts at the bracket of b8v: 266 and 300 us clear at 1045, 277 and 308 us set at 1100.

**What it shows and does not.** Bit 7, the vertex side's latch, sets between 1045 and 1100
iterations of the eight-instruction body on three vertices, and earlier with more vertices (before
538 at 48), so it is not a fixed count of a vertex's instructions or multiply-adds; HV-JOB, the
per-job count, misses at 12 and 48 vertices too. One run a point outside b8v; the sweep stops
leave b4v's first set point below 1760 unplaced.

**Correction 2026-11-10:** The results table copies the frozen scorer's "ok" for b4v under
HV-INSTR (2090..2200). The scorer calls it consistent because no point of that ladder was clear,
but the bit was already set at 1760, the lowest point run, below the window, so the window is
contradicted (post hoc reading of the frozen output, not the scorer's verdict): HV-INSTR places
none of the bodies, as the title says.

**Correction 2026-11-11:** The claim line above (and so its entry in `doc/evidence_log.md`, which
is built from it) still says HV-INSTR was "consistent for the 4-instruction body"; the correction
of 2026-11-10 was appended to this text only. That is wrong for the reason given there: b4v's
bracket is (none, 1760] (`score-q-v.txt` of the dataset, row b4v) and the window is 2090..2200,
so the bit was already set below the window's lower end. Right: HV-INSTR was REFUTED for the
16-instruction body and for 12 and 48 vertices, and its window was contradicted for the
4-instruction body (bit 7 already set at 1760). The frozen scorer printed "consistent" because its
test takes an open lower bound as 0 and allows a slack of one step on both sides; a strict overlap
of (last clear, first set] with the window, an open bound left open and no slack, gives the same
verdict as the scorer for the other 9 rows and differs for b4v only (post hoc reading of the kept
output, not the scorer's verdict). The claim line is the record's own front matter and is left as
written.
