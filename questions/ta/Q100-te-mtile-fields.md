+++
id = "Q100"
question = "what do the fields of CR_TE_MTILE1 and CR_TE_MTILE2 mean, given that flips of their bits change the image or fault the job at 256x256 and 1024x768?"
unit = "ta"
phase = 11
evidence = ["E247", "E257", "E407"]
terms = ["CR_TE_MTILE1", "CR_TE_MTILE2", "cmd_ta.te_mtile1", "cmd_ta.te_mtile2"]
+++

Both words reach the registers and the render follows them (E407): at 256x256 (0x01004004 and
0x02008008) te_mtile1 bits 12, 15, 16 leave 6144 to 16384 pixels wrong and bits 13 and 31 fault the
job; te_mtile2 bits 12 to 14 draw wrong and 15 to 20 fault; at 1024x768 (0x82010018 and 0x03018024)
most low bits do. Bits 8 and 20 of te_mtile1 and 8 to 10 do not take; bit 24 of te_mtile1 and bit 0
of te_mtile2 at 256x256 take and draw exactly.

What is open: what each field counts (macrotile columns and rows, a stride, an origin), and what the
unaffected bits are. To settle it: sweep each field over its values at 256x256 and 1024x768 with the
image's wrong pixels mapped (isp_words.py layout style), and compare with the rule's words of the
sizes between (E257).
