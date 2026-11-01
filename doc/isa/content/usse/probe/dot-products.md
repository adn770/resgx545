<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### Float dot products

*Measured on the hardware (2026-10-22).* **[HW]** throughout (probes `usse-dot-products-fdp-count`,
`usse-dot-products-fdp-incs`,
`usse-dot-products-fdp-rounding`, `usse-dot-products-fdp-specials`, `fdpc`, `fddp`, `fddpc`):

- **`fdp.repeatN d, a, b`** sums `N` products `(a+k)·(b+k)` (`N` = 1 without a repeat, up to 4)
  and **writes only register `d + N - 1`**; `d` to `d + N - 2` keep their values. `.incsXYZ`
  chooses which sources advance (*`.incsXYZ`*).
- **Rounding:** each product is rounded to binary32, then they are added in order, each sum
  rounded to nearest even, as a chain of `fmad` would (6 crafted and 42 random cases).
  Denormal inputs and results are flushed, `x - x` is +0, `-0 + -0` is -0, an overflow is `+inf`
  and an invalid operation (`inf × 0`) gives the NaN **`0x7fc00000`**, not the `0x7fffffff` of
  `frsq`.
- **`fdpc d, cpN, a, b`** gives `fdp`'s value and leaves `p0`-`p3` alone.
- **`fddp.repeatN d, iM, s0, s1, s2`** writes `d + N - 1 = s0·s1` and `iM = s0·s2` (`iM` is `i0`
  or `i1`). **`fddpc`** does the same but never advances its sources.

- **`fdpc` writes only its destination** **[HW]**: for every `cp0`-`cp7` and either sign, `d + 1`
  to `d + 3`, `i0`-`i2` and `p0`-`p3` keep their values (probe `usse-dot-products-fdpc-clip`).

**Undecided:** the rounding of `fdpc`, `fddp` and `fddpc` when a product or a sum is inexact
(measured on `fdp`; their exact results agree with it), the half-float source forms, and where
the clip-plane result of `fdpc`/`fddpc` (`cpN`) goes. Presumably to the
clipper with a vertex's outputs **[infer]**. A vertex program that runs `fdpc.repeat4` of the
position against a plane every vertex is outside of (or inside of, or half), on `cp0` and
`cp5`, before it emits, draws the first triangle exactly as without it **[HW]** (E095): with
the TA state our kernel sets, the result clips nothing. The user clip planes are enabled by
`OUTSEL` bits 7:0, and each takes its distance from a vertex output after the position: with
plane 0 on and a fifth vertex dword, `fdpc`'s value written there removes the triangle when it
is negative, as `fdp`'s does, and a triangle with any vertex outside is removed whole **[HW]**.
`cpN` names the plane `fdpc`'s value goes to, and it replaces that plane's distance
from the output dword; `fddpc` gives `s0 · s1` to its first `cp` and `s0 · s2` to its second
**[HW]** (E096).
