+++
id = "Q130"
question = "when does a load on one counter land while a wdf waits on another: why four ldad on drc0 issued after a wdf drc1 that waited for four ldad on drc1 landed in 8 of 10 runs, and four ldad on drc1 after two ldr on drc2 never did in 10"
unit = "usse"
kind = "hw"
value = "low"
phase = 11
evidence = ["E479"]
terms = []
+++

E479: a wdf drcN returns when its own counter's loads are done, and loads of another counter issued
after them are complete or not by timing: 0 of 10 runs with markers for the two cases with drc0
first (a wait on four drc0 ldad), 2 of 10 for drc0 loads after a wait on four drc1 ldad, and 10 of
10 for four drc1 ldad after a wait on two ldr (the data hold one of the ten runs; the counts are
those of scratch runs recounted by the reviewer).

What is open: the latency of ldad and ldr in time (the runner records none per case), whether the
loads of one counter are served in order against another's, and a wait that is long enough to cover
the others. To settle it: the same cases with the time of each load (a timer read before and after
the wdf) and a series of wait lengths, the wdf drc1 and the unwaited load counters (drc0, drc1,
drc2, drc3).
