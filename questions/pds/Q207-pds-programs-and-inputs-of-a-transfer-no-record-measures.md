+++
id = "Q207"
question = "what do the PDS programs of a transfer do with the inputs and instructions no record measured: if0 and if1, ir2, a movs reading ir1.l and tim.l in the primary program, and a program that is not one of the three templates the records ran?"
unit = "pds"
kind = "hw"
value = "medium"
phase = 12
evidence = ["E130", "E262", "E263", "E043", "E265", "E620"]
terms = ["PIXEL_EVENT.END_OF_TILE"]
+++

The transfer model (E620) runs the secondary, primary and pixel-event PDS programs of a fill or a
copy through the PDS simulator and refuses under this question whatever the simulator does not
know: an instruction or an input (`if0`, `if1`, `ir2`, the specials of a `movs` outside the
programs where they were measured) no record measured, and any program whose code is not one of the
three templates the records ran. The code of the three is pinned by hash because the simulator's
`alu_specials_in_movs` input (a `movs` reads `ir1.l` and `tim.l` as the ALU reads `ir1` and `tim`)
is measured for the secondary and the pixel-event programs (E263) and only supported by the unpoked
jobs' image hashes for the primary program; with it off 24 of 13679 scenes match. 890 scenes of
the transfer replay are refused here, 466 of which the hardware completed with an image, 338 with
a fault and 86 with a hang: the model does not use that outcome to refuse.

Open: whether `if0` and `if1` test true in the primary and pixel-event programs (they are open on
SGX), what `ir2` reads in them, what the primary program's `movs` reads of `ir1.l` and `tim.l`, and
what the hardware does with a program the templates do not cover.

To settle it: a primary-program probe that stores its `movs` specials for `ir1.l`, `tim.l` and
`ir2.l`, and one that branches on `if0` and `if1`, run on the laptop with a fill and a copy.
