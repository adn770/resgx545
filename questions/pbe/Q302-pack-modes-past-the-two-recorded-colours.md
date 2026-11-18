+++
id = "Q302"
question = "where do pack modes 9, 10, 12 and 13 put each pixel's whole colour (the layout in the target and what 12 and 13 write past it), why does mode 14 fault, and what do modes 4 to 6 and the ARGB8888-like modes store at sideband bits 8:6 other than 0?"
unit = "pbe"
kind = "hw"
value = "low"
phase = 11
evidence = ["E031", "E268", "E385", "E1135", "E1136", "E1146"]
terms = ["SIDEBAND.PACKMODE", "CR_REG_0400"]
+++

Split from Q044 when it retired (answered by E1135 and E1136, 2026-11-17): the refusals of
sgx-pipe's PBE (`pbe.rs`) that Q044 carried were not its question. E031 stored two colours only,
0x80ff8040 and the background 0xff203040, in every pack mode; sgx-pipe models modes 0 to 3, 7, 8,
15, 18, 20, 24, 25, 27 and 28 from E031, E383 and E999, and refuses the rest under this question
(22 and 34 under Q012). Of CR_REG_0400, E1135 and E1136 give bit 25 and the low byte in every mode
4 to 63 but 14 at the words they ran (0x80, 0x02000080, low bytes 0x00 to 0xff, 0xf80); sgx-pipe
admits only those words in the modes it models (`reg0400_known`).

To settle it: E031's form with colours whose channels differ between truncation and rounding at
4, 5 and 6 bits, every pixel, in modes 3 to 6 and 9 to 13; the scratch past the target for 9 to
13.

Narrowed 2026-11-18 by E1146 (r35-pk, a colour ramp over every byte value): RGB565 and modes 4
to 6 truncate every narrowed channel (rounding half up, half to even and scaling refuted), the 40
ARGB8888-like modes and 11 store mode 0's image, modes 9, 10, 12 and 13 store whole colours (in
the target and, 12 and 13, past it), and bit 25 with the low bytes 0x40 and 0xc0 inverts the
alpha before it is packed in modes 0, 4, 5 and 6, mode 4's threshold then reading 255 - alpha.
sgx-pipe models those clauses. Open: the layout of 9, 10, 12 and 13 (E1146 kept every pixel's
colour unique, fold/posthoc.txt; no raster map fits), mode 14's fault (a flagged row, R35-4 (a)),
and the other fields of sideband bits 8:6 in modes 4 to 6 and the ARGB8888-like modes.
