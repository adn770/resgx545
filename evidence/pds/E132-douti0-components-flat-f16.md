+++
id = "E132"
claim = "With DOUTI0 bits 23:22 at 0, 1 and 2 the textured triangle's iteration writes x; x and y; x, y and 0 to pa0 onward and the texel in the next dword at every pixel, with 3 the first two components hold x and y on 1058 and 1031 of the 1062 pixels but pa3 is 1.0 on 1004 and the texel on 58, so the texel is not always in the dword after the components; bit 21 gives every pixel -0.75, which is vertex 0's x (tried with source 1 only), and bit 28 writes x as a half float in the low half of the dword at all 1062 pixels"
unit = "pds"
method = "probes pds-iteration-sources-douti-pa0, -pa1, -pa2, -pa3 and -douti-bits of probes/pds/iteration-sources.toml (pds_tex.s: source 1 with the fetch, DOUTU1 0x02000004, DOUTI0 0x40000801 plus the bits of the case; the pixel shader writes pa0, pa1, pa2 or pa3 out as the colour, one probe each) on the laptop, linux fork with the debug option on: 64x64 triangle job with the coordinate set x, y at the vertices, one run of each case, fresh context each; the tables ran twice (the second is the follow-up run)"
tiers = ["HW"]
date = "2026-11-01"
data = ["pds-iteration-sources", "pds-iteration-sources-followup"]
terms = ["DOUTI0.FLAT", "DOUTI0.F16", "DOUTI0.ATTR_SOURCE", "DOUTI0.PERSPECTIVE", "DOUTU1.WAIT_FETCH"]
+++

**What runs.** The vertex shader gives each vertex its clip x and y as coordinate set 1
(x = -0.75, 0.75, -0.375 and y = -0.75, -0.375, 0.75, as in E047). The primary pixel program
starts the shader with the fetch wait, issues a `douti` of source 1 with DOUTI0 0x40000801 and
the bits of the case, and a `doutt`. The shader writes one primary attribute out, so one probe
shows `pa0` and others `pa1`, `pa2` and `pa3` for the same cases. The triangle covers 1062 of the
4096 pixels. In the table below x and y are the clip coordinates of the pixel, (px + 0.5) / 32 -
1 and (py + 0.5) / 32 - 1.

**Results.** Pixels counted as x or y by the value to within 1e-5; "other" is neither x, y, 0,
1.0 nor a texel (0xd0xxxxxx).

| DOUTI0 bits added | pa0 | pa1 | pa2 | pa3 |
|---|---|---|---|---|
| none | x 1062 | texel 1062 | 0 on 1050, texel 10, other 2 | 1.0 on 1059, other 3 |
| 22 | x 1062 | y 1062 | texel 1062 | 1.0 1062 |
| 23 | x 1062 | y 1062 | 0 1062 | texel 1062 |
| 22 and 23 | x 1058, other 4 | y 1031, x 4, other 27 | 0 1062 | 1.0 on 1004, texel 58 |
| 24 | x 1062 | texel 1062 | 0 on 1050, texel 10, other 2 | 1.0 on 1044, texel 18 |
| 22 to 26 | x 1031, other 31 | y 954, texel 73, x 4, other 31 | 0 1062 | 1.0 1062 |

(The 30 pixels where x and y have the same value are counted in the column's own component, x
in `pa0` and y in `pa1`.) So bits 23:22 = 0, 1, 2
put one, two and three components, the third 0, in `pa0` to `pa2` and put the texel in the
dword after them (`pa1`, `pa2`, `pa3`). With bits 23:22 = 3 the first two components are x and y
on nearly every pixel, the third is 0, `pa3` is 1.0 on 1004 pixels, with no texel there, and the
texel is in `pa3` on the other 58 (their columns run from 20 to 54).

In the bit-by-bit probe on `pa0` (17 cases): bit 21 gives -0.75 (0xbf400000) at all 1062 pixels,
vertex 0's x; bit 28 gives the half float of x in the low 16 bits (0x0000b5c0 for x about
-0.36) at all 1062, with the high half 0; bits 22 to 26 with bit 28 give, at all 1062
pixels, x in the low half and y in the high half of `pa0` as half floats. Bits 17, 19,
20, 22 to 26, 29 and 31 alone leave `pa0` as in the base case (x), and bits 18 and 27 change
every value, as described in E047.

**Second run.** The follow-up run gives the same pictures for the component bits and for the
bit-by-bit probe (bit 21 and bit 28 at all 1062 pixels), with fewer odd pixels in the component
cases and, in the bit-by-bit probe, 7 odd pixels (1055 x) in the case of bits 23 to 26 with bit 29
where the first run had none. Bits 22 and 23: `pa0` x 1050 (12 other), `pa1` y 1056 (6 other), `pa2`
0 at 1062, `pa3` 1.0 on 1056 and the texel on 6. Bit 24: `pa3` 1.0 on 1056, texel 6. Bits 22 to 26:
`pa0` x 1062, `pa1` y 1050 (texel 3, other 9), `pa3` 1.0 on 1061 and the texel on 1. The base case's
`pa3` is 1.0 on all 1062 (first run 1059).

**Not shown.** The reading "components less one" fits the cases 0 to 2; case 3 does not settle
where the texel goes (`pa4` was not read), and its 4 to 58 odd pixels per attribute are not
explained. Bit 24 changes `pa3` on 18 pixels, which this table does not explain either. Bit 21
was tried only with source 1; its reading as "vertex 0" rests on the value -0.75 being the x of
the first vertex. Each case ran once in each run.
