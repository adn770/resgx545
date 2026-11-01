+++
id = "Q080"
question = "what do the USSE words no form decodes (classes 2, 22 and 26) do: which stop the stores after them, and which write registers?"
unit = "usse"
kind = "hw"
value = "low"
phase = 11
evidence = ["E297", "E368"]
terms = []
+++

Twelve words the decoder rejects, three per class, ran in a fill without a hang or a fault;
eleven match no form's mask, and one of class 22 is bilin's word with a reserved format value
(enc[41:40] = 3), not a gap (E297).

Narrowed by E368: in classes 2, 22 and 26 enc[50] ends the program at the word. Each of the nine
words with enc[50] set, as run or flipped, lost the stores after it and the pixel's own final
write, the pixel keeping the job before's value; each with it clear ran on (six) or hung the job
(three: two class 2 words with enc[50] cleared, and one class 26 word as run, which completed in
11.7). Flipping any other bit of a class 2 and a class 26 word keeps the end; on a class 22 word
with enc[50] clear, bits 32, 33 and 51 remove the 3 or 4 pixels it writes 0, bits 44, 45 and 46
leave 7, 12 and 15 of them, and the other bits 2 to 6 (one run of each flip: the count of the
unflipped word varies, so only bits 44-46 are clear of it; repeats are needed).

What is open: what the words that run on write (the class 22 word's pixels of 0, the class 26
word that, with enc[50] cleared, writes r10-r17, r7 and r8), why some hang, and class 31 with
enc[50] set (one changed nothing).

To settle it: the run-on words with every register read back (all_dump.s), each run ten times so
that a hang is counted; class 31 words with enc[50] set and clear.
