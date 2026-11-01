+++
id = "Q099"
question = "what do bits 25, 8 and 19:12 of 0x04c4 (render details dword 18) hold, which move with a texture target and the parameter buffer's size in the closed driver's frames?"
unit = "render"
kind = "hw"
value = "low"
phase = 11
evidence = ["E326", "E408"]
terms = ["CR_ISP_CTL"]
+++

Of the 52 words of the render details' 3D register block our one-triangle job and the closed driver
differ in 0x04c4: 0x2046400 in the closed driver's frames (0x2046500 for a render to a texture,
0x200a400 with a 98-page parameter buffer) and 0x46400 in ours (E326). With the closed value on our
job at 64x64, 256x256 and 1024x768, three runs each, neither the image nor the time changes (E408,
which answers Q085's first half).

What is open: what bit 25, bit 8 and bits 19:12 hold, and whether any job shows them. To settle it:
capture 0x04c4 over the parameter buffer sizes of Q084 (the capture harness), and run our parameter-
buffer jobs with the closed values of each size through the kernel poke rd:18.
