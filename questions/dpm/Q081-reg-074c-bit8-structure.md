+++
id = "Q081"
question = "what does CR_DPM_REG_074C bit 8 make the DPM read or write near offset 0x6010 of the context's TA-data space, and what fixes that place?"
unit = "dpm"
phase = 11
evidence = ["E203", "E206", "E313"]
terms = ["CR_DPM_REG_074C", "cmd_ta.dpm_reg_074c"]
+++

With bit 8 set a 64x64 job faults on page 0x20006000 of its context, at 0x20006010 to 0x20006013,
whatever the other bits (E203) and whatever `CR_DPM_STATE_BASE1` holds (0x20006000 or 0x20042000,
E313). On a context for up to 4096x4096, whose TA data covers that page, the job renders exactly
and nothing reaches the DPM control, OTPM or state pages (E313).

What is open: what the access reads or writes; whether its place is fixed from the TA data's base,
from `CR_DPM_CONTROL_BASE` (0x5000 below it in a 64x64 context) or `CR_DPM_STATE_BASE0` (0x3000
below); and what the eight bits under bit 8 select, which the faults do not show.

To settle it: on a 4096x4096 context, dump the TA data with bit 8 set and clear after a job whose
tail-pointer page at 0x6000 is filled with a pattern, and repeat on a context where the kernel moves
the control and state pages (a 1024x768 context puts them at 0x4000 and 0x6000), with bit 8 and
with values of bits 7:0.
