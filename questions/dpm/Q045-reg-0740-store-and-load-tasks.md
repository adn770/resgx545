+++
id = "Q045"
question = "what sets the fields of register 0x0740 that the TA kick turns into DPM store and load tasks (a host write reads back 0: E456), and does a load task read back the macrotile lists a partial render stores in the RT data's state page?"
unit = "dpm"
phase = 11
evidence = ["E158", "E256", "E310", "E312", "E456", "E464"]
terms = ["CR_DPM_TASK_STATE", "CR_DPM_TASK_CONTROL", "CR_DPM_STATE_CONTEXT_ID"]
+++

On a first kick, or with command flag 0x8, the TA kick clears the DPM state of its context slot,
then issues a store task (code 1) with an index taken from a 9-bit field of register 0x0740, the
field chosen by the DPM context slot, and a load task (code 4), each only if that field is not zero
(E158).

0x0740 reads 0 in every sample of every job run (E256), the twelve partial renders of the 11.9
timelines included (E312). What a DPM store writes is now seen in another path: a partial render,
under DPM context slot 2, leaves the RT data's state page (`CR_DPM_STATE_BASE0`) holding sixteen
macrotile page lists and the global list (E310); every job without one leaves that page, the
control page and the OTPM page zero. So the store writes per-macrotile page lists; what the 0x0740
index counts, and whether a load reads these lists back, is not seen.

Narrowed by E456 (debugfs kregnow, linux fork commit 41): a host write to 0x0740 does not stay. The
register read 0 right after each of 156 writes (values 0x1ff to 0x3ffff in both fields, idle and
beside running renders) and in 64 of 64 samples after a job, and the 76 renders on one and two
contexts were exact. So the host does not set the fields through this register by a write at these
moments [infer: a status or derived register]. The partial-render half did not run in E456: the
tool reported an overflowing scene as a failed job (12 of 12) and dumped nothing.

Narrowed by E464 (`tri --keep-overflow --dump-each`, the partial-render half): the 1024x768 scene in
0x28 pages overflowed in 16 of 16 jobs and the tool dumped the TA data after each. The state page
holds 18 non-zero dwords after the partial renders (ten of them printed, three of the five pairs
read (1<<16 | n) and n, other values after a second job) and the control and OTPM
pages stay zero, in 2 of 2 runs; a ramp poked into the state page keeps 990 of 1024 dwords (34 left
the ramp) and the image does not change; flipping the second render's flag 0x8 changes nothing in
the page; 0x0740 reads 0 after every job and after writes of 0x200 and 0x3fe00 (2 of 2 each).

Open: what sets the fields (the DPM unit, a register the host writes elsewhere, a value from the
firmware's own state), whether a write is kept while a TA runs, and whether a load task reads a
partial render's lists back (the ramp was overwritten by the partial renders' store before any
final render could read it).

To settle it: sample 0x0740 with regtimeline during the TA of a render that overflows a small PB,
on the same context kicked again with command flag 0x8; poke the state page between the partial
render and the final render (a kernel switch that fills a page at the final render's kick) and
compare the image; read what the 18 dwords count.
