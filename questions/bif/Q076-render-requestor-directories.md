+++
id = "Q076"
question = "which pages does each bus-interface requestor of a render (the TA, the 3D, the EDM's PB load) need in the directory of the list it translates through (TA3DCtl writable; each of the buffers 6, 7, 8, 10 and 11 alone is not needed: E457), which of the 16 directory lists does each use, and what does a job do whose list was given to another context while it ran?"
unit = "bif"
kind = "hw"
value = "high"
phase = 11
evidence = ["E021", "E023", "E151", "E303", "E314", "E315", "E316", "E319", "E360", "E457",
            "E573", "E592", "E745", "E761"]
terms = ["CR_BIF_DIR_LIST_BASE1", "CR_BIF_BANK0", "ta3d_ctl", "ta3d_ctl.render_context_count"]
+++

A transfer's pixel side translates through the client's directory and read-only aliases of the
EDM's buffers suffice (E021, E151). Render jobs from userspace draw exactly (E023).

Narrowed by E457 (debugfs alias_skip, linux fork commit 42, with regtimeline on the bus interface):
during a completed render CR_BIF_BANK0 reads 1 for the TA index and the 3D index, and
CR_BIF_DIR_LIST_BASE1 holds a directory (12 of 12 completed runs). With any one of the buffers 6,
7, 8, 10 or 11 left out of the client directory's alias the renders are exact (10 of 10); with
TA3DCtl left out alone or with buffers 6 to 11 (4 of 4 runs), or read-only (2 of 2), the first job
faults at its page through list 1, and with every buffer left out it faults at the EDM's code heap,
again through list 1.

Known from E319 (one run, the first part of the former Q006): with the TA/3D control block mapped
read-only in the client's directory (debugfs `alias_ta3d_ro`) the first kick faults on the block's
page (bus status 0x80400) before the PB load writes dword 46 and before the DPM slot is taken; the
job stalls and the EDM answers no command until a reset. So the EDM's write to the block, made while
it loads the parameter buffer, translates through the client's directory and needs it writable
there.

Known from E360 (one run with 14 and with 16 render contexts alive, the former Q083): dword 49 of
the control block is the index of the directory list the EDM last gave a context: the k-th first
kick after a reset writes the context's page directory into `CR_BIF_DIR_LIST_BASE1` to `BASE14`
(k 1 to 14) or `BASE0` (the 15th) and the dword reads k mod 15; `BASE15` keeps the EDM's own
directory. A 16th live context takes list 1 from the first, whose next kick takes list 2; every
context renders its second render exactly.

Open (as written in 11.21; see the corrections in 11.34 below): that list 1 holds the client's
directory (E360 compared it with BASEk for k = 1 to 14 in 11.19 and E592 does so after a reset in
11.34; the statement here that it was not compared was wrong), and whether the buffers 6, 7, 8, 10
and 11 are needed together or in a larger scene (more than two renders, a partial render, a DPM
reload), and the buffers 0 to 5 and 12 to 15 one at a time. From the former
Q006: which directory the EDM's own requestor translates through while it loads a parameter
buffer for a render (whether the block must be writable in the client's directory or any list
that maps it would do). From the former Q083: what the TA and 3D requestors of a job do, and what
the bus interface reports, when the list they translate through is given to another context's
directory while the job runs.

Folded in 11.21: Q006 and Q083 are retired into this question, which is not an answer to either.
What Q006 asked about the kernel's own choice (whether a VM can carry a private copy of the control
block kept in step by the kernel) is not hardware knowledge and is not carried here. How a kick
tells that its directory is in no list (a firmware compare) is Q118, parked as an fw question.

To settle it (as written in 11.21; done in 11.34 for the comparison, the five and the partial
render): read the client directory's word (debugfs render_words `ctx:2`, which has shown it since
11.17, not "the debugfs files of the VM") and compare it with CR_BIF_DIR_LIST_BASE1 during a render;
rerun with masks of two and of five of the buffers 6, 7, 8, 10 and 11 and with the partial render of
1024x768 on 0x23 pages (`probe --tri`).

Narrowed in 11.33 (E573, 30 case runs): the buffers 1, 2, 3, 4, 5, 12, 13 and 14 each left out of
the client directory's alias alone leave the renders exact (2 of 2 runs each; the mask bit 15 names
no buffer of the layout and is a control, 2 of 2), and so do the pairs 6+7, 8+10, 10+11 and the
five 6, 7, 8, 10, 11 (2 of 2 each); buffer 0 (0x30000000) left out faults the first job (2 of 2,
bus status 0x91000 at 0x3000b022), the kick having written list 2 with the page directory of the
fault line. The debugfs layout's pd_phys is the EDM's own directory, CR_BIF_DIR_LIST_BASE15 (30 of
30), and differs from BASE1, so the client's directory in list 1 or 2 was not compared with the
client's own in that run (the comparison was possible, with render_words ctx:2: corrected in 11.34
below). Not run: pairs of the buffers 1 to 5, larger scenes and a partial render under a
mask, the lists given to another context while a job runs.

Narrowed in 11.34 (E592, 15 jobs; also correcting the two statements above that the client's
directory was not compared): the PD word of the render context's HW context (debugfs render_words
`ctx:2`, the VM's directory by construction) equals the list register the kick wrote in 15 of 15
jobs: CR_BIF_DIR_LIST_BASE1 after the first kick following a reset (3 of 3), the k-th process's
context in BASEk for k = 1 to 4 (4 of 4; E360 had it for k = 1 to 14), BASE1 for a partial render
of 1024x768 on 0x28 pages under alias_skip masks 0, 0xc0 and 0xdc0 (6 of 6, identical), and never
BASE15, the EDM's own directory, which the debugfs layout's pd_phys shows; a second context of the
same VM, rendered, took no list (BASE2 stays 0, 2 of 2) [infer: the EDM finds the directory already
in a list, Q118]. So of "which of the 16 lists does each use" the answer is: the kick's first-use
rule, list k for the k-th VM since a reset, is E360's and E592's, and the lists BASE1 to BASE14 hold
client directories; which requestor translates through which list at one time is not told apart.
Still open: which pages each requestor needs together (the buffers 0 to 5 in pairs, larger scenes
with more than two renders, a DPM reload under the masks), and what the requestors do, and what the
bus interface reports, when their list is given to another directory while the job runs (no switch
writes the list registers). H76-D, H76-P and H76-S were not blind: a pilot on the old module had
shown list 1 (E592).

Narrowed 2026-11-09 (S1, E745; a frozen held-out result with a passing control). Of the buffers 1
to 5, none of the pairs {1,2}, {1,3}, {2,3}, {4,5} and {1,5}, and not the five together, is needed
by a two-render job: left out of the client directory's alias, each leaves the renders exact (2 of 2
runs each, 12 of 12), and 6, 7, 8, 10 and 11 left out together are not needed over three renders
(2 of 2); a pair needed together (HJ) is refuted for these, and the single-buffer reading (a buffer
is needed only if leaving it out alone faults) holds. The control, buffer 0 left out, faulted
0x91000 at 0x3000b021 (2 of 2; E573 logged 0x3000b022). Post hoc (read after the run, from the
kept output and not held out): the two 1024x768 jobs on 0x23 pages (P = 0x23, both renders
overflowed) with the mask 0xdc0 were exact, diff 0, with identical target hashes in both runs; the
frozen scorer labelled them "split" through a pattern that does not match `tri: 0 of 2 renders ok,
2 overflowed`. The mask 0x1f of the other job includes buffer 0, so its fault (2 of 2) is buffer 0's
and says nothing about a pair among 1 to 4. Still open: a partial render under a mask as a frozen
result, a buffer reassigned within a job, which list each requestor walks, pairs among 12 to 15.

Narrowed 2026-11-10 (S1b, E761; the partial-render case under a mask, a frozen held-out result with
its controls). Two 1024x768 renders that both overflow the parameter buffer at render_pb_pages =
0x23 were exact (every diff 0, the same two target hashes as with no mask) with the mask 0x1e,
buffers 1 to 4 left out of the client directory's alias together, in 2 of 2 runs, and, as a repeat
of S1's post hoc reading, with buffers 6, 7, 8, 10 and 11 left out in 2 of 2; the control with
buffer 0 left out faulted 0x91000 at 0x3000b021 (as in S1; E573 logged 0x3000b022) and the no-mask
control was exact. So a partial render does not need buffers 1 to 4 together or 6, 7, 8, 10 and 11
together in that directory. Still open: which list each requestor walks, a buffer reassigned within
a job, pairs among 12 to 15, a partial render under other masks, and what the requestors do when
their list is given away while a job runs.
