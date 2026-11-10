+++
id = "E763"
claim = "In a render context made for 544 x 400, a 320 x 400 render at CR_TE_AA 0x20000000 mode 2 (S3's a4) had a TA data buffer of 0xa000 bytes (the maximum's layout: --max-width takes effect) and the TA wrote in it one array of 512 region headers at 0x4000 to 0x57f4, the target's own layout (2 x 2 macrotiles of 8 x 16 regions, rgn_size 0x1800, not the maximum's 0x2400), 250 inside the target with a stream block each and 262 flagged outside it, and nothing below 0x4000 or from 0x5800 to 0xa000 (1 run)"
unit = "ta"
method = "S3 stage s3-a-safe, attempt 20261110-003114, job a4-ctl-320x400-te20 (setup and provenance as the isp record of the same job): the kept --dump-render files a4-ctl-320x400-te20.tri.tadata.bin.gz (40960 bytes, sha256 of the raw file eded049c...) and .tri.param.bin.gz (4603904 bytes); the frozen scorer's knob proofs (tool echo, dump size, slot count: slots of 0x1800 from 0x4000 hold 762, 0, 0, 0 non-zero dwords, nothing below rgn) re-run; post hoc, not frozen: analysis/a4_tadata.py, a4_rh.py, a4_tilemap.py and the landed tools/usse-asm/pbdump.py on the decompressed copies"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-s3:out/20261110-003114/s3-a-safe/"]
terms = ["CR_TE_AA", "REGION_HDR.POS", "REGION_HDR.FLAGS", "REGION_HDR.STREAM", "CSTREAM.PRIM_TILES"]
+++
**Frozen part.** The knob proofs of a4 (tool echo, TA data size, slot count) were in the frozen
scorer and passed; the control's frozen image prediction failed (E762). The reading of the
headers below is post hoc, not frozen.

**Results [HW].** TA data 0xa000 bytes: pages 0 to 3 zero, page 4 566 and page 5 196 non-zero
dwords, pages 6 to 9 zero. From 0x4000 there are 512 three-dword headers (word 0 non-zero in
512 of 512,
word 2 zero in all): flags 0x00 242, 0x02 (outside the target) 262, 0x04 (first of a macrotile) 4,
0x10 (last of a macrotile) 3, 0x90 (last of a macrotile and of the scene) 1. The positions run over
four macrotiles of 8 x 16 regions (columns 0 to 7 and 8 to 15, rows 0 to 15 and 16 to 31), 32 x 16
pixels each: 10 x 25 regions inside the 320 x 400 target, each with a stream block in the parameter
slot, the rest flagged outside. The 250 stream blocks hold five forms (`4688 0007` with masks 1/1,
`4688 000e` 2/2, `4688 000f` 3/2 and 1/3, `4690 ffff` both tiles): the two primitives of the
clipped quad on either side of its diagonal.

**Scores.** The frozen knob proofs of a4 passed (echo 544x400, 0xa000, one array, nothing below
rgn); the control failed only on its image (E762).

**What it shows.** [HW] The kernel laid the TA data out for the maximum, and the TA wrote headers
for the target's macrotile grid only: the arrays of a smaller target in a larger context are
spaced by the target's rgn_size, which is the premise of S3's a5 (four arrays of 0x1800 from
0x4000 end exactly at 0xa000). [infer] It is one run at TE 0x20; that the four arrays at TE 0xe0
take the same spacing follows E728's doubling (1, 2, 4 arrays) but is not shown at this size.

**Not shown.** f (the job writes one array); whether a fifth array would be touched; the job at TE
0xe0 in this context (a5) or in one made for 320 x 400 (a6), neither of which ran.
