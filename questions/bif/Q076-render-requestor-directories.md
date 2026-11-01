+++
id = "Q076"
question = "do the TA and 3D requestors of a render need any of the EDM's buffers 6, 7, 8, 10 and 11 in the client directory beyond the writable TA3DCtl alias (each alone is not needed: E457), and is the directory in the list they translate through the client's?"
unit = "bif"
phase = 11
evidence = ["E021", "E023", "E151", "E457"]
terms = ["CR_BIF_DIR_LIST_BASE1", "CR_BIF_BANK0"]
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

Open: that list 1 holds the client's directory (not compared with the client's own), and whether
the buffers 6, 7, 8, 10 and 11 are needed together or in a larger scene (more than two renders, a
partial render, a DPM reload), and the buffers 0 to 5 and 12 to 15 one at a time.

To settle it: read the client directory's physical address (the debugfs files of the VM) and
compare it with CR_BIF_DIR_LIST_BASE1 during a render; rerun with masks of two and of five of the
buffers 6, 7, 8, 10 and 11 and with the partial render of 1024x768 on 0x23 pages (`probe --tri`).
