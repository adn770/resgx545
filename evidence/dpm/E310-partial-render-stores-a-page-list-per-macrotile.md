+++
id = "E310"
claim = "CR_DPM_STATE_BASE0 and CR_DPM_CONTROL_BASE hold the RT data's DPM state and control pages; after a job with a partial render the state page holds seventeen two-dword page lists, one per macrotile numbered down then across and the global list last, each the page count and head page then the tail page, and every other job leaves the TA data's control, OTPM and state pages zero; TA3DCtl dwords 35 and 39 read the page count less 2 and the macrotile the DPM aborted; one run"
unit = "dpm"
method = "probes/dpm/free-list.toml on the laptop (the jobs of E309, one run): the registers 0x0600-0x0750 (debugfs regs), the TA/3D control block (debugfs buf09) and the non-zero dwords of the render dump's TA data pages at the kernel's DPM control, OTPM and state offsets (the context's TA data layout); probes/dpm/partial-renders.toml for the macrotiles each partial-render image loses (E311) and the TA/3D control block after each of its jobs; read with dpm_words.py free-list and tiles"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["dpm-free-list", "dpm-partial-renders"]
terms = [
    "CR_DPM_STATE_BASE0", "CR_DPM_CONTROL_BASE", "CR_DPM_STATE_BASE1", "dpm_state",
    "dpm_state.mtile_lists", "dpm_state.global_list", "DPM_STATE_LIST.PAGE_COUNT",
    "DPM_STATE_LIST.HEAD", "DPM_STATE_LIST.TAIL", "ta3d_ctl.abort_page_count0",
    "ta3d_ctl.abort_status_mtile", "ta3d_ctl.abort_page_count1",
    "ta3d_ctl.threshold_ta_global_list", "ta3d_ctl.zls_threshold_step",
    "CR_DPM_ABORT_STATUS_MTILE", "CR_DPM_3D_PAGE_COUNTS", "partial render",
]
+++

**What runs.** The kernel puts each RT data's DPM control, OTPM and state pages in its context's
TA data, after the tail pointers: at 0x20001000, 0x20002000 and 0x20003000 for a context of up to
64x64, 0x20004000-0x20006000 for 1024x768 and 0x20040000-0x20042000 for 4096x4096.

**Results.** One run of each table.

- `CR_DPM_CONTROL_BASE` (0x0634) and `CR_DPM_STATE_BASE0` (0x062c) read the context's control
  and state page after every job: 0x20001000 and 0x20003000, 0x20004000 and 0x20006000,
  0x20040000 and 0x20042000 by the context's largest target, whatever its target.
- The TA data's control, OTPM and state pages are zero after every job without a partial
  render, the two-render context included.
- After the partial render of the 1024x768 triangle in 0x30 pages the state page holds 20
  non-zero dwords, after the 4096x4096 one in 0x100 pages 22; the control and OTPM pages stay
  zero. They pair into lists of two dwords, the first holding a page count in its high half
  and a page in its low half, the second a page: at 1024x768, entry 0 (0x00010002, 2), 1
  (0x00010005, 5), 2 (0x0001000d, 0xd), 4 (3), 5 (0x00030006, 0xb), 6 (0xe), 8 (4), 9
  (0x00030007, 0xc), 13 (8) and 16 (0x00010001, 1); at 4096x4096 entries 0-2, 4-6, 8-10, 13
  with 3 to 64 pages each, and entry 16 again one page, page 1.
- The entries with a list are, in both cases, the macrotiles whose image the partial render
  loses (E311) when the macrotiles of the 4 x 4 grid are numbered down then across; entry 16 is
  past the sixteen macrotiles and holds page 1, the first page of a job on a fresh table, which
  the 3D frees last (E309): the global list [infer: the name].
- The counts add up to the pages taken at the abort less one: 13 at 1024x768, where page status
  read 0xe when the partial render began (E312), 221 at 4096x4096 (0xde). TA3DCtl dword 35
  (`abort_page_count0`) reads 0xc and 0xdc, page status less 2, and dword 39
  (`abort_status_mtile`) 5 in both, the macrotile at column 1, row 1; the other out-of-memory
  dwords (33, 36-38, 40) read 0. Later jobs leave them.
- The partial-render table reads the same words after each of its jobs, (dword 35, dword 39):
  at 1024x768 (0xc, 5) in 0x30 pages, (4, 0) in 0x28, (0, 0) in 0x24 and (0xffff, 0x1f) in
  0x23; at 4096x4096 (0xdc, 5) in 0x100, (0x3c, 6) in 0x40 and (0x1f, 6) in 0x23. A job that
  does not overflow keeps the previous job's. 0xffff is page status 1 less 2: the 1024x768
  jobs in 0x23 pages last aborted at the first page, as the first partial render of 4096x4096
  in 0x23 pages does in E312's timeline [infer]. From the 0x28 case on, dwords 37
  (`threshold_ta_global_list`) and 38 (`zls_threshold_step`) also read non-zero (0x00010006
  and 0x20 at 0x28), the words E160 has the threshold raise write; since a job keeps the
  previous values, which jobs raised is not separated. Dword 36 reads 0 in every job.
- `CR_DPM_3D_PAGE_COUNTS` (0x0660) reads the pages used in its low half (2, 5, 0x13, 0x11f) and
  1 in its high half from 256x256 up, 0 at 64x64.

**Reading [infer].** At a partial render the DPM stores the TA's allocation state into the RT
data's state page: a page list per macrotile and the global list, in the layout of
DPM_STATE_LIST. A job that never overflows stores nothing there.

**Not shown.** What the control and OTPM pages are for; whether a later load reads the stored
lists (the store and load tasks of Q045 never run, E312); the meaning of the second dword of a
list beyond the tail page. `abort_page_count1` (dword 36) disagrees with E160's reading of the
firmware, open (Q036): E160 has the abort write it from `CR_DPM_GLOBAL_PAGE_STATUS`' page count
less 2, and that register read 0x00010001 at the 1024x768 abort (E312), which predicts 0xffff (as
dword 35 does wrap to 0xffff at 1024x768 in 0x23 pages), but dword 36 reads 0 after every job of
both tables. Dword 40 = 0 does fit E160 (bits 13:5 of the abort status, 5, 6 or 0x1f).
