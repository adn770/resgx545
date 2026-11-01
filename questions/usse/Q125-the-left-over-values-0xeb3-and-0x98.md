+++
id = "Q125"
question = "which code leaves 0xeb3 and 0x98 in pclink and 1101, 0101, 0001 or 1111 in p0-p3 of the instances that do not read the last job's value, and why do they come in aligned 2 x 2 quads of pixels?"
unit = "usse"
kind = "hw"
value = "low"
phase = 11
evidence = ["E475", "E477", "E484"]
terms = ["Universal Scalable Shader Engine (USSE)"]
+++

E475: of 2048 pixels, 4 to 76 of a pclink reader job read 0xeb3 (and 0x98 in 36 to 76 pixels of some
jobs) instead of the value the writer left, in aligned 2 x 2 quads of pixels (every deviant pixel
has its x^1, y^1 and diagonal neighbours deviant too, in all ten readers), at positions that change
from job to job (not from run to run: usse-pclink-pixels ran once). E477: 16 to 36 pixels of a
predicate reader job read other patterns. Neither 0xeb3 (3763) nor 0x98 (152) was written by any of
these jobs. E484, a second table of predicate readers that reads one predicate as the pixel, has
7 reader jobs with deviant pixels, 15, 15, 62, 66, 67, 71 and 75 of 2048, none a multiple of four,
so in that table the deviant pixels are not whole 2 x 2 quads (a second run's counts: 15, 15, 60,
68, 71, 72 and 72, positions not kept): the quad reading rests on E475's pixel maps alone.

What is open: whose values they are (the baseline triangle's shaders, the microkernel, a job run
before the writers), and why a quad: whether the four instances of a quad share one state slot, or
one quad's state is read through another job's quad, and why the single-predicate readers of E484
do not show quads. To settle it: pclink and predicates written by distinct programs of known
indices (the triangle's pixel program, a PDS-started fill of a different shape) in a run before the
writer, the readers' pixels kept as in usse-pclink-pixels, and the deviant positions mapped against
the quads.
