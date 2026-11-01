+++
id = "E237"
claim = "On values a half float does not hold, bit i of the coordinate-format word makes coordinate set i arrive cut to 10 mantissa bits towards zero: 0.1, 1/3 and 0.7 arrive as 0x3dccc000, 0x3eaaa000 and 0x3f332000 with bit i set, where with the word at 0 they arrive as 0x3dcccccc (or d or b), 0x3eaaaaa9 (or a) and 0x3f333331 (or 2); bit 0 acts on one set of four, bit 1 does nothing on it, and with two sets bit 0 cuts set 1 and bit 1 cuts set 2; one run"
unit = "tsp"
method = "the probes tsp-coordinate-sets-cfmt-05-<F>-pa<K> (F 0 to 2) and tsp-coordinate-sets-cfmt-12-<F>-pa<K> (F 0 to 3), K 0 to 3, of probes/tsp/coordinate-sets.toml: the 64x64 triangle with the vertex shader vtx_coord4p.s (o4 = x, o5 = 0.1, o6 = 1/3, o7 = 0.7), state word 16 at 0x05 (one set of four) or 0x12 (two sets of two), state word 17 at F, source 1 with four components and source 2 with two, pa0 to pa3 read back, on the laptop with the linux fork and the debug option on, one run (no follow-up run)"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["tsp-coordinate-sets"]
terms = ["COORDFMT.SET_F16", "COORDSIZE.SET_LAYOUT"]
+++

**What runs.** 0.1 is 0x3dcccccd as a float, 1/3 is 0x3eaaaaab and 0.7 is 0x3f333333. A half
float holds 10 mantissa bits, so rounded to nearest 0.7 would be 0x3f334000 and cut toward zero it
is 0x3f332000. The 14 table cases are state word 17 (coordfmt) at 0, 1 and 2 with state word 16
at 5 (one set: x, 0.1, 1/3, 0.7) and at 0, 1, 2 and 3 with state word 16 at 0x12 (two sets: set 1
x, 0.1 and set 2 1/3, 0.7).

**Results.** One run, every baseline before and after a probe clean. The values below are those
the iterated source delivers on the triangle's 1062 pixels (pa1 to pa3 of source 1 in the
one-set rows; pa0 and pa1 of source 2 in the two-set rows).

| size word | coordfmt | 0.1 | 1/3 | 0.7 |
|-----------|----------|-----|-----|-----|
| 0x05 (one set of four) | 0 | 0x3dcccccc (876 pixels), 0x3dcccccd (112), 0x3dcccccb (74) | 0x3eaaaaa9 (630), 0x3eaaaaaa (432) | 0x3f333331 (630), 0x3f333332 (432) |
| 0x05 | 1 | 0x3dccc000 (1062) | 0x3eaaa000 (1062) | 0x3f332000 (1062) |
| 0x05 | 2 | as 0 | as 0 | as 0 |
| 0x12 (two sets) | 0 | set 1: as above | set 2: 0x3eaaaaa9, 0x3eaaaaaa | set 2: 0x3f333331, 0x3f333332 |
| 0x12 | 1 | set 1: 0x3dccc000 | set 2: as 0 | set 2: as 0 |
| 0x12 | 2 | set 1: as 0 | set 2: 0x3eaaa000 | set 2: 0x3f332000 |
| 0x12 | 3 | set 1: 0x3dccc000 | set 2: 0x3eaaa000 | set 2: 0x3f332000 |

With the word at 0 the values are the iterator's own rounding of the three constants (not exact
copies, to the last bit). With bit i set the whole set is cut: the same single value on every
pixel, equal to the constant with its mantissa cut to 10 bits towards zero.

So bit i of the word carries set i at half precision **[infer]**: the cut values are exactly the
half floats below the constants, while rounding to nearest would give 0x3f334000 for 0.7.

**Not shown.** The sets' other bits (3 to 7), sets of more than two, coordinate values outside
the range of a half float (overflow, small values), and which varyings the closed stack asks for
at half precision. One run only.
