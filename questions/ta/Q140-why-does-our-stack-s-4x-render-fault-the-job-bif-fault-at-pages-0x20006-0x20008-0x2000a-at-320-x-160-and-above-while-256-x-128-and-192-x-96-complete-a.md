+++
id = "Q140"
question = "why does our stack's 4x render fault the job (BIF fault at pages 0x20006, 0x20008, 0x2000a) at 320 x 160 and above while 256 x 128 and 192 x 96 complete, and what size does the kernel allocate for a multisampled target"
unit = "ta"
kind = "kernel"
phase = 11
evidence = ["E507", "E729", "E788", "E824"]
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

Note 2026-11-10 (R2-pixel, E788; the question stays open, it is the kernel's). "4 against 5" is
answered for what the TA writes: four arrays (a1 at 256 x 160 and a2 at 320 x 128 held nothing in a
fifth slot) and a layout of exactly four (the TA data 0xa000 bytes = 0x4000 + 4 x 0x1800, a context
made for 544 x 400) completed 320 x 400 at `CR_TE_AA` 0xe0000000 with 0 of 128000 pixels wrong,
where a context made for 320 x 400 alone faulted at page 0x20008 (a6). [infer] The fault of the
sizes that fail on our stack is then a layout shorter than four arrays at that size and not a
missing fifth array; the kernel's own layout for those sizes was not read against it.
Open: the kernel's `sgx_render_layout` for the multisampled case (what it must allocate at 288 x
144, 256 x 288 and 384 x 384 and the sizes between 192 x 96 and 320 x 160) and the health triangles
that fault after a failed 4x job.

Note 2026-11-10: Q286 is retired, answered by E788 (four arrays of region headers, and four
suffice at 320 x 400); its two open clauses, the layout at other sizes and the health triangles
after a failed 4x job, are this question's (above).

Narrowed 2026-11-10 (K2 stage k-f4, E824; not retired). With the debug knob `render_rgn_arrays` at
4, the kernel's own layout completed 8 of 8 held-out 4x sizes (288 x 144, 256 x 288, 384 x 384, 320
x 160, 512 x 384, 640 x 480, 320 x 400, 1024 x 768) at `CR_TE_AA` 0xe0000000 with 0 wrong pixels and
the TA data sizes the model gave (0x8000 to 0x1e000); 288 x 144 at one array faulted again at page
0x20006 (E729). So the fault is the layout's single array and four suffice up to 1024 x 768. Open:
the kernel's default (four arrays; 4096 x 4096 needs 0x223000 bytes, over the 2 MiB TA-data slot)
and the health triangles after a failed 4x job (two failed, then a pass, after both 4x faults of
K2).
