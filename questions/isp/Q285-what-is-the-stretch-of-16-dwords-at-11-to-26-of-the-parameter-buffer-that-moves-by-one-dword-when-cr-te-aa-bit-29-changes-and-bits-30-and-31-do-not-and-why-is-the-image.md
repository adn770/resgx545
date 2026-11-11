+++
id = "Q285"
question = "what is the stretch of 16 dwords at 11 to 26 of the parameter buffer that moves by one dword when CR_TE_AA bit 29 changes and bits 30 and 31 do not, and why is the image empty without bit 29"
unit = "isp"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E728", "E415", "E281", "E825", "E827"]
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

Decoded from the dumps of E728, 2026-11-09 (existing data, not a new measurement). In the
parameter buffers of the kept msaa-b-te29 jobs with bit 29 clear and bit 30 or 31 set (0x40, 0x80,
0xc0 at 64 x 64 and 128 x 128, modes 0 and 2) dwords 0 to 10 are the controls' (0x20 and 0xe0, bit
29 set), dword 11 is 0x00000000, dword 12 is 0x00040101 and the rest of the stretch follows one
dword later: the "16 dwords at 11 to 26" are the format word, the four set masks and the packed
vertices (the glossary's PB_OBJ.FORMAT, SET_MASKS) displaced by one zero dword inserted between
the line widths (PB_OBJ.LINE_WIDTHS, dword 10) and the format word. In the controls the format
word is at dword 11. The cause stays open: it is either a dword the ISP expects in the object when
bit 29 is clear (a zero, so nothing is drawn) or an ISP that reads the old layout and takes the
zero as its format word; the dumps do not separate them, and separating them needs the dword
changed between the TA and the 3D, which no host path does. The cause may be parked under Q030.

Note 2026-11-10 (K2 stage k-pb0, E825): the three controls were frozen from a one-render job and the
stage ran two renders (job shape, shown by the regression session); the TE 0x40 image and stretch
reproduced, the TE 0x60 twin drew; k-pb (the pokes) did not run.
