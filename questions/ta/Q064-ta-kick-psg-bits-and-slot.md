+++
id = "Q064"
question = "what do the CR_TE_PSG bits 24 and 21 the TA kick ORs in do, and is bit 1 of CR_DPM_STATE_CONTEXT_ID the 3D's DPM slot as bit 2 is the TA's?"
unit = "ta"
phase = 11
evidence = ["E158", "E172"]
terms = ["CR_TE_PSG", "CR_DPM_STATE_CONTEXT_ID"]
+++

On every TA kick the EDM ORs 0x01000000 into CR_TE_PSG, and 0x00200000 too when the RT data's state
bit 8 is set; it writes the TA's DPM slot to bit 2 of CR_DPM_STATE_CONTEXT_ID and, at a clear, bit 0
(E158; E172 for the mask that runs the reload).

What is open (3d.md §4.4): what the two CR_TE_PSG bits mean, and whether bit 1 is the 3D's slot,
which only the 3D kick's use suggests. Q045 asks what the two DPM tasks indexed from 0x0740 move.

To settle it: on the laptop, regtimeline snapshots of CR_TE_PSG and CR_DPM_STATE_CONTEXT_ID through
a two-render context job and a job with RT state bit 8 set, and the TA command's te_psg word poked
with bits 24 and 21 already set or clear.
