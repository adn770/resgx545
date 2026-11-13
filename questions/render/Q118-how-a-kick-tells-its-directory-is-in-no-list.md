+++
id = "Q118"
question = "how does the firmware's kick tell that its context's page directory is in none of the bus interface's directory lists (a compare against the lists' registers, or a per-context record)?"
unit = "render"
kind = "fw"
phase = 11
evidence = ["E360", "E592"]
terms = ["ta3d_ctl.render_context_count", "CR_BIF_DIR_LIST_BASE1"]
+++

Split off in 11.21 from the former Q083, whose hardware part is carried by Q076. Known from E360
(one run, with 14 and with 16 render contexts alive at once): dword 49 of the TA/3D control block is
the index of the bus interface's directory list the EDM last gave a context. The k-th first kick
after a reset writes the context's page directory into `CR_BIF_DIR_LIST_BASE1` to `BASE14` (k 1 to
14) or `BASE0` (the 15th) and the dword reads k mod 15; `BASE15` keeps the EDM's own directory. A
16th live context takes list 1 from the first, whose next kick takes list 2; every context renders
its second render exactly. In the EDM dataflow the word is read and written in the one routine that
writes computed register numbers and `CR_BIF_CTRL`.

Open: how the kick tells that its directory is in no list (a compare against the lists' registers
or a per-context record). It is the closed firmware's own routine, not a hardware fact, so it is
parked.

Offline in 11.16: edm_dataflow.md holds the routine's registers (section 3) but not the
comparisons that decide whether a directory is in a list, so the dataflow cannot say how the kick
tells. To settle it: extend the dataflow to that routine's compares (offline, no hardware run).

Round 12 cites: E592 (the context's directory word equals the list register the kick wrote, 15 of 15
jobs).
