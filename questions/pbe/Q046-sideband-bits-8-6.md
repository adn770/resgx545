+++
id = "Q046"
question = "do SIDEBAND bits 8:6 select the channel only in pack mode 8, or in the other one-channel modes too (24, 25 and those that store G8B8), and what do sideband bits 11 and 12 do?"
unit = "pbe"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E030", "E031", "E210", "E269", "E383"]
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
