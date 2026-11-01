+++
id = "C0206"
source = "mesa-csbgen"
locator = "src/imagination/csbgen/rogue/pbestate.xml:400"
link = "https://gitlab.freedesktop.org/mesa/mesa/-/blob/ab2374a4a18ba0ae4c11d499ac35607dd7bbb571/src/imagination/csbgen/rogue/pbestate.xml#L400"
quote = "<field name=\"tilerelative\" start=\"57\" end=\"57\" type=\"bool\">"
terms = ["SIDEBAND.BIT9"]
+++

Line 400 of `pbestate.xml` in Mesa's Rogue csbgen names `tilerelative`. It backs the glossary flag
`SIDEBAND.BIT9`: marks the emit that completes the tile: the PBE counts the emits with it against
its tiles. Measured: needed for an emit to complete its tile: with it clear the only emit hangs; an
extra emit with it set leaves the PBE queue one emit behind, with it clear for one job only; not
tile-relative addressing [infer].
