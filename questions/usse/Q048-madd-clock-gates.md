+++
id = "Q048"
question = "do the MADD0 and MADD1 clock gates follow the USSE pipes' floating-point arithmetic, or their cache and texture traffic?"
unit = "usse"
phase = 11
evidence = ["E006", "E008", "E011", "E365"]
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

What is open: the status's bit layout and what the MADD units serve. Our debug interface's kreg
cannot write `CR_CLKGATECTL2`.

To settle it: a kernel switch that writes `CR_CLKGATECTL2` (each field 0 to 3 in turn, idle and
busy, status sampled), then the MADD gates held off under a floating-point loop, an integer loop
and a texture-fetching copy.
