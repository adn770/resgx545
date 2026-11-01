+++
id = "Q096"
question = "does the sampler cache erratum of host bridge revisions below 4 show when a texture and other data have addresses that differ only above bit 28?"
unit = "edm"
kind = "hw"
value = "low"
phase = 11
evidence = ["E002", "E011", "E013", "E033", "E035", "E041", "E114", "E432"]
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

Narrowed in 11.16 (E432, 72 jobs): the texture region half is run: the three sampler-cache probes
with the texture in the texture heap (0xf0000000) give the same results as in the general heap in
3 of 3 runs, 24 of 24 cases. No erratum shows on this bridge in that half; a texture and other
data at addresses that differ only above bit 28 at once is not run. Status: narrowed, not
answered.

Narrowed in 11.21 to the hardware part. Whether the firmware does anything for the erratum is not
the target; the records show only that it is the same code at every layout and is not told the
layout (E002, E011, E013). Open: the erratum itself, which no run shows on this
bridge (revision 3) in the general heap or the texture heap (E432), with a texture and other data at
addresses that differ only above bit 28 at once, as the last paragraph of the run above names.
