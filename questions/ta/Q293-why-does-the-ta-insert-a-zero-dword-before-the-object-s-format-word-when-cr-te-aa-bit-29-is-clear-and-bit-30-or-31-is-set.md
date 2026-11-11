+++
id = "Q293"
question = "why does the TA insert a zero dword between an object's line widths and its format word (dword 11 of the parameter buffer) when CR_TE_AA bit 29 is clear and bit 30 or 31 is set, which leaves the image empty because the 3D reads the zero as the format word"
unit = "ta"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E728", "E829"]
terms = ["CR_TE_AA", "Parameter Buffer (PB)", "PB_OBJ.FORMAT"]
+++
Split on 2026-11-11 from the TA side of a retired question answered by E829. E728: with
`CR_TE_AA` bit 29 clear and bit 30 or 31 set (0x40, 0x80, 0xc0, at 64 x 64 and 128 x 128, modes 0
and 2) the TA data equals the bit-29-set job's, and in the parameter buffer the object's format
word, set masks and packed vertices (PB_OBJ.FORMAT, SET_MASKS) sit one dword later, after a zero
dword at 11 inserted after the line widths (PB_OBJ.LINE_WIDTHS, dword 10). TE 0x20 equals 0x00, so
the shift appears only when bit 30 or 31 is set. E829: the 3D reads the object in the bit-29-set
layout (the twin's words poked into dwords 11 to 26 drew the twin's picture, 0xffffffff at dword 11
drew nothing), so the zero is what leaves the image empty.

Open: what the TA's extra dword is for (a field of a layout the TA writes for bit 29 clear that the
3D does not read in this configuration, or a TA behaviour the closed stack never selects), whether
the 3D reads the displaced layout under some other setting (another ISP or 3D register, or the
four-array layout of a context made for 4x targets), whether render 2's own object is read the
same way (not drawn in E829's jobs), and what other values at dword 11 do. Related: Q030 (the TE
bits).
