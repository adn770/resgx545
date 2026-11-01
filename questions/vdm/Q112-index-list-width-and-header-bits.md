+++
id = "Q112"
question = "what do bits 25:24 of the index list header do, which are clear in all 1888 captured lists, and does the TA take indices wider than the 16 bits the captured lists use?"
unit = "vdm"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E188", "E346", "E414"]
terms = ["VDM_INDEX0.PRIMITIVE_TOPOLOGY", "VDM_INDEX0.WORDS_PRESENT", "VDM_INDEX3.INDEX_WRAP"]
+++

The index list is six words: a header with bits 31:30 = 2, the topology in 29:26, bits 25:24 clear,
both trailing-word bits 23:22 set and the count in 21:0; the base; two trailing words; two task
words (E346). Topologies 0 to 4 (triangles, lines, points, strip, fan) were captured, and strips and
fans run on our job (E414). The captured index buffers hold 16-bit indices (E346), and the second
trailing word, 0x003fffff in every list, acts on the indices (E188).

Open: whether header bits 25:24 select the index width (16 or 32 bit) or something else, what
indices above 16 bits do when the list names them. The first trailing word's own bits are Q042 and
Q092. The geometry the simulator takes from indexed draws depends on the width.

To settle it: `probe --tri` with `--vdm N^=V` flipping the index list header's bits 25:24 over an
index buffer of 16-bit and of 32-bit values, the object's vertices and the primitive list
(`--dump-render`) compared with the unflipped job.
