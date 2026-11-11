+++
id = "Q293"
question = "why does the TA insert a zero dword between an object's line widths and its format word (dword 11 of the parameter buffer) when CR_TE_AA bit 29 is clear and bit 30 or 31 is set, which leaves the image empty because the 3D reads the zero as the format word"
unit = "ta"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E728", "E829", "E847"]
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

Note 2026-11-11 (round 4, an offline scan of 34 kept parameter-buffer dumps of four sessions: rg-pb,
k-pb0, r4's a-pb and a-pb0, and E824's k-f4; [data] for the counts, no new measurement). With
`CR_TE_AA` bit 29 clear and bit 30 or 31 set (0x40, 0x80 and 0xc0; 15 jobs at 64 x 64 and 128 x 128,
modes 0 and 2) dword 11 is 0 and the format word 0x00040101 is at dword 12. It is an insertion, not
a swap: against the 0x20 job, 0x40 and 0x80 differ in 89 dwords and everything from dword 11 sits
one later, the object growing from 26 to 27 dwords. The ten four-array 4x dumps (0xe0, bit 29 set)
have the format word at dword 11. All 15 jobs are the tool's one triangle, so whether the inserted
dword is always zero cannot be read from them; the planned rows (other values of the dword by poke,
render 2's own object, the four-array layout with bit 29 clear) are not run.

Note 2026-11-11 (round 4, session R4-render4x stage t, E847; not narrowed by a frozen verdict).
Frozen verdict: cannot tell, the two baseline controls NODATA: the scorer reads a job's dump as
`NAME.tri.param.bin.gz` and the probe rows (the 11.31 line and point) kept theirs under the
program's name, so it compared nothing for them (a naming mismatch of the session, not a
hardware result). The control t6 passed, and on a context made for 4x targets `CR_TE_AA`
0x40000000 and 0x80000000 gave dword 11 = 0, the format word at 12 and an empty image, as on one
array (rows held, gated). Read after the run with the frozen insertion check and predictions
[post hoc]: the baselines equal their frozen heads, and 0x40000000 inserted one zero dword right
before the format word of the line (dword 9) and of the point object (dword 11), both images then
empty, so the dword is zero for objects with a width too [infer: padding]. A frozen run of the
line and point rows with the dump name fixed in the scorer would make this a held-out result;
still open: other values at the dword, render 2's own object, a setting that makes the 3D read
the displaced layout.
