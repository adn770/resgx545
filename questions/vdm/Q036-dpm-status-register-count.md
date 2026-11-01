+++
id = "Q036"
question = "what do the high half of the DPM STATUS2 registers (0x0710, 0x071c) and the DPM's other status words (0x0748 bit by bit, CR_DPM_3D_PAGE_COUNTS' high half) hold, now that STATUS1 and STATUS2's low half are the free list's tail, head and page before the tail?"
unit = "vdm"
phase = 10
evidence = ["E160", "E184", "E256", "E309", "E310", "E312", "E358"]
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

What is open: whether STATUS2's high half ever holds anything; 0x0748 bit 2; and dword 36 against
E160's reading of the abort, which needs a partial render whose global list holds more than one
page.

To settle it: TA3DCtl dword 36 and `CR_DPM_3D_PAGE_COUNTS` through partial renders of scenes that
fill the global list (several hundred triangles on a 4096x4096 target with a small parameter
buffer).
