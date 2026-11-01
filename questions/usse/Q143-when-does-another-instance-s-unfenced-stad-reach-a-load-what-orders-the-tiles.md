+++
id = "Q143"
question = "when does another instance's unfenced stad reach a load, what orders the tiles and quads (the left 32 columns before the right, a quad together), and when is an idf drcN, bif needed for another reader (the host during the job, a texture fetch of the stored data, a firmware task)"
unit = "usse"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E512", "E513", "E514"]
terms = []
+++

E512 to E514: an instance sees its own unfenced stad and its store changes the dword the host reads
with no fence (a client pixel task); a load of a dword another instance stored returns it when that
instance ran earlier (2048 of 2048 for a quad, 1024 of 1024 lower-numbered in three masks, 1024 of
2048 for n ^ 1023, the pixels x >= 32) and for later ones only some (64 after no delay, 792 and 984
of 1024 after 64 and 192 `nop` for n ^ 2, 0 of 1024 for n ^ 32 after 192).

What is open: what runs the halves in order ([infer] the 32-wide tiles of the target), whether a
delay long enough shows the stores of the higher-numbered tile, an idf placed in the storing
instance after its stad (not run, only before the load), the host reading during the job, a texture
fetch of the stored data, and the same in a firmware task (phase 12). To settle it: the same table
with an idf in the storing instance before the loads, a target of other sizes, and a late host read
(`--late`).
