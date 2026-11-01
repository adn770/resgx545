+++
id = "Q156"
question = "which of the differences between the writer whose armed reader did not run within 100 ms (E537: sa and r and i written with sa63 and sa65, p0 = p1 = 1 at the tail call, 1 run) and the writer that was not (E536: no sa63 and sa65, p0 to p3 = 0, 0, 1, 1, 3 of 3 rounds) stops the tick after the closed task is called, and does the closed task use p0 to p3, sa63 or sa65 at all"
unit = "edm"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E537", "E533", "E536"]
terms = ["Event Data Master (EDM)"]
+++

Narrows Q152. E533's task skipped the closed task, E536's called it and kept the tick, and E537's
called it and did not. Candidates: the predicates the closed task finds at its entry (p0 = p1 = 1
against 0, 0, 1, 1), the write of sa63 or sa65 (sa65 held 0x02000000, the value of a tick's `pa1`),
the sa64 write (in both writers), and a first stop after a command that E536's rounds did not
see (E536 was 3 of 3, E537 1 of 1, and the two are different blobs). The writer of E533 and the
earlier wrappers (E532) are not controls: they differ in more than one of these.

To settle it: state3.s cmd 2, 3 and 1, each three times, then cmd 4 last, one reset at most per
stop, the stop rule first (a second stop ends the stage), predictions frozen after E537 and before
the first run. A repeat of cmd 4 alone would say whether the stop repeats.
