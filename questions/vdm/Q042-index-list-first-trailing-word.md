+++
id = "Q042"
question = "what does the index list's first trailing word (VDM_INDEX2) do, when 0, 0x10000000 and 0x70000000 leave what the TA writes byte for byte the same?"
unit = "vdm"
phase = 11
evidence = ["E188"]
terms = ["VDM_INDEX2.WORD", "VDM_INDEX0.WORDS_PRESENT", "VDM_INDEX3.INDEX_WRAP"]
+++

An index list in the VDM stream is a header word, the index base and two trailing words; the
glossary reads header bits 22 and 23 as announcing them. In the five-copy job (E188) the second
trailing word acts on the indices: 0 leaves them alone, 1 makes the TA write no object, 5 fits a
wrap of the indices by 5, and 8 hangs the job. The first trailing word does nothing seen: at 0,
0x10000000 and 0x70000000 the parameter buffer and the TA data are byte for byte those of the plain
five-copy scene. The value the job itself writes there was not read.

The glossary's reading of the word, an instance count or a split of the list, is a hypothesis from
other index-list formats: no run has shown a count or a split.

To settle it: dump the job's own VDM stream to read the word's value, then run the five-copy job
with the word at small values (1, 2, 3 and 5), with only bits 7:0 set and with only bits 27:24 set,
saving the parameter buffer and the TA data after each job, two runs each. An instance count would
repeat the copies in the object, a split would cut the primitive list, and a word that acts only on
hardware the job does not use would leave every dump unchanged.
