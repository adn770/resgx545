+++
id = "Q194"
question = "does a load that is not waited for land by itself in a firmware (EDM) task, at what distance, and is that a property of the task, of the bypass flag or of the page (E602: the new value in 32 of 32 stores after 32 loads with no wdf, 3 of 3 jobs; E517: a fill's load landed after 40, 100 and 128 nops and not after 48 and 64)"
unit = "edm"
kind = "hw"
value = "low"
phase = 11
evidence = ["E517", "E602"]
terms = []
+++
E602's control (command 9 of `p1137_wdf`, three jobs): 32 `ldad.bypassl1` into r20 to r51 from the
first input block, over old values loaded from the second block and waited for, then 32 `stad` of
the same registers with no `wdf` between: 96 of 96 stores wrote the new value, where the prediction
(from E517, a fill) was at least 28 of 32 old in every job. So "a load not waited for is read old"
was not seen in a firmware task at a distance of 32 instruction slots, and the 21 jobs of E602 with
a `wdf` (stores 3 to 101 slots after the loads) show that loads, one `wdf` and the stores is
sufficient, not that the `wdf` waits or is needed. It may be that the loads of a task land in order
within that distance, that `.bypassl1` loads from the results page are quicker than the loads of
E517 (the scratch buffer), or that 32 is past the latency; one distance and one task do not tell.

To settle it: the same task with the number of instructions between the loads and the stores varied
(0, 1, 2, 4, 8, 16, 32 and 64 `nop`), one load and several, `.bypassl1` against the other flags the
verifier accepts, loads from the first and the second page base, and a `wdf` before the stores as
the control. Until then the backend keeps the `wdf` ([infer]: the hardware may make no promise
either way).

Noted 2026-11-09: near duplicate of Q146, not merged (both ask when a load that is not waited for
lands (E517); Q194 adds the firmware task). A merge or a fold decides which text survives.
