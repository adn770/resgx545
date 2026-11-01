+++
id = "Q164"
question = "what does bit 21 of the control-stream primitive word mean, which puts one dword (0x00000400 in 336 cases and 0x00001000 in 30) after the object word in the forms 0xa0 to 0xbf, and what do the bits of the word's 15:8 beyond the low byte of the vertex mask hold"
unit = "ta"
kind = "hw"
value = "low"
phase = 11
evidence = ["E542", "E546", "E702"]
terms = ["CSTREAM.PRIM_TILES", "CSTREAM.OBJ_ISP_ADDR"]
+++

In the vertex-task jobs' streams (E546, 61 jobs) the primitive word's tile field takes the forms
0x80, 0x88, 0x8a, 0x8c, 0x90, 0x98 and also 0xa0, 0xa8, 0xaa, 0xac, 0xb0 and 0xb8: the same forms
with bit 21 set and one dword between the object word and the masks. Of the 4201 primitive words of
those jobs 366 have bit 21 (0xb0 191, 0xaa 77, 0xac 38, 0xa8 30, 0xa0 20, 0xb8 10) and their extra
dword is 0x00000400 in 336 and 0x00001000 in 30; 14 words have the tile field 0x81 (bit 16 set) and
are not read. The objects with the extra dword lie at high dword addresses (0xc31 and above: past
the first parameter page?). In the single-tile forms bits 15:8 are the low byte of the vertex mask
(3 bits for each listed primitive: 81 of 81 regions, E542), which cannot hold more than 8 vertices.

Open: what bit 21 and its dword mean (a page of the object? the object's vertex block address?), and
the mask's layout for objects of more than 8 vertices.

To settle it: objects placed on the second and third parameter pages (the heap offsets of E288) and
the dword compared with the object's page; objects of 9 to 16 vertices in single-tile forms. No
kernel change.

Stated in 11.39 (E702, E703; merge 14). The head of an object with bit 21 is on page (extra >> 10) -
1 of the parameter buffer, the
tail being the bytes before the object word: 45 of 49 objects on E546's 61 jobs (fitted there;
4 of 49 with the page before the tail), 12 of 13 objects in E702 (the one miss holds a
constant-row vertex, Q272) and 2 of 2 in E703's natural jobs, the page before the tail
identifying 0 of 25 in these; the 10 bit-21 objects of E703's forced jobs fail the claim (2 of
12 in that table), which is not a test of it, since those jobs are broken (Q271); all analysed
after the run and not frozen. The extra words seen are 0x400, 0x800, 0xc00
and 0x1000; the five 0x1000 objects and the form 0x81 are not explained; the decoders that assume
a contiguous object (first_object, all_objects) are to be fixed.
