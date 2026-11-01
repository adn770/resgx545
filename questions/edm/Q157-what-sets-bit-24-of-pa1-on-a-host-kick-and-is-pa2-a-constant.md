+++
id = "Q157"
question = "what sets bit 24 of pa1 on a host kick (E538: 0x03000000 in 3 of 3 runs, against a tick's 0x02000000: bit 24 and bit 25 are outside the 24 bits PDS #13 reads), and is pa2 a constant (0x01061a70 in 5 of 5 events across five boots: 2 ticks, 3 kicks) and not a timer"
unit = "edm"
kind = "hw"
value = "low"
phase = 11
evidence = ["E538", "E532", "E146"]
terms = ["Event Data Master (EDM)", "CR_EVENT_TIMER"]
+++

Beside Q153 (bit 25). The stubs log the raw `pa1` and test it with bit 25 cleared; a kick has bit
24 as well. Open: the meaning of bit 24 (a `CR_EVENT_STATUS` bit would be below 24, E146), whether
the TA finished and end of render events set others (Q033's Q2 was not run), and `pa2`: E532 read
it as the EDM timer less 16 and called it a running value [infer], but it is the same in five
events at different times in five boots, so it looks like a constant that the boot wrote and the
offset of 16 is unexplained. A reading of `pa2` after a pause of seconds (a slow task before the
read, E539) would show whether the stub's `pa2` is the value at the time of the event.
