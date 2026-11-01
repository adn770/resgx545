+++
id = "Q080"
question = "what do the USSE words no form decodes (classes 2, 22 and 26) do: which stop the stores after them, and which write registers?"
unit = "usse"
phase = 11
evidence = ["E297"]
terms = []
+++

Twelve words the decoder rejects, three per class, ran in a fill without a hang or a fault;
eleven match no form's mask, and one of class 22 is bilin's word with a reserved format value
(enc[41:40] = 3), not a gap. The three of class 31 changed nothing; the three of class 2, the
bilin word and one of class 26 left the program's sixteen stores unwritten, exactly the five
with enc[50] set (the `.end` bit of mov, nop, fmad and bilin); two of class 22 changed some
pixels (E297). About 4 percent of random words match no form's mask.

To settle it: on the laptop, first enc[50]: each of the five words with it cleared, and words of
classes 2, 22 and 26 with it clear set, so that an end of the program shows; then, per class,
words that differ from one with an effect by one bit at a time, so that the other bits that
matter show; the stores of the template replaced by moves to the pixel, so that a store that is
redirected rather than dropped is found; two runs.
