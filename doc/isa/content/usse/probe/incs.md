<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### `.incsXYZ`

*Measured on the hardware (2026-10-22).* The float multiply-add, dot-product, min/max and
derivative groups print `.incsXYZ` (`enc[47]`, `enc[46]`, `enc[40]`) when `enc[53]` is clear
**[RE]**. **Each bit lets one source advance by one register per iteration: X source 0, Y source
1, Z source 2; the destination advances whatever the bits say, and without `.incs` (`enc[53]`
set) every source advances** **[HW]**. `fmad.repeat2.incs001 d, a, b, c` computes `d = a·b + c`
and `d+1 = a·b + (c+1)`; `.incs000` repeats the first operation into `d+1` (probes
`usse-write-masks-incs-fmad`, `usse-dot-products-fdp-incs`, `fddp`,
`usse-float-minmax-fminmax-incs`). `fdp` has no
source 0, so its X bit does nothing, and `fddpc`, which has no `.incs`, never advances its
sources (probe `fddpc`).

`fmad16.repeat2.incsXYZ` advances `a`, `b`, `c` the same way (probe `usse-fmad16-incs`).

**`fdsx`/`fdsy` advance the same way: their `a` and `b` are sources 1 and 2**, so Y advances `a`,
Z advances `b` and X nothing **[HW]** (probe `usse-gradients-fds-incs`; the simulator does not model
`fdsx`/`fdsy` repeats yet).
