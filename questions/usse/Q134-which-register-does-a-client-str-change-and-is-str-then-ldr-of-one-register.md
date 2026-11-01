+++
id = "Q134"
question = "which register does a client str change, is str then ldr of one register ordered without a fence, and when is an idf drcN, bif required beyond an instance's own store (the host reading during the job, a texture fetch of the stored data)"
unit = "usse"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E480", "E481", "E512", "E513", "E514"]
terms = []
+++

The firmware toolchain's question whether `str` then `ldr` needs a fence is open: no landed record
shows a client `str` that changes something (usse_isa 6.21: a client `str #671` changed nothing;
7.11: a client `str` was not seen to land), tools/campaign/regwidth.py lists registers the host
writes through /dev/mem, which says nothing of a client `str`, and the simulator has no vector for
it. E481 shows that, with all 2048 instances of the fill storing the same value to the same dword,
`stad` then `ldad` of that dword returns the stored value without a fence; nothing is known of
`str` then `ldr`.

What is open: a register a client str can change and a client ldr can read back, and then the
ordering. To settle it: an EDM task of our own (phase 12), or a register found by other means that
a client str reaches.

Narrowed in 11.27: one instance sees its own unfenced `stad` (E512: each of the 2048 instances of
the fill stored a value of its own to a dword of its own and loaded it back, 2048 of 2048 pixels in
each of nine cases, with `ldad`, `.bypassl1`, `.fcfill`, `drc1`, a `wdf` only, two stores, an `idf`
between and the `idf` at the end), and its store changes the dword the host reads with no fence at
all (2048 dwords changed, 32 values read, in the seven cases that ended with no `idf` and no fence);
the four lanes of a quad each do the same (E513, where a test of `pa0` selected a quad of four
lanes, not one instance). A load of another instance's store returns it when that instance ran
earlier, whole quads and lower-numbered instances in 2048 of 2048 and 1024 of 1024 pixels, and in
part when it runs later (E514); no case run needed an `idf`. So the part of this question about one
instance's own store is answered for a client pixel task.

What stays open here is `str` then `ldr` (above), and, beyond the instance's own store, when an `idf
drcN, bif` after a `stad` is required for a reader other than a load of the same fill: the `idf` in
the storing instance, the host reading during the job, a texture fetch of the stored data and an EDM
task; the order in which instances run is Q143, and the EDM task is Q131.
