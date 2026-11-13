+++
id = "Q108"
question = "what do the page table entry flags WRITEONLY, CACHECONSISTENT and EDMPROTECT do on the hardware, which of the bus interface's requestors do they stop, and what does the fault report?"
unit = "bif"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E021", "E151", "E319", "E945", "E946"]
terms = ["CR_BIF_FAULT", "CR_BIF_INT_STAT"]
+++

A page table entry has a valid bit and four flags: WRITEONLY 0x2, READONLY 0x4, CACHECONSISTENT 0x8
and EDMPROTECT 0x10, with the address in bits 31:12 (doc/specs/hw_spec.md section 4, from the driver
headers, not from a run).

Seen on the hardware: only READONLY. A fill aimed at a page the context's directory maps read-only
writes nothing, never completes and leaves CR_BIF_FAULT naming the page (E021, E151); the EDM's own
write to a read-only block faults with CR_BIF_INT_STAT 0x80400 and CR_BIF_FAULT 0x32004005 (E319).
No record shows a run with any of the other three flags set, so what they do is not known.

Open: whether WRITEONLY faults a read and by which requestor; whether CACHECONSISTENT changes what a
unit sees of the host's writes or what it caches; whether EDMPROTECT keeps the client requestors
(the TA, the 3D, a transfer's pixel side) from a page the EDM may use, and what each fault leaves in
CR_BIF_INT_STAT and CR_BIF_FAULT beyond the bits already seen (Q003).

To settle it: a new kernel switch in the linux fork (so a run needs a fork change; like debugfs
`alias_ro`) that sets a chosen flag combination in the entries of one buffer's alias in a client
directory, then `fill` (a write), `copy` (a read) and
`tri` (the TA's and the 3D's reads and writes) aimed at that buffer, with `--regs` on the bus
interface's registers after each job and the job's status; a read of the host's write from the GPU
side for CACHECONSISTENT.

Narrowed 2026-11-13 (round 8, session r8-k2, decisions R8-5 a and R8-6 a; E945, E946). The round
8 kernel's debugfs vm_pte_flags put one flag on one client mapping. On a 64 x 64 render (E945,
frozen): WRITEONLY faulted both rows (H-WO-ALL held 2 of 2): the colour target's writes all
landed, then the job faulted at the target's last page with SB 31 (BIF_INT_STAT 0x80020), and the
read of the GENERAL page (VDM stream, indices, vertices) faulted before drawing (0x80008);
CACHECONSISTENT on that page changed nothing; EDMPROTECT faulted the colour write (0xa0020,
FAULT_TYPE 2, nothing written) and let the GENERAL page's read through. The transfer's rows (E946)
were gated cannot tell (the end control did not run) and read the same post hoc: WRITEONLY's fill
wrote then faulted at its last page (0x80020, SB 31), a copy's texture read of a READONLY +
WRITEONLY source faulted (0x80002), EDMPROTECT's fill faulted (0xa0020), CACHECONSISTENT on a
copy's source changed nothing. What stays: which access faults at the last page under WRITEONLY
(the pixel side's writes land), WRITEONLY alone on a texture read, EDMPROTECT on reads other than
the stream page's and on the TA's and the EDM's own buffers, flags together, CACHECONSISTENT on
data cached before the host's write, and a held transfer row.
