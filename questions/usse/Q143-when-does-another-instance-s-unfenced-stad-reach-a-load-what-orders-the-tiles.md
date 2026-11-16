+++
id = "Q143"
question = "when does another instance's unfenced stad reach a load, what orders the tiles and quads (the left 32 columns before the right, a quad together), and (moved from Q134) when is an idf drcN, bif needed beyond an instance's own store, for a reader other than a load of the same fill (the idf in the storing instance, the host reading during the job, a texture fetch of the stored data, a firmware task other than the one measured)"
unit = "usse"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E512", "E513", "E514", "E481", "E533"]
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

**Correction 2026-11-16 (round 31, with the user):** Q134's `idf` clause moves here (Q134 keeps
its `str` clause): when an `idf drcN, bif` after a `stad` is required beyond an instance's own
store, for a reader other than a load of the same fill. The line above says so and the list gains
Q134's evidence for it. From Q134's text: with all 2048 instances of the fill storing the same
value to the same dword, `stad` then `ldad` of that dword returns the stored value without a fence
(E481); one instance sees its own unfenced `stad` and its store changes the dword the host reads
with no fence at all (E512, E513), and no case of E514 needed an `idf`; in a firmware task of ours
a `stad` of the result followed by a load, a `wdf` and two more stores, then the flag the host
reads with no `idf`, landed in 18 of 18 runs (E533), and an unfenced store at the end of a task
acts as in a fill (E534). Open from it: the `idf` in the storing instance, the host reading during
the job, a texture fetch of the stored data and an EDM task other than the one measured (a task's
overlap is answered by E752).
