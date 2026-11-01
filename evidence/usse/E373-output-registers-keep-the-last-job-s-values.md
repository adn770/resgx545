+++
id = "E373"
claim = "An output register a job does not write holds what the job before left in that instance's output buffer: a fill that never writes o0 reads 0xff203040 on 1432 pixels and 0xff00ff00 on 616, in the same pixel positions in ten runs, pieces of the baseline triangle's image (its 0xff00ff00 triangle on its 0xff203040 background) laid out by tile; after a fill that writes 0x11223344 to o0 the next fill's unwritten o0 and o1 read 0x11223344 in every pixel, three runs"
unit = "usse"
method = "on the laptop, linux fork b5a86838ae59 with the debug option on: probes/usse/leftover-o0.toml (value.s with OUT = o0, every pixel read back): a fill that runs nop and mov.end o0, o0 ten times, then three rounds of a fill writing o0 = 0x11223344, a fill that never writes o0 and one whose pixel is o1; the campaign's baseline triangle (64x64, 1062 pixels of 0xff00ff00 on 0xff203040) runs before the table; one run"
tiers = ["HW", "infer"]
date = "2026-11-03"
data = ["usse-leftover-o0", "usse-destination-bank6"]
terms = []
+++

**Results.** The ten fills that never write o0 give the same image, pixel for pixel: 616 pixels
of 0xff00ff00, all in whole 2x2 quads but 36, forming diagonal-edged pieces of a triangle in each
32x16 tile, the rest 0xff203040. After the fill that writes 0x11223344, the unwritten o0 and o1
read 0x11223344 in all 2048 pixels, three rounds of three. In E366's output probe, o1-o7 read
the same two colours and values of earlier jobs.

**Reading [infer].** The colour 0xff00ff00 of Q018's jobs is the baseline triangle's, left in
the output buffers: a job that does not write o0 reads the last job's o0 for the same instance
slot, and its count depends on what ran before. E077's 348 pixels, E082's counts and the 269
and 185 of Q015's state probe are of this kind where those jobs' o0 was not written by their
own pass.

**Not shown.** Why o1 reads what o0 held; whether a job of another size maps the slots alike.
