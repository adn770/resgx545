+++
id = "Q071"
question = "how does the ISP use the ZLS control word's bits in a render with depth or stencil buffers?"
unit = "isp"
kind = "hw"
value = "high"
phase = 11
evidence = ["E057", "E169", "E216", "E228", "E284", "E411"]
terms = ["CR_ISP_ZLSCTL", "CR_ISP_BGOBJVALS.STENCIL", "ISP2"]
+++

ISP word 2 is answered (E284): its compare (27:25) with the eight relations, the compare mask
(15:8), the write mask (7:0) and the operations on stencil fail (24:22), depth fail (21:19) and
pass (18:16), each 0 keep, 1 zero, 2 replace, 3 and 4 increment and decrement clamped, 5 invert,
6 and 7 increment and decrement wrapping; bits 31:28 change nothing.

What is open (3d.md §11.5): bit 0 of `CR_ISP_ZLSCTL` lets the job complete with no pixel and the
other bits change nothing without depth or stencil buffers (E057); render flag 0x10 sets bit 0
(E169). How the ISP uses the bits the 3D kick adjusts, and the control values of a depth-buffered
render, are not shown.

To settle it: on the laptop, a render with depth and stencil buffers loaded and stored (the
depth-test script's ZLS pokes), the ZLS control word flipped bit by bit from the store value
0x17100c, the stored depth and stencil read back from the scratch buffer, two runs.

Narrowed in 11.15 (E411, two runs, identical per flip): with the store setup of load-store.sh the
control 0x17100c stores a stencil page and four depth pages. Clearing bit 2 stores nothing, clearing
bit 17 drops the stencil, clearing bit 18 drops the depth; setting bit 19 stores the depth as -1.0,
bit 24 as 0x00ffffff and bit 25 as 0xffffffff on two pages; bit 26 stores 640 dwords of 0x0000f000
on two pages; bit 3 and bit 4 shrink the stored region; bits 5 to 11 set fault the job; bit 0 set
leaves every pixel unwritten; the other bits change nothing seen. So the word's bits are store
enables, a depth format and a region, not only the "job completes with no pixel" of bit 0. Still
open: the meaning of bits 3, 4, 19, 24, 25, 26 beyond what they store, and the loads (Q088). Status:
narrowed, not answered; the format and region fields are a new question, Q101.
