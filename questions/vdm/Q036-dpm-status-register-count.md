+++
id = "Q036"
question = "what do the high half of the DPM STATUS2 registers (0x0710, 0x071c) and the DPM's other status words (0x0748 bit by bit, CR_DPM_3D_PAGE_COUNTS' high half) hold, now that STATUS1 and STATUS2's low half are the free list's tail, head and page before the tail?"
unit = "vdm"
phase = 10
evidence = ["E160", "E184", "E256", "E309", "E310", "E312"]
terms = ["Dynamic Parameter Management (DPM)", "Parameter Buffer (PB)", "ta3d_ctl"]
+++

What the four free-list status registers hold after a 3D is answered (E309): the page table in the
render dump, walked from its head after ten jobs (one run; E256's run repeats the registers), gives
STATUS1 (0x0700, 0x070c) as the list's tail page in the high half and its head in the low half, and
STATUS2 (0x0710, 0x071c) as the page before the tail in the low half. The DPM rewrites the table in
place, one 32-bit entry per page, appending each freed page at the tail; E184's and E256's values
(0x0001 and 0x94 after 4096x4096) are the tail and the page before it. During the TA the head rises
as pages are taken and STATUS2 holds the page before the initial tail (E312).

What is open: STATUS2's high half reads 0 in every sample, so what it would hold is not shown;
0x0748 reads 0x1f idle, 0xf while the TA holds pages and through a partial render, and 0x7 in some
samples while the TA takes pages, the 1024x768 abort among them (E312), its bits one by one not
separated; `CR_DPM_3D_PAGE_COUNTS` holds 1 in its high half from 256x256 up and 0 at 64x64 (E310),
which may count the global list's pages. TA3DCtl dword 36 (`abort_page_count1`) reads 0 after every
partial render, where E160's reading of the firmware has the abort write
`CR_DPM_GLOBAL_PAGE_STATUS`' page count less 2 there, which predicts 0xffff at the 1024x768 abort
(E310); whether that reading or the count it assumes is off is open.

To settle it: sample 0x0710, 0x0748 and 0x0660 through jobs with one, two and three renders on a
context and with partial renders in the middle, at sizes between 64x64 and 256x256; sample 0x072c
and TA3DCtl dword 36 through a partial render whose global list holds more than one page.
