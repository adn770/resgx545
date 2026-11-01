+++
id = "E380"
claim = "A store (stad) from pa0-pa7 or sa0-sa7 stores what a mov of the same register reads, in every one of 30 jobs: in a fill a mov to sa_n changes what pa_n and sa_n both read, a mov to pa_n changes neither, and an unwritten pa_n or sa_n reads the job's pixel colour (0x0da7a000, 0x11110000, 0x33330000, 0x55550000 as the case's colour was), which E366's r1 marker was; the r and o stores store their registers; so a store takes pa and sa as its data source and E366's r1 was the register's content, not a substitution"
unit = "usse"
method = "probes/usse/store-sources.toml on the laptop over the cable, linux fork b5a86838ae59 with the debug option on: attr_dump.s as a 64x32 fill's shader, r0-r7, pa0-pa7, sa0-sa7 and o1-o3 each given their own marker by mov (or not, per case), r10-r13 moves of pa0, pa1, sa0, sa1 as controls, then 32 stad of pa0-pa7, sa0-sa7, r0-r7, r10-r13, o1-o3 and r20 to scratch dwords 0-31 and the pixel colour as o0; three probes of 4, 4 and 3 cases, three, three and two runs"
tiers = ["HW", "infer"]
date = "2026-11-03"
data = ["usse-store-sources"]
terms = []
+++
**Results.**

| case | pa0-pa7 stored | sa0-sa7 stored | r10-r13 (moves of pa0, pa1, sa0, sa1) |
|---|---|---|---|
| pa then sa written (3 runs x 4 r1 variants) | sa's markers | sa's markers | sa's markers |
| pa written, sa not (3 runs) | the pixel colour | the pixel colour | the pixel colour |
| sa written, pa not (3 runs) | sa's markers | sa's markers | sa's markers |
| sa then pa written (3 runs) | sa's markers | sa's markers | sa's markers |
| neither (3 runs; then 2 runs x 3 colours) | the case's pixel colour | the same | the same |

r0-r7 stored their own markers in every case, and r1 its new value where the case changed it
after the setup. The pixel colour was 0x0da7a000 (r20) in the first two probes; in the third the
case set r20 to 0x11110000, 0x22220000 and 0x44440000 and the pixel to r20, #0x33330000 and
#0x55550000: the unwritten pa and sa read 0x11110000, 0x33330000 and 0x55550000, the pixel's colour,
not r20's.

**Reading [infer].** In a fill's pixel task pa_n and sa_n read one register, which a write to sa_n
sets and a write to pa_n does not; unwritten, it holds the colour the task writes to o0 (the
previous instance's or this one's: not told apart). E366's r1 marker was that colour.

**Not shown.** Why pa writes are lost, and whether pa and sa are one register in other task
kinds (the triangle's pixel task has its own pa from the iterator).
