+++
id = "Q191"
question = "what are the words that land in a kept owner's control page (0x00200047), OTPM page (0x04000417) and state page (0x00020001, 2) after the next context's render, what stores them and at which kick of that context, and does any task read them back?"
unit = "dpm"
kind = "hw"
value = "high"
phase = 11
evidence = ["E310", "E458", "E462", "E591", "E631", "E1084", "E1085"]
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

Narrowed in 11.38 (E631). The words of the 64x64 owner are in place at the end of the second
context's render, before any close (a copy of render_kept after the render and before the close
equals the one after the tool exits, 75 non-zero dwords, flag 0xc; none of the three words with
flag 0x4 alone). They do not follow the buffer's size (0x04000417 at P = 0x422, 0x300, 0x200,
0x100), the OTPM word is 0 after 2 or 3 renders of the first context, and the control page's word
follows the target (0x47, 0x44, 0x42 at 64x64, 64x32, 32x32); the state words are (count << 16 |
head) and tail of the owner's 2 pages in 8 of 8 jobs, all with 2 pages, so not separated from a
constant. A partial-render owner (1024x768, 0x28 pages) leaves no owner word in its control, OTPM
or state pages with either flag (flag 0xc: nothing in pages 1 to 4; flag 0x4: only 5 words in page
4, 0x00200057, 0x002000ad, 0x0020007e, 0x002000c0 and 0x00200087, a family with 0x00200047), and
its state page is zero after the second context's run (2 runs each, Q192). Not separated: the TA
kick against the render's end (the optional kernel switch K1), a load task reading the words back,
why a partial owner leaves no owner words, what the 5 words of page 4 are, and whether anything
holds for another size or P (the partial owner was run at one size and one P).

Round 19 (E1085, E1084), not narrowed. The kick-against-close test was not decided: on its first
row the copy of the kept 64x64 owner right after the close read 0 bytes (the context was parked
after the tool read, [infer] a race on the context's last reference) and the stage stopped; the
copy after the second render repeated E631's four words (1 of 1). E631's "page 4" words of the
partial owner with flag 0x4 are in its control page (page 4 of a 1024x768 context; E631's
correction), and E1084 saw them again after the second render (o2-4), and at P 0x30 four other
0x002002xx words there with flag 0xc. Still open: (a) close against render, (b) the 1024x768
owner's state words against a constant, (c) a load reading them back.
