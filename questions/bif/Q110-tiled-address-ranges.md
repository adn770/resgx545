+++
id = "Q110"
question = "what do the bus interface's tiled address ranges (BIF_TILE0 and up: start, end, stride) do to the addresses of a requestor whose accesses fall inside one?"
unit = "bif"
kind = "hw"
value = "low"
phase = 11
evidence = ["E021", "E151", "E246"]
terms = []
+++

The driver headers name a bus interface register set for tiled address ranges, each with a start, an
end and a stride, that the vendor driver programs when it boots (doc/specs/hw_spec.md section 4). No
glossary row or run of ours places them: the 11 bus interface registers the glossary places (E021,
E151 read some of them) have no tile row, and the register census (E246) kept every BIF register
off its write list, so no offset for a tile register is known.

Open: whether the ranges exist on this core, where they sit in the register file, whether an access
inside a range is re-strided (and for which requestors).

To settle it: read the bus interface's range 0x0c00 to 0x0cff for registers the glossary does not
place (the census table lists the 11 known), then write a candidate tile register only from an
exception to the campaign runner's deny list, with the MMU quiet (no job, the firmware idle, the
value put back, a fill and a triangle exact afterwards: a write to a BIF register can break the
MMU); then set a range over a buffer a `fill` writes and read the buffer back through the host for
the stride.
