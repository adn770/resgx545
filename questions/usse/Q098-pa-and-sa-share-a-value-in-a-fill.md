+++
id = "Q098"
question = "why do pa_n and sa_n read one value in a fill's pixel task, a mov to pa_n being lost, and why does an unwritten one read the job's pixel colour?"
unit = "usse"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E366", "E380", "E484", "E496"]
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
