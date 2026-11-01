+++
id = "Q179"
question = "how are the blocks and the data bits of formats 23 to 26 laid out (a data bit changes 7 to 13 pixels, the blocks of 23 and 24 do not differ by index in the colour), and does format 27 decode as ETC1 given a block order that is Morton with y in the low bit (the one of three tried that is consistent) and one pixel per data bit"
unit = "texture"
kind = "hw"
value = "low"
phase = 11
evidence = ["E568", "E342"]
terms = ["TEXFORMAT"]
+++

E568: 23 and 24 read 164 and 186 distinct values over 16x16 but the A pattern (block i = i *
0x11111111) reads one value, so the colour is not in those dwords; 27's low and high dword bits each
change one pixel, in the map bit i to (i div 4, i mod 4). To settle it: PVRTC data and ETC1 data of
known decode written by the program, compared with the reads (the capture of the plan's section 7
gives the closed driver's own data); the colour-space load for YUV, by a transfer command the fill
accepts.
