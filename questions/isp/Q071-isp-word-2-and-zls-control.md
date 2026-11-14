+++
id = "Q071"
question = "what do the bits of the ZLS control word that change nothing seen (12, 15, 16, 20 to 23, 27 to 31) do, alone and set together, what does bit 0 store with a control other than 0x0017100c, and how does the ISP use the control in a render with a stencil test?"
unit = "isp"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E057", "E169", "E216", "E228", "E284", "E337", "E411", "E465", "E466", "E467", "E665",
            "E989", "E997", "E1014", "E1030", "E1042", "E1053", "E1063", "E1069"]
terms = ["CR_ISP_ZLSCTL", "CR_ISP_BGOBJVALS.STENCIL", "ISP2"]
+++

ISP word 2 is answered (E284): its compare (27:25) with the eight relations, the compare mask
(15:8), the write mask (7:0) and the operations on stencil fail (24:22), depth fail (21:19) and
pass (18:16), each 0 keep, 1 zero, 2 replace, 3 and 4 increment and decrement clamped, 5 invert, 6
and 7 increment and decrement wrapping; bits 31:28 change nothing.

The control word is now read bit by bit (§11.5 of 3d.md): bit 0 completes the job with no pixel
(E057), bit 1 turns the load on with bits 13 (stencil) and 14 (depth) choosing what (E467), bit 2
the stores, bits 17 and 18 the stencil and depth stores, bits 11:3 the tile pitch minus one
(E465), bit 19 the negated float and bits 26:24 the stored format (E466). E411's pages changed by
bits 3 and 4 and its faults with bits 5 to 11 set fit the pitch running out of the scratch buffer
(E465's derivation by hand; no fault was reproduced) [infer].

What is open: bits 12, 15, 16, 20 to 23 and 27 to 31 change nothing seen in the stores of E411 (one
flip each of 0x17100c, two runs, on a 64 x 64 target: bits 12, 16 and 20 cleared, bits 15, 21 to 23
and 27 to 31 set; not tried with bit 1, a stencil test, formats 1 to 7, a larger target or a partial
render; E466 varies only bits 26:24, 19, 2, 17 and 18, E467 bits 1, 13 and 14). Bit 12 and bit 16
are set in the window-surface controls of the closed driver (0x0017100c, 0x0017700e), so they may
matter to a stage this setup does not reach; E337's control for a texture's depth attachment,
0x00140008, has both clear. Also open: the stencil test against a stencil the render loaded (Q121).
The stored formats 3 to 7 are Q120; bit 19 with the integer formats changes no dword on any route
that ran (E490, E981, E987; the viewport's word 10 is Q069's). To settle it: the same ramp stores
with each of those bits flipped in a render with a stencil test and a loaded stencil, the pitch and
format fields set so that the stored dwords are readable.

Folded here 2026-11-12 (round 6 housekeeping, decision R6-1 a): Q244 asked the same control bits
(12, 15, 16, 20 to 23, 27 to 31) set in combination, and bit 0 under another control; both fit
this question, and its evidence (E665) moves here. E411 flipped each bit of 0x0017100c once: bits
1, 12 to 16, 20 to 23 and 27 to 31 left the image and the stored pages as the control's; the closed
driver sets 12, 16 and 20 in every value (E337). The pipeline simulator (E665) ignores those bits
as the single flips showed and models bit 0 as E411's raw output shows it: with 0x0017100d (two
runs) the colour image is not written (4096 of 4096 pixels keep the sentinel) and the stored pages
are the control's (page 4 and pages 12 to 15, 5120 dwords, the same first values); the image and
the depth and stencil store are different things. Bit 0 with any other control was not run and
refuses. To settle it, besides the runs above: the control with several of these bits set
together, and bit 0 with other controls (the formats, the load bits, another pitch), with the
depth and stencil dumps kept and the image counted.

Narrowed 2026-11-13 (r10-x, E997). Bit 0 stores the depth as without it and writes no colour pixel
under formats 0, 1 and 2 at G 2 and with the depth load (4 of 4 held out). Bits 15, 21 to 23 and 27
to 31 set together change nothing; bits 12, 16 and 20 cleared together keep the values and counts
but store a linear image of the tile area, rows of 32 (G + 1) dwords (post hoc, 4608 of 4608 by the
x each value names). Open: which of bits 12, 16 and 20 selects the linear layout and its rows' y,
what the load reads under it, and the stencil test against a loaded stencil (Q121's stage).

Narrowed 2026-11-13 (E989, with E988's stencil test). Under a stencil test against a loaded stencil
(control 0x0017300e, E988), flipping bits 15, 21 to 23 and 27 to 31 (set) and 12, 16 and 20
(cleared) together makes the test read 0, not the loaded byte: every EQUAL-to-0 test passed and its
invert stored 0xff at every byte, while the depth dump and the loaded buffer stayed the base rows'.
So these bits are not all inert. Open: which of them does it (a flip of each under the same test),
and what they do to the depth path.

Narrowed 2026-11-13 (round 11 offline, decision R11-5 a; E1014, E997's correction). Under E989's
control the stencil test reads 0, not the loaded buffer at a linear offset: frozen before the rows
were read, H-ZEROLOAD held 2 of 2 and three linear load maps and E988's twiddled order failed 2 of
2, so E989's reading stands and "the load is linear too" is refuted. E997's linear store is ordered
in y as well (dword 96 y + x equals the twiddled control at (x, y), 4608 of 4608 in its three rows,
post hoc): its rows are named. No kept row clears a strict subset of bits 12, 16 and 20. Open:
which of them makes the store linear and which stops the stencil read (each bit and each pair
under E977's ramp store and E988's stencil test), and whether a depth load under them is linear.

Narrowed 2026-11-13 (r13-zls, E1030). Of bits 12, 16 and 20 cleared alone and in pairs, bit 16 alone
makes E977's ramp store E997's linear image (6 of 6 held out, byte for byte), and none of them makes
the stencil test read 0 (E988's 1024 drawn on all six); the set half (15, 21 to 23, 27 to 31) alone
does (2048 drawn, every stored byte 0xff, 7 of 7 held out). Post hoc, bit 12 cleared makes the
stencil load read a linear image of 64-byte rows and bit 16 cleared makes the stencil store one;
bit 20 changes nothing seen. sgx-pipe models bit 16's depth store and these stencil sources. Open:
which bit of the set half reads 0, the linear stencil images' rows at another pitch, bit 12 or 16
with a depth load, bit 20, and bit 0 under other controls.

Narrowed 2026-11-14 (r14-zls, E1042). No set-half bit alone makes E988's stencil test read 0 (no
frozen single-bit or group model held all 11 rows): bits 21 to 23 together do (2048 drawn, every
stored byte 0xff), 21, 22 and 27 to 31 alone and 27 to 31 together change nothing; post hoc bit 15
alone fails the test at every pixel and bit 23 alone has it read a value of x mod 16, not the loaded
byte. The linear images of bits 12 (the loads) and 16 (the stores) have rows of 32 (G + 1) units:
the stencil's bytes (P-G 4 of 4 at G 2), the depth load's dwords (H-DEPTH-LIN, bit 12 with a depth
load) and, in the 16-bit format, halfwords (L16-HALF). Open: what bits 15 and 23 alone do, 21 or 22
paired with 23, bit 0 under other controls, bit 20, and the ISP's use of the control.

Narrowed 2026-11-14 (r15-zls, E1053). E1042's post hoc forms held out: bit 15 alone fails E988's
stencil test at every pixel, the loaded byte kept (96 x 32 G 2 and against reference 1, H15-FAIL 2
of 2), bit 23 alone reads one of 0x3f, 0x80 and 0 by x mod 16 whatever was loaded (96 x 32 G 2 and
the index fill, H23-MOD16 2 of 2), and 21 or 22 with 23 read 0 as the three together do
(H-PAIR-ZERO 2 of 2). sgx-pipe's `stencil_source` models them. Open: why bit 23 reads those bytes,
bit 0 under other controls, bit 20, and the ISP's use of the control.

Narrowed 2026-11-14 (r16-zls, E1063). Bit 0 stores the depth and stencil as without it and writes
no colour with a loaded stencil too (E988's row, bit 16 cleared, formats 6 and 7: H-B0 4 of 4 held
out). Bit 23's bytes do not follow the reference, the compare mask or the background stencil
(H23-FIXED 3 of 3). Bit 20 cleared changed nothing at 640 x 480 in format 0 nor with bit 12 cleared
and a depth load, but in formats 6 and 7 it moved the stored per-tile records, packed one after
another from dword 2048 (post hoc, one size; H-INERT20 failed 2 of 2). Open: where bit 23's bytes
come from, bit 20's packed records at other sizes and formats, and the ISP's use of the control.

Narrowed 2026-11-14 (r17-zls, E1069). Bit 20 cleared in formats 6 and 7 packs the per-tile records
from dword 2048 at 96 x 48 G 2 and 128 x 64 G 3 too, the twin's records in address order (H-PACK2048
3 of 4 held out, the fourth by a record gathering the frozen rule got wrong; the end of the last
slot and an offset scaling with the pitch failed 4 of 4). Open: where bit 23's bytes come from, bit
20 in formats 3 to 5 and with an overlapping pitch, and the ISP's use of the control.
