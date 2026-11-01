+++
id = "Q083"
question = "what bounds TA/3D control block dword 49 at 15 values, and is it a count of render contexts or an index the EDM gives each one?"
unit = "render"
phase = 11
evidence = ["E303", "E314", "E315", "E316", "E319", "E360"]
terms = ["ta3d_ctl.render_context_count", "CR_BIF_DIR_LIST_BASE1"]
+++

The main part is answered (E360, one run with 14 and with 16 render contexts alive at once). Dword
49 is the index of the bus interface's directory list the EDM last gave a context: the k-th first
kick after a reset writes the context's page directory into `CR_BIF_DIR_LIST_BASE1` to `BASE14`
(k 1 to 14) or `BASE0` (the 15th) and the dword reads k mod 15; `BASE15` keeps the EDM's own
directory. A 16th live context takes list 1 from the first, whose next kick takes list 2; every
context renders its second render exactly. In the EDM dataflow the word is read and written in
the one routine that writes computed register numbers and `CR_BIF_CTRL`.

What is open: how the kick tells that its directory is in no list (a compare against the lists'
registers or a per-context record), and what a job of a context whose list was taken while the job
ran does.

Offline in 11.16: edm_dataflow.md holds the routine's registers (section 3) but not the
comparisons that decide whether a directory is in a list, so the dataflow cannot say how the kick
tells; extending it to that routine's compares is the missing piece. No hardware run. Status:
narrowed, not answered.
