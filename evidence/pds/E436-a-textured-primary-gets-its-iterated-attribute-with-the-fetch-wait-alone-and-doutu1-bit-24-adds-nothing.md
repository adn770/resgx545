+++
id = "E436"
claim = "In a textured primary whose program iterates an attribute (a coordinate set) into the primary attributes (DOUTI0 0x20000800: source 1, completion bit 29) and then fetches a texture, pa0 (the attribute) and pa1 (the texel) are the same image at every pixel in all three runs with DOUTU1 bits 24 and 25 set and with bit 25 alone (the fetch wait), and with bit 24 alone or neither bit pa0 and pa1 change from run to run in all three runs; bit 24 with a douti that lacks the completion bit hangs the job (24 of 24 jobs, bit 25 also set or not), while bit 25 alone gives the same pa0 and pa1 images with or without the completion bit"
unit = "pds"
method = "probes/pds/iter-wait-textured.toml on the laptop (direct cable), linux fork f1fad0ed9d0e with the debug option on: pds_tex_col.s as the triangle's primary pixel PDS program (--tri pixpds, --vtx-coords 2): DOUTI {A} (0x20000800 or 0x800: source 1, no fetch), DOUTI 0x46012201 and a doutt reading the 16x16 RGBA8888 scratch texture (dword i = 0xD0000000 | i), the shader's U1 {U} at 0x03000004 (bits 24 and 25), 0x02000004, 0x01000004 and 0x00000004, and a shader writing pa0, pa1, pa2 or pa3 out as the colour (four probes of 24 cases: two values of A, four of U1, three runs; 96 jobs); every pixel read"
tiers = ["HW", "infer"]
date = "2026-11-07"
data = ["pds-iter-wait-textured"]
terms = ["DOUTU1.WAIT_ITER", "DOUTU1.WAIT_FETCH", "DOUTI0.LAST_ITER", "DOUTI0.ATTR_SOURCE"]
+++

**What runs.** The 64x64 triangle (1062 pixels) with a primary program of two douti and one doutt:
the first iterates the coordinate set's x into the primary attributes (pa0), the second is the
fetch's coordinate source (source 36 with the fetch bit), the doutt reads the texture, whose texel
lands in pa1. The shader copies one primary attribute to o0. A (the first douti) has the
completion bit (0x20000800) in 12 of the 24 cases of each probe and lacks it (0x800) in the other
12; U1 is 0x03000004, 0x02000004, 0x01000004 and 0x00000004, three runs of each pair.

**Results.** Per probe, 24 jobs; jobs that hang are 24 of the 96, each one with U1 bit 24 set and A
without the completion bit (6 jobs a probe: bits 24 and 25, and bit 24 alone, three runs each).

| A | U1 | pa0 | pa1 |
|---|---|---|---|
| completion bit | bits 24 and 25 | one image, three runs | one image, three runs |
| completion bit | bit 25 alone | the same image | the same image |
| completion bit | bit 24 alone | a different image each run | a different image each run |
| completion bit | neither | a different image each run | a different image each run |
| no completion bit | bits 24 and 25, or bit 24 alone | hang | hang |
| no completion bit | bit 25 alone | the same image as with the completion bit | the same |
| no completion bit | neither | a different image each run | a different image each run |

pa0 holds 48 distinct values over the 4096 pixels in the stable image (the background's 0xff203040
among them; the coordinate set's x elsewhere), pa1 234 (the texels, 0xd0xxxxxx); the stable pa0 and
pa1 images are byte-identical across the three cases that give one (nine jobs each: A with the
completion bit under bits 24 and 25 or bit 25 alone, A without it under bit 25 alone). pa2 and pa3
change from run to run in every setting: leftovers.

**What it shows.** In a textured program the iterated attribute and the texel arrive when the shader
waits for the fetch (DOUTU1 bit 25); bit 24 adds nothing there, and without bit 25 neither it nor
the completion bit makes pa0 reliable. So the closed driver's bit 24 (E364) is not needed for the
iterated attribute to be read fresh in our textured triangle [infer: the closed driver's programs
that carry bit 24 also carry bit 25, as E364's 114 fetching primaries have a fetch, so the bit is
redundant there on this core]. The completion bit is also not needed under bit 25, but under bit 24
it is (a hang without it, as E048 found without a fetch).

**What it does not show.** A program with an iteration and no fetch under bit 24 (E048, E393 have
it), a douti of the vertex colour (source 32) or of several iterated registers (only source 1 and
one register were tried), another core, or the closed driver's own programs run here.
