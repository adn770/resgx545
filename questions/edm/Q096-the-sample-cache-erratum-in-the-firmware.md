+++
id = "Q096"
question = "does the firmware itself do anything for the sample-cache erratum, beyond the heap layout the host chooses?"
unit = "edm"
phase = 11
evidence = ["E002", "E011", "E013"]
terms = []
+++

The only visible part of the workaround is the heap layout: on a host bridge below revision 4
the DDK moves every heap but the textures below `0x3e000000` and gives the textures a region of
their own (doc/specs/boot_sequence.md §4); the kernel supports only that layout. The firmware is
the same code at every layout: srvinit patches its instructions with heap addresses and the page
directory only (E002, E011), and nothing in the boot payload depends on the host bridge. The
EDM dataflow (E013) shows no access that a reader can tie to the erratum, but it does not know
what such an access would look like, and 379 memory accesses stay unresolved.

Since the firmware is not told the layout, any part it played would run on every layout.

To settle it: sample a texture placed inside the general heap's range and the same texture in
the texture region, on the laptop, with the same firmware. If both sample correctly the erratum
does not show on this silicon; if only the misplaced one goes wrong, whatever the firmware does
(it runs in both cases) is not enough, and the layout is the workaround.
