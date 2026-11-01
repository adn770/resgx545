+++
id = "Q071"
question = "what do the rest of ISP word 2 and the ZLS control word's bits do in a render with depth or stencil buffers?"
unit = "isp"
phase = 11
evidence = ["E057", "E169", "E216", "E228"]
terms = ["CR_ISP_ZLSCTL", "CR_ISP_BGOBJVALS.STENCIL"]
+++

ISP word 2's compare (bits 27:25) tests the reference of ISP word 0 against CR_ISP_BGOBJVALS.STENCIL
(E216), and back faces take the stencil word of presence bit 5 (E228). Bit 0 of CR_ISP_ZLSCTL lets
the job complete with no pixel and the other 31 bits change nothing without depth or stencil buffers
(E057); render flag 0x10 sets it (E169).

What is open (3d.md §11.3 and §11.5): the rest of ISP word 2, how the ISP uses the ZLS control
bits the 3D kick adjusts, and the control values of a depth-buffered render.

To settle it: on the laptop, a render with depth and stencil buffers loaded and stored, ISP word 2
and CR_ISP_ZLSCTL each flipped bit by bit, the depth and stencil buffers read back with the pixels,
two runs.
