+++
id = "Q055"
question = "what do idf's modes other than bif, lock and release, setm and the cache-control operands do?"
unit = "usse"
phase = 11
evidence = ["E088", "E098", "E099", "E103", "E107", "E110", "E117"]
terms = []
+++

setm #0 to #15 masks nothing in a fill or a single-sample triangle (E099) and no sample of a 4x
multisampled one (E103). A counter incremented under lock #0 counts every instance (E110), and
.quadlead runs an instruction for a quad's top-left instance only (E088). No load cache mode keeps
an old dword the host rewrites while the job runs (E107), and eldd and eldq load nothing past their
limit (E098).

What is open (usse_isa.md §8, item 6): what idf does in its other modes, what lock and release
order beyond the counter, what setm masks when anything is masked, and what the cache-control
operands change.

To settle it: on the laptop, a two-phase fill in which phase 0 stores and phase 1 reads the same
address after each idf mode; lock and release around a read-modify-write of one word by every quad,
with the order of the results kept; setm once a per-sample path is found (E117 has not found it);
each cache-control operand on a load of a word the host changes.
