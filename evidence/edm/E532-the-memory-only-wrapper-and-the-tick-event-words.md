+++
id = "E532"
claim = "A stad from a firmware task of our own lands, and the tick event hands the task pa0 = 0x2, pa1 = 0x02000000 and pa2 = 0x01061a70 in 2 of 2 runs: a wrapper that reads a command dword of its results page (ldad.bypassl1, wdf) and stores pa0, pa1, pa2 and a marker, then idf drc0,bif, wdf drc0 and the state flag, finished within the tool's 100 ms of the command with all four dwords stored in 2 of 2 runs; the prediction declared before the runs, that a tick has pa1 = 0, was falsified (pa1 has bit 25 set)"
unit = "edm"
method = "as E531 (srcversion 7ED723C25D78D7FCB3C08C1, own_arm slots=0x1 entry=0 trc=8, no register written): asm/fwtask/mem.s (31 instructions, 290 bytes, command 1) armed in slot 0; the host wrote the results page's command dword last and read the page back; runs p1129-s3-mem and p1129-s3b-mem (one command each). The stage's own criteria were the state flag at 2, the command back at 0, the run id echoed and the marker 0x5a5a1129 in the fourth result dword. The prediction about pa1 is a separate row of the frozen predictions (sha256 38e364de9a46535b82cf9f045eab84d19d2b112f7907ffd2cd38bf4514f67183), not one of those criteria. The tool's verdict S3_mem was false in both runs because that row failed; after the first run the tool recorded the criteria apart from the prediction (a function flag, true in p1129-s3b-mem), so the first run's verdict file does not carry it and the criteria for it are read here from its page, which holds the same four dwords. The second run is the same experiment under a new name. A firmware task, not a client pixel task"
tiers = ["HW", "RE", "infer"]
date = "2026-11-08"
data = ["firmware-tasks-memory-only"]
terms = ["Event Data Master (EDM)", "CR_EVENT_TIMER"]
+++

**Results.** [HW] The task found its command (the results page, read through `ldad.bypassl1`, is
seen by the task a few hundred microseconds after the host wrote it) and stored `pa0` = 0x00000002,
`pa1` = 0x02000000, `pa2` = 0x01061a70 and the marker 0x5a5a1129; the host read them with the state
flag at 2 and the command back at 0, the echoed run id equal. Two runs, the same four values. `pa2`
is 0x10 below the value the boot writes to the EDM timer (the timer clock word 0x61a80 with bit 24,
E008). The two runs were two fresh boots with their commands at different tick numbers and read the
same 0x01061a70, so the value looks constant, not a counter read at a varying tick [infer]; the 0x10
offset is unexplained. `pa0` = 2 is the tick (the microkernel's tick handler tests `pa0` bit 1
**[RE]**, as `sgx-sim` has it).

**Falsified prediction.** Declared before the first run: `pa1` = 0 for a tick (E146, E155: a tick
has nothing in `ir1`). Seen: `pa1` = 0x02000000, bit 25, which PDS #13's 24-bit mask (E146) does not
look at, in 2 of 2 runs. Which event or state sets it is answered by E746 (a count byte). The
stage's own criteria
(done, command cleared, run id, marker) were met in both runs, so the stage's function stands and
only the prediction failed.

**First stad.** [HW] A `stad` from an EDM task changes the page the host reads, with an `idf` and a
`wdf` before the state flag in these two runs; the variant without the `idf` is in E534 (X9).

**Not shown.** The events of a host kick and of a job (Q033): only ticks were observed here, and a
kick was not caused. Whether `pa1` is the same on every tick (the two runs each read one).

**Correction 2026-11-10:** The measurements are unchanged. The inference that pa2 "looks constant,
not a counter" is withdrawn: pa2 is the EDM's EVENT_TIMER sampled for the event (bits 31:24 = 0x01,
bits 23:0 counting down from 400000 core clocks), and a tick served at once samples it 16 clocks
after its own reload, which is why two ticks gave 0x01061a70. A kick read at three phases gave three
other values that agree with the CR_TIMER stamps within 5.3 units (E746), and all 138 events of 14
client jobs had pa2 in that format and range (E747, frozen, held out); the 0x10 offset is the delay
after the reload. pa1 bit 25 is bit 1 of the count byte pa1 bits 31:24 (2 after the arm), not an
event bit (E746).
