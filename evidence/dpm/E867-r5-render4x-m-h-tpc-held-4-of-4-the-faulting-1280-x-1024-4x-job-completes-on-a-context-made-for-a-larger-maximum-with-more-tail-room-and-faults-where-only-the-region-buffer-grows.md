+++
id = "E867"
claim = "R5-render4x stage m (5 jobs, 1 fault): the 4x full triangle on four arrays, at target sizes that fault on their own maximum (E845), completed with 0 wrong pixels on a context made for a larger maximum whose tail-pointer room (4 side^2 bytes) is larger: 1280 x 1024 on 1280 x 1040 and on 2048 x 2048 (room 0x10000 against 0x4000, 321 scene pages) and 2048 x 1536 on 4096 x 4096 (0x40000, 769 pages), while 1280 x 1024 on 2048 x 1024, whose region buffer grows and whose room stays 0x4000, faulted with E845's word (BIF_INT_STAT 0x90100, BIF_FAULT 0x10000011), health ok after it; the control 1024 x 768 on 2048 x 2048 completed; the frozen verdict: H-TPC held, 4 of 4 rows decided, where every size rule predicted a fault in the three completed rows"
unit = "dpm"
method = "R5-render4x stage m (5 rows, fault limit 4: a fault-class event is a measured row, the stage stops at its fourth only with rows left; m0's fault would stop it) of the question-closing pass, round 5 (decisions R5-3 a, R5-4 a, R5-6 a), dataset render-closing-r5-render4x, attempt out/20261112-100112 (stage m 10:04:52 Mac time; driver log run-r5x.log), laptop host cedar, 2026-11-12, the boot, kernel, module (srcversion 99CD90DA26E3AFF9C450517), firmware and tool (sha256 e6951558...) of E865; each row `tri --tri-full --keep-going --keep-overflow --wait-ms 20000 --width W --height H --max-width MW --max-height MH --aa4` with E824's words (cmd:1=0xe0000000, cmd:10=0xeaa26e26, cmd:13=0x80000002, cmd:16=0xeaa26e26), --dump-render and --regs 0x0700-0x072c, render_rgn_arrays 0 and render_pb_pages 0x422 read back, a debugfs reset before each job, the fill and the strict health triangle after the fault; the rows' tail room, region offset and TA data size are the fork's layout formula (sgx_render.c at a2788bd8, transcribed in gen/rules.py and gen/pbmodel.py), for the maximum; H-TPC [infer] and the eleven rules' predictions frozen in predictions/m.tsv before the first job (FROZEN.sha256 e24977b3..., PREDICTIONS.sha256 6c700fa8...; the plan: closing5/render4x/exp-render4x-r5.md sections 1.4 and 3.2); scored by the frozen score/score_r.py m in the run (score-m.txt), re-run on the kept files on 2026-11-12 with byte-identical output; the layout numbers of the table below were computed at the fold with the frozen gen/rules.py lay()"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r5-render4x:out/20261112-100112/m/", "render-closing-r5-render4x:postrun/"]
terms = ["CR_TE_AA", "Parameter Buffer (PB)", "CR_BIF_FAULT", "CR_BIF_INT_STAT", "region header"]
+++
**What ran.** E845 and E846 left Q292 as a size fault of the 4x full triangle on four arrays, past
1024 x 768 and at or before 1280 x 1024, not an overflow. The round 5 plan found eleven rules that
fit the 13 cells on record (seven size rules and four variants of H-TPC [infer]: at 4x the TA keeps
4 bytes a tile of the doubled tile grid from the tail-pointer base on and clears them when it ends,
and where that extent passes the region headers of the context's layout the 3D reads zeroed headers
and faults at the request base). Only H-TPC depends on the context's maximum, through the kernel's
tail-pointer room, 4 side^2 bytes, side the power of two over the maximum's macrotile span. Stage m
ran the faulting sizes on larger maxima: m1, m2 and m4 with more tail room (every size rule: fault;
H-TPC: complete), m3 with a larger region buffer and the same room (both: fault, the control that
separates room from any larger maximum), m0 a completing size on a larger maximum (the control that
a larger maximum breaks nothing).

**Frozen verdict (as printed).** `m: survivors ['TPC-d-rgn', 'TPC-d-state', 'TPC-rs-rgn',
'TPC-rb-rgn'] of the 11 rules over 5 decided rows; H-TPC: the same faulting size completes on a
context made for a larger maximum when the tail room grows (m1, m2, m4 complete with 0 wrong) and
faults when only the region buffer grows (m3); every size rule predicted a fault in m1, m2, m4 (4 of
4 rows decided)`.

**Results [HW].**

| job | target | maximum | tail room (target's own) | outcome | scene pages, TA data |
|---|---|---|---|---|---|
| m0 | 1024 x 768 | 2048 x 2048 | 0x10000 (0x4000) | complete, 0 wrong | 193, 569344 |
| m1 | 1280 x 1024 | 1280 x 1040 | 0x10000 (0x4000) | complete, 0 wrong | 321, 311296 |
| m2 | 1280 x 1024 | 2048 x 2048 | 0x10000 (0x4000) | complete, 0 wrong | 321, 569344 |
| m3 | 1280 x 1024 | 2048 x 1024 | 0x4000 (0x4000) | fault 0x90100 at 0x10000011 | - |
| m4 | 2048 x 1536 | 4096 x 4096 | 0x40000 (0x10000) | complete, 0 wrong | 769, 2240512 |

m3's fault is the kernel's `BIF fault 0x90100 at 0x10000011 ... recovering` and the tool's `job
faulted, context lost`; the fill and the health triangle after it passed. In the four completed
rows the region headers of the target's doubled grid sit at the maximum's `td.rgn` with 0 off the
rule (the scorer's reported check; [infer] before, no dump on a larger maximum had been kept), and
the scene pages are U4's.

**What it shows.** [HW] The 4x fault is not a property of the target's size: the same target faults
or completes by the context it runs on. 1280 x 1024 completes on a context made for 16 more rows
(1280 x 1040), which moves the tail room from 0x4000 to 0x10000, and faults on a context made for
2048 x 1024, whose region buffer is a third larger and whose tail room is the same 0x4000. So what
decides is something the kernel sizes from the maximum and that the 1040-row maximum makes larger
and the 2048-wide one does not; of the layout's parts that is the tail-pointer room (H-TPC's
reading, held). Every size rule is refuted by m1, m2 and m4. [infer] The kernel's tail-pointer room
is too small for a 4x job past some size; E868 shows that none of H-TPC's four frozen extents is
the size at which it runs out.

**What it does not show.** The extent the 4x job needs (E868, E869), what the TA or the 3D writes
or reads there, and whether the room alone, without the other parts that grow with the maximum,
ends the fault (a kernel that sizes the room alone was not run). One run each, one boot.
