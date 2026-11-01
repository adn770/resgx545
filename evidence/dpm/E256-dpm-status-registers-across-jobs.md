+++
id = "E256"
claim = "While the TA runs, CR_DPM_TA_ALLOC_FREE_LIST_STATUS1 holds the parameter buffer's size in pages in its high half and the pages the TA has taken plus one in its low half, and STATUS2 the size less one; CR_DPM_PAGE_STATUS holds the pages taken in both halves; when the 3D starts the 3D pair copies the TA pair, and while it frees pages the high halves and STATUS2 change at every step, CR_DPM_PAGE_STATUS and CR_DPM_PAGE count down and 0x0730 reads 1; after the job the low half of STATUS1 keeps the TA's count plus one; 0x0740 reads 0 in every job, partial renders and two contexts included"
unit = "dpm"
method = "probes/platform/register-timelines.toml on the laptop, linux fork with the debug option on: regtimeline samples 206 registers (every glossary register and the 13 with no row, less the four that move on their own and those the kernel's register file never reads) from 50 ms before each job to its end, printing each change: the debugfs fills and copies, the 64x64 triangle, two renders in one context, two render contexts and the 1024x768 triangle in a 0x30-page parameter buffer, twice each, then the triangle at 96x64, 256x256, 512x512, 1024x768, 1366x768, 2048x2048 and 4096x4096; one run"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["platform-register-timelines"]
terms = [
    "CR_DPM_TA_ALLOC_FREE_LIST_STATUS1", "CR_DPM_3D_FREE_LIST_STATUS1",
    "CR_DPM_TA_ALLOC_FREE_LIST_STATUS2", "CR_DPM_3D_FREE_LIST_STATUS2", "CR_DPM_PAGE_STATUS",
    "CR_DPM_PAGE", "CR_DPM_GLOBAL_PAGE_STATUS", "CR_DPM_ABORT_STATUS_MTILE", "CR_DPM_REQUESTING",
    "CR_DPM_PARTIAL_RENDER", "CR_DPM_STATE_CONTEXT_ID", "CR_DMS_CTRL", "Parameter Buffer (PB)",
    "partial render",
]
+++

**What runs.** The register timelines of the snapshot table: every change of the DPM's registers
while each job runs. Below, "the first pair" is 0x0700 and 0x070c
(`CR_DPM_TA_ALLOC_FREE_LIST_STATUS1`, `CR_DPM_3D_FREE_LIST_STATUS1`), "the second pair" 0x0710 and
0x071c (the two STATUS2 registers), "page status" 0x0724 (`CR_DPM_PAGE_STATUS`).

**During the TA.** The high half of 0x0700 holds the parameter buffer's size in pages, 0x0422 with
the default buffer and 0x0030 in the 0x30-page one, and 0x0710 that size less one (0x421, 0x2f). The
low half of 0x0700 rises as the TA takes pages; page status holds the pages taken in both halves,
and the low half ends one above it: 2 and 3 at 64x64, 5 and 6 at 256x256, 0x13 and 0x14 at 1024x768,
0x11f and 0x120 at 4096x4096. 0x070c and 0x071c keep the previous job's values until the 3D starts,
then copy 0x0700 and 0x0710.

**During the 3D.** At the larger sizes, where the samples catch it: the high half of both first-pair
registers and both second-pair registers change at every step, together; page status counts down in
both halves, `CR_DPM_PAGE` (0x0728) holds the same count, 0x0730 reads 1 and
`CR_DPM_GLOBAL_PAGE_STATUS` (0x072c) reads 0x00010001; at the end all four read 0.

**After the job.** The low half of the first pair keeps the TA's count plus one; the high half and
the second pair hold values that are not page counts, for example 0x0001 and 0x94 after the
4096x4096 triangle. Read as the free list's head and tail page after the 3D handed the pages back,
in the order it freed them [infer]. So the values E184 saw (0x00020003, 0x00040005, 0x00010006 and
1, 3, 5) are: two pages for one 64x64 render, four for two, five for one 256x256 render, and the
last freed positions.

**Partial render.** In the 0x30-page buffer the partial render starts when page status reads 0xe
pages, and the status words then step as in a 3D. `CR_DPM_PARTIAL_RENDER` reads 1,
`CR_DPM_STATE_CONTEXT_ID` 2, `CR_DPM_REQUESTING` 1 and `CR_DMS_CTRL` gains bit 0 (0x57e08201) while
the partial render runs; `CR_DPM_ABORT_STATUS_MTILE` (0x0720) reads 0x10 from then on (0x5 for one
sample first in the second run), also in every later job. Both repeats show the same.

**0x0740.** It reads 0 in every sample of every job: first kicks, two renders in one context, two
render contexts, the partial renders and all eight sizes. The fields the TA kick reads from it
(E158) were 0 throughout, so these jobs issued none of the store and load tasks they gate.

**Not shown.** The second pair's and the high halves' values against the parameter buffer's pages (a
dump of the free list would say); what sets 0x0740; `contexts -n 2` renders nothing (E258), so two
contexts that each render were not run.
