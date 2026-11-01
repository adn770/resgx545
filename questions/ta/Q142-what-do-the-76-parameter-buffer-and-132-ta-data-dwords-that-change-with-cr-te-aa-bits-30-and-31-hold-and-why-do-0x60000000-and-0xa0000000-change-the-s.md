+++
id = "Q142"
question = "what do the 76 parameter-buffer and 132 TA-data dwords that change with CR_TE_AA bits 30 and 31 hold, and why do 0x60000000 and 0xa0000000 change the same number of dwords by different values"
unit = "ta"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E504"]
terms = ["CR_TE_AA"]
+++

E504: against CR_TE_AA 0x20000000, 0x60000000 and 0xa0000000 each change 76 parameter dwords and 132
TA-data dwords (0xe0000000: 204 and 279 in mode 2 at 64 x 64; the 76 and 132 of 0x60000000 and
0xa0000000 are the same in modes 0 and 2, and mode 0 with 0xe0000000 failed its image check and has
no dump), the first parameter dwords at 1056, 1058, 1120 and 1122 (0x4688000f, 0x00030001,
0x4690ffff, 0xc0000000 becoming 0x46880007, 0x00010001 and so on).

What is open: the layout of those dwords (the parameter buffer's block headers or the region-header
fields of §6.4) and what they say about the window. To settle it: decode the changed dwords against
the region header and primitive block layouts of the specification, with the dumps of E504.
