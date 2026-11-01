+++
id = "Q034"
question = "does the EDM start a TA command whose destination or source sync is incomplete when its context is the only one in the TA queue?"
unit = "edm"
phase = 10
evidence = ["E161", "E154"]
terms = ["ta3d_ctl"]
+++

The EDM's TA pick takes a context's next TA command only when a list of conditions holds: a
counted kick and no suspend, the READY bit, a complete transfer-queue sync, a free RT data set
for a first kick, and complete destination and source syncs (E161). As read from the firmware,
the last two checks (instructions `0x760` to `0x78e`) run only when the TA queue holds a context
other than the picked one; with a single context queued they are skipped [as read]. A command
whose syncs are not complete would then start whenever it is alone in the queue, which defeats
the syncs for the one-client case. Why the checks depend on a second context is not shown, and
nothing in E161 runs the firmware.

To settle it: two render contexts on the laptop. Submit to context B a TA command whose source
sync names a sync object with a pending count that no job will reach yet, first with context A
idle and then with a command queued on A. Record with the debugfs files whether B's TA starts
(its TA status words and the request bits of E154) before the sync object is completed from the
host. Repeat with the destination sync instead of a source sync.
