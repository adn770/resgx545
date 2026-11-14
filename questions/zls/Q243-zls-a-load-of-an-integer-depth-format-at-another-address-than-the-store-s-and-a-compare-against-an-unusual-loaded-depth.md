+++
id = "Q243"
question = "what address does the ZLS load read from when its base (render details dword 12, and dword 14 for the stencil) is not the store's, and with an integer stored format (bits 26:24 = 1 or 2) there?"
unit = "zls"
kind = "hw"
value = "low"
phase = 12
evidence = ["E467", "E628", "E664", "E977", "E995", "E1029", "E1040"]
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

Narrowed 2026-11-13 (r13-zls, E1029). A load at another address than the store's reads E465's
layout from the poked base (render details dword 12): moves of a tile, a page, 16 and 64 KiB and
onto the store's own buffer all held out (the frozen H-MOVED, 6 of 7; the store's base and the
unmoved base refuted), but a base 4 bytes off loaded as the unmoved one while 64 bytes moved it
(post hoc: the base rounded down to 8, 16, 32 or 64 bytes). Open: that granule (a base moved by 8,
16 and 32 bytes), and the moved base with an integer format or a moved stencil load base.

Text fix 2026-11-14 (round 14, decision R14-7 (a)). The question line drops the integer-format
compare, NaN, infinity and equal-depth clauses, answered by E977 (an integer load compares as the
dword's float) and E995 (the loaded depth enters the compare with its sign cleared, NaN above every
depth, under every compare); what stays is the moved base and an integer format at it.

Narrowed 2026-11-14 (r14-zls, E1040). The depth load base is rounded down to 16 bytes: frozen G16
held 5 of 5 held-out moves (+8 unmoved; +16, +32, +0x1008, +0x1020 moved), and with E1029's moves
no other granule of 4 to 128 bytes fits; formats 1 and 2 loaded from a base moved by a page read
E465's 32-bit layout from it, each dword a float (I-MOVED-L32 2 of 2), and the stencil load base,
dword 14, moved by a page moves the stencil load (S-MOVED, 2048 of 2048 bytes); every control
passed. sgx-pipe models the base (`zls::load_base`). Every clause of the question line is now
decided by held-out rows with passing controls: proposed for retirement as answered by E1040
(R14-6 (a), [infer], the lead to confirm). sgx-pipe's refusals that still cite Q243 (a load pass
over edge tiles, bit 19 with a load) would move to a question of their own on retirement.
