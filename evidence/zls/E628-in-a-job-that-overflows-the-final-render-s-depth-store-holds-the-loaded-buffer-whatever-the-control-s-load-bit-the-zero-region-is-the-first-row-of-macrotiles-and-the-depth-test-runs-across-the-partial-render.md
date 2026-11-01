+++
id = "E628"
claim = "In a job that overflows the parameter buffer the ZLS store holds, at every dword outside the zero region, the dword of the load buffer at that address (a load buffer of ascending indices, 559104 of 559104 dwords outside tile rows 0 to 11 at 1024x768 in 8 of 8 jobs, at 0x28 and 0x30 pages, scenes z = 0.5 and full-screen ramp) whether the control has the load bits 1 and 14 (0x0017510e) or not (0x0017110c): the same job in 0x422 pages stores the scene's depth without the load bits (0 of 2) and the loaded buffer with them (2 of 2, E467); the load buffer itself comes back from those 8 jobs with 195583 dwords changed to zero, all in tile rows 0 to 11 and none elsewhere, and from the 4 jobs that complete untouched (0 changed), so a store reaches the load address; the zero region of the store at 1024x768 with no overlap between tiles (G = 33, 34 slots a tile row for 32 tiles) is 195584 dwords: 336 whole target tiles and 48 half-zero tiles, 360 tile-equivalents of the 384 in tile rows 0 to 11 (24 tile-equivalents, 6.25 percent, short; the half-zero tiles sit at tx 6, 14, 23 and 31 of every row), and 22 zero slots of the 24 padding slots at tx 32 and 33 (11264 dwords) that are not target tiles (184320 = 360 tiles when the buffer is loaded), while at 4096x4096 with no padding (G = 127) it is 4193152 dwords, a prefix of 8189.75 of the first macrotile row's 8192 tile slots (2.25 tiles short, not a whole number of tiles; the band of a first row, 4.0 to 4.2 million, hit 2 of 2 and that of a first macrotile, 0.9 to 1.1 million, missed 2 of 2), so the zero rows are not one rule across the two sizes; with overlapping tiles the zeros are 15104 dwords at 1024x768 in all 26 overflowing jobs at G = 1 and 80640 and 48000 at 4096x4096 at G = 1 and 0 (E465's counts, 4 of 4), and the store's window is E465's rule at every size (64512, 326656, 196096, 16777216 dwords; 755712 for the whole buffer at 1024x768 with G = 33, 766976 in the overflowing jobs); two overlapping triangles whose depth decides the order (the first in a geometry kick, the second in the final render, the overflow coming while the second is tiled at 0x38 pages, 4 jobs) store the nearer one at 142323 and 141579 of 155833 overlap pixels (the 13510 others lie in the zero region, where the test sees nothing), A where the second is farther and B where it is nearer, 0 mixed, with the load bits and without (4 of 4), the store of each 0x38 job being equal to the 0x422 job's at all 571392 non-zero dwords; 12 more jobs at 0x3c to 0x48 pages complete and store the same minimum at all 155833 pixels"
unit = "zls"
method = "tri --depth with the ZLS flag, the bases and a control per job (--depth-ctl, --depth-fill, --depth-dump, --depth-store with a separate store buffer of its own marker fill for the dl jobs, --depth-ctl-next for the final render's control in the ov jobs), on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B, stock firmware, tool sgxfive-test-1135 (sha256 7732b945...): table depth (74 jobs, two runs of each case) and follow-up a, 1024x768 at 0x23 to 0x38 and 0x422 pages and 4096x4096 in 0x2000 pages; the dumps decoded by the address rule of E465 (tile (tx, ty) at dword 512 * (ty * (G + 1) + tx)) by the dataset's analysis/an_dl.py, the corrected recompute and an extra count of the load buffer's own dump"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["dpm-partial-model-batch"]
terms = ["CR_ISP_ZLSCTL", "CR_ISP_ZSTORE_BASE", "Dynamic Parameter Management (DPM)"]
+++

**What ran.** Table `depth` (74 jobs) and follow-up a, `tri --depth` with the ZLS flag, the bases
and a control per job (E461's setup; `--depth-ctl`, `--depth-fill`, `--depth-dump`,
`--depth-store` with a separate store buffer of its own marker fill for the `dl-*` jobs,
`--depth-ctl-next` for the final render's control in the `ov-*` jobs), 1024x768 at 0x23 to 0x38,
0x422 pages and 4096x4096 in 0x2000 pages (E465's identity), two runs of each case; the dumps and
a decoder of the address rule (tile (tx, ty) of 32 x 16 pixels at dword 512 * (ty * (G + 1) + tx),
G = control bits 11:3) in `analysis/an_dl.py` and the recompute. 12 `dl-*` jobs (a buffer of
ascending indices as the load buffer, the control with and without the load bits, P = 0x422, 0x28,
0x30), 18 `ov-*` jobs (two triangles tilted by --tri-z 0.25,0.75,0.25, B moved by -96 (farther in
the overlap) or +96 (nearer) pixels, P = 0x422, 0x38, 0x3c, 0x40, 0x48, with and without the load
bits for the final render), 6 `w4096-*` jobs (G = 1, 0, 127), 38 `dp-*` jobs. The load buffer's
own dump (`depth.1.bin` of the `dl-*` jobs) was not looked at by `an_dl.py`; it was counted for
this record.

**Results [HW].** H-load-yes (declared: the stored dword equals its index at tile rows 12 and
below iff the control loads): 4 of 8: the 4 jobs with the load bits at 0x28 and 0x30 hit and the 4
without missed (they hold the indices too), E467's 4 of 4 at 0x422 hit (0 of 2 without, 2 of 2
with). In the 8 overflowing `dl-*` jobs the store beyond the zero region equals the load buffer
outside the first macrotile row in every dword whatever the scene and the control; the first
macrotile row holds 184320 zeros and 12289 dwords that equal their index. The load buffer itself,
read back after the job, has 195583 of its dwords changed to zero (the index 0 is already zero),
every one of them in tile rows 0 to 11 and none outside, in the 8 overflowing jobs; in the 4
`dl-*` jobs in 0x422 pages it is unchanged (0 changed). So a store reaches the load address: the
zero region exists in the load buffer, and the store equals the load buffer outside that region
because the final render copies it (or loads and stores it). The scene does not appear in the
store: the indices as floats are denormals below every depth the scene writes, so the depth test
keeps the loaded value [infer: a test that passes only the nearer depth]. H-dload-yes (the test
across the partial render: the first triangle's depth is kept where the second is farther) 4 of 4,
H-dload-no (the second triangle's value overwrites it, mixed) 0 of 4, H-min (the minimum) 10 of
10; these three were "no data" in the frozen recompute (it read the depth buffer of a two-render
job from `depth.1.bin`, absent in the `ov-*` jobs, which have only `depth.2.bin`) and are scored
by the corrected copy (the dataset's method gives the frozen totals). Of the 16 `ov-*` jobs at
0x38 to 0x48 only the four at 0x38 overflow (the second triangle's need is 23 to 26 pages at
1024x768, E627, so the cases at 0x3c, 0x40, 0x48 are whole-buffer jobs and test H-min only): there
the stored overlap is A (the first triangle's depth) where B is farther and B where it is nearer
at all 142323 and 141579 overlap pixels outside the zero region, with the control's load bits or
without. The store of each `ov-*-same-0x38` job equals the 0x422 job's store at all 571392
non-zero dwords (0 differ, far and near); the 13510 overlap pixels in the zero region are the ones
the comparison cannot see, so "with the load bits or without" is a statement over the overlap
pixels only.

Zero region. H-zero-M1 (first macrotile, G = 1, G = 33, G = 127): the G = 1 and G = 0 counts
(15104, 80640, 48000) hit, the G = 33 count 184320 missed by 11264 in the 12 `dp-*` jobs without a
load, and the G = 127 band missed; H-zero-row hit (4193152 in 2 of 2), a band at 4096x4096 only.
At G = 33 the 195584 stored zeros are 336 whole target tiles and 48 half-zero tiles (the same as
E468's counts), 360 tile-equivalents of the 384 in tile rows 0 to 11, plus 22 zero slots of the 24
at tx 32 and 33, which are padding (11264 dwords, 22 slots of 512); the loaded job's 184320 is the
360 tiles alone. So the first row is 24 tile-equivalents (6.25 percent) short of its tiles at
1024x768, and 2.25 tiles short at 4096x4096, where there is no padding: "the first row less 1 to 2
tiles" was a sum of the two, and the zero rows are not one rule across the sizes. E468's own
predictions (zero_dwords 184320) missed against 195584 on its own fit rows (the 6 G = 33 runs of
the ramp). The window of the store: E465's rule and counts hit in 26 of 32 scored rows; the 6
misses are the declared 786432 (the whole buffer) for the G = 33 z = 0.5 jobs (the window is
755712 dwords in whole-buffer jobs, 766976 with the 11264 extra zeros in overflowing ones).

**Reading [infer].** The partial renders store the depth of the macrotiles they drew and the final
render loads it, whatever the control the host gives: the load bits of the host's control are not
what loads (they matter when the whole job is one render, E467). The first row of macrotiles (tile
rows 0 to 11 at 1024x768, 64 tile rows at 4096x4096) comes back zero from the load buffer and
stores zeros: either a partial render stores zeros at the load base for the region it does not
cover, or the load buffer is cleared as it is read; the zero region is the region the first
partial render's store does not cover or the final render loads as zero, and which of the two
readings holds is not separated. The row's tiles are not all zero and the shortfall is not a whole
number of tiles at 4096x4096 (8189.75 of 8192 slots). Not shown: the tile order of the store
(E468's 512 dwords), the colour reload with a depth buffer (the probe's depth scratch, a tool
option, was not implemented), the zero region at other macrotile counts, the 11264 extra zero
dwords' place.

**Not shown.** What the load reads when the buffer's base differs from the store's (the `dl-*`
jobs use two buffers, the store buffer's fill is untouched where the index buffer is not stored).
