+++
id = "E449"
claim = "On two render contexts sharing one parameter buffer, the sharing context's cleanup sends the RT data and context steps and no PB step and leaves the loaded-PB slots (TA3DCtl dwords 46 and 47) at the donor's descriptor, and the donor's cleanup, whose PB step clears them, runs after the sharing context has been released whichever of the two is closed first, in 8 of 8 closes of the sharing context and 8 of 8 of the donor; all 24 renders exact"
unit = "render"
method = "probes/render/cleanup-two-contexts.toml (cleanup-two-contexts.sh) on the laptop (direct cable), linux fork 01cff214d7d2 with the debug option on, module srcversion FC6EB50DEF21E3A6249727F (the loaded module, read from /sys/module, equal to the installed file's modinfo; both printed by the run), sgxfive-test tri --ctx2 --share-pb --close-trace [--close-first] [--overlap] (the first context is the donor; --close-first closes it before the second; after each close and 500 ms after both the tool prints the lines of debugfs render_cleanup, the last cleanup's RT, RC and PB steps with the loaded-PB slots around each, and TA3DCtl dwords 32, 46 and 47 from buf09); before each case a marker run on own PBs leaves the second context's cleanup (ctx 0x32423000, pbdesc 0x32423380) as the last trace, so that a trace seen unchanged is the marker's; shared-PB cases: three one-render runs of each close order and one two-render overlapping run of each; own-PB controls: one run of each order; the GPU reset before each case"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["render-cleanup-two-contexts"]
terms = ["ta3d_ctl", "hw_pb_desc.pb_flags"]
+++

**What runs.** linux fork commit 39 (debugfs render_share_pb) runs the next render context on its
sibling's PB descriptor. The sharing context (the second) keeps a reference on the donor (the first)
until it is freed, and its cleanup is sent with a zero PB descriptor, so that no PB step follows its
RT data and context steps. The kernel keeps the last cleanup only (debugfs render_cleanup): the
descriptors it named, and the TA and 3D loaded-PB slots (TA3DCtl dwords 46 and 47) before it and
after each step. 10 cases ran, 12 renders of each context in all (six shared-PB cases of one render,
two own-PB cases of one, two shared-PB overlapping cases of two).

**Results (the trace after each event).**

| case | read after the first close | read after the second close | 500 ms after both |
|---|---|---|---|
| shared PB, sharing context closed first (4 runs) | its trace: ctx 0x32423000 pbdesc 0, steps RT and RC, slots 0x32411380 throughout | the same trace, unchanged | the donor's: ctx 0x32411000 pbdesc 0x32411380, steps RT, RC, PB, slots 0x32411380 until the PB step, then 0 |
| shared PB, donor closed first (4 runs) | the marker's trace, unchanged (ctx 0x32423000 pbdesc 0x32423380) | the sharing context's, as above | the donor's, as above |
| own PBs, second closed first (1 run) | its trace: ctx 0x32423000 pbdesc 0x32423380, steps RT, RC, PB, slots cleared at the PB step | the first's: ctx 0x32411000 pbdesc 0x32411380, slots 0 throughout | the same |
| own PBs, first closed first (1 run) | its trace: ctx 0x32411000 pbdesc 0x32411380, slots at 0x32423380 (the other context's PB) before and after every step, the PB step too | the second's: slots cleared at its PB step | the same |

TA3DCtl dword 32 read 0x32423000 (the sharing context's address) after the sharing context's
close and 0x32411380 (the donor's PB descriptor) 500 ms after both, in all 8 shared-PB runs. All
24 jobs of the 12 renders completed and every render of both contexts was exact (0 wrong inside,
outside and at the edges, guard 0); the health fill and triangle ran exact before and after.

**What it shows.**

- The PB is released by the PB step of the donor's cleanup, never by the sharing context's, which
  sends none: with the PB shared, the RT and RC steps of the sharing context leave dwords 46 and 47
  at the donor's descriptor in 8 of 8 runs, and the donor's PB step clears them in 8 of 8 [HW].
- Closing the donor first does not run its cleanup at once: in 4 of 4 runs the trace right after its
  close was still the marker's, and the donor's cleanup was the last one 500 ms after both were
  closed, in both orders (8 of 8) [HW]. That the donor's release waits for the sharing context's
  (the reference the kernel holds) is the kernel's design, which the order of traces fits [infer].
- With own PBs a PB step unloads the slots only when they hold the PB it names: the first
  context's cleanup, run while the slots held the second's, left them at the second's PB (1 run)
  [HW].
- Dword 32 holds the operand of the last CLEANUP command the kernel sent, the context page for a
  context that sends no PB step and the PB descriptor for one that does [infer, from the 8 runs
  and the own-PB controls].

**What it does not show.** What the render context's own cleanup waits for once its RT data set is
gone (Q029's first half). The cleanups ran with the contexts idle; a cleanup of a context with a
job in flight, or with its PB loaded by a running TA, was not run.

**Provenance.** The kernel tip and srcversion above were read at run time.
**Provenance.** The sgxfive-test binary of these runs is the one whose sha256 each env.toml names
(ddd670a1...); it was built from source not yet committed, which was later committed in f63c7d19.
