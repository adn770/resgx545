+++
id = "E085"
claim = "c0-c63 read the same fixed table in a fill shader, through a store's source and through a mov alike (c0-c2 zero, c3 1.0, c4-c13 powers of two 2 to 1024, c14-c27 0.5 down to 2^-14, c28-c39 e, 1/e, sqrt 2, 1/sqrt 2, pi/4, pi/2, pi, 1/pi, 2/pi, 4/pi, 2 pi and 2^-16, c40-c44 small values from 1.55e-6 to 2.08e-2, c45-c47 two f16 1.0s, c48-c51 zero, c52-c55 1.0, c56-c59 all ones, c60-c63 0x7fff7fff); g0-g63 read small values only, most of them zero"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/constant-banks.toml, probes cbank and gbank, a fill whose pixel program stores 16 registers of the bank to scratch, four cases for c0-c63 (g0-g63) read as a store's own source and four moved to r1-r16 first; the gbank stores of two runs (the second is the follow-up run)"
tiers = ["HW", "infer"]
date = "2026-11-01"
data = ["usse-constant-banks", "usse-constant-banks-followup"]
terms = ["REGTYPE.FPCONSTANT", "USE.NUM_HW_SPECIAL_CONSTS"]
+++

**What runs.** Eight cases per probe: for bank 5 numbers 0 to 63 (c, the constants) and 64 to 127
(g, the global registers the hardware fills per task, tile and instance), each
set of 16 registers is stored from the shader as the store's own source (cases 0 to 3) and
after a `mov` to r1-r16 (cases 4 to 7), and the scratch dwords are read back.

**Results.** The c bank: both readings agree word for word in all four sets of 16. The table:

| registers | values |
|---|---|
| c0-c2 | 0 |
| c3 | 1.0 |
| c4-c13 | 2, 4, ... 1024 (2^1 to 2^10) |
| c14-c27 | 0.5, 0.25, ... 2^-14 (0x3f000000 down to 0x38800000 in c27) |
| c28-c39 | e, 1/e, sqrt 2, 1/sqrt 2, pi/4, pi/2, pi, 1/pi, 2/pi, 4/pi, 2 pi, 2^-16 |
| c40-c44 | 1.5501e-6, 2.1701e-5, 2.6042e-4, 2.6042e-3, 2.0833e-2 (0x35d00d01 to 0x3caaaaab) |
| c45-c47 | 0x3c003c00 (two half-precision 1.0s) |
| c48-c51 | 0 |
| c52-c55 | 1.0 |
| c56-c59 | 0xffffffff |
| c60-c63 | 0x7fff7fff |

The reading for c39 is 0x37800000 = 2^-16 = 1.5259e-5.

The g bank, read through the store's own source in the two runs of the table: g18, g19, g20, g21,
g23, g24, g25, g39, g41, g42 (0x3f800000) and g43 (0xff000000) are nonzero, g20 and g41 read 1 in
both runs, and g18, g21, g23, g24 and g39 take other values in the follow-up run (the stored
instance is not named); every other g register reads 0. A `mov` to r1-r16 first gives the same
except g19, which then reads 0 (the second of the four sets of 16 registers, both runs).

**Reading [infer].** Up to c39 the table follows the order of the public special-constant
list of the Rogue GPU instruction set reference (zero, the integers, 1.0, powers of two up
and down, e, 1/e, the square roots and pi multiples), which makes the bank this chip's form
of that table; c40 and up are the chip's own.

**Not shown.** One table, two runs. g19 reads 0x1a through the store's source in both runs
and 0 as a mov source and as a pixel (E086): which of the two is the register is open.
