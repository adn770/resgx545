+++
id = "Q015"
question = "what makes VDM state word 1 with bits 11:9 = 7 hang some runs of a job and complete others?"
unit = "vdm"
phase = 6
evidence = ["E060", "E185", "E299", "E300"]
terms = ["VDM_STATE1.BITS11_9"]
+++

The question as first asked, why the sweep's job hangs with bits 11:9 = 7 (`vdm:1^=0xa00`) and the
probe job with the same word renders, is answered in part (E299): not by the job builder or the
pixel program. Split three ways on the library's triangle job and three ways on the probe's, one run
each, three of six jobs hung, and in this run the hangs followed the pixel readback exactly: the
three jobs with every pixel read back (the library job, the probe with a shader writing its colour
and the original probe) hung, the three without it completed, whatever the render dump. The
library job that completed drew the job's own image with render memory byte for byte that of bits
11:9 = 2. The earlier table ran the other way in both its runs (its sweep hung without the readback,
its probe completed with it, E060 and E185), so that the readback does not decide the hang from run
to run rests on the two tables together [infer]. The unpoked five-copy job also hung once with
every pixel read back (E300, first run).

What is open: what decides whether a job with 7 hangs, whether the readback takes part in it, and
what the value selects when it does not hang (E185 and E299 see it tile as 2; Q047 asks what the
field selects).

To settle it: the library job with 7 ten times in a row with every pixel read back and ten times
without, alternating, then the same after a fresh firmware boot (kernel log and the `regtimeline`
snapshot of the VDM and TA registers around each), to see whether the hangs follow the readback,
the GPU's state before the job or come at random; the control word with the readback the same
number of times, for the rate of readback hangs without 7; the same with 3 and 5, which have
rendered every time so far.
