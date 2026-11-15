+++
id = "Q088"
question = "what reads the render details' unpatched ZLS control word that the closed driver writes between frames (0x0011700a), now that bit 14 is known to load the depth and bit 13 the stencil?"
unit = "zls"
kind = "fw"
phase = 11
evidence = ["E335", "E336", "E337", "E411", "E467", "E665", "E997", "E989", "E1014", "E1081", "E1083", "E1088", "E1093", "E1094"]
terms = ["CR_ISP_ZLSCTL", "hw_render_details.isp_zlsctl"]
+++

The hardware part of this question is answered (E467): with bit 1 the load is on, bit 14 loads the
depth and bit 13 the stencil, each from the address the store writes, the loaded depth takes part
in the depth test and its sign bit is cleared. E411 had found that bits 13 and 14 act only with bit
1 and that the loaded sentinel 0xdeadbeef came back as 0x5eadbeef; E467 shows which bit loads what,
with a stencil buffer of its own.

The closed driver's first render of a window surface stores depth and stencil with `CR_ISP_ZLSCTL`
`0x0017100c`; every later render, cleared or not, has `0x0017700e`, bits 1, 13 and 14 added, and
`ExternalZBufferMode=2` gives `0x0017300e` (1 and 13, not 14) from the context's setup (E335,
E337). Every window render has both ZLS render flags, so no capture parts depth from stencil.
Between frames the driver also writes `0x0011700a` into the render details' own word, which the
next render's 3D patch overrides (E336); no captured kick shows what reads it (a partial render's
reload is a candidate).

What is open is the closed firmware's or driver's behaviour, parked as kind fw: what reads the
unpatched word. Whether the final render's reload loads the depth at all is the hardware question
of Q038, not this one. To settle it: a scene that runs out of parameter memory with the render
details' word poked to a marked value, to see whether the partial render's reload takes it (the
same job answers the reload half of Q038; the tile pitch and the stores of E465 make the marked
word readable now).

Round 12 cites, context for the word's bits: E665 (the ZLS control fields decoded), E997 and E989
(bits E411 flipped singly, flipped together), E1014 (the stencil test under E989's control reads 0).

Narrowed 2026-11-14 (r19-dpm, E1083 and E1081). A partial render stores with the ZLS control word
its own kick carries (the render details' word as set per render): the G of render 1's word lays
out the partial render's store, not the final's nor a constant (H-RD 6 of 6, G 33 and G 1 both
ways, at 0x28 and 0x30). The load half is not decided: after a kick that was not raised the final
loads only with its load bits, after a raised one it leaves a separate store untouched (E1081, no
frozen form held on all rows), so the word stays parked as fw (R19-5's retirement needed both).
Open: what reads the closed driver's unpatched word between frames.

Narrowed 2026-11-15 (r20-zls, E1088). With the host's 0.25 refill of the load buffer between a
raised kick and a moved final, no frozen reload form held (H-LOADBASE, H-STOREBASE, H-NOSTORE,
H-HOSTBITS 0 of 7): post hoc the final stores the load buffer's 0.25 to the store buffer outside a
65536-dword zero region of tile rows 0-11, raised or not when it has load bits, so E1081's untouched
store was the loaded indices written back; the raised partial render stores the loaded buffer and
no triangle depth. The ZLS registers read during each render (post hoc, the frozen zregs control
failed: 0x0484 and 0x0488 hold the offsets rd:12 and rd:13): 0x0480 = rd:11 with bits 14 and 19 set
during the partial renders, bits 14 and 15 after them. Not retired (R20-2 a needed a frozen form);
open: the zero region, bit 15, and what reads the closed driver's unpatched word.

Narrowed 2026-11-15 (r21-zls, E1093 and E1094). What reads the word: for every render of a kick
the firmware loads CR_ISP_ZLSCTL from the render details' word and ORs bits 14, 18 and 19 into it
for each partial render (rd:11 | 0x000c4000, H-PRMASK 10 of 10 held out, E336's 0x0011700a read as
0x001d700a raised or not; E1094). The reload half after a raised kick: with the load buffer
refilled at 0.75 the final writes the load buffer back to the store and draws no triangle depth,
load bits or not (H-LOADNOTEST 4 of 4, H-LOADTEST 0 of 4; E1093). After a kick that was not
raised the final follows its word without load bits (H-HOSTBITS 2 of 2), but with load bits
H-HOSTBITS failed (0x2e: the loaded 0.75 written back, T2 not drawn, as after a raised kick; post
hoc). Not retired (R21-2 a needed every clause decided by held-out rows): open, the not-raised
load clause as a frozen form (whenever the final loads, it draws no triangle at z 0.5 against a
0.75 load [infer]) and why; the zero region (Q107); bit 15 after the partial renders; what the
closed driver means the unpatched word for between frames.
