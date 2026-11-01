+++
id = "E705"
claim = "The tool's -n 4 runs four renders one after the other, one triangle each, so the frozen 'four stacked' and 'four apart' cases are not four-triangle scenes, and their two predictions (disj4 against stack4: HG, HT) are void, not right or wrong; the page need of one triangle at 1024x768 depends on its position: moved by 0, 192, 384 and 576 pixels it reaches status 0x13, 0x14, 0x11 and 0xc (19, 20, 17 and 12 pages) in 0x422 pages, four renders of the unmoved one 0x13 four times; E625's overflow rule (overflow iff P - 0x22 is below the need) gives the outcome of all 8 distinct conditions (the 4 positions at each of P = 0x28 and 0x30; the 22 renders include 14 repeats of an input already rendered, all with the same outcome) (post hoc), the raise of the threshold (dwords 37 and 38) being in all 4 conditions at 0x28 and in none of the 4 at 0x30"
unit = "dpm"
method = "table dpm-stack (10 jobs, safe: tri --width 1024 --height 768 -n 1 or 4 --keep-overflow --dump-each, the triangles of the later renders moved by --move 2:192,0 --move 3:384,0 --move 4:576,0, P 0x28, 0x30 and 0x422, regtimeline over 0x0624-0x0628, 0x0654-0x0660 and 0x0720-0x0724), on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed and loaded, equal in the ten scripts), stock firmware (sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a), tool ~/sgxfive-test-1140 (sha256 bd55ffe69cf310f574f019ac3cbe3cccf0464d2e2addf0e47f940570440ffa76), debugfs reset, kpoke, hold_recovery and render_pb_pages only (no kreg, no kregnow, no clock-gate register written), run-all-1141ta.sh: 157 jobs in ten tables run in one pass (ten scripts, rc 0 each; the exit=1 at the end of the log is the runner's last test, not a failure), one process per job, a marker per job in the kernel log (157 of 157, in case order), every raw output and dump gzipped with its raw sha256 (741 files, every one equal to the sha256 printed at the run); predictions-declared.tsv (sha256 0641f37b18588b3da43d5cca8a6465221b0d634f23b636e495b10e6426d12b12) and the 82-file manifest (sha256 0817d98ea3d381aea4cf0e8135a09dfbe80da150a765ef762a6c06d100d6bc84) frozen before the first job (freeze1141ta.sh verify: files verified after the run); scored by analysis/post_1141ta.py (standard library, written after the run, not frozen) because the frozen recompute_1141ta.py cannot read the capacity dumps (it looks for NAME.param.bin.gz, the tool wrote NAME.<program>.param.bin.gz) nor the o4 rows (it reads `row N:` at line start, the tool prints `probe pix_pa0: row N:`); the frozen scorer also scored the two dpm-oom jobs that did not run (oom-1400-0x422 and oom-1300-0x422, refused by the tool, rc 2) as passes, which post_1141ta.py counts as void, and the reader of the eot-store table was replaced as well (a text regex became the job's rc; it gives the same 6, 8 and 4 of 10); the frozen predictions and scripts are unchanged (freeze1141ta.sh verify); plan.md is not in the 82-file manifest and was written (14:07:55) after it (14:06:18), so its criteria are attested by file times only, as is the freeze as a whole (local file times and the run log's clock, no external stamp); the output of post_1141ta.py is kept beside it"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["vdm-verification-1141ta"]
terms = ["Dynamic Parameter Management (DPM)", "ta3d_ctl"]
+++
**What ran.** Q211 asked whether the pages a scene needs add up for four triangles that overlap
('stack4') or lie apart ('disj4'), against one triangle ('n1'). The tool's -n N is N successive
renders of the same one-triangle scene (each render has its own words and dump, `tri.k`), not N
triangles in one render: the output of every job shows `tri 1024x768 #1` to `#4` with their own job
lines. So the series measure four renders each, and nothing was run on a scene with more than one
triangle. The frozen predictions (one pair, at P = 0x422: disj4 has more pages than stack4, HG, or
the same, HT) used the maximum of the status over the job; the frozen recompute has no reader for
these jobs.

**Results.** [HW] At P = 0x422 (no overflow): n1 peak status 0x13 (19 pages, E625's number), stack4
0x13 four times (one run of the status per render: 0.358, 1.234, 2.080 and 2.927 s), disj4 0x13,
0x14, 0x11 and 0xc for the triangle moved by 0, 192, 384 and 576 pixels (triangle areas 207456,
205536, 176736 and 113376 pixels). The pair of frozen predictions, HG (disj4 above stack4) and HT
(equal), is void: the disj4 job renders four different single triangles, and its maximum status
(0x14) is above stack4's (0x13) only because the one moved by 192 pixels needs 20 pages, which is
the position dependence and not the geometry of a multi-triangle scene. The first draft scored 'HG
right, HT wrong' by hand from the maximum status; those two scores are withdrawn. At P = 0x30 (first
threshold 14 pages): every render of n1 and stack4 overflows (5 of 5), disj4's first three overflow
(need 19, 20, 17) and the fourth, whose need is 12, completes. At P = 0x28 (6 pages): all 13 renders
overflow (n1 1, stack4 4 with its repeat 4, disj4 4). So E625's rule, overflow iff the need exceeds
P - 0x22, with the needs measured at 0x422, gives all 22 render outcomes of the two P (9 at 0x30, 13
at 0x28); they are 8 distinct conditions, the 4 positions at each P: the unmoved triangle is
rendered 10 times at 0x28 and 6 at 0x30 (n1, stack4, its repeat and the first of disj4) with the
same outcome and the same dwords 37 and 38 each time, so 14 of the 22 are repeats. This was computed
after the run, with a rule fitted on the default triangle only and needs read from the same scenes,
so it is a consistency check and not a held-out test. The control block of every render: dword 37 =
0x10006 (1 << 16 | P - 0x22) and dword 38 = 0x20 (the raise) at 0x28 in 13 of 13 (4 conditions),
both 0 at 0x30 in 9 of 9 (4 conditions), as E625's boundary says for the unmoved triangle (the raise
needs twice the first threshold below the need plus k, 2 or 3 at 1024x768: 12 below 21 at 0x28, 28
not below 22 at 0x30); the moved ones at 0x30 do not separate k (none raised).

**What it shows.** [HW] The page need of a one-triangle scene is not a constant: 19, 20, 17 and 12
pages for one triangle at four positions, so `dpm.rs` cannot take 19 pages for 'a triangle at
1024x768' (E625's number is the one of the default position). [infer] The need would follow the
macrotile lists the triangle fills; the count of macrotiles per render was not read from the state
page here. Whether stacked or disjoint triangles of one scene add differently (the question) is not
answered: it needs a tool that puts more than one triangle in one render (Q211).

**Not shown.** A scene of 2 to 4 triangles; the need as a function of macrotile coverage; P other
than 0x28, 0x30 and 0x422.
