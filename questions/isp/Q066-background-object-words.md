+++
id = "Q066"
question = "what do the three background-object words the 3D kick writes mean to the ISP, and what are the other words of a render's background object?"
unit = "isp"
kind = "hw"
value = "high"
phase = 11
evidence = ["E069", "E162", "E209", "E216", "E410", "E590", "E970", "E971", "E972", "E973", "E1006"]
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

Narrowed in 11.15 (E410, one run each): the render details dwords 76 and 77, flipped bit by bit and
at 0 and 0xffffffff, change nothing on the one-triangle job (66 of 66 jobs give the control's
image); dword 69 (0x32411214) with 11 of its 32 bits flipped gives one other image (2860 of 4096
pixels wrong, the background pixels green) and with the other 21 bits, and at 0 and 0xffffffff,
faults the job. So the first word is the one the background pixel program starts from and the second
and third are not read as poked by this job [infer]. Still open: what the second and third words
mean to the ISP, and the rest of a render's background object. Status: narrowed, not answered.

Narrowed in 11.34 (E590, kernel commit 46: kpoke space `bg`, 169 jobs, 64x64, one triangle on a
coloured background, ISP_BGOBJVALS 0x300): the object of this render, which has no texture layer,
is 17 dwords, the three PDS words, six zero words and eight words that read as the corners of a
rectangle [infer] (0x463000 of the debugfs render_param dump). A poke of any one of the words 3 to
16, at ten values each (8 bit flips, 0 and 0xffffffff: 140 jobs, 131 of them changing the word),
and of all of them together at three values (6 jobs), changes no pixel, and the poked value reads
back in the object after the job each time; a poke of the words 0 to 2 is not in the object after
the job (18 of 18: the EDM's value, E162) and changes nothing. So in this scene the ISP is not
shown to read the words 3 to 16; there is no positive control for that (every word the ISP is shown
to read is rewritten by the EDM after a poke), only E410's change of the image through the render
details' dword 69, which shows that the path from the object to the image is live in this job. The
words 1 and 2 are not shown read or not read: the EDM rewrites them after the poke, and E410's jobs
poked the render details, not the object. Still open: what the three PDS words mean (word 0 starts
the background pixel program, E410), the rest of the object in other scenes (another size, another
ISP_BGOBJVALS, more triangles), and whether an object with texture layers (the 23-dword form of a
copy) reads its coordinate words and which of the words 3 to 8 then matter, Q190. Status: narrowed,
not answered.

Note 2026-11-13 (round 9 offline, decision X-1 a (O9-3); no record, no claim settled). Round 9's
K1 session r9-k1 (module B60AB0B4's `render_bg_layer` and `render_bg_src` knobs, the 23-dword
background object with a texture layer, Q190) reads parts of this question's open clauses as
exploration rows: the vertex words 15 to 22 of the layered object one at a time (whether the
layer's plane is anchored at the vertices they give or at the fixed render box), words 9 to 14
(format and zero words, eight values of word 10), and word 1's rows at 0, 1 and 4 with a texel
layer (whether the texel still arrives). Words 0 to 2 are not poked (the EDM rewrites them, E590).
Their reading lands in that session's records.

Narrowed 2026-11-13 (r9-k1: E970 to E973; Q190 retired as answered by E971 and E972). With a
texture layer (module B60AB0B4's `render_bg_layer`) the render's object is the copy's 23 words
(E970); words 3 to 8 are the layer's (u, v) at TL, TR and BL, read vertex by vertex (E971), and the
vertex words 15 to 22 anchor the layer's plane at the vertices E590's decoding gives (TL in 15 and
16, TR in 17 and 18, BL in 20 and 21; 19 and 22 unread in those rows) while the render box stays
covered whatever they say (E972). Words 9 to 14 and the format word 10 change nothing at 1.0 and
at seven format values; at 0xffffffff the format word gives texel (0, 0) everywhere, as in a copy,
words 11, 12 and 14 each remove one coordinate's variation and words 9 and 13 change nothing
(E973). The command's attribute-row word (bgobj_words[1], copied into word 1) gives each pixel its
own texel at one and four rows and other texels at zero (E973). Still open: what words 11 to 14
hold (only 1.0 and 0xffffffff ran), word 13's and 9's role, the three PDS words beyond word 0
(E410), and other scenes (sizes, ISP_BGOBJVALS, more than one layer). Status: narrowed, not
answered.

Narrowed 2026-11-13 (round 10, r10-geo stage bgw, E1006). Words 12, 14 and 11 at 0.25, 0.5, 1.5 and
-1.0 and words 9 and 13 at 2.0 and -1.0 leave every background pixel its own texel (16 of 16 held
out), and a scale of one coordinate by the word (0 read as 1) is refuted on 12 of 12: with E973
the finite values run change no texel and only a NaN does. sgx-pipe's `bglayer::check` admits the
values that ran. Still open: what words 11 to 14 hold (terms that are zero in this scene
[infer]), word 13's and 9's role, the three PDS words beyond word 0 (E410), and other scenes.
Status: narrowed, not answered.

Moved 2026-11-15 from Q019 (R24-3 a, with E1104: a fill's douta reaches attributes 0-63 at every
size from 0 to 8 rows, so the size field's effect seen here belongs to this scene). Round 10's note
there (decision R10-1 a (O10-5); no claim settled): E973 is the first
record in which the secondary attribute size changes a result: in r9-k1's layered background object,
bgobj_words[1] at 0 rows (0x30000) gave each background pixel a texel of the source but its own at
only 74 of 3034 (143 distinct texels, mostly within 8 columns and 4 rows of its own; no texel at
all, H-NOTEX, refuted), while at 1 and 4 rows every pixel had its own texel. So at 0 rows the field
limits what reaches the background layer's task [infer], unlike E125's and E391's fill, where 0 rows
passed all of the attributes tried. Which attributes go missing is not read (the texels are a
symptom, not a register dump), and the 32 or 64 attribute experiment of Q019 has since run (E1104:
no limit up to 64 in a fill).
