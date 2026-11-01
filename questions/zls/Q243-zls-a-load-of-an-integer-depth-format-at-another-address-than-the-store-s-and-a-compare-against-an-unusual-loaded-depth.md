+++
id = "Q243"
question = "what does the ZLS load do with an integer stored format (bits 26:24 = 1 or 2), at an address other than the one the store writes, and when the loaded depth is a NaN or infinity or is compared with a depth equal to it?"
unit = "zls"
kind = "hw"
value = "low"
phase = 12
evidence = ["E467", "E628", "E664"]
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
