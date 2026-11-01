+++
id = "E468"
claim = "In a 1024 x 768 job that overflows the parameter buffer (0x28, 0x23 and 0x30 pages) with the ZLS store of the control 0x0017110c (no two tiles at one address), the 336 tiles of tile rows 0 to 11 hold zeros (48 more are half zeros, at tile columns 6, 14, 23 and 31), the other 1152 tiles hold the depth with the sign bit set at the address of E465 (602112 of 602112 dwords), and 11264 more stored dwords (their value was not tabulated) lie in the 2 slots each tile row has beyond its 32 tiles; the aliased job of the control 0x0017100c equals those tiles written in raster order with the first 8 x 12 tile macrotile last, except 512 dwords (0x28, 0x23) and 1536 (0x30)"
unit = "dpm"
method = "probes/zls/store-layout.toml (store-layout.sh) on the laptop (direct cable), linux fork 6ee9501832af: render_pb_pages 0x28, 0x23 and 0x30, sgxfive-test tri --keep-overflow --tri-full --tri-z with the depth ramps of E465 and the buffer filled with 0xdeadbeef, at G = 33 (control 0x0017110c) and G = 1 (0x0017100c), the stored dwords decoded and counted on the laptop (python3); one pass of each pb and G, the GPU reset before each pb size (not before each G); each dataset ran once, after one run by hand of the script (outside the data) that had no G = 1 comparison, the two tile orders being added after it, and the choice of the first macrotile last was made from the zeros seen; the dataset holds output.txt, kernel.log, env.toml and the script and no raw dumps, so the counts are the script's own at run time and cannot be recomputed from the stored data"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["zls-store-layout"]
terms = ["CR_ISP_ZLSCTL", "Parameter Buffer (PB)", "Dynamic Parameter Management (DPM)"]
+++

**What runs.** The full-screen ramp triangle of E465 on a context whose parameter buffer is too
small for the scene (`render_pb_pages`), so that the job overflows and returns -ENOSPC with its
context kept (`--keep-overflow`): partial renders store and the final render ends the job. The ZLS
store is the clearing control with G = 33 (no two tiles share an address) and, for a second job, G
= 1 (the library's pitch, E461). The depth buffer is read back after each job and decoded as in
E465 (the sign bit cleared before decoding).

**G = 33.** At each of 0x28, 0x23 and 0x30 pages the printed counts are the same: 797696 dwords,
of which 184320 are zero, 602112 have the sign bit set and none is positive. Every one of the
602112 dwords with the sign bit set decodes, with the sign cleared, to the pixel whose address
E465 gives it (0 not at the rule's address). The zeros are the tiles of tile rows 0 to 11: 336
tiles are all zero and 48 (tile columns 6, 14, 23 and 31, in the 12 rows) are half zero; the other
1152 tiles (rows 12 to 47) are all non-zero and negated. That the 48 half-zero tiles lie one per
column per row and hold 256 zeros each is by subtraction (184320 - 336 * 512 = 12288 = 48 * 256);
the script prints only their count and the 4 columns. If the library's macrotiles are 4 x 4 of 8 x
12 tiles at this size (the library's geometry, not in this data), rows 0 to 11 are the first row
of macrotiles. A further 11264 stored dwords (value not tabulated; 22 slots of 512 if whole, in
the 2 slots each of the 48 tile rows has beyond its 32 tiles, 96 slots) lie where a job that does
not overflow leaves nothing (E465: slots observed equal predicted). The tiles below are the ramp
negated, as E461's -1.0 and -0.5 are the 1.0 and 0.5 of its z = 0.5 triangle with the sign set
(E461, not this data).

**Against E461 at 0x30 pages.** E461's z = 0.5 triangle at 1024 x 768 in 0x30 pages (control
0x0017100c, G = 1) keeps the whole-buffer values behind its leading zeros (47018 x 1.0 and 2390 x
0.5, positive; E461 took it as the one-partial-render case [infer]) and sets the sign only from
0x28 pages down. Here the ramp job at 0x30 pages (G = 33) negates every non-zero dword (602112 of
602112, none positive) as at 0x28 and 0x23. The two disagree and the data does not explain it. The
scenes differ (a ramp over the whole target against the z = 0.5 triangle of 207456 pixels, and G =
33 against 1), and how many partial renders each job made is not known; it is open (Q107) [infer:
nothing shows that the number of partial renders is the reason].

**G = 1.** The aliased job stores 64512 dwords. Writing the G = 33 job's tiles at the pitch-two
addresses in raster order leaves 2816 (0x28, 0x23) and 4096 (0x30) dwords different; writing the
first macrotile's tiles (tile columns 0 to 7 of rows 0 to 11) last leaves 512 (0x28, 0x23) and
1536 (0x30) different. So the stored tiles of an overflowed job are nearly the no-alias tiles in
raster order with the first macrotile written after the rest [infer: two orders tried, the
remainder not explained; the second order was chosen after the zeros were seen]. The first 15104
dwords of E461's window (zeros) would then be the first macrotile's tiles that no later tile
overwrote [infer: not computed from the tiles' addresses].

**What it shows.** What the final render of an overflowed job stores is the whole depth buffer
with tile rows 0 to 11 zero and every other tile with the sign bit set. The sign bit is not
explained by the control these jobs ran with: bit 19, which stores the float negated (E466), is
clear in 0x0017110c and 0x0017100c, and bit 1 is clear too, so there was no load, and a load
clears the sign, it does not set it (E467). So the sign bit is set by something the control word
does not show, probably the partial-render path [infer]. The zero rows and the half-zero tiles fit
macrotiles whose geometry came before the last partial render being stored without a depth
[infer].

**What it does not show.** Whether the final render loads the partial renders' depth (Q038): the
controls of every job here had bit 1 clear (no load) and bit 19 clear, and no case with a load or
with bit 19 was run, so whether either changes the zeros or the sign is not shown; why the 0x30
job differs from E461's (above); the depth test across partial renders with overlapping triangles;
what the extra 11264 stored dwords beyond each row are and what writes them.
