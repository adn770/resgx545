+++
id = "E291"
claim = "CR_ISP_LINE_SAMPLE_POS is the line sample position and not a depth-bias format: with a depth sloped across the triangle and the polygon offset on, the units (0x100000) and the factor (4.0) each move the depth test's boundary by the same four columns and a factor of 64.0 removes the triangle, identically with 0x0418 at 1 and at 0, in two runs; the factor acts on a sloped depth"
unit = "isp"
method = "probes/isp/line-bias.toml on the laptop, linux fork with the debug option on: the 64x64 triangle with its clip z set to its clip x (vtx_zx.s), so its depth runs 0.5 + 0.5 x across it, ISP word 0 0x00500200 (depth less, no depth write) against the clear depth 0.5 (render command word 14), ISP word 1 with the polygon offset bit 23, render-details words 5 (CR_ISP_POLY_OFFSET_UNITS), 6 (CR_ISP_POLY_OFFSET_FACTOR) and 26 (0x0418) as kernel pokes; every pixel read back; two runs"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["isp-line-bias"]
terms = ["CR_ISP_LINE_SAMPLE_POS", "CR_ISP_POLY_OFFSET_FACTOR", "CR_ISP_POLY_OFFSET_UNITS", "ISP1.POLY_OFFSET"]
+++

**What runs.** The notebook's comparison with other GPUs left two readings of 0x0418: the sample
position of thin lines, or the format of the depth bias (integer or float). E279 measured the
first. Here the second: a triangle whose depth is below the clear depth 0.5 where its clip x is
negative, so with depth less it draws its left half; a polygon offset pushes the boundary. Eight
cases per run: units 0 and factor 0, units 0x100000, factor 4.0 and factor 64.0, each with 0x0418
at 1 and at 0.

**Results.** Both runs, both values of 0x0418 alike: 714 pixels with no offset (the columns up to
31); 586 with units 0x100000 and 586 with factor 4.0 (the columns up to 27); none with factor 64.0.

**What it shows.** 0x0418 changes no depth-bias result, so it does not select a depth-bias
format, and with E279 it is the line sample position, which reproduces the notebook's reading. The
factor register, which adds nothing to a flat triangle (E071), moves a sloped one's depth: it
scales the offset by the depth's slope [infer: two values of the factor].
