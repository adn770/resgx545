+++
id = "Q036"
question = "what do the high half of the DPM STATUS2 registers (0x0710, 0x071c) and the DPM's other status words (0x0748 bit by bit, CR_DPM_3D_PAGE_COUNTS' high half) hold, now that STATUS1 and STATUS2's low half are the free list's tail, head and page before the tail?"
unit = "vdm"
phase = 10
evidence = ["E160", "E184", "E256", "E309", "E310", "E312", "E358", "E438", "E443"]
terms = ["Dynamic Parameter Management (DPM)", "Parameter Buffer (PB)", "ta3d_ctl"]
+++

What the four free-list status registers hold after a 3D is answered (E309): STATUS1 holds the
list's tail page in its high half and its head in the low half, STATUS2 the page before the tail
in its low half; during the TA the head rises as pages are taken (E312).

Narrowed by E358 (timelines through one to three renders on a context at 64x64 to 256x256 and a
1024x768 render with partial renders, two runs): the STATUS2 registers' high halves read 0
throughout; 0x0748 reads 0x1f idle and clears one bit while one step runs (bit 4 while the TA
takes pages, bit 0 at a PB load, bit 1 for about 10 us before each page the 3D frees, bit 3 at the
out-of-memory event; bit 2 never cleared); 0x072c reads 0x10001 from the TA's first page to the
3D's last free; `CR_DPM_3D_PAGE_COUNTS` holds 2 at 64x64, 3 at 128x128, 5 at 256x256, a high half
of 1 at 128x128 and 256x256 (0x10003, 0x10005), its low half the pages a job used (E310) [infer].
TA3DCtl dword 36 reads 0 after the partial renders again.

What is open: whether STATUS2's high half ever holds anything; what 0x0748 bit 2 marks; and how
dword 36 follows the global list's pages against E160's reading of the abort.

To settle it: a timeline of the DPM registers (0x0710, 0x071c, 0x0748, `CR_DPM_3D_PAGE_COUNTS`) at
the finest sampling through a partial render of scenes whose global list holds more than five
pages (more triangles in a bigger parameter buffer than the 0x422 pages that overflow at 1500
vertices), with the runs split by whether 0x0748 bit 2 clears.

Narrowed in 11.16 (E438, 66 jobs, three runs of each case; E443, 12 timelines): the tool's scenes
now hold up to 1500 vertices. After the 42 jobs that completed or overflowed, STATUS2's high halves
(0x0710 and 0x071c) read 0 again, with global lists of up to five pages, and in every sample of the
12 timelines through scenes of 3 to 1500 vertices; TA3DCtl dword 36 reads 2 and 3 after the
4096x4096 jobs of 900 and 1500 vertices in 0x422 pages (global lists of 4 and 5 pages), 1 after the
1024x768 job of 1500 vertices in 0x23 pages and 0 after the other overflows, so it is not always 0
after a partial render; 0x0748 clears bit 2 (the value 0xb) in 4 of the 12 timelines (the three
runs of 300 vertices in 0x100 pages and one of 900 in 0x422) and in none of the other 8. A scene of
300 or more vertices at 4096x4096 in 0x40 or 0x23 pages, or 900 or more in 0x100 pages, hangs where
the one-triangle scene recovers (24 of 24 jobs; Q103). Status: narrowed, not answered; missing:
what makes 0x0748 bit 2 clear, and a scene whose global list holds more than five pages.
