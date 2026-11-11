+++
id = "Q140"
question = "what makes the health triangles after a failed 4x job fault before one passes (two after each 4x fault of K2, one after R3-rgn4's j2, none after its 4096 x 4096 fault), now that our 4x faults are known as the kernel's one array of region headers and a context made for 4x targets gets four"
unit = "ta"
kind = "kernel"
phase = 11
evidence = ["E507", "E729", "E788", "E824", "E828"]
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

Narrowed 2026-11-11 (R3-rgn4, E828; not retired). The question was "why does our stack's 4x
render fault the job (BIF fault at pages 0x20006, 0x20008, 0x2000a) at 320 x 160 and above while
256 x 128 and 192 x 96 complete, and what size does the kernel allocate for a multisampled
target". Both parts are answered: the fault is the kernel's single array of region headers (E788,
E824), and the fork's commits 11 and 12 (the 4 MiB TA-data slot and the context flag
`DRM_SGXFIVE_CTX_RENDER_AA_4X`) allocate four arrays for a context made with the flag, while a 4x
job on a context made without it is refused at submission. E828 ran it: 288 x 144 with the flag
completed with 0 of 41472 wrong and the dumps of E824's h1; without the flag the job was refused
with EINVAL; with `render_rgn_arrays` forced to 1 E729's fault came back (BIF_INT_STAT 0x90004,
BIF_FAULT 0x20006061) and E827's 4x row `ctl-a1-256x160-tee0` reproduced byte for byte. The
4096 x 4096 context is created but its 4x job faulted at the parameter buffer's base; that is
Q292, with the size where 4x starts to fault. Open here: the health triangles after a failed 4x
job, now seen as two, one or none failing before a pass.

Note 2026-11-11 (round 4, decision R4-3; not yet merged into Q003, see that question's note of this
date). The question line's "after a failed 4x job" is too narrow: the faulting state follows any
fault word 0x90004, not 4x. Over 543 kernel logs of resgx545-data "SGX recovery failed: -110" (the
EDM boot's "no INIT_COMPLETE after 500 ms") follows a `BIF_INT_STAT` 0x90004 fault 51 times of 157
and none of the other fault words (about 1180 faults; closing4/rank/faultseq.out). In K2 the
health triangle (a 64 x 64 context of its own, TA data 0x6000 bytes) faulted at the previous job's
address in 4 of 4 (0x20006061 twice after c1, 0x20008061 twice after k-bif f2), a page its own
layout does not reach, and after the faults that are not 0x90004 (k-bif f1, f1r 0x90008, f3
0x90002, R3-rgn4's j4 0x90100) the next health triangle passed. [infer] The TA's pending
region-header write survives the soft reset and is issued again when the TA next runs, through
whatever directory is then current; one boot's log, not held out (the K2 health-triangle reading,
closing4/render4x/exp-render4x-r4.md section 1.2). The 4x sizes are not special.
