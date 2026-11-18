+++
id = "Q193"
question = "what holds a temporary a task did not write: which earlier job's value does it read, per instance, and what clears it (a power cycle, a module reload, a job of another context)?"
unit = "usse"
kind = "hw"
value = "low"
phase = 11
evidence = ["E484", "E485", "E593", "E1145"]
terms = []
+++

E593: in the i0-i3 job (the job reads r123 and writes only r20 to r23), with a GPU reset by debugfs
in front of it, the pixel was the marker of the job just before in 2048 of 2048 pixels in one order,
and in the other order those of two jobs 9 and 7 jobs earlier in 1536 and 512 pixels (2 jobs, one
register, read through the pixel only, no coordinates). So [HW] a register a task does not write
read back a value an earlier job wrote after a reset in front of the job; [infer] the reset does not
clear it (what the reset does to the register banks is not known) and the instance slots are not
shown. E593's declared falsification criterion fired in these 2 of 50 jobs; its "E485 stands" reads
the claim as about written registers.

To settle it: a job that writes nothing and stores a register to the scratch, run after jobs that
write distinct markers to that register, with a reset, a context close, a module reload and a power
cycle between them; the stored dwords (every instance with `--pixels` and the coordinates) name the
earlier job and the instance slot each read comes from. A power cycle is not allowed by the safety
rules of the batches so far; a module reload needs a kernel batch.

Note 2026-11-18 (E1145, r35-sa stage t: nothing decided). Its reader form control (r20 read
right after its writer, frozen at 2048 of 2048) read the marker in 2024 pixels and 0x0000200f in
24, so every held-out reader is cannot tell. Post hoc [infer], not frozen: an unwritten r20 read
the last r20 write in about 2024 pixels after a colour fill, the t10 triangle and a debugfs reset;
23-24 pixels at even coordinates read small values 0x0000n00f/0x0000n02f at positions that change
between runs; after a fill with 8 temporaries 1388 pixels read that fill's r4. A rerun needs a
reader control that tolerates (or explains) the small values; the power cycle and module reload
stay open (R35-5a).
