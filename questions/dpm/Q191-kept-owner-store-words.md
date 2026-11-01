+++
id = "Q191"
question = "what are the words that land in a kept owner's control page (0x00200047), OTPM page (0x04000417) and state page (0x00020001, 2) after the next context's render, what stores them and at which kick of that context, and does any task read them back?"
unit = "dpm"
kind = "hw"
value = "high"
phase = 11
evidence = ["E310", "E458", "E462", "E591"]
terms = ["CR_DPM_TASK_STATE", "CR_DPM_STATE_BASE0", "CR_DPM_CONTROL_BASE", "ta3d_ctl"]
+++

E591: after a kept DPM owner's context is closed with its memory kept, the second context's render
is followed by 16, 20 and 34 dwords changed of the owner's TA data pages 1, 2 and 3 (word 0 of page
1 0x00200047, of page 2 0x04000417, the state page's first list 0x00020001 and 2, the other 32
dwords 0), over ramps of 0xa5000000 + i; with bit 2 alone or no flag nothing is written (6 of 6).
The ramps (junk in the pages) change no render (9 of 9 exact), so no read was seen. Not known: the
meaning of the words (the control page's 0x00200047, the OTPM page's 0x04000417), whether the store
is made when the second context's TA is kicked or at its first render's end (E462 saw the registers
unchanged until the fault), whether it is the same store a partial render's TA makes for its own
state (18 non-zero dwords, E464), and whether a load task (code 4) of any kick reads the pages back.

To settle it: the same case with regtimeline on 0x0600-0x0750 and the kept context's pages read
through render_kept at the second context's kick (a hold after the kick), a ramp of junk lists in
the state page with a partial render owner, and a second kick of the second context.
