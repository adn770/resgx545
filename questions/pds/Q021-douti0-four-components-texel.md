+++
id = "Q021"
question = "with 4 components (DOUTI0 bits 23:22 = 3) where does the texel land, given pa3 reads 1.0 on most pixels?"
unit = "pds"
phase = 7
evidence = ["E132"]
terms = ["DOUTI0.ATTR_SOURCE", "DOUTU1.WAIT_FETCH"]
+++

The textured triangle's primary program issues a `douti` of source 1 (x and y at the vertices) with
the fetch wait and a `doutt` (E132). Bits 23:22 of DOUTI0 at 0, 1 and 2 put one, two and three
components in `pa0` onward, the third 0, and the texel in the dword after them: `pa1`, `pa2`, `pa3`
at every pixel (1062 of them).

With bits 23:22 = 3, `pa0` is x on 1058 pixels and `pa1` is y on 1031, `pa2` is 0 on 1062, and
`pa3` is 1.0 on 1004 pixels and the texel on 58 (columns 20 to 54). In the follow-up run `pa3`
is 1.0 on 1056 and the texel on 6. `pa4` was not read, so the texel might be there on the pixels
where `pa3` is 1.0. The 1.0 may be a fourth component (w) and the texel one dword later, but
nothing here shows it; the 58 pixels with the texel in `pa3` say the texel is not always where
the "components less one" rule of the other cases would put it. The other columns of the table (bit
24, bits 22 to 26) show the same odd pixels and are not explained either.

To settle it: run bits 23:22 = 3 with the shader writing `pa3`, `pa4` and `pa5` out in turn, each
probe at least five times in a fresh context; count per pixel which of the three holds the texel
and which 1.0, and whether the pixels with the texel in `pa3` are the same across repeats. Compare
with a source whose fourth component is not 1.0, to tell a fourth component from a constant.
