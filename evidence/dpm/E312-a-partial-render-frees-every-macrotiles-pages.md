+++
id = "E312"
claim = "Through a partial render CR_DPM_ABORT_STATUS_MTILE reads the aborted macrotile (5) as the TA stops, CR_DPM_STATE_CONTEXT_ID turns 2 and CR_DPM_STATE_BASE1 is set to the RT data's state page; the 3D then frees the pages of every macrotile, page status counting down to the global list's one page, and the TA resumes from the list's head; with 0x23 pages the first partial render starts at the first page; 0x0730 reads 1 while the 3D holds the global page, from a partial render's start (or the render's, without one) to the final render's last free, the TA's runs between partial renders included; 0x0738 reads 0 while a render runs, and 0x0748 0x1f idle, 0xf while the TA holds pages and through a partial render, 0x7 in some samples while the TA takes pages; 0x0740 stays 0"
unit = "dpm"
method = "probes/dpm/partial-timelines.toml on the laptop, linux fork with the debug option on: its script partial-timelines.sh runs regtimeline over 0x0600-0x0750 (read-only, a line at each change, about one sample every 80 microseconds) around the triangle at 64x64 and 1024x768 with 0x422 pages, at 1024x768 with 0x30 pages and at 4096x4096 with 0x100 and 0x23 pages; one run; read with dpm_words.py timeline"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["dpm-partial-timelines"]
terms = [
    "CR_DPM_PARTIAL_RENDER", "CR_DPM_ABORT_STATUS_MTILE", "CR_DPM_STATE_CONTEXT_ID",
    "CR_DPM_STATE_BASE1", "CR_DPM_PAGE_STATUS", "CR_DPM_PAGE", "CR_DPM_GLOBAL_PAGE_STATUS",
    "CR_DPM_REQUESTING", "CR_DPM_3D_PAGE_COUNTS", "CR_DPM_TA_ALLOC_FREE_LIST_STATUS1",
    "CR_DPM_REG_0730", "CR_DPM_REG_0738", "CR_DPM_REG_0748", "partial render",
]
+++

**What runs.** One job a case; the times below are from the start of sampling (the job starts
0.2 s in). Stretches where `CR_DPM_PARTIAL_RENDER` (0x0658) reads 1: none at 64x64 and 1024x768
in the whole buffer, one at 1024x768 in 0x30 pages (1.29 ms), one at 4096x4096 in 0x100 (28.5 ms)
and ten in 0x23 (27.0 to 27.2 ms each), as E204 counted: twelve partial renders in all.

**The 1024x768 job in 0x30 pages, in order.**

1. The TA has taken pages: STATUS1 0x0030000d (tail 0x30, head 0xd), STATUS2 0x2f,
   `CR_DPM_PAGE_STATUS` 0x000e000e; `CR_DPM_ABORT_STATUS_MTILE` (0x0720) 5,
   `CR_DPM_GLOBAL_PAGE_STATUS` 0x00010001, `CR_DPM_REQUESTING` 1, 0x0748 0x7.
2. The partial render starts: `CR_DPM_STATE_CONTEXT_ID` 2, 0x0658 1, `CR_DPM_STATE_BASE1`
   (0x0674) 0x20006000 (the context's state page; it held 0x20042000 from an earlier 4096x4096
   job), 0x0720 0x10, `CR_DPM_PAGE` 0xe, 0x0730 1, 0x0738 0, `CR_DPM_3D_PAGE_COUNTS` 0x0001000e,
   0x0604 the TA's list 0x0030000f.
3. The 3D frees pages: page status and `CR_DPM_PAGE` count down 0xd, 0xc, ... to 1 while the
   tail (STATUS1's high half) takes 2, 5, 0xd, 3, 0xb, 0xe, 4, 0xc, 8: the pages of macrotiles 0,
   1, 2, 4, 5, 6, 8, 9 and 13 in that order (E310's lists), not only macrotile 5's.
4. The TA resumes with one page held (the global list's): STATUS1 0x00080012, the head moving
   on from 0xf; 0x0738 1, 0x0748 0x1f; 0x0630 still 2.
5. The final render starts: 0x0630 and 0x0658 back to 0 in the sample where 0x0738 turns 0. It
   frees the rest, page status to 0, and leaves STATUS1 0x00010015; 0x0730 turns 0 with the last
   free.

**4096x4096 in 0x23 pages.** The ZLS threshold is 1 (0x23 - 0x22, E201): the first partial
render starts with page status 0x00010001, before any macrotile holds a page; each later one
starts at 0x21 pages, 0x0720 having read 0x1f, 5 and 6 in one sample each between (0x10
otherwise). Each frees the macrotile pages and the TA resumes. `CR_DPM_STATE_CONTEXT_ID` reads 2
from the first partial render's start through every gap and the final render, still 2 at the
last sample (1944.844 ms); at 4096x4096 in 0x100 pages, as at 1024x768 in 0x30, it goes back to
0 when the final render starts.

**Other registers.** 0x0730 reads 0 while the TA takes pages before any render, with
`CR_DPM_GLOBAL_PAGE_STATUS` already 0x00010001 (1024x768 in the whole buffer, 297.695 ms), and 1
from the start of the first render or partial render (one sample earlier at 4096x4096 in 0x23
pages). Once a partial render has run it stays 1 while the TA runs again, with 0x0738 at 1 (1024x768
in 0x30 pages at 299.550 ms, 4096x4096 in 0x100 from 1669.762 ms, and every one of the ten TA runs
after a partial render in 0x23 pages, but one sample at 1749.653 ms), and it falls to 0 only when
the final render frees the last page. 0x0738 reads 1 when no render runs and 0 from a render's start
to its end. 0x0748 reads 0x1f idle and from the last TA's end (already in the sample after the
resume at 1024x768 in 0x30 pages), 0xf while the TA holds pages and through each partial render, and
0x7 in six samples while the TA takes pages: the 1024x768 abort (page status 0xe), 4096x4096 in
0x100 at page status 0x51, long before its abort at 0xde, which reads 0xf, and four of the ten TA
runs after a partial render in 0x23 pages, one just after a TA resume (1665.921 ms, page status 1)
and one with 0x0720 at 0x10 (1833.389 ms). `CR_DPM_REG_074C` and 0x0740 read 0 throughout. The 64x64
job shows the TA side only for a moment: STATUS2 0x421 (the page before the initial tail), STATUS1
0x04220003, page status 2, then the final values of E309.

**Reading [infer].** A partial render renders and frees every macrotile tiled so far, keeping
the global list, under DPM context slot 2. 0x0730 reads as the 3D side's global page count: the
EDM stores its low half to `hw_pb_desc.global_page_count` beside the TA side's
`CR_DPM_GLOBAL_PAGE_STATUS` (edm_dataflow.md), and 1 is the one global page the 3D holds from its
first render or partial render until the final render frees it [infer: RE store + HW]. 0x0738
marks an idle 3D and 0x0748 a TA allocation state. Their names are ours.

**Not shown.** What 0x0748's bits are one by one; the samples miss steps shorter than 80
microseconds (four of the 3D's frees at 1024x768, in two gaps: pages 6 and 9 of macrotile 5,
7 and 0xa of macrotile 9).
