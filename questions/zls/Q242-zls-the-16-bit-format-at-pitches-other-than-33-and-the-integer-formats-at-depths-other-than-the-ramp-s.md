+++
id = "Q242"
question = "which pixel's value does a dword shared by two overlapping tiles hold, what do the integer formats store past the target at an odd width or height, and why did E411's G 3 job store past its 16-page buffer (pages 16 and 18) without the fault G 5, 9 and 17 met (the formats' values over 0 to 1 and past an 80 x 40 target are E977's and E991's floor rule)?"
unit = "zls"
kind = "hw"
value = "low"
phase = 12
evidence = ["E466", "E490", "E663", "E977", "E411", "E465", "E991"]
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
