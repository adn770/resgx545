+++
id = "Q097"
question = "does a store take pa or sa as its data source, and what does it store instead?"
unit = "usse"
phase = 11
evidence = ["E366", "E380"]
terms = []
+++

Answered (E380): a store takes pa and sa as its data source and stores what a mov of the same
register reads: in 30 jobs (three probes, two or three runs each) every stad from pa0-pa7 and
sa0-sa7 stored the value the controls' moves of pa0, pa1, sa0 and sa1 read, and the r and o stores
their registers. E366's r1 marker was the register's own content: in a fill pa_n and sa_n read one
value, a mov to sa_n sets it, a mov to pa_n does not, and unwritten it holds the job's pixel colour
(as E366's r1 was). So there is no restriction on the store's data source to put in isa/usse.

What is left: why a fill's pa_n and sa_n read one value and a mov to pa_n is lost (Q098).
