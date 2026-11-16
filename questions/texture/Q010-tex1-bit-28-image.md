+++
id = "Q010"
question = "which job clears colour-space set 0 between jobs, given that a copy that does not load it converts with the last loaded words across a debugfs reset (E1097, E1103, E1112), and with zeros after the kit's health fill and triangle with no fault or hang and after a recovered hang followed by them (E1112), and the first job of a session after hung jobs converts with zeros (E271)?"
unit = "texture"
kind = "hw"
value = "low"
phase = 6
evidence = ["E037", "E039", "E046", "E271", "E399", "E1097", "E1103", "E1112"]
terms = ["transfer_cmd.load_yuv_csc", "TEXFORMAT", "T1.TEXFORMAT"]
+++

T1 bit 28 is TEXFORMAT's top bit: the copy reads its source as YUYV (TEXFORMAT 28) and converts it
through colour-space set 0, which gives opaque black while set 0 holds zeros (E271). With set 0
loaded the image is the YUYV conversion at every pixel over both sources, and T1 bits 28 and 24
read UYVY. So the original question, which field bit 28 is and why black, is answered.

Narrowed in 11.14 (E399): neither the driver's GPU reset (debugfs reset) nor a 5 s idle clears
colour-space set 0: a YUYV copy that does not load it converts as one that does, every pixel, two
runs. What zeroed it in E271's first job (a recovery after hangs, a power-off) is still open.

What is open: E271's first job saw zeros and every later job the last loaded words, without
loading them. That a GPU reset after the earlier hangs cleared them is a reading; the record does
not reset the GPU on purpose. Whether a recovery, a power-off or a firmware path loads set 0 is not
shown, nor whether set 1 and the luma-key words behave alike.

To settle it: load set 0, hang a job on purpose (an odd EMIT2 count, E266, or EMIT1 bit 31,
E267), and run the YUYV copy without a load; then the same after a power-off and idle.

Narrowed 2026-11-16 (round 29, session r29-flag2, E1112; the question line is reworded, the
question is not retired: R29-3 (a)'s rule reads "narrow only"). It read "what clears the
colour-space words between jobs, given that a copy that does not load set 0 converts with the last
loaded words, and the first job of a session after hung jobs converts with zeros?". Frozen H-KEEP
(no recovery clears the set) failed: after each of two recovered bit-24 hangs a copy without the
load read the zeros set (H-RECOV-CLR's reading, 2 of 2). But the first copy of the stage read zeros
too with no fault or hang since a BT.601 copy, only the kit's health fill and triangle and debugfs
resets between, while a copy after a load and a debugfs reset alone kept BT.601 (as E1097 and
E1103) [post hoc]. So the set survives a debugfs reset and does not survive the health pair (the
t10 `fill` or `tri`) [infer]; each recovery also ran that pair, so whether a recovery clears it by
itself is not shown. Open: which of the fill and the triangle clears it (or loads zeros), a
recovery without a health job, the power-on state, set 1 and the luma-key words.
