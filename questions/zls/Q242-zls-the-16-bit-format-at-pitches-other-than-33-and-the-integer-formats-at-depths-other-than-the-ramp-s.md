+++
id = "Q242"
question = "which pixel's value does a dword shared by two overlapping tiles hold, what do the integer formats store past the target at an odd width or height, and why did E411's G 3 job store past its 16-page buffer (pages 16 and 18) without the fault G 5, 9 and 17 met (the formats' values over 0 to 1 and past an 80 x 40 target are E977's and E991's floor rule)?"
unit = "zls"
kind = "hw"
value = "low"
phase = 12
evidence = ["E466", "E490", "E663", "E977", "E411", "E465", "E991", "E996", "E1041"]
terms = ["CR_ISP_ZLSCTL"]
+++

The pipeline simulator (E663) stores the 24-bit format as round(z * 0xffffff) and the 16-bit one as
that shifted right by 8, two rows to a dword at 256 dwords a slot, and refuses everything the dumps
did not cover: a 16-bit store at a pitch other than G = 33 (the layout was derived at G = 33 only,
E490), any integer format over a depth other than 0.25 to 0.4166 and 1.0, a store whose tiles
overlap (a pitch under the tiles of a row: E465 counted the dwords written there and recorded
no values), and, in E411's 16-page scratch arrangement, a pitch G above 3 (bits 5 to 11 of the
control set: the jobs faulted, read as the pitch running out of the buffer, [infer]).

The depth of the format runs lies in 0.25 to 0.4166 (the f0 dumps hold 0.250081 to 0.416585; the
clear value 1.0 is stored by E411's two rows). Four rules were tried on the 786432 dwords of the
24-bit run: floor and ceil of z * 0xffffff differ, round(z * 0xffffff) and floor(z * 2^24)
clamped to 24 bits both give 0 differences. They agree over the range above and differ for most
depths from 0.5 up, so the dumps do not choose between them there.

What would settle it: the format runs of E466 repeated with the depth ramp over 0 to 1, at two or
three other pitches, with the 16-bit format at G of 0, 1 and 511, a target with edge tiles, and
tiles that overlap with a per-tile marker; a scratch run with a buffer longer than the pitch needs;
the dumps kept.

Status: open.

Narrowed 2026-11-13 (E977). The 24-bit format stores min(floor(z * 2^24), 0xffffff) and the 16-bit
one its >> 8, held out over 0 to 1 at G 7, 9 and 2 and on a target with edge tiles (within the
target); round(z * 0xffffff) fails from 0.5 up (E466 and E490 corrected), and E490's 16-bit layout
holds at those pitches. Open: the values past the target in edge tiles for the integer formats,
which pixel a dword shared by overlapping tiles holds, and E411's faults with G past 3.

Narrowed 2026-11-13 (round 10 offline, decision R10-1 a, E991). Past the target of E977's 80 x 40
job (G 2, tiles of 96 x 48) the integer formats store the floor rule of the float the same pixel
stores in format 0 (E831's band and the background 1.0): 1408 of 1408 dwords in format 1 and 704 of
704 in format 2, frozen before the read, against 0 for the fill left and 832 and 683 for the rounded
rule; sgx-pipe stores the integer formats at an edge of an even size by it. E465's address rule
recomputed for E411's 64 x 64 scratch arrangement gives E411's stored pages up to the first page
past the 16-page buffer each faulting row reaches, and E977's G 7 and 9 with a buffer sized to the
extent did not fault, so the extent past the buffer faults the job, not the pitch field [infer]; the
misfit is G 3, whose tile rows 2 and 3 land on pages 16 and 18 without a fault. Open: which pixel a
dword shared by overlapping tiles holds (the round 10 ranking plans stage zov), the integer formats
at an odd width or height (their float band is rule A, E885, E903; not run in an integer format),
and what lies past page 15 in E411's arrangement.

Narrowed 2026-11-13 (r10-x, E996). A slot shared by overlapping tiles holds the 512 dwords of the
tile the 3D visits last in the region header order (macrotiles column-major, 4 x 4-region blocks
raster inside): 5 of 5 held out pitches at 64 x 32 to 256 x 64 and format 1 at 64 x 32 G 0, every
shared dword, no slot mixed; the raster order fails where it parts from the header order. Open: the
integer formats at an odd width or height, what lies past page 15 in E411's arrangement, and an
overlapping store with edge tiles or four macrotiles a side.

Narrowed 2026-11-14 (r14-zls, E1041). Past odd targets (63 x 31 at G 1, 65 x 33 at G 2) formats 1
and 2 store the floor rule of the float the same pixel stores in format 0 at every dword of the edge
tiles (INT-FLOOR-EXT 4 of 4 held out); an overlapping store holds the tile the 3D visits last in
region header order with edge tiles (65 x 33 at G 1) and at four macrotiles a side (640 x 480 at
G 2; H-LATE/HDR 2 of 2, raster order failed where it parts); E411's G 3 arrangement with 20 pages
stores tile rows 2 and 3 on pages 16 and 18, 1024 dwords each, as E465's rule puts them
(H-NEXTTILE); the control passed. sgx-pipe stores the integer formats at odd sizes and the float
format's overlaps with edge tiles and four macrotiles a side, replaying the kept rows. Every clause
of the question line is decided by held-out rows with a passing control: proposed for retirement as
answered by E1041 (R14-6 (a), [infer], the lead to confirm). sgx-pipe's refusals that still cite
Q242 (overlaps in the 16-bit format and in the 24-bit one with edge tiles or four macrotiles,
integer values outside 0 to 1) would move to a question of their own on retirement.
