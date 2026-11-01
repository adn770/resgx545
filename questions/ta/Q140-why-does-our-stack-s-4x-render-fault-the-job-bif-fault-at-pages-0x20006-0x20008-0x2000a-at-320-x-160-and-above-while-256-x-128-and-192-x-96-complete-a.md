+++
id = "Q140"
question = "why does our stack's 4x render fault the job (BIF fault at pages 0x20006, 0x20008, 0x2000a) at 320 x 160 and above while 256 x 128 and 192 x 96 complete, and what size does the kernel allocate for a multisampled target"
unit = "ta"
kind = "kernel"
phase = 11
evidence = ["E507", "E729"]
terms = ["CR_TE_AA", "CR_ISP_MSAA"]
+++

E507: with the unpoked rule words, mode 2 and CR_TE_AA 0xe0000000, the render draws exactly at six
sizes up to 256 x 128 and 192 x 96 and faults at the six held-out sizes from 320 x 160 to 640 x 480
(`BIF_FAULT` 0x90004, pages 0x20006 to 0x2000a).

What is open: whether the kernel's render layout (the region headers, tail pointers and pages sized
from the target without the multisampling factor) is what runs out, and the size between 192 x 96
and 320 x 160 where it first does. To settle it: read the kernel's `sgx_render_layout` for the
multisampled case, then render at 256 x 160, 288 x 144 and 320 x 128 and read the fault address
against the layout.

Run in 11.39 (E729, 5 held-out sizes): 256 x 160 and 320 x 128 complete, 288 x 144, 256 x 288
and 384 x 384 fault at pages 0x20006, 0x20006 and 0x20008 (the job's own first fault). With
E507's 12 sizes the number f of region-header arrays is 4 or 5 (3 refuted; 6 or more refuted
post hoc, under the layout formula as transcribed and integer f). Not
settled: 4 against 5, the kernel fix, and the health triangles that fault after a failed 4x job
(Q286). Faulted 4x jobs leave state that makes the next health triangle fault until a reset; no
reported result is affected.
