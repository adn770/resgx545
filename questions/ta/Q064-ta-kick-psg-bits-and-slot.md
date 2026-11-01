+++
id = "Q064"
question = "what does the region header mark that CR_TE_PSG bit 21 makes the TA write mean to the 3D, and is bit 1 of CR_DPM_STATE_CONTEXT_ID the 3D's DPM slot as bit 2 is the TA's?"
unit = "ta"
phase = 11
evidence = ["E158", "E172", "E305", "E409", "E424"]
terms = ["CR_TE_PSG", "CR_DPM_STATE_CONTEXT_ID", "REGION_HDR.FLAGS"]
+++

On every TA kick the EDM ORs 0x01000000 into CR_TE_PSG, and 0x00200000 too when the RT data's state
bit 8 is set; it writes the TA's DPM slot to bit 2 of CR_DPM_STATE_CONTEXT_ID and, at a clear, bit 0
(E158; E172 for the mask that runs the reload).

On the hardware (E305, one run) CR_TE_PSG reads 0x01400000 after every unpoked job. Bit 21 set
through the TA command stays in the register and makes the TA set bit 29 of word 0 in the header of
every region of the target, with or without a stream, nothing else of its output or the image
changing. Bit 24 is set on every kick, so setting it beforehand shows nothing. The command's word at
0 faults the job; that it faults for want of the kernel's bit 22 is a reading [infer: one value, 0].
CR_DPM_STATE_CONTEXT_ID reads 0 after one render, two renders and a scene of two kicks, so its bits
cannot be read once a job is over.

What is open (3d.md §4.4): what the 3D does with region headers marked by bit 29, which needs an
RT data whose state bit 8 is set; what bit 24 does; whether bit 1 of the slot register is the 3D's
slot.

To settle it: `regtimeline` snapshots of 0x0630 during two-render jobs (11.3's tool samples while
the job runs); a render whose RT data state has bit 8 (the kernel poke rtds:19) against one
with bit 21 set through the command, every pixel and the visibility counters read back.

Narrowed in 11.15 (E409, 15 runs): CR_DPM_STATE_CONTEXT_ID reads 0 at every one of 2.96 million
samples taken while one to three 1024x768 renders ran, so the slot's bit 1 cannot be read this way;
CR_TE_PSG drops from 0x01400000 to 0x00400000 for 17 microseconds at each render's kick (bit 24
cleared and set again), and with the command's bit 21 set it reads 0x01600000 before the first dip.
The render whose RT data has state bit 8 set could not be made with the switches known then (the
render context flags of E168 are not it); the kernel poke rtds:19 sets it (E424). Status:
narrowed, see below.

Narrowed in 11.16 (E424, 48 jobs): no kernel change is needed to set the RT data's state bit 8: it
is dword 13 of the RT data, rtds:19 of the kernel poke. With it set the firmware ORs 0x00200000
into CR_TE_PSG at the kick and the TA marks every region header exactly as the command's bit 21
does (the TA data identical, 3 of 3 runs at 64x64 and at 1024x768), and no image differs from the
control's; CR_DPM_STATE_CONTEXT_ID reads 0 in every job again. What is open: what the 3D does with
a marked header (a scene whose pixels the mark could change) and whether bit 1 of the slot
register is the 3D's slot (sampling cannot read it). Status: narrowed, not answered.
