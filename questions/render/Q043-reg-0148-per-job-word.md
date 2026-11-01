+++
id = "Q043"
question = "does CR_REG_0148, which the firmware loads for every render, partial render and transfer, change anything a job does, when six address forms of it in the triangle job write nothing and change no pixel?"
unit = "render"
phase = 11
evidence = ["E056", "E163", "E160", "E015", "E028"]
terms = ["CR_REG_0148"]
+++

The firmware loads register 0x0148 from render details dword 9 at every 3D kick (E163), from the
render details again when it starts a partial render (E160), and from the transfer command with
the transfer's other register words (E015). Set through a kernel poke of render details dword 9 to a
page of the job's scratch buffer in six numberings, it writes nothing to the buffer and changes no
pixel of the triangle (E056, one run per value). The transfer command sweeps flip every bit of every
word of the command (E028); the record gives the classes of all 1429 cases, not the outcome of the
word that loads 0x0148.

What is open: whether any bit of the register acts on a job, and on which unit. The glossary's
reading, a per-job base or mode for a feature these clients leave off, is a hypothesis.

To settle it: first read the outcome of the transfer word that loads 0x0148 from the sweep data
already taken. Then flip every bit of render details dword 9, and set 0 and 0xffffffff, in the
triangle job, in the five-copy scenes under depth less and punch-through, in a multisampled render
and in a render small enough in parameter buffer to take partial renders, two runs each, every pixel
read back and the register read back after the job. A bit that changes nothing in every job, and
reads back as written, is left for a client that turns on more than these jobs do.
