+++
id = "Q061"
question = "does a DOUTU word's EXE field stop at bit 19, leaving CBASE in bits 3:0, or do the 18 program-counter bits reach bit 21?"
unit = "pds"
phase = 11
evidence = ["E004"]
terms = ["PORT.DOUTU", "DOUTU0.TEMPS"]
+++

In the closed stack's transfers EXE in bits 19:4 is a program's offset from the heap base in 8-byte
instructions, 512 KiB of reach, and CBASE in bits 3:0, read as the offset's bits 22:19, is 0 in
every capture, so EXE alone gives the offset (E004). Our
programs keep code low enough for both readings to agree (doc/specs/transfer.md §4.2).

What is open (pds_isa.md §7, item 7): which reading the hardware takes for a program placed high in
its heap.

To settle it: on the laptop, a fill whose USE program sits 1 MiB above the heap base, which both
readings reach, and one 4 MiB above it, which only CBASE reaches, with a program of another colour
at the heap base; each DOUTU written once with the offset's bits 22:19 in CBASE and once with its
bits 20:19 in word bits 21:20, every pixel read back. If the CBASE words draw the placed program
and the bits 21:20 words do not, EXE stops at bit 19 and CBASE extends the offset to 8 MiB. If the
bits 21:20 word draws the program at 1 MiB and the CBASE words do not, the 18 program-counter bits
reach bit 21, 2 MiB, and the program at 4 MiB is out of reach.

Not run in 11.15: the settle plan needs a fill whose USE program sits 1 MiB and 4 MiB above the heap
base, and the tool places programs only low in its heap (no option to move a program); the two DOUTU
encodings are ready but not the placement. Status: narrowed, not answered; missing: a program
placement option in the fill tool.
