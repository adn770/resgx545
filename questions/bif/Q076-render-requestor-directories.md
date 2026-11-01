+++
id = "Q076"
question = "which pages does each bus-interface requestor of a render (the TA, the 3D, the EDM's PB load) need in the directory of the list it translates through (TA3DCtl writable; each of the buffers 6, 7, 8, 10 and 11 alone is not needed: E457), which of the 16 directory lists does each use, and what does a job do whose list was given to another context while it ran?"
unit = "bif"
kind = "hw"
value = "high"
phase = 11
evidence = ["E021", "E023", "E151", "E303", "E314", "E315", "E316", "E319", "E360", "E457", "E573"]
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

Open: that list 1 holds the client's directory (not compared with the client's own), and whether
the buffers 6, 7, 8, 10 and 11 are needed together or in a larger scene (more than two renders, a
partial render, a DPM reload), and the buffers 0 to 5 and 12 to 15 one at a time. From the former
Q006: which directory the EDM's own requestor translates through while it loads a parameter
buffer for a render (whether the block must be writable in the client's directory or any list
that maps it would do). From the former Q083: what the TA and 3D requestors of a job do, and what
the bus interface reports, when the list they translate through is given to another context's
directory while the job runs.

Folded in 11.21: Q006 and Q083 are retired into this question, which is not an answer to either.
What Q006 asked about the kernel's own choice (whether a VM can carry a private copy of the control
block kept in step by the kernel) is not hardware knowledge and is not carried here. How a kick
tells that its directory is in no list (a firmware compare) is Q118, parked as an fw question.

To settle it: read the client directory's physical address (the debugfs files of the VM) and
compare it with CR_BIF_DIR_LIST_BASE1 during a render; rerun with masks of two and of five of the
buffers 6, 7, 8, 10 and 11 and with the partial render of 1024x768 on 0x23 pages (`probe --tri`).

Narrowed in 11.33 (E573, 30 case runs): the buffers 1, 2, 3, 4, 5, 12, 13 and 14 each left out of
the client directory's alias alone leave the renders exact (2 of 2 runs each; the mask bit 15 names
no buffer of the layout and is a control, 2 of 2), and so do the pairs 6+7, 8+10, 10+11 and the
five 6, 7, 8, 10, 11 (2 of 2 each); buffer 0 (0x30000000) left out faults the first job (2 of 2,
bus status 0x91000 at 0x3000b022), the kick having written list 2 with the page directory of the
fault line. The debugfs layout's pd_phys is the EDM's own directory, CR_BIF_DIR_LIST_BASE15 (30 of
30), and differs from BASE1, so the client's directory in list 1 or 2 is still not compared with the
client's own. Not run: pairs of the buffers 1 to 5, larger scenes and a partial render under a
mask, the lists given to another context while a job runs.
