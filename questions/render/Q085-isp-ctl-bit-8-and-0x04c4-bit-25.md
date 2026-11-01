+++
id = "Q085"
question = "does our tri job's image or time change with the closed driver's two other 3D register values, CR_ISP_CTL bit 8 clear and 0x04c4 bit 25 set?"
unit = "render"
kind = "hw"
value = "low"
phase = 11
evidence = ["E326", "E408"]
terms = ["CR_ISP_CTL.PROCESS_EMPTY_TILES", "CR_ISP_CTL"]
+++

Of the 52 words of the render details' 3D register block, our one-triangle job and the closed
driver's differ in two besides the addresses (E326): `CR_ISP_CTL` is 0xf0000 in every closed
capture and 0xf0100 in ours (bit 8, `PROCESS_EMPTY_TILES`), and 0x04c4 is 0x2046400 in the closed
driver's (0x2046500 for a render to a texture, 0x200a400 with a 98-page parameter buffer) and
0x46400 in ours (bit 25). Our job draws exactly with its values; the closed driver clears its
window with drawn geometry, so every tile has an object and bit 8 would change nothing for it.

What is open: whether the closed values change anything on the hardware for our job, whose
background-object clear needs the empty tiles visited; and what 0x04c4's bits 25, 8 and 19:12
hold (they move with a texture target and with the parameter buffer's size).

To settle it: run our tri job at 64x64, 256x256 and 1024x768 with `CR_ISP_CTL` 0xf0000, with 0x04c4
0x2046400 and with both (render details words through the kernel poke), comparing the image and
the render time with the control; and capture 0x04c4 over the parameter buffer sizes of Q084.

Narrowed in 11.15 (E408, three runs each): our tri job's image does change with CR_ISP_CTL at the
closed driver's 0xf0000 (bit 8 clear): 36352 of 65536 pixels at 256x256 and 542720 of 786432 at
1024x768 stay the sentinel, none at 64x64; 0x04c4 at 0x2046400 changes neither the image nor the
time at 64x64, 256x256 and 1024x768, and times follow the number of pokes, not the values. So the
first half is answered; what 0x04c4's bits 25, 8 and 19:12 hold stays open (and the capture over the
parameter buffer sizes of Q084), now Q099. Status: narrowed, not answered.
