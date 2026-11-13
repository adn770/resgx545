+++
id = "Q201"
question = "under a CR_ISP_MULTISAMPLECTL byte 0 other than 0x88, does an attribute iterated from a coordinate set read at the point byte 0 places, as the coverage sample does (E1018) and [infer] the position source does (E437: x + 0.5 under 0x88; E502, E1010: x + 0.375, y + 0.125 under byte 0 = 0x26)"
unit = "isp"
kind = "hw"
value = "low"
phase = 11
evidence = ["E606", "E437", "E502", "E1010", "E064", "E1018"]
terms = []
+++
In 700 triangles E606 fits pa0 (the vertices' clip z) and pa1 (their clip x) of source 1 (two
components, E437's program) to the plane at the pixel centre (none of the other 255 points of the
1/16 grid fits better; (0.375, 0.125) is the 96, 32 cell and does not). E437 reads source 0 at
x + 0.5 and y + 0.5 under the library's cmd:16 (0x88); E502 and E1010 read it at x + 0.375 and
y + 0.125 under 0xeaa26e26 in every mode tried.

Why the two differ is answered (round 12, E1018): byte 0 of `CR_ISP_MULTISAMPLECTL` is the sample
point, x in bits 3:0 and y in bits 7:4 in sixteenths of a pixel (256 of 256 counts of E064's sweep,
225 held out, 27 of 27 image classes). 0x88 is the centre and 0x26, byte 0 of 0xeaa26e26, is
(0.375, 0.125): the position source's two readings are the two settings' points [infer], so why
source 0 differed from E606's centre is a setup difference, not a second rule. Every setup of
E606 ran under 0x88, so whether an iterated coordinate set also moves with byte 0 is open, and
sgx-pipe refuses an attribute iterated under another value (`iter::sample_point`).

To settle it: E437's position-source program and a coordinate set carrying the vertices' own
window x and y, iterated in one program, under cmd:16 byte 0 = 0x26, 0x3c and 0x0f on a triangle
at several places; compare each with x + lo/16 and y + hi/16 per pixel (about 6 jobs, safe class).
Then the question retires.
