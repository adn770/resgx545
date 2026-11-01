+++
id = "Q094"
question = "what decides how many vertices the closed driver gives a vertex task (VDM_TASK0.MAX_VERTICES 15, 13, 9, 7 or 2 in the captures)?"
unit = "vdm"
phase = 11
evidence = ["E346"]
terms = ["VDM_TASK0.MAX_VERTICES", "VDM_TASK1.OUTPUT_SIZE"]
+++

Over 1888 captured index lists the field is 15 for most GLES2 draws (one to four output rows,
one attribute), 13 with eight vertex attributes and two output rows, 2 with nine output rows,
9 for every GLES1 draw (three output rows) and for GLES2's point-size shader (three), and 7 for
the clears and screen-space pieces (two output rows) (E346). A budget over the attribute and
output rows fits the eight-attribute and nine-output draws, but not GLES1's 10 vertices at three
output rows against 16 at four in the shader corpus.

To settle it: capture shaders that step the outputs from one to nine rows and the attributes
from one to eight, one at a time, and on the laptop run our triangle with the field at the values
the closed driver picks and above them, with as many output rows, to see where a task overruns.
