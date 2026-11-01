+++
id = "Q125"
question = "which code leaves 0xeb3 and 0x98 in pclink and 1101, 0101, 0001 or 1111 in p0-p3 of the instances that do not read the last job's value, and why do they come in aligned 2 x 2 quads of pixels?"
unit = "usse"
kind = "hw"
value = "low"
phase = 11
evidence = ["E475", "E477", "E484", "E500"]
terms = ["Universal Scalable Shader Engine (USSE)"]
+++

E475: of 2048 pixels, 4 to 76 of a pclink reader job read 0xeb3 (and 0x98 in 36 to 76 pixels of some
jobs) instead of the value the writer left, in aligned 2 x 2 quads of pixels (every deviant pixel
has its x^1, y^1 and diagonal neighbours deviant too, in all ten readers), at positions that change
from job to job. E500 ran the 15 jobs three more times (four runs of ten reader jobs, 40): the
deviant pixels are again aligned 2 x 2 quads in every job, 0xeb3 in exactly 64 pixels (16 quads) in
29 of the 40 jobs and in 48 to 80 in all, 0x98 in 16 to 64 pixels of 12 of the 40 jobs, no third
value; the positions repeat from run to run in part, not whole (two runs of one reader job share 4
to 52 pixels, 1 to 13 quads, where two random sets of 16 of 512 quads share about 0.5; all four runs
share 0 to 16 pixels; two reader jobs of one run share 1 to 16 quads, as much as a job shares across
runs). E477: 16 to 36 pixels of a predicate reader job read other patterns.
Neither 0xeb3 (3763) nor 0x98 (152) was written by any of these jobs. E484, a second table of
predicate readers that reads one predicate as the pixel, has 7 reader jobs with deviant pixels, 15,
15, 62, 66, 67, 71 and 75 of 2048, none a multiple of four, so in that table the deviant pixels are
not whole 2 x 2 quads (a second run's counts: 15, 15, 60, 68, 71, 72 and 72, positions not kept):
the quad reading rests on the pclink pixel maps of E475 and E500.

What is open: whose values they are (the baseline triangle's shaders, the microkernel, a job run
before the writers), why the same quad positions come back in part, what 64 pixels (16 quads) of
0xeb3 means, and why a quad: whether the four instances of a quad share one state slot, or one
quad's state is read through another job's quad, and why the single-predicate readers of E484 do not
show quads. The run-to-run question of E475 is answered in part by E500: the positions are neither
fixed nor independent. To settle it: pclink and predicates written by distinct programs of known
indices (the triangle's pixel program, a PDS-started fill of a different shape) in a run before the
writer, the readers' pixels kept as in usse-pclink-pixels, and the deviant positions mapped against
the quads and the jobs before.
