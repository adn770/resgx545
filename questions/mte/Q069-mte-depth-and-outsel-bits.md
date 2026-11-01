+++
id = "Q069"
question = "is a depth outside [0, 1] clipped, and what do OUTSEL bits 12 and 13 and the rest of the state block's presence word select?"
unit = "mte"
phase = 11
evidence = ["E061", "E066", "E192", "E193", "E198"]
terms = ["OUTSEL", "VIEWPORT.Z_OFFSET", "VIEWPORT.Z_SCALE"]
+++

The viewport's words scale and place the triangle (E061) and the depth is the z offset plus the z
scale times z (E193); on a flat triangle it is the z offset alone (E066). A coordinate set takes
OUTSEL's vertex size and two other words changed together (E192), and OUTSEL bits 7:0 enable user
clip planes (E198).

What is open (3d.md §9, §9.1 and §9.4): whether depth outside [0, 1] is clipped, what OUTSEL bits
12 and 13 do, and the state block's presence word beyond the fields named.

To settle it: on the laptop, the triangle with its depth driven past 0 and 1 by the z offset against
a loaded depth buffer; OUTSEL bits 12 and 13 flipped with one and two coordinate sets and the
parameter buffer dumped; the presence word's bits flipped one at a time, three runs.
