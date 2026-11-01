<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### Encoding bits no field maps

*Measured on the hardware (2026-11-02; `probes/pds/encoding-bits*.toml`, written by
`tools/usse-asm/pds_bits.py`, recorded runs).* Before this round the 27 forms left 281 bits
neither identifying nor in a field. Each probe runs one form's base instruction as a fill's
secondary program and flips one such bit per case; a bit is read if the readback differs from
the base's, or the job fails (E259, E260) **[HW]**:

- **Read: 12 bits.** `bra` and `call` bits 19-23 are target bits: each flip sent the fetch
  `4 << k` bytes past the program (the fault addresses 0x2e200000 up to 0x30000000) and the job
  faulted, so the target is 24 bits (E260). `abs`'s `ds1[n]` form reads bit 15 as the sixth bit
  of `n`, as `not`'s does: `abs ds0[52], ds1[16]` with it set gives the absolute value of
  `ds1[48]` (E261). `mov128`'s bit 15 makes it write `ds0[8]`, `ds0[9]` (the data's row 4 `ds0`
  pair) to both halves of its destination, from every source row into `ds[52]`, and at four
  destinations from rows 2 and 31 and from row 2 with `swap` (E261; why row 4: Q077).
- **Ignored: every other bit.** `movs`, `movsa` bit 4; `mov16` 23:17; `mov64` 23:17, 9:8, 1:0;
  `mov128` 23:16, 9, 7, 1:0; the ALU group 16, 9:7; `mul` 8:7; `abs` 23:16, 9, 7 and 16:9, 7;
  `not` 23:16, 9, 7 and 16:9, 7; `tstz`, `tstn` 23:16, 9, 7:3 and 16:9, 7:3; `shl`, `shr` 15,
  7; `load`, `store` 23; the fences 26:1; `rtn`, `halt` 23:0; `nop` 26:0, which also leaves the
  fetch pc as the plain `nop` does (E260, E261). `mov32`'s 23:17, 8, 0 and `alum`'s 23:1 were
  measured before (*`mov16`/`mov32` specials*, `pds-moves-mov32-spare`, `pds-alu-alum-spare`).

So 270 bits are unmapped now (bra and call 0, abs 10 where it had 11), and 269 of them change
nothing the probes can see; `mov128`'s bit 15 is the one read that no field describes.
