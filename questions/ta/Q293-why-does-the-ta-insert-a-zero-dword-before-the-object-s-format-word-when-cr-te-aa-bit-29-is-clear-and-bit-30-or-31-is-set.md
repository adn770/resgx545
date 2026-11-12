+++
id = "Q293"
question = "with CR_TE_AA bit 29 clear and bit 30, 31 or both set the TA inserts one zero dword right before the format word of a triangle, line or point object (E728, E847, E865, E888), and the 3D reads whatever that dword holds as the format word and draws nothing (E829, E888): what does the TA write for render 2's own object, and how does the 3D read it"
unit = "ta"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E728", "E829", "E847", "E865", "E888", "E897"]
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

Narrowed 2026-11-12 (round 5, session R5-render4x stage t, E865; the question text above is the
narrowed one). Frozen verdict, 6 of 6 rows decided, every control passed (E827's row, the unpoked
11.31 line and point): the dword the TA inserts is zero and sits right before the object's format
word, at dword 9 of the line and dword 11 of the point with 0x80000000 (held out) as with 0x40000000
(E847's post hoc reading, replicated), and at dword 11 of the triangle on a context made for 4x
targets with both values, the image empty in every case. H-FIELD (a non-zero field) was not seen;
[infer] the dword is padding the TA writes in this configuration. So the dword is zero for every
object kind the tool draws, at both values and whatever the region-header array count (settled by
E865). Open: whether any register makes the 3D read the displaced layout, 0xc0000000 on a line or a
point, a non-zero value poked into the dword, render 2's own object.

Reworded 2026-11-12 (round 6 housekeeping, decision R6-1 a; section 5 of the round 6 render4x
plan) to its bounded items. Whether some setting makes
the 3D read the displaced layout has no finite test (any ISP or 3D register, in any combination)
and is not pursued; the question keeps the three items a run can settle, with the four rows the
plan offers: t5 and t6, `CR_TE_AA` 0xc0000000 on the 11.31 line and point (predicted: one zero
dword before the format word, at 9 and 11, and an empty image, as with 0x40000000 and
0x80000000); t7, the 0x40000000 triangle with a non-zero value poked into dword 11 (predicted: an
empty image, the 3D reading it as the format word as in E829); t8, the round 5 control of stage t.
Render 2's own object is not among them.

Narrowed 2026-11-12 (round 6, session R6-render4x stage t, E888; the question text above is the
narrowed one). Frozen verdict, 3 of 3 rows decided, the control (E827's row) passing: with
`CR_TE_AA` 0xc0000000 the TA inserts one zero dword right before the format word of the 11.31 line
(dword 9) and point (dword 11) and the image is empty, as at 0x40000000 and 0x80000000 (held out);
on the 0x40000000 triangle 0x00000001 poked into the inserted dword 11 of render 2 (applied, the
format word at 12) drew nothing, so the 3D reads a non-zero value there as the format word too, as
E829's 0xffffffff (held out). Answered: 0xc0000000 on a line and a point, a non-zero value in the
dword. Open: render 2's own object, the one item the plan's rows did not run.

Note 2026-11-12 (round 7, offline, E897; post hoc, not narrowed by a frozen verdict). The kept
dumps of the two-render rows already hold render 2's own object: in 13 of 13 at 0x40000000 it
starts at dword 27 with a zero at its dword 11 and the format word at its dword 12, the layout of
render 1's object, and in the 11 jobs whose render 1 object stayed displaced render 2 drew no
pixel of its full-target triangle. Not separated: whether the 3D skips render 2's object for its
own zero or stops at render 1's displaced object first (every empty job had both displaced). The
plan's held-out rows (closing7/a/exp-pixel-r7.md section 3.5: three renders, pokes into render 2's
object only) would answer the item; until they run, it stays open.
