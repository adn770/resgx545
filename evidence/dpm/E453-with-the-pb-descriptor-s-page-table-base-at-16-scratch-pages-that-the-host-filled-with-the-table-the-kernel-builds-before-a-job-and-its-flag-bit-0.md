+++
id = "E453"
claim = "With the PB descriptor's page-table base at 16 scratch pages that the host filled with the table the kernel builds before a job and its flag bit 0 clear, a 64x64 render comes out exact in 6 of 6 runs and changes 4 scratch dwords, not 1058, and with flag bit 0 set over that table it comes out exact in 6 of 6 runs and changes the same 4; a table of the values a finished job leaves faults the render in 3 of 3 runs, and a zero table faults it in 4 of 4 unflagged runs; the plain health triangle after the last faulted run faulted too"
unit = "dpm"
method = "probes/dpm/ctx-table-host-filled.toml and probes/dpm/ctx-table-flag-order.toml on the laptop (direct cable), linux fork 01cff214d7d2 with the debug option on, module srcversion FC6EB50DEF21E3A6249727F (the loaded module, read from /sys/module, equal to the installed file's modinfo; both printed by the run), debugfs alias_ctx_rw set before each sgxfive-test tri (64x64, one render, its context for 64x64), --dump-render, --scratch 16 --scratch-fill 0 --scratch-at (0x3e101000) --kpoke-render 1:pb:4=0x3e101000 (the descriptor's page-table base), --scratch-file TABLE (new: the first dwords of the scratch pages are the table, the tool's report counts the dwords the render changed against it): table H = the table dump of an unflagged job (entry 0 = 0, entry 1 = 0x04220002) three runs; table K = the table the kernel builds before a job (entry i, 1 to 0x422, = ((i - 1) & 0xffff) << 16 | (i + 1), the last entry's next 0xffff; the layout of E309) six runs; zeros, four runs; flag bit 0 (1:pb:0=0x1) over H once, over K six runs (both poke orders), over zeros seven runs (both orders); the GPU reset before each"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["dpm-ctx-table-host-filled", "dpm-ctx-table-flag-order"]
terms = ["hw_pb_desc.page_table_base", "hw_pb_desc.pb_flags"]
+++

**What runs.** E446 showed that with the table's base at zeroed scratch pages and flag bit 0 set
the render writes 1058 dwords there and renders exactly, and that with the flag clear the render
faults on the empty table and changes 0 to 2 dwords. Here the host fills the scratch with a table
first, with the new --scratch-file option.

**Results.**

| scratch pre-filled with | flag bit 0 | runs | job | scratch dwords changed | image |
|---|---|---|---|---|---|
| K, the kernel's pre-job table | clear | 6 | ok in 6 | 4 (3 in the first page from entry 1, 1 at entry 0x422) | exact in 6 |
| K | set (either poke order) | 6 | ok in 6 | 4 (the same) | exact in 6 |
| H, the table a finished job leaves | clear | 3 | faulted in 3 | 1 | none drawn |
| H | set | 1 | faulted | 4 | none drawn |
| zeros | clear | 4 | faulted in 4 | 2 | none drawn |
| zeros | set (either poke order) | 7 | ok in 2, faulted in 5 | 1058 in all 7 | exact in the 2 |

The 4 dwords the render changes in K are the first dword of entry 1 (0x04220002, the value an
unflagged job leaves there, E446) and 2 more in the first page, and the dword of entry 0x422
(0x04210001, at page 1 +0x88): the ends of the list. A faulted job is reported by the tool as "job
faulted, context lost". The runs of "zeros, flag set" that faulted (5 of 5) each followed a run that
had faulted; the two that rendered exactly (the first of each poke order) followed a run that had
not: 1058 dwords were written in all 7, so the fault is not the build failing to run.

The health check at the end of the flag-order run failed as well: after the GPU reset that follows
the last faulted run (a zero table, no flag), the health fill was ok and the plain triangle (no
pokes, alias_ctx_rw N) drew nothing (4096 of 4096 pixels differ, first 0xdeadbeef against
0xff203040, no "tri 64x64 #1" line; its env.toml records it in `after`). The host-filled run's
health check was clean. The kernel logs hold two faults in that health run, BIF fault 0x90004 at
0x10000052 (job 484) and at 0x10000051 (job 485), and 7 lines "SGX recovery failed: -110", each
followed by "render context cleanup failed, resetting": 5 in the flag-order log (after the
faulted runs of jobs 470, 472, 476 and 482, and in the health run, job 485) and 2 in the host-filled
log (after Z1 and CZ1). The fault address is 0x3e140081 in the 3 H runs and 0x10000051 in every
zero-table run of the case table (host-filled and flag-order alike); the flagged H run CH1 also
faulted at 0x10000051, the address the zero-table runs fault at, right after Z1 whose recovery
had failed, although its scratch held H.

These do not line up with the runs that were followed by a fault: of the 4 flagged zero runs of
flag-order that faulted, 2 followed a run whose recovery failed (flag-then-base-zero-2 and -3)
and 2 followed one whose recovery did not (base-then-flag-zero-2 and -3), and K-2 rendered
exactly right after base-then-flag-zero-2, whose recovery had failed.

**What it shows.**

- A host-filled table in the kernel's pre-job layout makes the render with flag bit 0 clear complete
  exactly, and the scratch changes by 4 dwords only (6 of 6): the render itself does not write the
  1058 entries [HW]. With the flag set over the same table the scratch changes by the same 4, while
  over zeros it changes 1058: the flagged build either writes values equal to K's, which would make
  K the builder's result, E309's layout, or does not write over a table that is there [infer]. That
  the flag's action (E200) is what makes the 1058 stores is [HW] by elimination: the render without
  the flag does not.
- The values a finished job leaves are not a valid table for the next job: H faults 3 of 3 [HW].
- The flagged build over zeros rendered exactly after a run that had not faulted (2 of 2) and
  faulted after a run that had (5 of 5), a GPU reset between the runs notwithstanding [HW]; what a
  faulted job leaves was not found. A plain triangle with no pokes (the health check) faulted
  after the last faulted run too [HW], so the effect is probably not specific to the flagged build
  over zeros [infer]; whether the failed recoveries are part of it is not shown.

**What it does not show.** Whether the settle routine waits for the other pipe to go idle (Q036's
second half, with the timelines of E448 still unread for it); why a flagged build over zeros faults
after a faulted run.

**Provenance.** The sgxfive-test binary of these runs is the one whose sha256 each env.toml names
(83318889...); it was built from source not yet committed, which was later committed in f63c7d19.
