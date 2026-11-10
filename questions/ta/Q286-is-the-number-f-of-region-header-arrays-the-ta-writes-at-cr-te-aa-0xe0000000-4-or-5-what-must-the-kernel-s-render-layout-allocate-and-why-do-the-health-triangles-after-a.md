+++
id = "Q286"
question = "is the number f of region-header arrays the TA writes at CR_TE_AA 0xe0000000 4 or 5, what must the kernel's render layout allocate, and why do the health triangles after a 4x fault fault again"
unit = "ta"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E729", "E507", "E504", "E762", "E763"]
terms = ["CR_TE_AA", "CR_ISP_MSAA"]
+++
E729: f in {4, 5} (f = 3 and f >= 6 refuted; fault behaviour cannot separate 4 from 5). After each
failed 4x job the next one or two plain 64 x 64 triangles faulted too (pages 0x20006 to 0x20008)
before a reset recovered the GPU, with "SGX recovery failed: -110" and "render context cleanup
failed, resetting" in the log. To settle it: a completing size (256 x 160) with a TA data dump
read for the number of header arrays (the TA's pointers at the end of the stream), and a kernel
layout with f = 4 and f = 5 at 288 x 144, 256 x 288 and 384 x 384; for the recovery, the kernel's
cleanup path after a BIF fault in a render.

Status: open. Narrows Q140 (the fault page and the sizes that complete).

Analysis of the dumps of E728, 2026-11-09 (existing data, not a new measurement). The 11 TA data
dumps of msaa-b-te29 (24576 bytes each, region headers from 0x4000 in arrays of 0x300 bytes, 64 x
64 and 128 x 128) hold, in non-zero dwords per array: TE 0x20 one array (72); 0x40 and 0x80 two
(80 or 128, then 64); 0xc0 and 0xe0 four (96, 64, 64, 64 at 64 x 64; 128, 128, 64, 64 at 128 x 128
in mode 2). Each of bits 30 and 31 doubles the count, 1, 2, 4. Nothing is written in the fifth
slot (0x4c00) or past it in any of the 11 dumps, and the part below 0x4000 is zero in all. So f =
4 by what the TA writes at CR_TE_AA 0xe0000000. This does not show that the TA touches no fifth
array: a fifth array read and not written would fault the same way, and E729's fault formula needs
f >= 4 only. Sufficiency (a layout with exactly four arrays completes at the sizes that fault) is
untested, so the question stays open on f = 4 against 5. The other clause, why the health
triangles after a 4x fault fault again, is recovery of our kernel (E729's contamination note) and
not hardware behaviour; it is not split off here.

Post hoc note, S3 (2026-11-10, dataset render-closing-s3; the question is unchanged: the frozen
verdict is `Q286: cannot tell (a control failed: a4 False, a6 False)`, a6 never ran). S3's first
job, the control a4 (320 x 400, `CR_TE_AA` 0x20000000, `--tri-full`, in a render context made for
544 x 400), failed its frozen `diff 0 of 128000` with 28 wrong pixels, first (304, 128), and
closed the gate of the decisive a5 and its control a6, so neither ran, nor a1 to a3. The failure
is a design error of S3, not a hardware effect (E762, post hoc): E727's landed region model, run
after the session, predicts exactly 28 background pixels with the first at (304, 128) for that
job (and 0 at `CR_TE_AA` 0xe0000000), with the TA's own masks as well as the model's; the
frozen "diff 0" took the 64 x 64 control of E728 as the rule. Its knob proofs held (E763, post
hoc): the TA data of the 544 x 400 context is 0xa000 bytes, and the TA wrote one array of 512
region headers at 0x4000 with the target's own spacing of 0x1800, nothing below 0x4000 or from
0x5800. The premise of a5 (four arrays of 0x1800 from 0x4000 end exactly at 0xa000, a fifth needs
page 0xa) is the layout of that one array continued by E728's doubling, at TE 0x20 only; it was
not tested at TE 0xe0 (f stays 4 against 5 as above). A rerun's control must predict the image
with the model, or use a size where it gives diff 0 (64 x 64, 320 x 128), not "diff 0" at 320 x
400.
