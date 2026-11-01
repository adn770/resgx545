+++
id = "Q140"
question = "why does our stack's 4x render fault the job (BIF fault at pages 0x20006, 0x20008, 0x2000a) at 320 x 160 and above while 256 x 128 and 192 x 96 complete, and what size does the kernel allocate for a multisampled target"
unit = "ta"
kind = "kernel"
phase = 11
evidence = ["E507"]
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
