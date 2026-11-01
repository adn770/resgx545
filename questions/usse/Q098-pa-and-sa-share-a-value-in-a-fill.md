+++
id = "Q098"
question = "why do pa_n and sa_n read one value in a fill's pixel task, a mov to pa_n being lost, and why does an unwritten one read the job's pixel colour?"
unit = "usse"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E366", "E380"]
terms = []
+++

In a fill's pixel task pa_n and sa_n read one value: a mov to sa_n sets what both read, a mov to
pa_n changes neither, and unwritten both read the colour the job writes to o0 (0x0da7a000,
0x11110000, 0x33330000, 0x55550000 as the case's colour was), 30 jobs (E380). E366's r1 marker
was that colour.

What is open: why a mov to pa is lost in a fill (a fill's task with no primary attributes, or
pa_n naming sa_n there); whether the unwritten value is this instance's colour or the previous
one's; whether the same holds in other task kinds (the triangle's pixel task has iterated pa).

To settle it: the store-sources probe with the pixel colour written per instance (from the
instance's own place) to tell this instance's colour from the previous one's; the same pa and
sa writes in the triangle's pixel task.
