+++
id = "E826"
claim = "R3k stage k-bif (K2, 5 jobs, Q003 what clears a latched fault, 4 held bus-interface faults: a TA read (f1, f1r, CR_BIF_INT_STAT 0x90008, CR_BIF_FAULT 0x3e000001), a TA write (f2, E788's a6, 0x90004 and 0x20008061) and a texture fetch (f3, 0x90002 and 0x3e017001), plus the idle row n0): n0 passed (the four writes with nothing held changed nothing, BIF_CTRL restored); in each held row the write of 0x1 (an unset bit) and the write of the fault word without bit 19 to CR_BIF_INT_STAT (0x10008, 0x10008, 0x10004, 0x10002) left CR_BIF_INT_STAT and CR_BIF_FAULT as they were at the kernel's read after the write (4 of 4); setting bit 4 of CR_BIF_CTRL (the debugfs flip, CLEAR_FAULT) made the kernel's read after the write return 0x80000 and 0 (f1, f1r, f3) or 0 and 0 (f2); clearing the bit again returned both registers to the fault's values (4 of 4); the registers stayed latched through the 2.5 s watch, the jobs never completed and only the debugfs reset cleared them; all four held rows are OTHER by the frozen rule: 'Q003: cannot tell: no held row could be read'"
unit = "bif"
method = "R3k session K2 (R3K-pixel; decisions R3-K4, R3-K6 and R3-K7), dataset render-closing-r3k-pixel, 2026-11-10, attempt out/20261110-193547 (one driver call, run/k.sh, from 19:35:47 Mac time: k-f4 19:35:48, k-pb0 19:37:30, k-pb skipped by its gate, k-bif 19:38:04; out/k.log), kernel 7.3.0-resgx545, the new module of round 3 (fork resgx545 8fc748b0, srcversion 230E0EF50FFFD606C53AE3C, installed = loaded, checked at each preflight; gma500_gfx.ko sha256 06bf58db6e1c78f2bd9858bcc7b9e63d752786e098e50b5c67345ce69f2ceb78 as recorded in env.json), stock firmware sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a, the laptop (host cedar) on the home LAN, not the direct cable, rebooted into the new module at 18:48 (boot-test-kernel.sh then test-session.sh, health ok), tool ~/sgxfive-test-r1 (sha256 bf4f8be2d8a8fe50034559450928e05695dc96d396d4892f9b00ea6bc0d4f053, R1's build, not rebuilt) with the pinned tool source (TOOLSRC.sha256); preflight per stage: srcversion loaded = installed = 230E0EF5..., the debugfs files, the defaults (hold_recovery N, render_pb_pages 0x422, alias_skip 0, render_rgn_arrays 1), the six kregnow rows; a debugfs reset before each job, render_rgn_arrays written per row (read back, written back to 1 at every exit and checked by the driver), 5 fault-class events at most per stage, health after every fault and stage; 24 jobs frozen (k-f4 11, k-pb0 3, k-pb 5, k-bif 5), 19 run, 5 skipped; FROZEN.sha256 2ff760c33774cd3e7666a284ad0d986dbb7e71ec97b542c50d3bacfc8f6f9af5 and PREDICTIONS.sha256 0d2138ffdd52feef33cf80be21b579d8f00d4b44a40bec37db804158e802c179 written before the first job and verified at each stage; no failed attempt, no refreeze; stage k-bif (last of the session, the riskiest): n0 first, then f1, f1r, f2 (320 x 400, knob 1, 4x) and f3 (probe of the texture program s1d-tw64x64-l2e2, 16 scratch pages) held with hold_recovery Y; per held row, after the fault is latched and read (snapshot b0): the four writes by debugfs kregnow, each followed by a snapshot of the registers and by the kernel's own log line of the registers it read under its lock right after the write: (1) 0x0c04=0x1, (2) 0x0c04=the fault word without bit 19 (0x10008, 0x10004, 0x10002; the idle bit never written), (3) 0x0c00 ^= 0x10 (BIF_CTRL bit 4 set, CLEAR_FAULT), (4) 0x0c00 ^= 0x10 (cleared), then a watch of 2.5 s (snapshot b5; tool rc and whether the job completed), the registers read, the debugfs reset (the two new reset lines read: after the halt, after the fault clear), hold_recovery N read back, health; a write that the module refused or fewer than four kernel log lines made a row NODATA (none); 4 fault-class events in the stage; the kernel log lines were read from the fork's source, not from a run, before the run (PREFLIGHT.md DEVIATION 8) and matched; scored by the frozen score/score_k.py k-bif (out/20261110-193547/score-k-bif.txt, whose per-row readings are the kernel's log lines after each write; the snapshots are read from runner.log and the kept regs files). The frozen verify of this session pins the landed userspace/libsgxfive/tools/sgxfive-test.c (sha256 4250ca36...) by absolute path; main's file changed afterwards (8a2e8c5, libsgxfive: refuse a ba in a placed --tri slot) so the scorer refuses on main today (FROZEN FILES CHANGED); the three stage scores, the gate and the verdict were rescored from the copy in resgx545-data in a scratch copy with the pinned file (main's parent of 8a2e8c5) and the path rewritten in a scratch FROZEN.sha256, and are byte-identical to the kept ones"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-r3k-pixel:out/20261110-193547/k-bif/"]
terms = ["CR_BIF_CTRL", "CR_BIF_CTRL.CLEAR_FAULT", "CR_BIF_INT_STAT", "CR_BIF_FAULT"]
+++
**What ran.** Q003 asks what clears a latched fault in `CR_BIF_INT_STAT` and `CR_BIF_FAULT` while
leaving the bus usable. E767's lead was that the kernel's halt (the soft reset) leaves both
registers reading zero before it writes the clear bit; three hypotheses for what a host write can
do on a held fault: H-W1C (writing the set bits to `CR_BIF_INT_STAT` clears them), H-CLR (setting
`CR_BIF_CTRL` bit 4 clears them, and they stay clear), H-RST (only the reset does). The new
module's `kregnow` rows for 0x0c00 and 0x0c04 are accepted only with nothing running or a recovery
held.

**Frozen verdict (as printed).** `SUMMARY: k-bif: Q003: cannot tell: no held row could be read
({'f1-ta-read': 'OTHER', 'f1r-ta-read': 'OTHER', 'f2-ta-write': 'OTHER', 'f3-tex': 'OTHER'})`,
with `n0-idle: PASS: idle: nothing changed after any of the four writes (INT_STAT 0x80000, FAULT
0)`.

**The kernel's reads right after each write (the frozen scorer's input), CR_BIF_INT_STAT /
CR_BIF_FAULT [HW].**

| row | the fault | after 0x0c04=0x1 | after 0x0c04=set bits | after BIF_CTRL bit 4 set | after it is cleared |
|---|---|---|---|---|---|
| f1 | 0x90008 / 0x3e000001 | same | same (wrote 0x10008) | 0x80000 / 0x0 | 0x90008 / 0x3e000001 |
| f1r | 0x90008 / 0x3e000001 | same | same (0x10008) | 0x80000 / 0x0 | 0x90008 / 0x3e000001 |
| f2 | 0x90004 / 0x20008061 | same | same (0x10004) | 0x0 / 0x0 | 0x90004 / 0x20008061 |
| f3 | 0x90002 / 0x3e017001 | same | same (0x10002) | 0x80000 / 0x0 | 0x90002 / 0x3e017001 |

**The register snapshots of the runner (a regs read about 270 ms after each write) [HW].** With
bit 4 set (snapshot b3, BIF_CTRL 0x10) the two registers did not all read clear: f1 INT_STAT
0x90008 and FAULT 0x0 (FAULT clear, INT_STAT latched), f1r INT_STAT 0x80000 and FAULT 0x3e000001
(INT_STAT clear, FAULT latched), f2 0x80000 and 0x0 (both clear), f3 0x80000 and 0x0 (both clear).
After the bit was cleared (b4) all four rows were latched again as at the fault, still so after
the 2.5 s watch (b5) and before the reset (snapshot 2). The jobs never completed (tool rc 1, 1, 1,
3). The reset cleared everything: both new reset lines read BIF_INT_STAT 0x80000 and BIF_FAULT 0x0
in every row (E767's frozen lead, held), CR_EVENT_STATUS2 0x400 after.

n0: all four writes returned status 0, the six snapshots and the four log lines read INT_STAT
0x80000 and FAULT 0 throughout, BIF_CTRL 0x10 after write 3 and 0 after write 4.

**Reading the rows against the frozen hypotheses (post hoc, from the frozen prediction rows and
the data, not the scorer's verdict).** H-W1C predicted the registers clear after write 2: they
were unchanged in 4 of 4, so a write of the set bits does not clear. H-RST predicted them
unchanged after write 3: they read clear in 4 of 4, so the reset is not the only thing that makes
them read clear. H-CLR predicted clear after write 3 and still clear after write 4: the first held
in 4 of 4, the second did not (the fault returned in 4 of 4). So no hypothesis fits all three
readings, which is the frozen OTHER, and the rows are not MIXED: they agree.

**What it shows and does not.** Writing the fault's set bits to `CR_BIF_INT_STAT` does not clear a
latched fault (4 of 4, three requesters). Setting `CR_BIF_CTRL` bit 4 makes the registers read
clear while the bit is set, at the kernel's own read after the write in 4 of 4 and at a later read
in 2 of 4 rows for both (1 of 4 for FAULT only, 1 of 4 for INT_STAT only) [infer: the held job's
requester keeps raising the fault and the bit holds the latch back rather than clearing a latch;
not separated], and the fault is back when the bit is cleared: the bit alone is not a clear that
lasts while the faulting job is stalled. The reset clears them. Not shown: whether a clear with
the requester no longer stalled would stay (no row had one), the order of the halt's and the clear
bit's effects inside the reset, the faults of the 3D's own fetches or the ZLS, whether bit 4's
effect differs by requester (the later reads differ between f1 and f1r, the same fault).
