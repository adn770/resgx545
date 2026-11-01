+++
id = "E708"
claim = "The end-of-tile task's per-tile store of the global registers, with the E130 form (a register-offset store to r4 + a tile slot from sa15, 128x128 and 256x128, 5 jobs), completes in 5 of 5 (no fault line, one job the sa-only control), and 32 tile slots hold their own g16 to g31 and g39 to g43 plus sa0 to sa10 in 16 dwords each (all 32 tiles at 128x128, 32 of the 64 at 256x128): g19 = 0x1a, g25 = 3, g16 and g26 to g31 = 0, g43 = 0xff000000, g17 in 0 to 3, g23 in {1, 0x11}, g24 in {1, 9}, g18 and g21 changing from tile to tile, but g20, g41 and g42 read 0 where E572 read 1, 1 and 1.0"
unit = "usse"
method = "table eot-globals (5 jobs, safe: probe --temps 8 --tri pixev:60 with the end-of-tile slot eot_tile_ga.bin (g16 to g31), eot_tile_gb.bin (g39 to g43, sa0 to sa10) or eot_tile.bin (sa0 to sa15, control), 128x128 and 256x128, probes built with the landed probe.py from probes/ta-eot.toml), on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed and loaded, equal in the ten scripts), stock firmware (sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a), tool ~/sgxfive-test-1140 (sha256 bd55ffe69cf310f574f019ac3cbe3cccf0464d2e2addf0e47f940570440ffa76), debugfs reset, kpoke, hold_recovery and render_pb_pages only (no kreg, no kregnow, no clock-gate register written), run-all-1141ta.sh: 157 jobs in ten tables run in one pass (ten scripts, rc 0 each; the exit=1 at the end of the log is the runner's last test, not a failure), one process per job, a marker per job in the kernel log (157 of 157, in case order), every raw output and dump gzipped with its raw sha256 (741 files, every one equal to the sha256 printed at the run); predictions-declared.tsv (sha256 0641f37b18588b3da43d5cca8a6465221b0d634f23b636e495b10e6426d12b12) and the 82-file manifest (sha256 0817d98ea3d381aea4cf0e8135a09dfbe80da150a765ef762a6c06d100d6bc84) frozen before the first job (freeze1141ta.sh verify: files verified after the run); scored by analysis/post_1141ta.py (standard library, written after the run, not frozen) because the frozen recompute_1141ta.py cannot read the capacity dumps (it looks for NAME.param.bin.gz, the tool wrote NAME.<program>.param.bin.gz) nor the o4 rows (it reads `row N:` at line start, the tool prints `probe pix_pa0: row N:`); the frozen scorer also scored the two dpm-oom jobs that did not run (oom-1400-0x422 and oom-1300-0x422, refused by the tool, rc 2) as passes, which post_1141ta.py counts as void, and the reader of the eot-store table was replaced as well (a text regex became the job's rc; it gives the same 6, 8 and 4 of 10); the frozen predictions and scripts are unchanged (freeze1141ta.sh verify); plan.md is not in the 82-file manifest and was written (14:07:55) after it (14:06:18), so its criteria are attested by file times only, as is the freeze as a whole (local file times and the run log's clock, no external stamp); the output of post_1141ta.py is kept beside it"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["vdm-verification-1141ta"]
terms = []
+++
**What ran.** E130's per-tile program: the pixel-event program passes each tile's slot in sa15 as
(64 << 16) | slot, and the end-of-tile task stores to 0x5CAF0000 + k * 4 with the register offset r5
= (sa15 & 0x3ff) | 0x400000, so that dword 16 * slot + k of the scratch holds the k-th stored source
of the tile. The stored sources: g16 to g31 (ga), g39 to g43 and sa0 to sa10 (gb), sa0 to sa15 (the
control, ctl), at 128x128 (ctl, ga, gb) and 256x128 (ga, gb). Frozen: all five complete (E130's form
completed with sa stores, 60 of 64 per-tile stores landed there).

**Results.** [HW] 5 of 5 completed (rc 0, no fault or hung line, health triangle not needed). Each
job lists 544 changed dwords: the 16-dword blocks of 32 tile slots (0 to 3, 8 to 11, ..., 56 to 59:
four tiles a row, eight rows, slot = 8 * row + column) at both widths, and two more blocks (slots 64
and 768) [infer: the slot word's clamp, tasks that did not get the slot, as the template says]. At
128x128 (4 x 8 tiles of 32x16) that is every tile; at 256x128 (8 x 8) the same 32 slots hold data
and the other 32 tiles are not in the readout. In every tile block of ga: g16 0, g19 0x1a, g20 0,
g25 3, g26 to g31 0; g17 in {0, 1, 2, 3} (0 in 14 of 32 tiles at 128x128), g18 in 0xa to 0x16
(even), g21 in 0x3 to 0x1f, g22 in {0, 1}, g23 in {1, 0x11}, g24 in {1, 9}. In gb: g39, g40, g41 and
g42 0, g43 0xff000000 in all 32; sa0 and sa1 equal and varying per tile (4 to 0x1c07 at 128x128),
sa2 2 (6 in 3 tiles), sa3 to sa10 the target colours (0xff203040 or 0xff00ff00).

**What it shows.** [HW] The per-tile values of g17, g18 and g21 to g25 are readable at the end of a
tile without a fault, which E572 could not do (only the last tile's store survived, and a store
faulted the job): [infer] g25 = 3 and g23 and g24 with bit 0 set in all 32 tiles read as the values
of the task's last instance (instance 3 of a quad). g18 and g21 differ from tile to tile without a
rule read here (Q053's open part for the end-of-tile task is now a table; the vertex-task part is
not run). [HW] g20 reads 0 in every tile (64 of 64 blocks of the two ga jobs) and g41 and g42 read 0
in every tile (64 of 64 of the two gb jobs), where E572's 37 stores read g20 = 1, g41 = 1 and g42 =
0x3f800000 at 64x64 and E374 had them so in the pixel task; g19 = 0x1a and g43 = 0xff000000 agree
with E572. The two forms differ (address by `[r1,+#0]` against `[r4,+r5]`, the pixev program, 8
temporaries against 32, 128 wide against 64): which difference moves g20, g41 and g42 is not shown
(Q275).

**Not shown.** The rule for g18 and g21; the vertex task; the tiles of the 256x128 target that are
not in the readout.
