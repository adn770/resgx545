+++
id = "Q096"
question = "does the firmware itself do anything for the sample-cache erratum, beyond the heap layout the host chooses?"
unit = "edm"
phase = 11
evidence = ["E002", "E011", "E013", "E033", "E035", "E041", "E114"]
terms = []
+++

The only visible part of the workaround is the heap layout: on a host bridge below revision 4
(the laptop's is revision 3) the DDK moves every heap but the textures below `0x3e000000` and
gives the textures a region of their own (doc/specs/boot_sequence.md §4). The firmware is the same
code at every layout and is not told the layout (E002, E011, E013).

Narrowed (analysis of runs on record): every texture our probes sample lies in the probe's scratch
buffer in the general heap (`0x3e003000` and up), outside the texture region, and samples as
expected on this revision-3 bridge: address modes and borders (E033), twiddled fetches (E035),
mipmaps and filters (E041). The one cache effect seen, stale texels after a USSE store (E114), is
the sampler cache keeping what it fetched, not an address clash. So the misplaced half of the
test is done and shows no erratum, with the same firmware running.

What is open: the texture-region half (no job of ours maps a texture there yet), and whether the
erratum needs a texture and other data at clashing addresses at once, which no run tried.

To settle it: the sampler-cache probes with the texture mapped in the TEXTURE heap and, apart,
with a render target and a texture whose addresses differ only above bit 28.
