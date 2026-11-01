+++
id = "Q036"
question = "what do the high halves of CR_DPM_TA_ALLOC_FREE_LIST_STATUS1 and CR_DPM_3D_FREE_LIST_STATUS1 (0x0700, 0x070c), and CR_DPM_TA_ALLOC_FREE_LIST_STATUS2 and CR_DPM_3D_FREE_LIST_STATUS2 (0x0710, 0x071c), hold after a 3D has handed the pages back?"
unit = "vdm"
phase = 10
evidence = ["E184", "E256"]
terms = ["Dynamic Parameter Management (DPM)", "Parameter Buffer (PB)", "ta3d_ctl"]
+++

The four registers agree in pairs (E184). Sampled through every job (E256): while the TA runs, the
high half of CR_DPM_TA_ALLOC_FREE_LIST_STATUS1 (0x0700) holds the parameter buffer's size in pages
and CR_DPM_TA_ALLOC_FREE_LIST_STATUS2 (0x0710) that size less one, and the low half of 0x0700 counts
the pages the TA takes, one above `CR_DPM_PAGE_STATUS`; the 3D copies the TA pair into
CR_DPM_3D_FREE_LIST_STATUS1 (0x070c) and CR_DPM_3D_FREE_LIST_STATUS2 (0x071c) when it starts. So the
low half is a count, the pages of the scene plus one, and it keeps that value after the job: E184's
3, 5 and 6 are two, four and five pages.

What is open: during the 3D the high halves and the second pair change at every step while the
page count falls, and after the job they hold values such as 0x0001 and 0x94 that are no count.
Read as the free list's head and tail after the pages went back, in the order the 3D freed them
[infer]; no run has read the free list to check it.

To settle it: save the parameter buffer's free list (the DPM page table) after a 64x64 and a
1024x768 triangle and after a partial render, with the four registers, and compare the high
halves and the second pair with the list's first and last entries.
