+++
id = "Q168"
question = "what limits the temporaries of a firmware task above TRC 48 (E540 predicted a hang for 49 and 64; E550 armed 32 to 48 with trc_hazard=1 and read r123 back in 10 of 10), and can a register above r123 (up to the 4T - 1 of the allocation) be reached, through an indirect or banked access, so that the top of a large allocation can be tested"
unit = "edm"
kind = "hw"
value = "low"
phase = 11
evidence = ["E540", "E550", "E603"]
terms = ["Event Data Master (EDM)", "Universal Scalable Shader Engine (USSE)"]
+++

E550 armed T = 32 to 48 with the hazard word and read r123 back, a register that exists at T = 31
as well (E540): it shows that these arms run, and nothing of the storage above r123 or of how many
registers T = 32 to 48 allocate. r124 to r127 cannot be named, so the top of a 128 to 192 register
request was never written. Whether the allocator's limit is a TRC value between 49 and 63, the size
of the physical bank or the arm gate is not known, and the arm of 49 was not run (not approved).

To settle it: (a) a source form that names a register above r123 (an indexed or banked operand, if
the instruction set has one), read from the specification, not from any closed code; (b) with
approval, arm 49 and one above with the hazard word and the stop rules of E550, a reset and the
gate after each. The question needs the closed task only for the tick.

Round 12 cites: E603 (at trc 31 every register r0 to r123 is real storage in a firmware task, 21 of
21 jobs).
