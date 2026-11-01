+++
id = "Q134"
question = "which register does a client str change, is str then ldr of one register ordered without a fence, does one instance see its own unfenced stad and does its store reach the host at the end of the job, and when is an idf drcN, bif required"
unit = "usse"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E480", "E481"]
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

Also open, from E480 and E481: whether one instance sees its own `stad` unfenced, and whether one
instance's unfenced store reaches the host at the end of the job. All 2048 instances stored the same
value to the same dword in those probes, so a load may have seen another instance's identical store
and a lost store of one instance would be hidden by the others (not run: the same programs with a
per-instance address, from pa0 or the instance number in the pointer, or one instance selected by a
test of pa0, as the emitpds probe does; a load of a dword the instance did not store, to read the
store of another). And when an `idf drcN, bif` after a `stad` is required (another instance, the
host during the job, a texture fetch of the stored data): no case in E480 or E481 needed one, and
none tested those readers.
