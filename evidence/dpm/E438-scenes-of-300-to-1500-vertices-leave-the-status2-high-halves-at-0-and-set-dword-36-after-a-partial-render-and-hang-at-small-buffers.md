+++
id = "E438"
claim = "In 66 jobs of the triangle and copies of it (3 to 1500 vertices) on a 4096x4096 and a 1024x768 target with parameter buffers of 0x422 to 0x23 pages, the high halves of CR_DPM_TA_ALLOC_FREE_LIST_STATUS2 (0x0710) and CR_DPM_3D_FREE_LIST_STATUS2 (0x071c) read 0 after all 42 jobs that completed or overflowed (their low halves 1 to 0x241), TA3DCtl dword 36 reads 2 and 3 after the 4096x4096 jobs of 900 and 1500 vertices in 0x422 pages (global list of 4 and 5 pages, three runs each) and 1 after the 1024x768 job of 1500 vertices in 0x23 pages (one page), and 0 after the other overflows, and all 24 jobs of 300 or more vertices at 4096x4096 in 0x40 or 0x23 pages or 900 or more in 0x100 pages hang"
unit = "dpm"
method = "probes/dpm/partial-wide.toml (partial-wide.sh) on the laptop (direct cable), linux fork f1fad0ed9d0e with the debug option on: probe --tri pixel --vertices N (3, 300, 900 or 1500; 3, 300 or 1500 at 1024x768) with a green pixel shader, render_pb_pages at 0x422, 0x100, 0x40 and 0x23 (4096x4096) and 0x422 and 0x23 (1024x768), three runs of each of 22 cases (66 jobs), the render memory dumped, then the debugfs regs (0x0600 to 0x0750 as the file lists them), buf09 (TA3DCtl) and the TA data's state page read after each job"
tiers = ["HW", "infer"]
date = "2026-11-07"
data = ["dpm-partial-wide"]
terms = ["CR_DPM_3D_FREE_LIST_STATUS2", "CR_DPM_3D_PAGE_COUNTS", "CR_DPM_REG_0748", "Dynamic Parameter Management (DPM)", "Parameter Buffer (PB)", "ta3d_ctl"]
+++

**What runs.** The tool's rig now maps nine gen pages, so a scene holds up to 1500 vertices (500
copies of the triangle, each moved 1/16 pixel on, so they pile up near the first). Each case runs
three times on a fresh context; a job that overflows the buffer fails with -ENOSPC and keeps its
context, and one that hangs is recovered.

**Results.** Jobs by outcome: 15 complete, 27 overflow, 24 hang (of 66).

- 4096x4096 in 0x422 pages: 3 and 300 vertices complete (6 jobs); 900 and 1500 overflow (6).
- 4096x4096 in 0x100 pages: 3 and 300 overflow (6), 900 and 1500 hang (6). In 0x40 and 0x23 pages:
  3 vertices overflow (6), 300, 900 and 1500 hang (18).
- 1024x768 in 0x422 pages: 3, 300 and 1500 complete (9). In 0x23 pages 3, 300 and 1500 overflow (9).
- In all 42 jobs that completed or overflowed 0x0710 and 0x071c have a high half of 0. After the 24
  hangs they read 0 whole. 0x0724, 0x0728, 0x072c, 0x0730 and 0x074c read 0 after every job that
  did not hang; 0x0738 and 0x0748 are not in the file the kernel shows (0x0748 stays unread; Q036).
- TA3DCtl dwords 35 and 36 and the global list in the TA data's state page (offset 0x80, the page
  count in the high half of its first dword [infer]) after the overflows, the same in three runs
  of each:

| case | dword 35 | dword 36 | global list |
|---|---|---|---|
| 4096x4096, 0x422, 900 vertices | 0x3fe | 2 | 4 pages |
| 4096x4096, 0x422, 1500 | 0x3fe | 3 | 5 pages |
| 4096x4096, 0x100, 3 / 300 | 0xdc / 0xfc | 0 | 1 page |
| 4096x4096, 0x40 / 0x23, 3 | 0x3c / 0x1f | 0 | 1 page |
| 1024x768, 0x23, 3 | 0xffff | 0 | 1 page |
| 1024x768, 0x23, 300 | 0x1f | 0 | 2 pages |
| 1024x768, 0x23, 1500 | 0x1f | 1 | 1 page |

  The completed jobs read 0 and 0 in the first run and, at 4096x4096 in 0x422 pages with 3 and 300
  vertices, 0x1f and 1 in runs 2 and 3: the values of the job before (1024x768, 0x23, 1500), a job
  without a partial render not writing the two dwords [infer].

**What it shows.** The STATUS2 high halves stay 0 after jobs with global lists of up to five pages
and up to 0x241 in the low half; whether they hold anything during a job is not read here
(E358's timelines did not either). Dword 36 is not always 0 after a partial render: it holds 2 and
3 with four and five pages in the global list, and 1 once with one page, so it is not the list's
page count less one alone, and E160's reading of the abort (written from the page counts) is not
ruled out [infer]. A wide scene in a small buffer does not take the overflow path: it hangs, in 24
of 24 jobs where the one-triangle scene recovers (new question Q103).

**What it does not show.** 0x0748's bits; the registers during a job; why 300 vertices in 0x100
pages overflow and in 0x40 hang.
