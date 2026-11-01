+++
id = "E296"
claim = "Of the 238 unmapped bits of nop, setfc, moest, setm, imo, the immediate smoa, smr, smbo and smlsi, pcoeff, depthf and atst8, flipped one at a time in a fill, 235 change nothing and three hang the job: enc[51] on setfc, enc[51] on imo and enc[44] on depthf"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/encoding-bits-state.toml (written by tools/usse-asm/usse_bits.py), as E295: one base per form as a raw .long in dump.s, case 0 the base, each other case one unmapped bit flipped; atst8 after a test that sets p0; readbacks compared by usse_bits.py eval; one run, 238 flipped cases and 12 bases; the three hangs recovered by the driver, the triangle clean after each probe and the fill and the triangle clean after the table"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["usse-encoding-bits-state"]
terms = []
+++

**What runs.** The bases are `nop` (enc[37:2] unmapped), `setfc #0, #0` (55:54, 51, 49:9, 7:1),
`moest r17, #0` (54, 49:47, 42:34, 31:28, 20:0; the pixel is r17), `setm #0` (55:54, 51:44,
42:4), `imo #0, #0, #0, #0` (55:54, 51, 49:48), the immediate `smoa`, `smr`, `smbo` and `smlsi`
with zero operands (55:54, 49:48 each), `pcoeff r1, r2, r3` (55:54, 46:44, 42:35, 33:32, 27:21),
`depthf r1, r2, r3, nfb` (54, 47:44, 40:38, 33:32, 27:21) and `atst8 r10, p0, r1, r2, r3, nfb`
(47:44).

**Results.** Each base left every stored register and the pixel as the template's marks, so
none of them changes what a fill shows (as E083, E099 and E109 found for pcoeff, depthf, setm,
moest and setfc). Of the flipped cases 235 matched their base. Three jobs hung and were lost
(the driver recovered each; no BIF fault):

- `setfc` with enc[51] set;
- `imo` with enc[51] set (the table's comment called enc[51] ignored for imo);
- `depthf` with enc[44] set.

In the MOE group enc[51] selects the register forms of smoa, smr, smlsi and smbo; on setfc and
imo it does something that stops the task **[infer]**.

**Not shown.** What the three bits select; whether the hangs need the fill (a vertex or
end-of-tile task was not tried). One run.
