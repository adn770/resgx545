+++
id = "Q089"
question = "where does the closed driver's 4x multisampled render become a 64x64 image, when its PBE words are those of a single-sampled 64x64 target and the hardware stores 4x samples as 2x2 blocks; and do alpha to coverage and sample coverage reach the hardware at all?"
unit = "isp"
phase = 11
evidence = ["E333", "E339"]
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
