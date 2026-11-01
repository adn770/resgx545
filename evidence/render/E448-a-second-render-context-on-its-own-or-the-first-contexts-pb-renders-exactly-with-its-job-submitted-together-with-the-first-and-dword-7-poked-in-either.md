+++
id = "E448"
claim = "A second render context in the VM, on a parameter buffer of its own or on the first context's (the PB descriptor and block of the first), renders the triangle exactly in 69 of 69 renders at 64x64 and 256x256, with the two contexts' jobs run one after the other or the second's job submitted before the first's was waited for (the overlap in the firmware was not timed), and with render context dword 7 poked to 0xdeadbeef or 0xffffffff in the first context, the second or both (20 renders per context in 10 cases, and 2 per context in a last one, 69 per context in all: 32 + 20 + 2 + 15): no fault, no recovery, the first context's 69 renders exact too, and the second context's dword 7 reading 0x10c63000 before the first render and 0xdeadbeef after the first and after the second render"
unit = "render"
method = "probes/render/two-contexts-one-pb.toml (two-contexts-one-pb.sh) on the laptop (direct cable), linux fork ef6ba7cd1b9f with the debug option on: sgxfive-test tri --ctx2 [--share-pb] [--overlap] [--kpoke-render 1:ctx:7=V] [--kpoke-render2 1:ctx:7=V] (--share-pb writes debugfs render_share_pb before the second context is created; --overlap submits its job before waiting for the first's; with a second-context poke the tool waits 30 ms after the first's job is submitted before arming the poke and submitting the second's job), n = 4 renders (64x64 and 256x256, own and shared PB, sequential and overlapping: 8 cases), n = 2 renders for the dword 7 cases; the newest context's words (debugfs render_words, --words) after each render; five regtimeline runs over the DPM and event registers"
tiers = ["HW", "infer"]
date = "2026-11-07"
data = ["render-two-contexts-one-pb"]
terms = ["hw_render_context.ready_renders_tail", "hw_render_context.run_node_prev_3d", "hw_render_context.run_node_next_3d", "hw_transfer_context.pd_dev_paddr"]
+++

**What runs.** The fork had no second context on one PB (Q068's route). linux fork commit 39
(debugfs render_share_pb) makes the next render context take the PB descriptor and block of the
newest render context of its VM, so that its HW context and TA commands name that descriptor; the
sharing context is destroyed first and does not send the CLEANUP of the PB. sgxfive-test tri --ctx2
creates the second context in the same VM and renders the same scene on it in the other pair of
colours after each render of the first, each against its own triangle.

**Results.**

| case | renders per context | both contexts' renders |
|---|---|---|
| own PBs, one after the other, 64x64 and 256x256 | 4 each | exact |
| shared PB, one after the other, 64x64 and 256x256 | 4 each | exact |
| own PBs, overlapping, 64x64 and 256x256 | 4 each | exact |
| shared PB, overlapping, 64x64 and 256x256 | 4 each | exact |
| shared PB, overlapping, dword 7 of the HW context poked in the first, in the second, in both; own PBs and shared PB one after the other, both poked; own PBs, overlapping, both poked; values 0xdeadbeef and 0xffffffff | 2 each | exact |
| the last, with the second context's words read | 2 each | exact; dword 7 of the second context reads 0x10c63000 before render 1 and 0xdeadbeef after render 1 and after render 2 |
| regtimeline over the DPM and event registers, own PBs (3 runs) and shared PB (2), overlapping | 3 each | exact; 12.7 to 12.9 thousand samples |

All 69 renders of each context were exact (0 wrong inside, outside and at the edges, guard 0) and
no job failed; the kernel's log shows no fault, hang or recovery, and the 18 pokes of the dword
applied once each. The kernel's value of dword 7, the address of its parameter-heap object (E361,
E323), is replaced by the poke and stays through the next render.

**What it shows.**

- Two render contexts run on one parameter buffer, the jobs one after the other or the second's
  submitted before the first's was waited for, and draw what they draw alone: the renders are
  exact [HW]; the EDM, TA and 3D take the shared PB descriptor without a fault and give each
  context its own picture [HW].
- With the jobs submitted together, dword 7 of either context's HW context set to 0xdeadbeef or
  0xffffffff changes nothing: no fault, no wrong pixel [HW]. The word stayed what it was set to, so
  nothing of the kernel or firmware rewrote it [HW]. The word is not read on these paths [infer];
  E361 covered the single-context paths and the cleanup.
- The tool gives each job to the kernel with one submit call after the other (with a second-context
  poke, 30 ms after the first's); that both jobs were in the firmware at once, that the EDM
  switched between the contexts' jobs and that a PB swap happened were not timed or seen, so they
  are not shown to occur [infer].

**What it does not show.** The dataflow's 379 accesses through a base of unknown origin; a context
switch in the middle of a TA (no run interrupts a TA, Q068's route); contexts of different VMs (the
sharing needs one directory); a PB swap while the first context still has its renders to do; the
DPM timelines kept in the data were not analysed for the settle routine's wait (Q036's second half).

**Provenance.** The campaign read the srcversion of the installed module file (modinfo), not of
the loaded module. The run printed E431D4FEB0F36E3C337AD50 for the installed file; that it was
also the loaded module is inferred (the four runs that print it share one boot, 183 to 511 s of
uptime, after the install, with no reload logged). The kit's env.toml was patched after the runs.
The edm/host-events run, E444, was on an earlier boot with a different installed file. This record
uses render_share_pb (fork commit 39).

The linux series was revised after these runs (tip 01cff214d7d2, the one of the control runs of E445
and E446): the debug switches (kregnow's arm, alias_ctx_rw, render_share_pb, tadata_fill) are
disarmed at a firmware load and at a reset, kregnow's arm, read and write and the host-interrupt
restore run under one lock, a render context that shares a PB holds a reference on its donor until
it is freed, and the cleanup commands and the TA data fill are moved into helpers with the same
order and effect. The scripts of these runs reset the GPU before they arm anything, nothing resets
between the arming and its use, and the shared PB's context is closed before its donor, so the
revision does not change the paths the runs used (read against the diff of the two tips and the
scripts) [infer].
