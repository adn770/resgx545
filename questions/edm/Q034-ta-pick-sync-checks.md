+++
id = "Q034"
question = "does the EDM hold back a TA command whose destination sync is incomplete when another context is queued (source and transfer-queue syncs: E450)?"
unit = "edm"
phase = 10
evidence = ["E161", "E154", "E320", "E450"]
terms = ["ta3d_ctl", "cmd_ta.shared"]
+++

The EDM's TA pick takes a context's next TA command only when a list of conditions holds; as read
from the firmware, the checks of the destination and source syncs (instructions `0x760` to `0x78e`)
run only when the TA queue holds a context other than the picked one (E161) [as read].

The one-context half is shown (E320, one run): a lone context's geometry kick whose one source sync
is incomplete (read and write pending values 0x5a5a5a5a against a word that reads 0) starts and
completes, and the scene renders. As a control, the same kick with its transfer-queue sync set
never starts: the pick reads the sync's second pointer, and with it left at 0 the EDM faults.

Answered for the source sync and the transfer-queue sync by E450 (two render contexts in the VM,
three runs of each case): with a second context in the VM, a command with an incomplete source sync
or transfer-queue sync is held (the job hung and was lost), whichever context holds it, and the
other context's job completes (7 cases overlapping, 3 sequential). The second context's command
is held also when the first context's job has finished and nothing of it is queued, so what the
check needs is another context in the TA queue, not another command. A lone context's command
starts (E320).

Open: the destination sync (command dword 15), not tried, and whether the other context is in the
queue from its creation or from its first job.

To settle it: a command whose destination sync list (dword 15, naming a sync object whose write
pending value is ahead of the word it points at) is incomplete, on the first and the second context,
overlapping and sequential, with the cases of E450 as controls; and a second context created after
the first's job, to separate creation from the first job.
