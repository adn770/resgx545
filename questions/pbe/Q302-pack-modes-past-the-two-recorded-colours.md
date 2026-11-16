+++
id = "Q302"
question = "what do pack modes 4 to 6, 9 to 14 and the 40 ARGB8888-like modes other than 0 store for colours other than E031's two (how each narrows or rounds its channels, what 9 to 13 write past the target, why 14 faults), how does RGB565 round a channel where truncation and rounding differ, and do CR_REG_0400 words no record ran in a mode (bit 25 with another low byte, another sideband field) store as E1135 and E1136 read?"
unit = "pbe"
kind = "hw"
value = "low"
phase = 11
evidence = ["E031", "E268", "E385", "E1135", "E1136"]
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
