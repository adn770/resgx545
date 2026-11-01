+++
id = "Q076"
question = "which page directory do a render's TA and 3D requestors translate through, and do read-only aliases of the EDM's buffers suffice there as they do for the transfer path?"
unit = "bif"
phase = 11
evidence = ["E021", "E023", "E151"]
terms = ["CR_BIF_DIR_LIST_BASE1", "CR_BIF_BANK0"]
+++

A transfer's pixel side translates through the client's directory and read-only aliases of the EDM's
buffers suffice (E021, E151). Render jobs from userspace draw exactly (E023).

What is open (3d.md §14): the same for a render's TA and 3D requestors.

To settle it: on the laptop, CR_BIF_BANK0 and the directory list registers sampled with regtimeline
during the TA and the 3D of a render on a client context, and the render rerun with the EDM's
buffers aliased read-only and not at all in the client directory.
