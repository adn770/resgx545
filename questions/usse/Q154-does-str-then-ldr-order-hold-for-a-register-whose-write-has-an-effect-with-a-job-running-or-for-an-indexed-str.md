+++
id = "Q154"
question = "does str then ldr of one register stay ordered for a register whose write starts work or that another writer changes, with a job running, and what does an indexed str (the register-index forms, never run) do"
unit = "usse"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E534", "E445"]
terms = ["Universal Scalable Shader Engine (USSE)"]
+++

E534 answers the order for 0x0814 and 0x0a78 while the EDM is idle and no job runs. Open: the
registers whose write has an effect (never run: they are on the deny list, and a first run of writes
to `CR_CLKGATECTL2` froze the laptop once, E445), a job in flight, the hardware's or the closed
task's own writes of a register, the register-index forms of `ldr` and `str` and an index of more
than 14 bits (never run, usse_isa 6.21; the simulator refuses them too), a `str` of a value wider
than the register (no run stored one; the simulator refuses it), and the time of a `str` (E534's X11
is a bound of 3 to 4 counts of `CR_TIMER`, whose unit is not established).
