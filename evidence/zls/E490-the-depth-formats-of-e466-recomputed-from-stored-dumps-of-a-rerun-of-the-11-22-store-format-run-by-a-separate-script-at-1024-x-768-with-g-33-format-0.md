+++
id = "E490"
claim = "The depth formats of E466 recomputed from stored dumps of a rerun of the 11.22 store-format run, by a separate script: at 1024 x 768 with G = 33, format 0 holds the float z of the ramp at 786432 of 786432 pixels (within 1e-5 of the geometry's), format 1 holds round(z * 0xffffff) at 786432 of 786432 (z is the float format 0 stores at that pixel; floor, 333955), format 2 packs two rows in one dword in 256 dwords a tile with the dword index lx0 ly1 lx1 ly2 lx2 ly3 lx3 lx4 and the half ly0, derived from the dumps alone (786432 halves, 512 of 512 slots the same in every tile), formats 4 and 7 store nothing without a stencil buffer (0 dwords), formats 3, 5 and 6 store 965120, 96580 and 86084 dwords in 1885, 1508 and 1536 slots in the x ramp (the y ramp stores 965120, 84480 and 73760; format 3 reaches the last dword of the buffer, so its count is a lower bound), and bit 19 stores the float depth negated at 786432 of 786432 pixels and changes no dword of formats 1 and 2 (the dumps are byte-identical to the dumps without it, same sha256), where E466 had shown it by three frequent dwords"
unit = "zls"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1122 (sha256 ec423efc3d9aa34576553da70916be4ceb715a729cbc02cc4bd89fa052511244): probes/zls/store-format-dumps.toml (script store-format-dumps.sh, store-format.sh with the depth dumps of its parts A and B (formats 0 to 7 and bit 19) kept, gzip level 6, 22 files of 1.3 MB; parts C and D, the enable bits and the stencil, ran as before but their dumps were not kept), run by hand over ssh with a manifest written by hand (as E489); recompute_e466.py of the dataset reads the dumps; output.txt equals the 11.22 run's but for the clock line and one job time (476 us there, 418 us here)"
tiers = ["HW"]
date = "2026-11-08"
data = ["zls-store-format-dumps"]
terms = ["CR_ISP_ZLSCTL"]
+++

**What runs.** The 11.22 script: a 1024 x 768 target, G = 33, a depth ramp across x and across y,
the control 0x0017110c with bits 26:24 set to 0 to 7 and with bit 19 (and formats 1 and 2), the
buffer filled with 0xDEADBEEF; each job's dump kept as `dumps/f<n>-ramp{x,y}.bin.gz` and
`b19_<n>-ramp{x,y}.bin.gz`.

**The recompute.** From the geometry only (z of a pixel = 0.25 + 0.5 (p + 0.5) / (3 size)): format
0's stored floats against it; format 1's integer against round and floor of the format 0 stored z;
for format 2, each 16-bit half of each dword of both ramps decoded to a pixel (the z resolution,
1/65536, is finer than the 0.094 pixel of the ramp's slope), from which (dword in the tile, half)
-> (lx, ly) is derived for every tile and checked to be one mapping; changed dwords and slots for
the others; bit 19's floats against -z.

**Results.** Format 0: 786432 of 786432 pixels within 1e-5. Format 1: stored minus round(z *
0xffffff), z the float format 0 stored at the same pixel (with the geometry's double z instead, the
reviewer's recount gives -1 at 122563 and +1 at 35970 pixels of the x ramp and a wrong value at
242829 of the y ramp, not in the data's recompute), is 0 at 786432 of 786432 (minus floor: 0 at
333955, 1 at 452477). Format 2: 393216 dwords changed, 786432 halves decoded, none outside the
target, 512 slots (dword in tile, half) each with one pixel across all tiles, and the mapping is
dword k = lx0 | ly1 << 1 | lx1 << 2 | ly2 << 3 | lx2 << 4 | ly3 << 5 | lx3 << 6 | lx4 << 7 (tile
base 256 dwords x (ty * 34 + tx)), half = ly0. Formats 4 and 7: 0 changed dwords; 3: 965120 in 1885
slots; 5: 96580 in 1508; 6: 86084 in 1536 (the x ramp; the y ramp changes 965120, 84480 and 73760
dwords in the same slots, so for 5 and 6 the count depends on the stored data, and format 3 reaches
dword 1023999 of the 1024000 of the buffer, so 965120 is a lower bound, as E466's "The buffer's end"
says). Bit 19: 786432 dwords changed with 1674 distinct values in the float format and the float is
-z at 786432 of 786432 pixels (the dword is the format 0 dword with bit 31 flipped at all of them);
for formats 1 and 2 the dumps of both ramps are byte-identical to the dumps without bit 19 (same
sha256: bit 19 changes no dword). The output of the rerun is the 11.22 run's, line by line.

**What it shows.** [HW] E466's counts are reproduced by a second run and recomputed from stored
data; the format 2 layout is derived from the data, not assumed; bit 19 of the control negates the
stored float depth at every pixel, not only at the dwords counted, and does nothing to the integer
formats 1 and 2. Formats 3, 5 and 6 are not decoded here (layouts only counted).

**What it does not show.** The layouts of formats 3, 5 and 6; the stencil dumps (not kept); bit 19
with a depth that is negative before the conversion to an integer format (not run; the ramp is
positive).
