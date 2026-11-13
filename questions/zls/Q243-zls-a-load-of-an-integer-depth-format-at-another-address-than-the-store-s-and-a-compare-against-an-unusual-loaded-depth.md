+++
id = "Q243"
question = "what does the ZLS load do with an integer stored format (bits 26:24 = 1 or 2), at an address other than the one the store writes, and when the loaded depth is a NaN or infinity or is compared with a depth equal to it?"
unit = "zls"
kind = "hw"
value = "low"
phase = 12
evidence = ["E467", "E628", "E664", "E977", "E995"]
terms = ["CR_ISP_ZLSCTL", "CR_ISP_ZLOAD_BASE", "CR_ISP_ZSTORE_BASE"]
+++

E467 ran the load with the float format and with one load and one store buffer each for depth and
stencil, each tile read at the index it is written; E664's model refuses everything else: a load
with an integer format, a load at an address that is not the store's (the load and store bases are
two registers, E058), and a compare where the loaded dword is a NaN or an infinity (0x7fffffff or
0x7f800000 after the sign is cleared; a pass under the test never only copies it, as E467 saw). The
compare against a loaded depth within 3 units of the triangle's is refused with Q200.

What would settle it: the load run with the formats 1 and 2 (the stored dumps kept), with the load
base moved by a tile and by a page from the store base, and with loaded NaN and infinity patterns
under the depth test less; bit 19 with a load, and a triangle depth other than 0.5.

Status: open.

Note 2026-11-11 (E831). The band of the store past the target (E831) was measured without a load:
`sgx-pipe`'s pass over a target with edge tiles refuses here, since what a load and the pass hold
past the target is not measured. To settle it: E467's load run at 34 x 18 with the dumps kept.

Narrowed 2026-11-13 (E977). A load of format 1 or 2 is compared as the stored dword's float
(0x00400000 fails less against 0.125, 0x3fff3fff passes less against 0.5), and a loaded NaN passes
less and fails greater against 0.5 while infinity follows IEEE: every load row matches an unsigned
compare of the bit patterns [infer]. Open: a load at another address than the store's, other compare
modes against NaN and equal depths.

Narrowed 2026-11-13 (r10-x, E995). A loaded depth enters the compare with its sign bit cleared:
-0.25, -0.75 and -0.0 act as 0.25, 0.75 and 0, and NaN as a value above every depth, under the
compares 1, 2, 3, 4, 5 and 6 (14 of 14 held out, the raw unsigned compare refuted on 4); E977's
[infer] is corrected to it. Open: a load at another address than the store's (the moved load base).
