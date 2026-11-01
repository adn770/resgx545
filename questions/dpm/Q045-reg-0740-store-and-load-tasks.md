+++
id = "Q045"
question = "what sets the fields of register 0x0740 that the TA kick turns into DPM store and load tasks (a host write reads back 0: E456), does a load task read back the macrotile lists a partial render stores in the RT data's state page, and what accesses the state page (0x20003000 for a context of up to 64x64) when a render follows a kept owner's gone context?"
unit = "dpm"
kind = "hw"
value = "high"
phase = 11
evidence = ["E158", "E256", "E310", "E312", "E456", "E458", "E462", "E464", "E574", "E591"]
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

Folded in 11.21 from Q106 (retired into Q036 and this question; a fold is not an answer). A render
on a second context faults at page 0x20003000 (BIF fault status `0x90004` at `0x200030c1` through
list 1, 6 of 6 runs) after the first context, which kept the DPM owner with render flag bit 3, is
closed, and is exact with both contexts alive (E458, E462); the close leaves the kept words in place
(TA3DCtl dwords 20 and 25 both the first context's RT data + 0x18). For a context of up to 64x64
that page is the TA data's DPM state page (E310), the page this question's store and load tasks use.
Open then: what accesses page 0x20003000 (the slot step storing the kept owner's state through the
second context's directory, or reading the first's), and whether the fault needs the closed
context's memory to be freed or only the context to be gone; the case with the first context's
memory kept was run in 11.34 (E591, below). The owner words themselves are in Q036.

Narrowed in 11.33 (E574): 0x0740 read 0 in every line of 36 more jobs (triangles of 3 to 900
vertices at 4096x4096 in 0x100 to 0x422 pages, 30 of them overflowing into partial renders). The
state page's reader and the page 0x20003000 part are not run: they need a kernel switch (the first
context's memory kept, a poke at the final render's kick).

Narrowed in 11.34 (E591, kernel commits 47 and 48: debugfs render_keep and render_kept, 29 job runs
on the module built before the review's fixes): with the first context's mappings, slot and memory
kept at its close, the second context's render after a kept DPM owner (render flags 0xc) is exact
in 13 of 13 jobs, where it faults at 0x200030c1 without keep (2 of 2, as E458), and TA3DCtl dwords
20 and 25 are cleared as with the first context open. So the fault needs the page unmapped or its
memory gone, not the context's absence. What accesses the page is a store [infer]: after the second
context's render the kept first context's control page (page 1, 16 ramp dwords replaced, word 0
0x00200047), OTPM page (page 2, 20 dwords, word 0 0x04000417) and state page (page 3, 34 dwords,
words 0 and 1 0x00020001 and 2) differ from the ramps put there (9 of 9 jobs), and with bit 2 alone
or no flag nothing is written (6 of 6); the ramps do not change the render (exact in 9 of 9). The
pages were read after the tool exited, so when the store is made, and by what (a hardware task or
the firmware), is not shown, and no read of the pages is seen [infer]; the data cannot tell a page
that is mapped but freed from one that is unmapped. The partial-render half is not tested: a kept
first context that rendered 1024x768 in partial renders holds 18 non-zero dwords in its state page
(4 of 4, E464's finding again), and the tool did not render the second context after an overflowed
render, so a second context's store over that page was not run (Q192). Still open: the first part
(what sets the fields of 0x0740), what the stored words are and at which kick (Q191), and whether a
load task reads a partial render's lists back.
