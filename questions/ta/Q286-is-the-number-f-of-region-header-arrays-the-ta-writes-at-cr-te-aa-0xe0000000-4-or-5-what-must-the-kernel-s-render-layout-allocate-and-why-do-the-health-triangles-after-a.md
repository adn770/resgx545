+++
id = "Q286"
question = "is the number f of region-header arrays the TA writes at CR_TE_AA 0xe0000000 4 or 5, what must the kernel's render layout allocate, and why do the health triangles after a 4x fault fault again"
unit = "ta"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E729", "E507", "E504"]
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
