+++
id = "Q089"
question = "where does the closed driver's 4x multisampled render become a 64x64 image, when its PBE words are those of a single-sampled 64x64 target and the hardware stores 4x samples as 2x2 blocks; and do alpha to coverage and sample coverage reach the hardware at all?"
unit = "isp"
kind = "hw"
value = "high"
phase = 11
evidence = ["E333", "E339", "E439", "E502", "E503", "E508", "E510"]
terms = ["CR_ISP_MSAA.MODE", "CR_TE_MTILE1", "CR_TE_MACROTILE_STRIDE", "EMIT1.MAXCLIP_X"]
+++

The closed driver's 4x render to a 64x64 texture sets `CR_ISP_MSAA` mode 2, a rotated-grid
`CR_ISP_MULTISAMPLECTL`, halved TE macrotile words and a macrotile stride of 4, but hands the PBE
the end-of-tile words of the single-sampled render: a 64x64 rectangle, a pitch of 64 pixels and the
texture's address (E333, E339). On the hardware mode 2 stores the four samples of a pixel as a 2x2
block of the target (§11.7, E210), which a 64x64 rectangle cannot hold. The only other difference
is one bit of an instruction of the end-of-render program's second task. Alpha to coverage and
sample coverage, plain or inverted, change no word the captures reach (E339).

To settle it: on the laptop, a 4x render of our own stack (mode 2 and the closed driver's TE words)
with the closed driver's PBE words, reading which pixels land and whether they are sample averages,
then the same with that instruction bit flipped in our end-of-render task's equivalent; and a
capture walk that also follows the pixel programs' secondary data for coverage words.

Not run in 11.15: the settle plan needs the closed driver's PBE words and a capture walk of the
pixel programs' secondary data; the poke indices for the PBE words (the closed driver's words are
in a surface description, not in the render details) are not mapped, and no 4x render of our own
stack with them was made. Status: narrowed, not answered; missing: a mapped poke for the PBE words.

Run in 11.16 (E439, 12 probes, three runs each): our stack's 4x render (mode 2, the closed driver's
render and TE words) through our end-of-tile task with the closed driver's PBE words (a 64x64
rectangle, pitch 64) and sidebands (0x200, 0x2200), and with the emit's bit 48 set in either emit,
writes all 4096 pixels of a 64x64 target in 1248 triangle and 2848 background pixels and no other
colour, the same with either sideband and with bit 48 set; a 64x64 rectangle on a 128x128 target
leaves 12288 pixels unwritten. No pixel is a blend of samples, bit 48 changes nothing, and sideband
bit 13 moves the pixels without changing the counts. The end-of-tile task therefore does not
resolve the image; where the closed driver's 4x render becomes 64x64 remains open, and the capture
walk of the pixel programs' secondary data was not run. Status: narrowed, not answered; missing:
where the resolve is (a later pass of the closed driver [infer]) and the coverage words' capture
walk.

Run in 11.26 (E502, E503, E508, identity maps, 48 runs of 40 configurations): with the closed
driver's settings (mode 2, CR_TE_AA 0xe0000000) the stored 64 x 64 image holds 1024 distinct source
pixels of the 4096, each in a 2 x 2 block (by E503's rule, read post hoc, which every tile equals),
and the identity maps cannot show a blend or a resolve, since every sample slot of a pixel holds the
same iterated value (E510 has the colour test). The hardware's stored image is the quarter
window of E503, not a resolved image: the closed texture's 64 x 64 pitch needs something more
(Q138). The capture walk of the coverage words was not run.

Run in the 11.26 resume (E510, msaa-resolve, 66 jobs, 4 of them failed): each single bit of the
end-of-tile sideband flipped from 0x200 and from 0x2200 either leaves the image as it was (50 of 64)
or changes the colour byte order (bits 0, 1), packs two ARGB1555 pixels a dword (bit 2), writes 1024
pixels (bit 3) or a few patterns (bits 9, 12); 4 jobs fail. No pixel is an average of the two
colours (the control image has 24 aligned 2 x 2 blocks that mix them): no single sideband bit of our
emit resolves; combinations of bits and the closed driver's own sideband are not excluded. The
coverage words are still open. Status: narrowed, not answered; missing: Q138 (the later pass of the
closed driver [infer]) and the coverage words.
