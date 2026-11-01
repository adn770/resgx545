+++
id = "Q034"
question = "does the EDM hold back a TA command whose source or destination sync is incomplete when another context is queued, as E161 reads the pick to do only then?"
unit = "edm"
phase = 10
evidence = ["E161", "E154", "E320"]
terms = ["ta3d_ctl", "cmd_ta.shared"]
+++

The EDM's TA pick takes a context's next TA command only when a list of conditions holds; as read
from the firmware, the checks of the destination and source syncs (instructions `0x760` to `0x78e`)
run only when the TA queue holds a context other than the picked one (E161) [as read].

The one-context half is shown (E320, one run): a lone context's geometry kick whose one source sync
is incomplete (read and write pending values 0x5a5a5a5a against a word that reads 0) starts and
completes, and the scene renders. As a control, the same kick with its transfer-queue sync set
never starts: the pick reads the sync's second pointer, and with it left at 0 the EDM faults.

Open: the two-context half, that the checks hold a command back when another context is queued,
and why they depend on a second context; the destination sync, not tried.

To settle it: two render contexts with commands queued at once (a mode of sgxfive-test that
submits on a second context without waiting): context A's command held back by its transfer-queue
sync (dword 26 and dword 28 both pointing at words that hold what dword 27 and not dword 25), so
it stays queued without a fault; then on context B a command with an incomplete source sync
(expected to stay queued) and one without (expected to run). Repeat with the destination sync.
