+++
id = "E489"
claim = "The address rule of E465 recomputed from stored depth dumps of a rerun of the 11.22 store-layout run, by a script written separately from the run's script: of 3415552 dwords stored in the 18 cases (13 target sizes, G 0 to 511), 3279132 decode to a pixel whose rule address is the dword's own, 7780 are the background depth 1.0 of pixels past the target, and 128640 (48000 and 80640 in the two overflowed 4096 x 4096 jobs) are zero in both ramp dumps, none is at another address (0), the pixel to address direction holds for all 1098340 pixels of the four cases whose tiles do not overlap, and every one of the 18 lines of the run (changed, slots, not at the predicted address, background) equals the 11.22 run's, so the zeros of E465 are measured zeros, not an inference about the decoding"
unit = "zls"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1122 (sha256 ec423efc3d9aa34576553da70916be4ceb715a729cbc02cc4bd89fa052511244): probes/zls/store-layout-dumps.toml (script store-layout-dumps.sh, part A of store-layout.sh with each depth dump kept after the run, gzip level 6, 36 files of 1.0 MB in all; part B, the overflowed parameter buffer runs of E468, not rerun), run by hand over ssh, not by the campaign runner (the runner keeps output.txt only), so the dataset's manifest was written with the runner's own digest; recompute_e465.py of the dataset reads the .bin.gz dumps and the run's output.txt on the Mac (python3 -I); the 8 repeat runs of E479 ran on the same GPU in the minutes between two cases"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["zls-store-layout-dumps"]
terms = ["CR_ISP_ZLSCTL"]
+++

**What runs.** The 18 cases of E465's script (4 `fit` at 1024 x 768 with G 0, 1, 2, 33; 12 `ho`;
4096 x 4096 with G 1 and 0), each two jobs (a depth ramp across x, then across y), the raw depth
buffer filled with 0xDEADBEEF before. The script of this rerun keeps each dump as
`dumps/<case>-<W>x<H>-G<g>-ramp{x,y}.bin.gz` and prints its raw size and the sha256 of the raw
dwords (dumps.txt), so that the gz can be checked against the raw. The 4096 x 4096 dumps (67 MB
raw) compressed to 78 and 85 KB (G = 1) and are kept; nothing was left out.

**The recompute.** `recompute_e465.py` builds the in-tile order from a bit list (y0 x0 y1 x1 y2 x2
y3 x3 x4 from the lowest), decodes every stored dword of the x-ramp dump with the y-ramp dump at
the same dword to a pixel (z = 0.25 + 0.5 (p + 0.5) / 3 size, within 0.05 of a pixel's centre), and
compares the dword with 512 (ty (G + 1) + tx) + the in-tile index. A dword that both ramps hold as
0x3F800000 is the background depth; one that does not decode is counted and its values listed.
Where G + 1 is at least the tiles in a row (no two tiles share an address) it also walks every
pixel of the target to its rule address and checks that both ramp dumps hold the pixel there.

**Results.** 18 cases, 3415552 dwords stored: 3279132 at the rule's address (all that decode to a
pixel), 7780 background (1124 at 34 x 18 and 3584 and 3072 in the 4096 x 4096 jobs), 128640
undecodable, all of them 0x00000000 in both ramps (48000 for G = 0 and 80640 for G = 1 at 4096 x
4096), 0 at another address. The slot sets equal the rule's in 18 of 18. The walk over pixels holds
for 1098340 pixels in the four cases with no overlap (1024 x 768 G = 33: 786432 pixels, 640 x 480 G
= 511: 307200, 64 x 64 G = 1: 4096, 34 x 18 G = 3: 612 target pixels). The numbers of the run
script (changed, slots, not at the address, background, slot sets equal) are the 11.22 run's in 18
of 18 lines.

**What it shows.** [HW] E465's rule is recomputed from stored data and agrees; the dwords the 11.22
script could not place at 4096 x 4096 are zeros in both ramps, 128640 of them, which settles the
"zeros [infer]" of E465 as measured (that they are the sign of an overflowed parameter buffer,
E468, remains an inference). [HW] The rerun reproduces 11.22's counts exactly (a second run of the
same 18 cases, one run each). Differences from the first run: part B was not rerun and the tool and
the module are the same.

**What it does not show.** E468's overflow windows (part B); a second recompute at other sizes; the
in-tile order of a tile larger than 32 x 16.
