+++
id = "E457"
claim = "With any one of the firmware buffers 6, 7, 8, 10 or 11 left out of a render VM's alias in the client directory, 2 renders are exact in 10 of 10 runs, as in the 2 controls; leaving out buffer 9 (TA3DCtl) alone, buffers 6 to 11 or all sixteen faults the first job in 6 of 6 runs, as TA3DCtl read-only does (2 of 2)"
unit = "bif"
method = "probes/bif/render-directories.toml (render-directories.sh) on the laptop (direct cable), debugfs alias_skip (linux fork commit 42) set before sgxfive-test tri -n 2 --keep-going on a new VM, under regtimeline 0 0.3 0x0c00-0x0c8c; 10 cases of two runs, the GPU reset before each, alias_skip and alias_ta3d_ro put back after each; sgxfive-test 6f8f2bf8, linux fork ea5482bc59a6 with the debug option on, module srcversion 9A7BCDC4FC2A2166A409EEA (loaded and installed equal, both printed by the run)"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["bif-render-directories"]
terms = ["CR_BIF_DIR_LIST_BASE1", "CR_BIF_BANK0"]
+++

**What runs.** A render VM gets read-only aliases of the EDM's buffers in the client's page
directory, and the control block TA3DCtl (buffer 9) writable, when its first render context is
made. The linux fork's debugfs `alias_skip` (commit 42) names buffers (by id: 6 CCB, 7 its control
block, 8 kicker, 9 TA3DCtl, 10 HostCtl, 11 misc) that this alias leaves out; the existing
`alias_ta3d_ro` makes buffer 9 read-only. `tri -n 2` rendered the 64x64 triangle twice on a new VM
under `regtimeline` sampling the registers 0x0c00-0x0c8c (the bus interface: INT_STAT 0xc04, FAULT
0xc08, the directory list bases 0xc38-0xc84 and BANK0 0xc78, whose INDEX_EDM is bits 3:0, INDEX_TA
7:4, INDEX_3D 15:12). Ten cases, two runs each, the GPU reset before each: no mask, each of the ids
6, 7, 8, 9, 10 and 11 alone, ids 6 to 11 (0xfc0), every id (0xffff) and `alias_ta3d_ro`.

**Results.**

| alias leaves out | runs | result |
|---|---|---|
| nothing (control) | 2 | exact in 2 |
| buffer 6, 7, 8, 10 or 11 alone | 10 | exact in 10 (two renders each) |
| buffer 9 | 2 | first job faulted in 2: INT_STAT `0x90400`, BIF_FAULT `0x32004001` |
| buffers 6 to 11 | 2 | faulted in 2: INT_STAT `0x90400`, BIF_FAULT `0x32004001` |
| TA3DCtl read-only (`alias_ta3d_ro`) | 2 | faulted in 2: INT_STAT `0x80400`, BIF_FAULT `0x32004001` |
| every id (0xffff) | 2 | faulted in 2: INT_STAT `0xd1000`, BIF_FAULT `0x3000b021` |

The 8 faulted runs each stopped at the first job (-EIO, context lost), which the driver recovered;
no recovery failed. The 12 completed runs rendered both triangles exactly (0 wrong, guard 0).
BANK0, sampled at every change, took the values `0x0f`, `0x11`, `0x1f`, `0x1011` and `0x101f` in
the 12 completed runs, and `0`, `0x0f` and `0x11` in the 8 faulted ones. INDEX_TA read 1 in 12 of
12 completed runs and in 8 of 8 faulted ones; INDEX_3D read 1 in 12 of 12 completed runs and in
none of the faulted; INDEX_EDM read 1 in 5 of 12 completed runs and in 8 of 8 faulted ones.
`BIF_DIR_LIST_BASE1` (0xc38) read 0 before the renders and a non-zero directory address (a
different one in each run) while they ran, in all 20 runs.

**What it shows.**

- During a completed render the TA index and the 3D index of BANK0 read 1 while the directory list
  base 1 holds a directory: the TA and 3D requestors translate through list 1, the list the EDM
  gives the first context after a reset (hw_spec section 5.5) [HW]. That the directory in list 1 is
  the client's is [infer]: it was not compared with the client's directory in these runs. Correction
  (11.34): the comparison was possible, with debugfs render_words `ctx:2`, which has shown the
  client's directory since 11.17 (E360 compared it with BASEk in 11.19, E592 with BASE1 after a
  reset); this text did not know of it. Partial evidence for
  Q076's open part [infer]: in the 8 faulted runs kernel.log prints a page directory equal to the
  BIF_DIR_LIST_BASE1 value sampled in that run, and the driver blamed the render context; the driver
  reads that directory from the list base register itself, so this is the register agreeing with
  itself, not an independent match.
- The aliases of buffers 6, 7, 8, 10 and 11 are not needed in the client directory for this render:
  each left out alone, the renders are exact (10 of 10) [HW]. Two or more of them left out together
  were not run: the masks that name several include buffer 9.
- Buffer 9 is needed there, and writable: left out, or read-only, the first job faults at the page
  0x32004000, with BIF_FAULT naming list 1 (CID 1) (2 of 2 each) [HW]. That the access is the EDM's
  own write to TA3DCtl is the kernel's documented cause (render_uapi.md), which the INDEX_EDM = 1
  in 8 of 8 faulted runs fits [infer].
- With every id left out the first fault is at page 0x3000b000, again through list 1: an address in
  the EDM's code heap (base 0x30000000) [infer: the heap], so the EDM runs through list 1 while it
  handles the render and needs its other buffers there too.

**What it does not show.** Subsets of two or more of the buffers 6, 7, 8, 10 and 11, the buffers 0
to 5 and 12 to 15 one at a time, larger scenes (more than two renders, partial renders, DPM
reloads), a context that is not the first on its VM, and which requestor makes the access that
faults.

**Sources of the counts.** kernel.log is authoritative for the facts only the log holds (no
"recovery failed", the eight BIF fault lines); output.txt lost most dmesg lines.

**Provenance.** linux fork commit ea5482bc59a6 with the debug option on, module srcversion
9A7BCDC4FC2A2166A409EEA (the loaded module, read from /sys/module, equal to the installed file's
modinfo; both printed by the run), sgxfive-test sha256
6f8f2bf8295d302f50594b02b92989a72a127adc36b0a8cf245cbd14c53da4f5 (built from this phase's overlay
source, named in each env.toml), the laptop over the direct cable.
Revised after these runs: the series was rebuilt on tip 6ee9501832af, which clears armed pokes on
load and reset (commit 40), moves the submission's poke calls into one function,
sgxfive_submit_xfer_pokes() (40), makes alias_skip refuse bits 16-31 with -EINVAL (42) and rewords
comments and commit messages (40 to 42); the module of these runs is the one built from
ea5482bc59a6. The paths this run used did not change [infer]: git diff ea5482bc59a6 6ee9501832af
changes the alias code only in comments, alias_skip reads back in the same format, and
render-directories.sh writes it after the reset of each case with masks of 0 to 0xffff, all of which
the new check accepts.
