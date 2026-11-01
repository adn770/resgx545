+++
id = "E446"
claim = "With the render context's page mapped writable in the client directory (debugfs alias_ctx_rw) and render flag bit 0 of the PB descriptor set at the first kick, a 64x64 render comes out exact in 3 of 3 runs on the kernel's own page table (the table after the job equal to that of the job without the flag, byte for byte) and in 3 of 3 runs with the descriptor's page-table base aimed at 16 zeroed scratch pages, where 1058 dwords (0x422 pages) of the table at the base change, 1023 in the first scratch page from dword 1 on and 35 in the second from dword 0, and moving the base by 0x1000 or 0x2000 moves them by as much (a control with the base at scratch and flag bit 0 clear, 6 of 6 runs, faults the render and changes 0 to 2 scratch dwords, so the 1058 stores need the flag [HW]; that the EDM's builder makes them is [infer]); with no alias_ctx_rw the same pokes fault as in E362 (once each)"
unit = "dpm"
method = "probes/dpm/ctx-page-writable.toml (ctx-page-writable.sh) on the laptop (direct cable), linux fork ef6ba7cd1b9f with the debug option on: debugfs alias_ctx_rw set before each sgxfive-test tri (64x64, one render, its context for 64x64), --kpoke-render 1:pb:0=0x1 (the descriptor's flag word), with --scratch 16 --scratch-fill 0 --scratch-at (0x3e101000, a heap address above where the tool allocates) and --kpoke-render 1:pb:4=ADDR (the descriptor's page-table base) in the other cases; the tool's report of the scratch dwords the job changed, debugfs render_param (--dump-render) compared with the unpoked job's; the control (probes/dpm/ctx-page-writable-control.toml, linux fork 01cff214d7d2) runs case A once, case C once and, with the base at scratch, the pb:4 poke alone three times and with --kpoke-render 1:pb:0=0x0 three times"
tiers = ["HW", "infer"]
date = "2026-11-07"
data = ["dpm-ctx-page-writable", "dpm-ctx-page-writable-control"]
terms = ["hw_pb_desc.page_table_base", "hw_pb_desc.pb_flags", "CR_BIF_INT_STAT"]
+++

**What runs.** E362 set flag bit 0 and the EDM's write to the render context's page (where the PB
descriptor lies, at +0x380) faulted, because our kernel maps that page read-only in the client's
directory. debugfs alias_ctx_rw (linux fork commit 37) maps the next render context's page
writable. The kernel's page table is 0x422 entries of one dword, entry i at base + 4i for the
pages 1 to 0x422 (entry 0 is not used), built by the kernel (E309).

**Results.**

| case | runs | job | image | page table / scratch |
|---|---|---|---|---|
| writable, no poke | 3 | ok | 0 of 4096 pixels differ | the context's parameter dump equal to run 1's |
| writable, flag bit 0, kernel's table | 3 | ok | exact | dump equal to the unflagged job's, 0 bytes differ |
| writable, flag bit 0, base = scratch | 3 | ok | exact | 1058 scratch dwords changed: 1023 in page 0 (first at +0x4, 0x04220002), 35 in page 1 (first at +0x0, 0x03ff0401) |
| the same with the base at +0x1000, +0x2000 | 1 each | ok | exact | 1058: pages 1 and 2, then 2 and 3, the same first dwords |
| read-only (as E362), flag bit 0, kernel's table, then with the scratch base | 1 each | faulted, context lost | none drawn (the 0xdeadbeef fill stays) | scratch: 0 dwords changed |
| control: writable, base = scratch, flag word left as the kernel sets it (F) | 3 | job faulted, context lost (BIF fault 0x90004 at 0x10000051) | none drawn | scratch: 2 dwords changed (first +0x0 0xffff0000) in 2 runs, 0 in 1 |
| control: writable, base = scratch, flag word poked to 0 (G) | 3 | job faulted, context lost (the same fault) | none drawn | scratch: 2 dwords changed in 1 run, 0 in 2 |
| control: case C again on the revised series | 1 | ok | exact | 1058 scratch dwords changed, the same pages and first dwords as C; the kernel's table unchanged (`ffff0002 00010003 00020004`) |

With the base on the scratch pages the kernel's table is not used: after the job it reads, for
entries 0 to 3, 0 and 0xffff0002, 0x00010003, 0x00020004 (as the kernel built it) and the job
without the flag shows 0, 0x04220002, 0x0001ffff, 0xffff0004: the render edits a table that exists
(E309; the DPM, §6.5 of 3d.md), so the 0x04220002 at the scratch's dword 1 is the value the
unflagged job leaves in its own table [HW].

**What it shows.**

- With flag bit 0 set, the stores into the table named by the base are 4 bytes per page, from the
  base: 1058 dwords for the 1058 pages the descriptor names, none beyond them, entry 0 left alone,
  and a base moved by 0x1000 moves the whole run by one page [HW]. With the same base and flag bit
  0 clear (left as the kernel sets it, or poked to 0) the render faults in 6 of 6 runs, reading the
  zeroed table at the scratch (BIF fault 0x90004 at 0x10000051), and 0 to 2 scratch dwords change,
  not 1058 [HW]. So the table is filled only with flag bit 0 set, and the render does not fill it
  alone; the unflagged runs' 0x04220002, 0x0001ffff, 0xffff0004 in the kernel's own table are what
  the DPM leaves in a table that already exists, the values C's scratch holds after the build
  [infer]. That the EDM's page-table builder (the flag's action, E200) makes the stores is [infer]
  and no longer rests on an unisolated render. Under it the layout is E309's for a host-built
  table, measured for the EDM's own: the builder does not scale the offset by more than the dword
  [infer]. The control's faulting render is not a clean no-builder baseline: it ends at the first
  read of the empty table.
- With the page writable the fault E362 saw at the context's page is gone: the renders end, exact,
  with flag bit 0 set on the kernel's own table too, and that table after the job equals the one
  after the job without the flag [HW]. Case B cannot tell a builder that rebuilt the same table
  from one that did not run [infer].
- The faults of E362 are the read-only page's alone: the same pokes with the page read-only fault
  again here (one run each).

**What it does not show.** The values the builder wrote (the tool reports the first changed dword of
each page, not each dword: the match with the kernel's table is byte for byte only on the kernel's
own table); whether the builder's result depends on the block list (the PB's block was the
kernel's); a descriptor with other counts; the settle routine's wait, which this does not touch
(Q036's second half). What the 2 scratch dwords of the control (first +0x0 0xffff0000, in 3 of 6
runs) are, and whether a render that does not fault with the table at the scratch and flag bit 0
clear exists (a table filled by the host first would give one).

**Provenance.** The campaign read the srcversion of the installed module file (modinfo), not of
the loaded module. The run printed E431D4FEB0F36E3C337AD50 for the installed file; that it was
also the loaded module is inferred (the four runs that print it share one boot, 183 to 511 s of
uptime, after the install, with no reload logged). The kit's env.toml was patched after the runs.
The edm/host-events run, E444, was on an earlier boot with a different installed file. This record
uses alias_ctx_rw (fork commit 37).

The linux series was revised after these runs (tip 01cff214d7d2, the one of the control runs of E445
and E446): the debug switches (kregnow's arm, alias_ctx_rw, render_share_pb, tadata_fill) are
disarmed at a firmware load and at a reset, kregnow's arm, read and write and the host-interrupt
restore run under one lock, a render context that shares a PB holds a reference on its donor until
it is freed, and the cleanup commands and the TA data fill are moved into helpers with the same
order and effect. The scripts of these runs reset the GPU before they arm anything, nothing resets
between the arming and its use, and the shared PB's context is closed before its donor, so the
revision does not change the paths the runs used (read against the diff of the two tips and the
scripts) [infer].
