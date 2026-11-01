+++
id = "Q081"
question = "what does CR_DPM_REG_074C bit 8 make the DPM read or write near offset 0x6010 of the context's TA-data space, and what fixes that place?"
unit = "dpm"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E203", "E206", "E313", "E362", "E447"]
terms = ["CR_DPM_REG_074C", "cmd_ta.dpm_reg_074c"]
+++

With bit 8 set a 64x64 job faults on page 0x20006000 of its context, at 0x20006010 to 0x20006013,
whatever the other bits (E203) and whatever `CR_DPM_STATE_BASE1` holds (E313). On a context for
up to 4096x4096, whose TA data covers that page, the job renders exactly and nothing reaches the
DPM control, OTPM or state pages (E313).

Narrowed by E362 (one run): with 0x100 and 0x1ff, on contexts for 4096x4096 and for 1024x768 (whose
control and state pages lie at 0x4000 and 0x6000), the triangle is exact, nothing faults, and
the TA data equals an unpoked control's to the dword. So the access writes nothing new there: a
read, or a write of the value already in place.

Narrowed again by E447 (the TA data page at 0x6000 filled with a ramp or a constant before the job,
debugfs tadata_fill, on a context for 4096x4096): with bit 8 and bits 7:0 of 0x00, 0x01, 0x02, 0x04,
0x08, 0x10, 0x20, 0x40, 0x80, 0xff, 0x55 or 0xaa the page comes back as written and the image is
exact in all 17 runs, so the access neither writes there nor reaches the picture through what it
reads.

What is open: whether what it reads reaches a register or the DPM's state; what bits 7:0 select, as
no value changes anything seen (twelve values were run, not all 256); what fixes that place (the
TA data's base, `CR_DPM_CONTROL_BASE` or `CR_DPM_STATE_BASE0`); other pages near 0x6000.

To settle it: the DPM registers (0x0700 to 0x0760) and CR_DPM_REG_074C's neighbours sampled under
regtimeline across the cases of E447, with the page filled with addresses, with zeroes and with
a ramp.
