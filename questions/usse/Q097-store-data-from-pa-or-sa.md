+++
id = "Q097"
question = "does a store take pa or sa as its data source, and what does it store instead?"
unit = "usse"
phase = 11
evidence = ["E366"]
terms = []
+++

In the bank 6 attributes probe (attr_dump.s, usse-destination-bank6-attributes), 32 `stad` stores
of pa0-pa15 and sa0-sa15 stored r1's value (the marker 0x00030002) in all 32 dwords of each of
the ten cases, the control without the bank 6 write included, while the same template storing
o0-o7 and r0-r23 (usse-destination-bank6-outputs) stored the registers' own values. The assembler
encodes the data source's bank by the form table (`F_SRC2D`: bank 0 r, 1 o, 2 pa, 3 sa, checked
in the probe's words), so the words are what they say: it looks like a restriction of the
hardware on a store's data source, not a probe error. The moved probes (copy_dump.s) read pa and
sa through `mov` for that reason.

Open: whether a store takes pa or sa as its data source at all, and what it stores when given
one. r1 is the value seen, and r1 was also the template's pixel register (OUT); no probe tells
r1 from another register the hardware may substitute.

To settle it: a probe with distinct values in r0-r3 and in pa and sa, then `stad` from pa0, pa1,
sa0 and sa1 (and from r and o as controls), each store's dword read back and compared with the
four registers.
