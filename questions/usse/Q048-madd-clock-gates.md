+++
id = "Q048"
question = "do the MADD0 and MADD1 clock gates follow the USSE pipes' floating-point arithmetic, or their cache and texture traffic?"
unit = "usse"
phase = 11
evidence = ["E006", "E008", "E011", "E365", "E445"]
terms = ["MADD", "CR_CLKGATECTL2", "CR_CLKGATESTATUS"]
+++

The GPL kernel's register header gives `CR_CLKGATECTL2` two bits per unit, MADD0 in bits 13:12 and
MADD1 in 21:20 (hw_spec.md §5.3); the header never expands the name. Two readings exist:
floating-point multiply-add units, and the main cache's arbiter and decompression unit of another
SoC's manual (cites/ti-omap4430-trm). srvinit sets every field to 2, `CR_CLKGATESTATUS` reads 0x20
after a boot and 0 after a stop (E006, E008, E011).

Narrowed by E365 (read only): with the gates as the boot leaves them the status reads 0x000fffa7
and 0x000fffa4 while a fill runs a loop of fmads and the same values for a loop of integer
multiply-adds; renders add 0x78, 0xccff8 and 0xfffff, the EDM tick reads 0xccfa0; bits 20 and above
never read 1. So the status as left by the boot does not tell the two loops apart.

Narrowed by E445 (CR_CLKGATECTL2 written through debugfs kregnow while idle, 22 settings): each of
seven two-bit fields, the MADD0 and MADD1 fields among them, at 0, 1 and 3 changes neither the
values CR_CLKGATESTATUS reads (the same five, 0x20, 0x000ccfa0, 0x000fffa4, 0x000fffa7 and
0x000fffff, under a floating-point loop, an integer loop, a texture copy and a fill) nor the 44 ms
the loops take, and no job of those settings hangs. Six runs with both MADD fields written during
a loop ten times as long (0.3 s in) all hung ("job hung, context lost", the GPU reset), and the 0
the status reads after is the reset's. The control, the same long loops with no write, hung too:
the floating-point loop in 3 of 3 runs and a plain run, the integer loop in 2 of 3 (the third
finished in 434 ms), so the hang is not shown to come from the write, and the write-while-busy
half is untested.

What is open: what the status's bits and the MADD fields gate, since no field tried while idle
shows in the status or in the speed of the jobs run; what a write during a loop that finishes does,
and why a loop of 12500000 iterations hangs by itself; the fields at bits 3:2 to 11:4 (a first run
over those fields froze the laptop until its watchdog reset it, and its output was lost); a job
that loads the main cache or the arithmetic units harder than these.

To settle it: the MADD fields written during a loop that finishes (between 1250000 and 12500000
iterations, the length at which the loop starts to hang found first), the remaining fields, one
machine reset at a time, with the jobs of E445, and a job whose time depends on the cache (a
texture copy of a large image, repeated).
