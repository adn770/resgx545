+++
id = "Q027"
question = "where do the values of a no-wait iteration go, given that pa0 never holds the iterated value and holds 0, 2, 6 and a few other values instead?"
unit = "pds"
phase = 7
evidence = ["E131", "E048", "E393"]
terms = ["DOUTI0.ATTR_SOURCE", "DOUTU1.WAIT_FETCH"]
+++

Narrowed (E393): the no-wait iteration does not write pa0 while the shader runs: read at once or
after 4, 16 or 64 nops pa0 never holds the iterated value at any of the 1062 pixels (20 jobs), but
0, 2, 6 and a few other values, while the same iteration with the completion bit and the wait gives
the iterated x everywhere (two runs). So it is not a late write the shader sometimes wins; E131's
clip x in one run is not seen.

What is open: where the no-wait iteration's values go, and what the 0, 2 and 6 are. Status:
narrowed, not answered.
