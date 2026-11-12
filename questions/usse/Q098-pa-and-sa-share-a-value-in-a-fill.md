+++
id = "Q098"
question = "why do pa_n and sa_n read one value in a fill's pixel task, a mov or ima32 to pa_n being lost, and why does an unwritten one read the job's pixel colour?"
unit = "usse"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E366", "E380", "E484", "E496", "E748", "E820"]
terms = []
+++

In a fill's pixel task pa_n and sa_n read one value: a mov to sa_n sets what both read, a mov to
pa_n changes neither, and unwritten both read the colour the job writes to o0 (0x0da7a000,
0x11110000, 0x33330000, 0x55550000 as the case's colour was), 30 jobs (E380). E366's r1 marker
was that colour.

Narrowed in 11.24 (E484): in a pair of fills a reader that reads an sa nobody wrote (sa6, 2 of 2)
or one set two jobs back and not written by the job before (3 of 3) reads the colour the job
before it wrote (0xC01C0001 and 0xC01C0002, the two writers' colours), the reader writing no colour
before its read. So the unwritten value is what the pixel output holds: the job's own colour when
it has written it (E380) and the one the job before left when it has not [infer; 5 of 5 readers].

Narrowed in 11.25 (E496): `ima32.u pa0, ...` is lost as `mov pa0` is (2 jobs with `ima32.u`, 1 with
`mov`: pa0 read back as before in the same job, 3 of 3), while `ima32.u` to sa0, o0, i1 and i2 is
read back; job 8 read the sa0 value written by `ima32.u` in job 7 (0x79, 2048 of 2048 pixels), which
is also the colour job 7 output, so one job's persistence of an sa0 written by `ima32` is not
separated from the colour rule; the job after it read the same value in pa0, which is also job 8's
colour, so that does not separate the two either; a pa0 nobody wrote read 0xff00ff00 in 1536 pixels
and 0xff203040 in 512 in the first seven jobs of that table, each outputting what it read, the first
value unchecked (Q136). Not shown: that a destination of pa1 to pa4 or an `o` or `g` write is lost
or kept.

What is open: why a mov to pa is lost in a fill (a fill's task with no primary attributes, or
pa_n naming sa_n there); whether the left-over colour is read by every instance or by most
(the 12 odd pixels of the sa writers, Q129); whether the same holds in other task kinds (the
triangle's pixel task has iterated pa).

To settle it: the store-sources probe with the pixel colour written per instance (from the
instance's own place) to tell this instance's colour from the previous one's; the same pa and
sa writes in the triangle's pixel task.

Reading of existing records, 2026-11-09 (analysis, not a measurement). The fill case is wider than
the simulator's refusal says: E380 gave pa0 to pa7 each a marker by `mov` in a fill and a mov to
pa_n was lost for all eight (the 30 jobs), so a `mov` to pa1 to pa7 in a fill is measured, and
only `ima32` to pa1 and above is unmeasured (E496 did pa0). The question is about a fill's pixel
task, while the boot needs the EDM task, whose pa is a different object; this question does not
answer that one. For the EDM task the records give one inference and one prediction. E537's
control reader, before its writer ran, read sa64 = 2 and sa65 = 0x02000000, exactly the pa0 and
pa1 that a tick hands the general task (E532); E536's writer wrote sa64 and it still read 2 in
every reading (3 of 3 rounds and both controls), so a write to sa64 does not take, or the event
path rewrites it. [infer] pa_n of an EDM task may be sa_(64+n): the three words PDS #13 passes
would then land in the task's attribute store at base 64. It makes one prediction no run has
tested, sa66 = 0x01061a70 (E532's pa2); no record read sa66. If it holds, a write to pa2 of an EDM
task is a write to sa66, and E537's writer, which wrote sa65 and stopped the tick, wrote what a
tick hands as pa1 (whether the closed task uses sa65 is Q294's, not shown). The run is a read of
sa64 to sa68 by a firmware task of ours with the verifier as it is, then the writes only if sa66
reads 0x01061a70.

Narrowed 2026-11-10 (S2, E748; the read side of an EDM task, which is not the fill's question). In a
firmware task of ours in the general slot, pa0 to pa4 read what sa64 to sa68 hold in 3 of 3 read
passes, the frozen held-out prediction sa66 = 0x01061a70 held (3 of 3, with sa0 not equal to pa0),
and a marker written to sa67 or sa68 by the allowed mov was read back through pa3 or pa4 in the same
pass and in the next task (3 of 3 markers each), the original values written back afterwards. So for
an EDM task pa_n names sa_(64+n), at least for n = 0 to 4, as the reading of 2026-11-09 predicted.
Not shown: the direction pa to sa (a mov to pa_n of an EDM task is refused by the verifier, so
whether it is lost as in a fill is unmeasured), pa5 and above, and an event that is not a tick. The
question stays open for the fill (why a mov to pa_n is lost there) and for the write direction in an
EDM task.

Narrowed 2026-11-10 (K1 stage e2b, E820; not retired). Write direction in an EDM task (first run of
a `mov` to pa2 to pa4): pa3 aliases sa67 (a marker read back through both in the same pass and the
next, 3 of 3), pa2 aliases sa66 in the same pass (3 of 3) and the next pass finds the old value, a
`mov` to pa4 is lost (neither pa4 nor sa68 changed, same pass and next, 3 of 3); neighbours
unchanged. So no single rule for pa2 to pa4. Open: the fill's lost `mov` to pa_n (this question's
own case), why pa4 differs from pa3, pa5 and above, an event that is not a tick.

Note 2026-11-12 (round 6 housekeeping, decision R6-1 a): Q136's clause "why is pa0 not written by
ima32 or mov" moves here: it is this question's lost write to pa_n (E496: `ima32.u pa0` and `mov
pa0` lost in 3 of 3, while `ima32.u` to sa0, o0, i1 and i2 is read back). Open from it, besides the
fill's `mov`: whether `ima32` to pa1 and above is lost too (E380 measured `mov` to pa0 to pa7).
