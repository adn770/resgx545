+++
id = "E450"
claim = "With two render contexts in a VM, a TA command with an incomplete transfer-queue sync (dword 25 set, dwords 26 and 28 naming a zero word) or an incomplete source sync does not complete (job hung, context lost after 4 s) in 3 of 3 runs of every case, whichever context holds it, while the other context's job completes in the cases where only one is held; the second context's command with such a sync is held also when the first context's job has finished (3 of 3 runs each); the destination sync was not tried"
unit = "edm"
method = "probes/edm/ta-sync-two-contexts.toml and probes/edm/ta-sync-second-first.toml on the laptop (direct cable), linux fork 01cff214d7d2 with the debug option on, module srcversion FC6EB50DEF21E3A6249727F (the loaded module, read from /sys/module, equal to the installed file's modinfo; both printed by the run), sgxfive-test tri -n 1 --ctx2 --overlap [--wait-second] --wait-ms 4000 with the TA command's words poked through the kernel poke ta:N before the kick (first context: --kpoke-render; second: --kpoke-render2, 30 ms after the first's job is submitted): transfer-queue sync = ta:25 = 0x5a5a5a5a, ta:26 and ta:28 = a zero word of the context's page (the context's ctx:4 less 0x100 plus 0x280: 0x32411280 for the first, 0x32423280 for the second); source sync = ta:33 = 1, ta:34 and ta:36 = 0x5a5a5a5a, ta:35 and ta:37 = the same word; the second run waits for the second context's job first (--wait-second, which needs --ctx2 and --overlap) so that a first job that never ends does not hide the second's; seven cases overlapping and three sequential, three runs each (30 runs), the GPU reset before each; the first run (21 runs, seven cases) waited for the first context's job first"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["edm-ta-sync-two-contexts", "edm-ta-sync-second-first"]
terms = ["ta3d_ctl", "cmd_ta.shared"]
+++

**What runs.** E320 started a lone context's command with an incomplete source sync and held one
with the transfer-queue sync set (the pick reads the second pointer, here the same zero word, so
that the sync is incomplete only by its first word). E161 read the pick's source and destination
sync checks (3d.md section 4.2 step 6) as run only when the TA queue holds another context. Here
two contexts exist in the VM and both jobs are submitted before either is waited for.

**Results** (second run, three runs of each case, identical in all three; "held" is a job that
did not complete in 4 s and was lost):

| poked | first context's job | second context's job |
|---|---|---|
| nothing | completes, exact | completes, exact |
| first: transfer-queue sync | held | completes |
| first: source sync | held | completes |
| second: transfer-queue sync | completes | held |
| second: source sync | completes | held |
| first: transfer-queue sync, second: source sync | held | held |
| both: source syncs | held | held |
| sequential, nothing poked | completes, exact | completes, exact |
| sequential, second: source sync | completes | held |
| sequential, second: transfer-queue sync | completes | held |

The first run (the first context's job waited for first) gave the same first-context outcomes in all
21 runs; the second's job was not waited for when the first was held. The images of the jobs that
completed beside a held one were not checked (the tool stops at the failed job); the controls'
images, both contexts, were exact in 6 of 6 runs.

**What it shows.**

- With a second render context in the VM, a command with an incomplete source sync is held back
  and its job hangs, while the other context's job completes: 3 of 3 runs for each context [HW].
  With one context in the VM the same command starts (E320). So the source sync check is made when
  the TA queue holds another context [HW]. That the other context's command is taken first, in
  its place, is read from that job completing while the held one hangs [infer].
- The other context need not have a command queued: the second context's command was held in the
  sequential cases, where the first context's job had finished (3 of 3 runs for each sync) [HW].
  What counts is that the first context is in the queue, not that it has a command; whether it
  is in the queue as soon as it is created, or after its first job, was not separated [infer].
- The transfer-queue sync holds the command whichever context holds it (3 of 3 each), as in E320
  [HW].
- That the held command stays queued, rather than being dropped or started late, is read from the
  hang: the job never completed in 4 s and the kernel's recovery followed [infer].

**What it does not show.** The destination sync (command dword 15), the sync's complete side (a
command with a source sync that is complete, beside another context), more than two contexts, and
how long a held command waits if the other context keeps the TA busy.

**Provenance.** The first run (seven cases, 21 runs, edm/ta-sync-two-contexts) used the tool
before its --wait-second option, sha256 ddd670a1... in its env.toml; the second run (30 runs,
edm/ta-sync-second-first) used the tool with the option, sha256 7de509d3.... Both were built from
source not yet committed, which was later committed in f63c7d19.
