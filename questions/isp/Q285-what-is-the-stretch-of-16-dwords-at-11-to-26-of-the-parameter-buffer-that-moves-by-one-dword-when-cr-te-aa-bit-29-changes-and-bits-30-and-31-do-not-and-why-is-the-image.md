+++
id = "Q285"
question = "what is the stretch of 16 dwords at 11 to 26 of the parameter buffer that moves by one dword when CR_TE_AA bit 29 changes and bits 30 and 31 do not, and why is the image empty without bit 29"
unit = "isp"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E728", "E415", "E281"]
terms = ["CR_TE_AA"]
+++
E728: TE 0x40 and TE 0x60 (bit 29 alone) give identical TA data and a parameter buffer identical
except that dwords 11 to 26 of the 0x40 job are the 0x60 job's delayed by one dword (13 of 15
positions differ because the stretch has zeros). The same shift for 0x80 against 0xa0 and 0xc0
against 0xe0 at modes 0 and 2, at 64 x 64 and 128 x 128. To settle it: decode the words of the
stretch (the first is 0x00040101 in the bit-29-set job at dword 11: a header word), find which
field of the stream (a region or primitive header) the extra dword belongs to, and whether the
empty image follows from the displaced word.

Q030's text that bit 29 alone changes nothing stays: TE 0x20 equals 0x00 in the parameter buffer
and the TA data (0 dwords differ), so the shift appears only when bit 30 or 31 is set.

Status: open. Narrows Q030 (the TE bits).
