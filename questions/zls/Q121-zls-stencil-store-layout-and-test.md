+++
id = "Q121"
question = "what is the in-tile order of the stencil store (one byte a pixel, 128 dwords a 32 x 16 tile) and what does the stencil test do against a loaded stencil?"
unit = "zls"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E466", "E467"]
terms = ["CR_ISP_ZLSCTL", "CR_ISP_STENCIL_LOAD_BASE", "CR_ISP_STENCIL_STORE_BASE"]
+++

E466: with the stencil flag and bases the stencil store is 128 dwords a tile (196608 dwords for
1536 tiles), at the depth's tile pitch (last dword 208639 = (47 * 34 + 31) * 128 + 127), every byte
0 (the clear). E467: bits 1 and 13 load the stencil from the address the store uses, a copy of each
dword. Neither says which byte holds which pixel, because the loaded bytes were copied, not tested.

What is open: the byte order inside a tile (the depth's order with the pixel in four bits less of
the dword index, or another), and how the stencil test (ISP word 2, E284) reads a loaded stencil.
To settle it: a stencil buffer loaded with a pattern of the byte's own pixel index and a stencil
test that keeps or replaces by the loaded value, stored and read back; the state block needs the
second ISP word, which `tri` does not set.

Note 2026-11-11 (E831). E831 measured the depth store of edge tiles only; `sgx-pipe` refuses the
stencil store of a target with edge tiles here, its slots and what they hold past the target being
unmeasured.
