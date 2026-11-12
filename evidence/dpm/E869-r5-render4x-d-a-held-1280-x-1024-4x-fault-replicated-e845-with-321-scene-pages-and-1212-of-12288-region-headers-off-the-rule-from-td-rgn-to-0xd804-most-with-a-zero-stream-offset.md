+++
id = "E869"
claim = "R5-render4x row d (1 held job): the 4x full triangle at 1280 x 1024 on its own maximum faulted with E845's word (BIF_INT_STAT 0x90100, BIF_FAULT 0x10000011), replicating E845, and the held dumps were read: the parameter buffer holds 321 scene pages, as U4 and H-TPC predicted (the TA finished its scene), and in the TA data 1212 of the 12288 region headers are off the doubled-grid rule, from td.rgn 0x7000 (header 0 among them) to 0xd804, past the 0xa000 and 0xc000 bounds frozen for H-TPC's extents, so the extent fits no variant; read after the run, 1023 of the 1212 keep their word 0 and have a zero stream offset (word 1) where the tile is inside the target, 189 have word 0 off as well, they lie in macrotiles 0 to 2 only and in 15 runs (the longest 512 headers from 0x7000, then runs from 0x9004, 0xc004 and 0xd000), and every dword below td.rgn is zero"
unit = "dpm"
method = "R5-render4x stage d (1 row, last, fault limit 1, exploratory) of the question-closing pass, round 5 (decision R5-3 a, the render plan's 3 a), dataset render-closing-r5-render4x, attempt out/20261112-100112 (stage d 10:07:57 Mac time; driver log run-r5x.log), laptop host cedar, 2026-11-12, the boot, kernel, module (srcversion 99CD90DA26E3AFF9C450517), firmware and tool (sha256 e6951558...) of E865; hold_recovery Y written and read back, the 4x command of E867 at 1280 x 1024 on its own maximum without --dump-render, --regs or --pixels (a held fault loses the context), the registers read at 2.8 s and 1 s later (snapshots 1 and 2), debugfs render_param and render_tadata read in the hold, the kernel's debugfs reset, hold_recovery N read back, then the fill and the strict health triangle; the replication (every rule: fault with E845's word), the scene pages (321) and the header bounds of H-TPC's variants (headers off the rule all below 0xa000 for d, 0xc000 for rs and rb, header 0 among them) frozen in predictions/d.tsv before the first job (FROZEN.sha256 e24977b3..., PREDICTIONS.sha256 6c700fa8...); scored by the frozen score/score_r.py d in the run (score-d.txt), re-run on the kept files on 2026-11-12 with byte-identical output; the kinds, macrotiles and runs of the off headers and the area below td.rgn were read after the run by postrun/posthoc_d.py with the frozen header rule (gen/rlib.py headers(); postrun/posthoc_d.out), and the snapshots' 0x0724 from the runner's log (post hoc)"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r5-render4x:out/20261112-100112/d/", "render-closing-r5-render4x:postrun/"]
terms = ["CR_TE_AA", "Parameter Buffer (PB)", "CR_BIF_FAULT", "CR_BIF_INT_STAT", "region header"]
+++
**What ran.** No faulting 4x job had left a dump: a fault loses the context, and the one held try
(E846's o5) did not fault. Row d held E845's 1280 x 1024 fault and read the parameter buffer and
the TA data in the hold. Frozen for every rule: the fault replicates (a completion would void l and
m). Frozen under H-TPC: the TA finished its scene (321 pages), and the headers off the rule of the
doubled grid (E867's check) start at header 0 and end below the variant's extent, 0xa000 (d) or
0xc000 (rs, rb), every header past it on the rule.

**Frozen verdict (as printed).** `d: E845's fault replicated; scene pages 321 (H-TPC: 321); 1212 of
12288 headers off the rule, from 0x7000 to 0xd804, header 0 off; extent fits no variant`.

**Results [HW].** The kernel's `SGX BIF fault: stat 0x100 addr 0x10000011`, `BIF fault 0x90100 at
0x10000011 ... stalls job 639, recovering` and `recovery held (debugfs hold_recovery)`; snapshots
1 and 2 read BIF_INT_STAT 0x00090100, BIF_FAULT 0x10000011, CR_EVENT_STATUS2 0x440 and
CR_CLKGATESTATUS 0x000ccfa3; after the reset 0x20 and BIF_INT_STAT 0x80000, the EDM up after 142 us,
no `recovery failed` line, the fill and the health triangle passed. The held parameter dump (4603904
bytes) has 321 non-zero scene pages; the held TA data (212992 bytes) has 12288 headers from td.rgn
0x7000, 10240 of them inside the target, 1212 off the rule from 0x7000 to 0xd804, header 0 off.

**Read after the run [HW, post hoc].** Of the 1212 off headers 1023 have word 0 as the rule gives it
(x, y, the macrotile, no outside flag) and word 1, the stream's offset from the request base, zero
for a tile inside the target; 189 have word 0 off too and a non-zero word 1. They lie in macrotiles
0 (689), 1 (102) and 2 (421) and nowhere else, in 15 runs: 512 headers from 0x7000 to 0x8800, then
short runs to 0x9ac0, and runs of 170 or 171 headers over 0x9004 to 0x97fc, 0xc004 to 0xc7fc and
0xd000 to 0xd804, each within 4 bytes of a 2 KiB boundary at both ends. Every dword from 0 to 0x7000
(the tail pointers, control, OTPM and state pages) is zero in the held dump. Snapshots 1 and 2 read
the register 0x0724 as 0x01410141, 0x141 = 321 in each half.

**What it shows.** [HW] E845's fault replicates, and the TA had written its whole scene (321 pages)
when the 3D faulted. The region headers are not zeroed as H-TPC said: most of the off ones keep
their word 0 and lost only the stream offset, and they reach 0xd804, past every frozen extent.
[infer] A 3D that reads a header with a zero stream offset reads the request base, page 0x10000 of
the slot, which is never mapped: the fault's address (E845). What cleared the offsets (the TA's tail
pointers reaching into the headers, or the region headers written before the tail area was cleared)
is not read from one dump.

**What it does not show.** Whether the off headers are the same in another run, at another size or
on a larger maximum (E867's completed rows had none off); what 0x0724 holds in general (one held
reading, K2's held 0x000b000b); what wrote the off headers. One held job, one boot (Q292).
