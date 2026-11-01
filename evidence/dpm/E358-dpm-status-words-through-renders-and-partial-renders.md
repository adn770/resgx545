+++
id = "E358"
claim = "Sampled through one to three renders on a context at 64x64, 128x128 and 256x256 and a 1024x768 render with partial renders, the high halves of CR_DPM_TA_ALLOC_FREE_LIST_STATUS2 (0x0710) and CR_DPM_3D_FREE_LIST_STATUS2 (0x071c) read 0 in every job; CR_DPM_REG_0748 reads 0x1f idle, clears bit 4 while the TA takes pages, bit 0 briefly at a TA's PB load, bit 1 for about 10 us before each page the 3D frees and bit 3 at the out-of-memory event; 0x072c reads 0x10001 from the TA's first page to the 3D's last free; TA/3D control block dword 36 reads 0 after the partial renders; two runs"
unit = "dpm"
method = "probes/platform/event-timelines.toml on the laptop, linux fork b5a86838ae59: regtimeline over 0x0658, 0x0660, 0x0700, 0x070c, 0x0710, 0x071c, 0x072c and 0x0748 (with five other registers) from 50 ms before each job, every change kept; the TA/3D control block (debugfs buf09) after the partial-render job"
tiers = ["HW", "infer"]
date = "2026-11-03"
data = ["platform-event-timelines"]
terms = [
    "CR_DPM_TA_ALLOC_FREE_LIST_STATUS1", "CR_DPM_TA_ALLOC_FREE_LIST_STATUS2",
    "CR_DPM_3D_FREE_LIST_STATUS2", "CR_DPM_REG_0748",
    "CR_DPM_3D_PAGE_COUNTS", "CR_EVENT_STATUS.DPM_OUT_OF_MEMORY_MT",
]
+++

**Results** (the values each register takes, in order, per job):

| job | 0x0710 | 0x0748 | 0x0660 |
|---|---|---|---|
| 64x64, 1 render | 0x1, 0x421, 0x1 | 0x1f | 0x2 |
| 64x64, 2 and 3 renders | rises by 2 a render (0x3, 0x5) | 0x1f, 0xe, 0x1f (one run) | 0x2 |
| 128x128, 3 renders | 0x421, 0x422, 0x3 ... 0x9 | 0x1f, 0xe (one run) | 0x10005, 0x10003 |
| 256x256, 1 to 3 renders | 0x421, 0x422, 0x2 ... 0xc | 0x1f, 0xf, 0x1d | 0x10005 |
| 1024x768, 0x30 pages, 2 renders | 0x2f, 0xc ... 0x13 | 0x1f, 0xf, 0x7, 0xd | 0x10003, 0x1000e |

- `0x071c` follows `0x0710` through the jobs but does not show its values at the PB load (where
  0x0710 reads 0x421, 0x2f at 1024x768 and 0x071c keeps the old value); the high half of both is 0
  throughout.
- *0x0748.* 0xf from the TA's first page allocation (`CR_DPM_TA_ALLOC_FREE_LIST_STATUS1` low half
  rising) to the TA's end; 0xe for one sample at a TA's PB load (0x0700 = 0x04220001); during the
  partial render (0x0658 = 1) 0xd for about 10 µs before each change of 0x0700's high half, the page
  the 3D frees, and 0x1d before a free after the render; 0x7 at the sample where `CR_EVENT_STATUS`
  bit 1 (out of memory) is set.
- *0x072c.* 0x10001 from the TA's first allocation to the last free of the 3D, 0 otherwise.
- The 1024x768 render overflows (-ENOSPC, as E312's). TA/3D control block dword 36 reads 0 after it
  and dword 35 0xc, in both runs.

**What it shows.**

- The STATUS2 registers' high halves hold nothing in these jobs [HW].
- 0x0748's bits 0, 1, 3 and 4 are busy or event flags of the DPM, each cleared while one step runs:
  the PB load, a 3D free, the out-of-memory event, the TA's allocation [HW: timing] [infer: the
  steps named by what moves beside them]; bit 2 never cleared here.
- 0x0660's low half (2 at 64x64) is the pages a job used, as E310 reads this register, so it is the
  3D's page counts, the global count in its high half [infer].
