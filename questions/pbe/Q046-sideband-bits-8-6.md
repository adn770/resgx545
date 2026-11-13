+++
id = "Q046"
question = "what are the words sideband bit 12 stores in pack modes 0 to 6 (post hoc, E1028 and E1034: a high half fixed pixel for pixel, a low half and a per-pixel class layout that vary between runs, 0xff fields that follow the colour), and what does bit 11 do (it faults the job in modes 0 to 8, at page 0x37001000 with BIF_INT_STAT 0x91000, E383 and E1034)?"
unit = "pbe"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E030", "E031", "E210", "E269", "E383", "E999", "E1028", "E1034"]
terms = ["SIDEBAND.BITS8_6", "SIDEBAND.PACKMODE", "CR_ISP_MSAA"]
+++

Bits 8:6 choose the channel pack mode 8 stores: 0 alpha, 1 red, 2 green, and 3 to 7 the byte
0x40, the blue of both colours run, which this run cannot tell from another source of 0x40
(E269). At
1 to 7 they change no pixel under CR_ISP_MSAA modes 1 and 2, on a 128x128 target, or in pack
modes 4, 5, 9 and 26 (E269), as E030 found for modes 0 and 3. So whether the field does anything
is answered: it is a channel select for a one-channel mode.

Narrowed in 11.14 (E383): bits 8:6 select the channel in pack modes 8 and 7 only: in mode 8, 0
alpha, 1 red, 2 green and 3 to 7 blue (with colours whose bytes all differ); in mode 7, 0 alpha and
red, 1 to 7 green and blue; modes 15, 18, 24, 25 and 28 ignore them. So whether 3 is blue (yes) and
4 to 7 (as 3) is answered. Bit 12 stores fixed words in modes 0-6 (the same in both runs) and zeros
in 7 and 8; bit 11 faults the job in each of modes 0-8.

What is open: the other modes that store one or two channels (24 and 25 store B8; 15, 18, 20, 27
and 28 the low 16 bits) were not run with the field; whether 3 is blue, and whether 4 to 7 read
the same source as 3 (a two-bit select with bit 8 ignored, or a clamp), needs colours whose
channels differ. Sideband bit 11 faults the job, and bit 12
stores values of no colour at every pixel (E269).

To settle it: bits 8:6 at 0 to 7 in pack mode 8 and in pack modes 7, 15, 18, 24, 25 and 28 with
the coded colours of E270; bits 11 and 12 with each pack mode 0 to 8.

Note 2026-11-12 (round 6 housekeeping, decision R6-1 a): the clause on sideband bits 11 and 12 is
this question's alone; Q054 dropped its copy and keeps the emit flags.

Correction 2026-11-13 (round 10 offline, decision R10-1 a (O10-5); ranking
closing10/rank/rank-round10.md finding 6). The "What is open" paragraph above was written before
11.14 and is overtaken by the paragraph before it (E383): modes 15, 18, 24, 25 and 28 were run with
bits 8:6 and ignore them, 3 is blue and 4 to 7 read as 3 in mode 8, with colours whose bytes all
differ. What stays open is pack modes 20 and 27 with the field (not run), what the fixed words of
bit 12 in modes 0 to 6 are, and bit 11, which faults the job in each mode run and is not safe to
sweep; the question line now says so.

Narrowed 2026-11-13 (r10-x, E999). Pack modes 20 and 27 store the low 16 bits of the colour, the
image of mode 15, at bits 8:6 = 0 to 3 with both colours (16 of 16 held out): the field selects
nothing there. Open: bit 11 (faults the job in every mode run, not safe to sweep) and what the
fixed words of bit 12 in modes 0 to 6 are.

Narrowed 2026-11-13 (round 13, session r13-tex, decisions R13-1 a and R13-11 a; E1028; the
question line is rewritten). Text fix: the clause on bits 8:6 in pack modes 20 and 27 is dropped,
E999 answered it (the field selects nothing there, 16 of 16). r13-tex's stage sb12 drew no verdict
on bit 12: its colour 0 replicate control failed (172 of 4096 pixels outside E383's words). Post hoc
(fold/sb12_post.py, not held out): the colour 1 image follows the colour 0 image of its mode by one
word map (4056 to 4096 of 4096), the 0x66 fields fixed and the 0xff fields the colour's, and the
layout of the classes differs from E383's on 390 to 799 pixels. What stays: what sets the layout and
the colour fields' rule, and bit 11.

Note 2026-11-13 (round 13, session r13-flag stage f2, decision R13-3 a; E1034). The stage's frozen
control, bit 12 in mode 0 with at least 4055 of 4096 words in E383's set, failed (3900), so nothing
is scored. Post hoc, the words' high 16 bits are E383's pixel for pixel (4096 of 4096, in this run
and in r13-tex's replicate) and the low 16 bits vary run to run (813 and 799 pixels from E383, 122
between the two round 13 runs): bit 12's words are a fixed high half and a varying low half [post
hoc]. Ungated, bit 11 faulted modes 0, 4 and 8 again with E383's status 0x91000 at page 0x37001000
(low address bits 0x21, 0x11, 0x11, not E383's). Open: what lies at that page and what bit 11
selects; the source of bit 12's low half.
