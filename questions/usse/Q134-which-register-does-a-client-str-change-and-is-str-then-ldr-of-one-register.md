+++
id = "Q134"
question = "which register does a client str change, and when is an idf drcN, bif required beyond an instance's own store (the host reading during the job, a texture fetch of the stored data)"
unit = "usse"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E480", "E481", "E512", "E513", "E514", "E533", "E534"]
terms = []
+++

The firmware toolchain's question whether `str` then `ldr` needs a fence, answered in 11.29 for a
firmware task and two registers (below): no landed record shows a client `str` that changes
something (usse_isa 6.21: a client `str #671` changed nothing; 7.11: a client `str` was not seen to
land), tools/campaign/regwidth.py lists registers the host writes through /dev/mem, which says
nothing of a client `str`, and the simulator has no vector for it. E481 shows that, with all 2048
instances of the fill storing the same value to the same dword, `stad` then `ldad` of that dword
returns the stored value without a fence; nothing is known of `str` then `ldr`.

What was open: a register a client str can change and a client ldr can read back, and then the
ordering. It was to be settled by an EDM task of our own, or a register found by other means that a
client str reaches; the first is done for two registers (11.29, below), the second is not.

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

After 11.27 what stayed open was `str` then `ldr` (answered below for a firmware task) and, beyond
the instance's own store, when an `idf drcN, bif` after a `stad` is required for a reader other than
a load of the same fill: the `idf` in the storing instance, the host reading during the job, a
texture fetch of the stored data and an EDM task; the order in which instances run is Q143, and the
EDM task is Q131.

Narrowed in 11.29 (not retired). A firmware (EDM) task of ours, which the question named as the way
to settle it, ran `str` then `ldr` of one register: for 0x0814 and 0x0a78 the `ldr` read the stored
value and the host read it afterwards, with 0 to 16 instructions between (and a second `ldr` 64
`nop`s later, which also read it), a `wdf`, an `idf` and a `wdf`, an `idf` alone, or a second `str`,
in 318 of 318 runs (228 of the 306 of the matrix could tell a landed `str` from one that did not,
138 on 0x0814 and 90 on 0x0a78; E534). The 318 are four fresh loads, and the replicates within a
load are not independent. So for these two registers, in a firmware task while the EDM is idle, no
fence was needed between a `str` and the next `ldr`. A `stad` of the result followed by a load, a
`wdf` and two more stores, then the flag the host reads with no `idf`, landed in 18 of 18 runs, and
`ldr` in a firmware task reads `CORE_ID` and `CORE_REVISION` as the host does (E533). That part of
the question is answered for those two registers; the registers whose write has an effect, a job
running, the register-index forms and the time of a `str` are split off as Q154.

What stays open here: which register a *client* `str` changes (the ordering for a client task
follows only once one is known), and when an `idf drcN, bif` after a `stad` is required for a reader
other than a load of the same fill: the `idf` in the storing instance, the host reading during the
job, a texture fetch of the stored data and an EDM task other than the one measured (the order in
which instances run is Q143, a task's overlap Q131). The question is not retired because those parts
have no record.
