+++
id = "Q056"
question = "where does a write to destination bank 6 with value 0 (printed i.) land?"
unit = "usse"
phase = 11
evidence = ["E091", "E147"]
terms = []
+++

The decoder prints the destination as `i.`; the simulator does not model it and stops on a vector
that writes it, as on any operand it does not model (E147); the form-coverage round has no case
that reads it back (E091).

What is open (usse_isa.md §8, item 8): whether the write lands in an index register, another bank,
or nowhere.

To settle it: on the laptop, a fill that writes a marker through this destination and then stores
every register bank it can read (temporaries, outputs, primary and secondary attributes, the index
registers through the forms that read them), three runs.
