+++
id = "Q292"
question = "why does a 4x render at 4096 x 4096 on a context made for 4x targets (four region-header arrays) fault at the parameter buffer's base (BIF_INT_STAT 0x90100, BIF_FAULT 0x10000011) with 1048576 of 16777216 pixels right, and at what target size between 1024 x 768 and 4096 x 4096 does a 4x render on four arrays start to fault"
unit = "dpm"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E828", "E824"]
terms = ["Parameter Buffer (PB)", "CR_TE_AA", "CR_BIF_FAULT"]
+++
Split on 2026-11-11 from the laptop check R3-rgn4 (E828), job j4: with the fork's 4 MiB TA-data
slot a context made with `DRM_SGXFIVE_CTX_RENDER_AA_4X` for 4096 x 4096 is created, but the 4x job
(E824's words, `CR_TE_AA` 0xe0000000, mode 2, `--keep-overflow`) faulted with `BIF_INT_STAT`
0x90100 and `BIF_FAULT` 0x10000011. Page 0x10000 is the first page of the PARAMETERS heap, the
`param_base` of a render context in slot 0 in the kernel's layout, below the PB pages it maps from
`param_base` + 0x1000 (E828, read from the fork's code). 1048576 of 16777216 pixels were right
and the first wrong one is (1024, 0); 1048576 is 1024 x 1024, which would fit a right block at the
top left, but no image was kept to check it. No dump was written, so the four-array TA data size
there (0x223000 bytes by the layout model) was not measured. The health check passed 3 of 3
after it.

Known around it: four arrays complete every 4x size run from 64 x 64 to 1024 x 768 (E824, 8 of 8
held out; E828's 288 x 144 with the flag). Not run: any 4x size between 1024 x 768 and 4096 x
4096. Not examined when this was written: how full the parameter buffer (0x422 pages, its maximum and
default; the debugfs `render_pb_pages` only shrinks it from 0x23 up) gets at 4x; the "ZLS buffer"
of the first reading is `td.zls`, the ZLS external-Z region headers, not a depth buffer.

What is open: whether the fault is the parameter buffer running out at 4x (a DPM behaviour, as in
Q103's overflowing scenes), the ZLS buffer, or something else in the layout at that size; and the
size where 4x on four arrays first faults. If the answer turns out to be our kernel's sizing
alone, that part is split off as a kernel question.

To settle it: on a flagged context, a ladder of 4x sizes from 1024 x 768 to 4096 x 4096 (for
example 1280 x 1024, 2048 x 1536, 2048 x 2048, 4096 x 2048), with `--dump-render` and the fault
read at each; then the same size at 1x as a control, with the kept image to see which pixels are
right. A larger `render_pb_pages` cannot run: 0x422 is both the default and the maximum (the PB's
page table sits at `SGX_RENDER_PARAM_PT` 0x423000), so the knob only shrinks the buffer.

Note 2026-11-11 (round 4, an offline reading of E824's dumps and of the fork; [infer], a fit and
not a test; the reading is not held out). Page need at 4x: the non-zero pages among the 0x422 PB
pages of E824's eight dumps (k-f4, four arrays, `--tri-full`, `CR_TE_AA` 0xe0000000) and of the two
64 x 64 dumps equal 1 + ceil(2 x (W / 16) x (H / 16) / 32) in 10 of 10 (2, 2, 12, 19, 37, 14, 49,
76, 33, 193 pages; page 0 holds the object, every later page 32 full 128-byte slots; the formula is
one stream per 16 x 16 pixels twice over, twice E773's 1x count), and K2's held c1 agrees from the
register 0x0724 (0x000b000b, 11 pages, 288 x 144). By that fit E828's j4 needs 4097 pages at 4096 x
4096 against the 1024 a buffer of 0x422 pages gives when a scene overflows below P - 0x22 (E625,
E735, E773): an overflow by about 3073 pages, and the same triangle at 1x would need about 2049
[model]. So j4 would be the first 4x partial render on record, and the narrowed question is why an
overflowing scene faults at 4x where it ends in -ENOSPC at 1x (the fork has no partial renders:
`sgx_render.c` returns -ENOSPC and leaves the image undefined; E311, E438 and E412 ended that
way). "At what size does 4x start to fault" becomes where the need exceeds P - 0x22: above about
2048 x 2032 for the full triangle, with 2048 x 2048 one page over. The fault word has a precedent:
`BIF_INT_STAT` 0x90100 with `BIF_FAULT` 0x1000001x in E511's HS jobs (0x10000016, 0x10000012,
0x10000013), page 0x10000, `SB` 1, requestor bit 8, which no other record shows; page 0 of a
parameter slot is never mapped, so a 3D-side reader following a zero stream pointer would give it.
After j4's reset `CR_CLKGATESTATUS` read 0x78 and `CR_EVENT_STATUS2` 0x440 (K2's texture fault read
0x20 and 0x440), which fits a TA still waiting for pages; confound: j2's TA write fault came 54 s
earlier on that boot. 1048576 right pixels with the first wrong at (1024, 0) is one 1024 x 1024
block, a macrotile of a 4 x 4 split [infer; no image kept]. Refuted by: a 4x size with a need below
1024 pages that faults, or a small 4x overflow that ends in -ENOSPC. A held-out check (the 1x
control, a 4x size just under and just over the limit, and 1024 x 768 at P 0x80 and 0x100) is
planned for the next laptop session, not run.
