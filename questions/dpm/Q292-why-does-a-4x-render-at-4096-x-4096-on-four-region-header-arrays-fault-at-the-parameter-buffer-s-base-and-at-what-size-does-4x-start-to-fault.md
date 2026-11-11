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
4096. Not examined: the ZLS buffer, which keeps one array's size, and how full the parameter
buffer (0x422 pages by default, debugfs `render_pb_pages`) gets at 4x.

What is open: whether the fault is the parameter buffer running out at 4x (a DPM behaviour, as in
Q103's overflowing scenes), the ZLS buffer, or something else in the layout at that size; and the
size where 4x on four arrays first faults. If the answer turns out to be our kernel's sizing
alone, that part is split off as a kernel question.

To settle it: on a flagged context, a ladder of 4x sizes from 1024 x 768 to 4096 x 4096 (for
example 1280 x 1024, 2048 x 1536, 2048 x 2048, 4096 x 2048), with `--dump-render` and the fault
read at each; then the faulting size again with a larger `render_pb_pages`, and the same size at
1x as a control, with the kept image to see which pixels are right.
