+++
id = "Q048"
question = "do the MADD0 and MADD1 clock gates follow the USSE pipes' floating-point arithmetic, or their cache and texture traffic?"
unit = "usse"
phase = 11
evidence = ["E006", "E008", "E011"]
terms = ["MADD", "CR_CLKGATECTL2", "CR_CLKGATESTATUS"]
+++

The GPL kernel's register header gives `CR_CLKGATECTL2` two bits per unit for `PBE`, `CACHEL2`,
`UCACHEL2`, `USE0`, `ITR0`, `TEX0`, `MADD0`, `USE1`, `ITR1`, `TEX1`, `MADD1` and `PDS1`, from bit 0
up (hw_spec.md §5.3), so there is one MADD per USSE pipe, beside the pipe's iterator and texture
unit, its gate in bits 13:12 (MADD0) and 21:20 (MADD1), and `CR_EVENT_STATUS` has a bit for the
completion of a MADD cache invalidation (hw_spec.md §6.4). The header never expands the name. Two
readings exist: floating-point multiply-add units with a cache of their own, a guess from the name
and the gates' place; and the unit a public technical reference manual of another SoC with an SGX540
(cites/ti-omap4430-trm) calls the mux/arbiter/demux/decompression unit, the wrapper of the main
cache that arbitrates the PDS, USSE and texture requests and decompresses textures.

What our records show of the gates as a whole: srvinit's boot payload names `CR_CLKGATECTL2` =
0xaaaaaa, every field at 2, and polls for idle on `CR_CLKGATESTATUS` with the mask 0xffffffdf
(E011); the deinit script writes `CR_CLKGATECTL2` = 0 (E006); after a boot `CR_CLKGATESTATUS` reads
0x20, and 0 after a stop (E008). No run has set or watched the MADD fields, and no record or spec
gives the bit layout of `CR_CLKGATESTATUS` or what each value of a two-bit field selects.

To settle it: first map the status. With the GPU idle and then under a job that keeps every unit
busy, set each `CR_CLKGATECTL2` field in turn to 0, 1, 2 and 3, the others as the boot payload names
them, and read `CR_CLKGATESTATUS` whole after each write, two runs each: the status bits that follow
one field are that unit's, and the value under which a unit's bits never change while it works is
the one that holds its gate. Then, with the fields as the boot payload names them, read the MADD0
and MADD1 status bits while each of four jobs runs: a loop of floating-point multiply-adds, an
integer loop of the same length, a copy that fetches a texture on every pixel, and an idle GPU; many
samples per job, two runs each. A multiply-add unit opens its gate for the first job only; a cache
front end for the copy and for whatever fetches. Last, hold each MADD gate as the first step found
and run the same jobs: the jobs that hang or slow down name what the unit serves.
