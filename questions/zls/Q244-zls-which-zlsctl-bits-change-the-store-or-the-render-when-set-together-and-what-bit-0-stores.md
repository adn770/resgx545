+++
id = "Q244"
question = "what do the bits of CR_ISP_ZLSCTL that no record reads (12, 15, 16 and 20 to 23, 27 to 31) do when set in combination, and what does bit 0 store with a control other than 0x0017100c?"
unit = "zls"
kind = "hw"
value = "low"
phase = 12
evidence = ["E057", "E337", "E411", "E665"]
terms = ["CR_ISP_ZLSCTL", "FRAG_FLAGS.SET_ZLSCTL_BIT0"]
+++

E411 flipped each bit of 0x0017100c once: bits 1, 12 to 16, 20 to 23 and 27 to 31 left the image and
the stored pages as the control's. The closed driver sets 12, 16 and 20 in every value (E337). The
pipeline simulator (E665) ignores those bits as single flips showed, decodes the others as the
records read them, and models bit 0 as E411's raw output shows it: with 0x0017100d (two runs) the
colour image is not written (4096 of 4096 pixels keep the sentinel) and the stored pages are the
control's (page 4 and pages 12 to 15, 5120 dwords, the same first values). An earlier reading
called that a contradiction; it was not, the image and the depth and stencil store are different
things. Bit 0 with any other control was not run and refuses.

What would settle it: the control with several ignored bits set together, and bit 0 with other
controls (the formats, the load bits, another pitch), with the depth and stencil dumps kept and
the image counted.

Status: open.
