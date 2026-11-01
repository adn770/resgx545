+++
id = "Q066"
question = "what do the three background-object words the 3D kick writes mean to the ISP, and what are the other words of a render's background object?"
unit = "isp"
phase = 11
evidence = ["E069", "E162", "E209", "E216"]
terms = ["CR_ISP_BGOBJVALS", "hw_render_details.pds_bgnd"]
+++

At each 3D kick the EDM writes dwords 0 to 2 of the RT data's background object from the render
details (E162). In a transfer's background object the coordinate words are read vertex by vertex
(E209), and the format word after them changes nothing over eight values (E069). CR_ISP_BGOBJVALS
bit 9 decides whether the object is drawn (E216).

What is open (3d.md §5.3): what the three words mean to the ISP, and the rest of a render's
background object.

To settle it: on the laptop, the triangle job's background object poked word by word and bit by bit
through the render-details words it is built from (rd:69, rd:76, rd:77), with a coloured background
so that a change shows, every pixel read back.
