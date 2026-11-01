+++
id = "Q081"
question = "what does CR_DPM_REG_074C bit 8 make the DPM read or write near offset 0x6010 of the context's TA-data space, and what fixes that place?"
unit = "dpm"
phase = 11
evidence = ["E203", "E206", "E313", "E362"]
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

What is open: what it reads, and what bits 7:0 select.

To settle it: the TA data's page at 0x6000 filled with a pattern before the job (a kernel or tool
feature: no poke reaches the TA data), bit 8 with values of bits 7:0, the image and the pattern
compared.

Not run in 11.16: no poke reaches the TA data. Kernel need: a debugfs hook that fills the TA data
page at 0x6000 of the render context with a pattern before a job, then bit 8 with values of bits
7:0 (the dpm/reg-074c probes and kpoke ta: are ready). Status: narrowed, not answered.
