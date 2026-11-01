+++
id = "Q100"
question = "what do the fields of CR_TE_MTILE1 and CR_TE_MTILE2 mean, given that flips of their bits change the image or fault the job at 256x256 and 1024x768?"
unit = "ta"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E247", "E257", "E407", "E505", "E506", "E509"]
terms = ["CR_TE_MTILE1", "CR_TE_MTILE2", "cmd_ta.te_mtile1", "cmd_ta.te_mtile2"]
+++

Both words reach the registers and the render follows them (E407): at 256x256 (0x01004004 and
0x02008008) te_mtile1 bits 12, 15, 16 leave 6144 to 16384 pixels wrong and bits 13 and 31 fault the
job; te_mtile2 bits 12 to 14 draw wrong and 15 to 20 fault; at 1024x768 (0x82010018 and 0x03018024)
most low bits do. Bits 8 and 20 of te_mtile1 and 8 to 10 do not take; bit 24 of te_mtile1 and bit 0
of te_mtile2 at 256x256 take and draw exactly.

What is open: what each field counts (macrotile columns and rows, a stride, an origin), and what
the unaffected bits are. To settle it: sweep each field over its values at 256x256 and 1024x768
with the image's wrong pixels mapped (isp_words.py layout style), and compare with the rule's words
of the sizes between (E257).

Run in 11.26 (E505, E506, the safe script, 106 jobs of which 15 controls): at the two-macrotile
sizes (256 x 256, 512 x 384) the first and third boundary fields are free (36 of 36 words exact);
at the four-macrotile sizes (640 x 480, 768 x 640, 1280 x 720) a first boundary of 0 or of one less
faults the job and a third boundary below the rule's faults at 640 x 480, so the fields are tile
boundaries read one by one when n = 4 [infer]. The declared PB and PC fail at n = 4 (4 of 55) and
PA at n = 2 (8 of 36); against the sets declared, PB and PC are right on 30 of 67 fit cases and 10
of 24 held out, PA on 40 and 18.

Run in the 11.26 resume (E509, the risky script, 223 jobs): at two macrotile columns B2 alone
decides (56 of 56 B1 or B3 words over 0 to 20 exact, 0 of 28 B2 words), the stride must be the
rule's (22 of 22 not exact at 256 x 256 and 640 x 480), B2 one and four more is not exact at all
three held-out sizes (12 of 12), and at four columns B1, B2 and B3 are all read. Over all 329 jobs
PA is right on 190 of 278 fit cases and 30 of 36 held out, PB on 204 and 22, PC on 192 and 22; by
columns, the coded PC (B2, bit 31 and the stride the rule's, B1 and B3 free) is right on all 123 fit
cases at n = 2 and PA on 131 of 155 at n = 4, so none fits both (the declared prose says "B2 only",
which is not the code; as a recount under it PC is right on 110 of 123 and 58 of 155). Status:
narrowed, not answered; the open part is what the fields count at four columns and the cases Q139
lists.
