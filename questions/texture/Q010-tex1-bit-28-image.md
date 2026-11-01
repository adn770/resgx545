+++
id = "Q010"
question = "what clears the colour-space words between jobs, given that a copy that does not load set 0 converts with the last loaded words, and the first job of a session after hung jobs converts with zeros?"
unit = "texture"
phase = 6
evidence = ["E037", "E039", "E046", "E271", "E399"]
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
