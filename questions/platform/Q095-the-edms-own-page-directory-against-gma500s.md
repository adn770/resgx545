+++
id = "Q095"
question = "does giving the EDM a page directory of its own, rather than gma500's default one, change anything beyond the coupling of their teardowns?"
unit = "platform"
phase = 11
evidence = ["E008", "E018", "E021"]
terms = ["CR_BIF_DIR_LIST_BASE15", "CR_BIF_DIR_LIST_BASE0"]
+++

The kernel builds a page directory for the EDM and puts it in `BIF_DIR_LIST_BASE15` and TA3DCtl
dword 23; `BIF_DIR_LIST_BASE0` keeps gma500's default directory, written back after the reset
(E008). Every run so far uses this split: the transfers run through the EDM's own directory
(E018) and through client directories the kernel builds (E021). With a directory of its own,
the EDM's mappings cannot be freed by gma500's unload under the running firmware, and gma500's
GEM mappings are not visible to it (doc/specs/boot_sequence.md §5, an inference). No run has
booted the firmware on gma500's default directory, so whether anything else differs (faults on
gma500's own mappings, the stolen-memory aperture at its fallback address, the cost of gma500's
flushes) is not known.

To settle it: a kernel switch that boots the EDM with gma500's default directory in
`BIF_DIR_LIST_BASE15`, the heaps kept out of gma500's aperture, then the fill, transfer and
triangle runs and a modeset while the firmware runs, compared with the same runs on the EDM's
own directory.
