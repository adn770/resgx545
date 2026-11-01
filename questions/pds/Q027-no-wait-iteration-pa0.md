+++
id = "Q027"
question = "where do the values of a no-wait iteration go, given that pa0 never holds the iterated value and holds 0, 2, 6 and a few other values instead?"
unit = "pds"
kind = "hw"
value = "medium"
phase = 7
evidence = ["E131", "E048", "E393", "E430"]
terms = ["DOUTI0.ATTR_SOURCE", "DOUTU1.WAIT_FETCH"]
+++

Narrowed (E393): the no-wait iteration does not write pa0 while the shader runs: read at once or
after 4, 16 or 64 nops pa0 never holds the iterated value at any of the 1062 pixels (20 jobs), but
0, 2, 6 and a few other values, while the same iteration with the completion bit and the wait gives
the iterated x everywhere (two runs). So it is not a late write the shader sometimes wins; E131's
clip x in one run is not seen.

What is open: where the no-wait iteration's values go, and what the 0, 2 and 6 are. Status:
narrowed, not answered.

Narrowed in 11.16 (E430, 60 jobs): after a no-wait iteration none of pa0 to pa15 holds the waited
pa0 at its pixel beyond chance (0 to 25 of 1062 pixels per register, three runs), and pa4, pa8 and
pa12 hold the render target's pre-fill 0xdeadbeef on 258 to 288 pixels in every run; the other
registers hold 0, 2, 6, 2.0 and other floats that differ between runs on 7 to 54 percent of the
pixels. So the values are not in the pixel's first sixteen registers when the shader reads; whether
they arrive later or in another task's registers is not shown. Status: narrowed, not answered.
