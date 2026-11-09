+++
id = "Q145"
question = "why does the control word's addend of an emitpds, from 0xFFF to 0x2000, leave the fill's own dword 0x403 where 0x100 gives 3 or 2, and what 0x800 does"
unit = "usse"
kind = "hw"
value = "low"
phase = 11
evidence = ["E520"]
terms = []
+++

E520: 3 or 2 at 0 to 0x400 and at 0x4000 and above (24 of 27 probes outside the window), 0x403 at
0xFFF, 0x1000, 0x1001, 0x1010, 0x1100 and 0x2000 (12 of 12), 0x401 and 0x400 at 0x800 (2 probes) and
0x400 at 0x10 in one of its two probes, the 10 base probes interleaved among them reading 3 or 2;
every job faulted or hung.

What is open: what the addend is (an offset the PDS adds to an address, [infer]), the values between
those run, what the 0x400 bit of the stored dword marks (it was also read at the addend 0x10 once),
and whether the 0x800 and 0x10 readings repeat. To settle it: the addends 0x7FF to 0x801, 0x1FFF to
0x2001, 0x3FFF; a PDS program that stores more than one input word (Q128).

Noted 2026-11-09: near duplicate of Q128, not merged (Q128's question includes what the control
word's addend of an emitpds does (E520), which is Q145's). A merge or a fold decides which text
survives.
