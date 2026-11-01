+++
id = "E096"
claim = "With a user clip plane enabled by the output-select word, fdpc's cpN value becomes plane N's distance for the vertex, replacing the distance dword the vertex writes, and has no effect on a disabled plane; fddpc gives its first product (s0 * s1) to cpA and its second (s0 * s2) to cpB"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/mte/user-clip-planes.toml, probes fdpc-cp, fdpc-cp-p01 and fddpc-cp, the triangle's vertex shader writing a distance dword (o4, o5) with a mov and then running fdpc or fddpc against r4-r7 and r12, with the output-select word 0x53001 (plane 0 on) or 0x63003 (planes 0 and 1), a 64x64 render; one run"
tiers = ["HW"]
date = "2026-11-01"
data = ["mte-user-clip-planes"]
terms = ["OUTSEL.PLANES"]
+++

**What runs.** The vertex shader writes o4 (plane 0's distance dword; o5 for plane 1) to +1 or
-1, then `fdpc.repeat4 r8, cpN, pa0, r4` against a plane held in r4-r7 whose value is -1 (every
vertex outside) or +1 (inside), or `fddpc r8, i0, cpA, cpB, pa3, r4, r12` with r4 = -1 and
r12 = +1 in either order.

**Results.** The triangle is 1062 pixels of 0xff00ff00 on 3034 background when drawn, and
nothing (background everywhere) when removed.

- fdpc-cp (output-select 0x53001, plane 0 on): o4 +1 with no fdpc draws; o4 +1 and `fdpc cp0`
  outside removes the triangle; `fdpc cp0` inside draws; `fdpc cp1` outside draws (plane 1 is
  off); o4 -1 with `fdpc cp0` inside draws: the fdpc value wins over the distance dword.
- fdpc-cp-p01 (0x63003, planes 0 and 1 on, o4 and o5 +1): no fdpc draws; `fdpc cp1` outside
  removes the triangle, and so does `fdpc cp0` outside.
- fddpc-cp (0x53001): `fddpc ... cp0, cp1, pa3, r4 (-1), r12 (+1)` removes the triangle;
  `cp1, cp0` with the same operands draws; `cp0, cp1, r12 (+1), r4 (-1)` draws; and
  `cp1, cp0, r12, r4` removes it. So the first product (s0 * s1) reaches the first named
  plane and the second (s0 * s2) the second: the triangle is removed exactly when plane 0
  receives the negative product.
- One more fdpc-cp case, labelled "o4 +1, fddpc cp0 and cp1 both outside", draws the
  triangle.

**Not shown.** What the last labelled case's operands do (its text is not examined here), and
the clip plane output of a vertex shader without the output-select word set. One run.
