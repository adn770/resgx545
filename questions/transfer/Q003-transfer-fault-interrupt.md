+++
id = "Q003"
question = "which event (if any) does a bus-interface fault raise, and what do the fault-request bits of CR_BIF_INT_STAT name, and what clears a latched fault in CR_BIF_INT_STAT and CR_BIF_FAULT while leaving the bus usable?"
unit = "transfer"
kind = "hw"
value = "medium"
phase = 4
evidence = ["E021", "E024", "E317", "E318", "E319", "E320", "E354", "E355", "E357", "E444",
            "E203", "E313", "E362", "E363", "E395", "E457", "E476", "E573", "E631", "E722", "E729",
            "E764", "E765", "E766", "E767"]
terms = ["CR_BIF_FAULT", "CR_BIF_INT_STAT", "misc_info"]
+++

In E021 a fill aimed at a page the context's directory maps read-only writes nothing and never
completes; no SGX interrupt came (the host enables only SW_EVENT, E006). Held without recovery
(E317, E319, one run each) render faults behave the same way: the interrupt counters do not move
and `CR_BIF_INT_STAT` keeps the fault until a reset. Its low bits differ by what faulted: bit 3
for the TA's read of an unmapped stream page (0x90008), bit 10 for the EDM's write to a read-only
page (0x80400, E319; again for the PB builder's write, E362), bits 10 and 16 with 18 for a
background program's fetch at a low address (0xd0400) and bit 13 for one in the pixel PDS heap
(0x92000, E363); bit 5 for E021's transfer write; bit 19 is set when idle.

Narrowed by E357 (one fault sampled from before its kick): the fault raises no bit of
`CR_EVENT_STATUS` or `CR_EVENT_STATUS2` of its own other than `CR_EVENT_STATUS2` bit 7, which sets
right after it, as it does for a TA that hangs without a fault. `CR_BIF_FAULT`'s bits 3:0 name the
faulting directory list (E360).

Narrowed by E444 (debugfs kregnow writes the host enables while a fault is held, 14 held faults of
three kinds): the bits that follow a TA read fault and a background-program fetch fault,
`CR_EVENT_STATUS2` bits 7 (`TRIG_TA`) and 6 (`TRIG_3D`), are host events (alone they raise the host
interrupt once enabled), but bit 7 is the TA trigger's and not the fault's alone (E357); the EDM's
write fault sets none. `CR_EVENT_STATUS` bit 29 (`TIMER`) and `CR_EVENT_STATUS2` bit 10
(`DCU_INVAL_COMPLETE`), set when idle, are host events too. The EDM's write to a read-only page
leaves the status registers as they are idle.

Open: which requester each of bits 15:0 of `CR_BIF_INT_STAT` names beyond those seen; bits 16 and
18; whether a fault of another unit (the 3D's own fetches, the texture unit, a transfer) sets
another status bit; what raises bits 7 and 6 of `CR_EVENT_STATUS2` besides a hang.

Known from the former Q028 (E024, E317-E319, E354, E355): on a fault the kernel stops and resets
the core, boots the firmware again in place and later jobs run exactly (E024). Held without
recovery (debugfs `hold_recovery`), a faulted job leaves the fault in `CR_BIF_INT_STAT`, and a
faulted or hung job wedges the EDM: GETMISCINFO is not answered, other contexts' jobs do not run and
the tick's count stays still (E317-E319); that the stall is the EDM's task waiting on the faulted
bus is a reading of the still count (E317) [infer]. A debugfs reset written while the hold is set
recovers the held job with blame, once, the held job failing with its detector's error and not
running again (E354), and a cleanup that fails while held keeps the hold (E355).

Open, from the former Q028: which part of the reset a latched fault needs to clear
`CR_BIF_INT_STAT` and `CR_BIF_FAULT` (the core reset alone, with the bus interface's registers
rewritten, or the firmware boot after it), and what leaves the bus wedged for another context's
jobs, seen through the registers alone: `CR_BIF_INT_STAT`, `CR_BIF_FAULT`, `CR_BIF_CTRL` and the
status registers before and after each step. Which steps the kernel's recovery should take is the
kernel's design and is not the target.

To settle it: the same enables over faults of the other requesters (a transfer to a read-only page,
a texture fetch from an unmapped page, a 3D store to one), the status registers read and the
interrupts counted for each; and, after a held fault, the debugfs register writes one reset step at
a time (kregnow) with the bus interface's registers read after each and a job on another context
after the last.

Folded in 11.21: Q028 is retired into this question, which is not an answer to it. Q111 holds the
other event sources and what sets each status bit.

Requestor table, 2026-11-09 (a compilation of the words the records already hold, not a new
measurement; `FAULT_REQ` is bits 15:0 and `FAULT_TYPE` bits 18:16, glossary G0772 and G0773). The
word is `CR_BIF_INT_STAT` at the fault, type is bits 18:16, req the bit set in 15:0:

| word | type | req bit | what faulted | record |
|---|---|---|---|---|
| 0x80020 | 0 | 5 | a transfer's pixel write to a read-only page | E021, E024 |
| 0x90020 | 1 | 5 | a transfer job (3 of E024's 4 faults; which was which is in E024) | E024 |
| 0x90002 | 1 | 1 | a texture fetch past the probe's scratch [infer] | E722 |
| 0x90004 | 1 | 2 | a render's access past the end of the TA data | E203, E313, E729 |
| 0x90008 | 1 | 3 | the TA's read of an unmapped stream page | E317, E318, E444 |
| 0x80400 | 0 | 10 | the EDM's write to a read-only page | E319, E362, E457 |
| 0x90400 | 1 | 10 | buffers 6 to 11 left out; a partial owner closed unkept | E457, E631 |
| 0xd0400 | 5 | 10 | a background program's fetch at a low address | E363 |
| 0x91000 | 1 | 12 | buffer 0 (0x30000000) left out; a placed program's `lapc` | E573, E476 |
| 0xd1000 | 5 | 12 | every buffer id left out (0xffff) | E457 |
| 0x92000 | 1 | 13 | a PDS program's fetch in the pixel PDS heap | E363 |
| 0xd2000 | 5 | 13 | PDS store faults | E395 |

Bits seen in 15:0 are 1, 2, 3, 5, 10, 12 and 13; not seen are 0, 4, 6 to 9, 11, 14 and 15. Type 0
appears with a write to a read-only page and type 1 with an unmapped page [infer]; type 5 (bits 18
and 16) appeared with a fetch of the background program at a low address, a PDS store, and the
case where every buffer id was left out. Bit 19 is set in every word and when idle. The words name
the requestor of the faulting access, not a list or a context; the table does not say which bit a
fault of the 3D's own fetches or of the ZLS would set, since none has faulted. The rows marked
[infer] carry the reading of the record's author, not a separate test of the bit. The question
stays open: bits 16 and 18 beyond the types, the unseen requestors, and what clears a latched
fault.

Note 2026-11-10 (a reading of the published kernel logs, not a new measurement). The requestor table
above says that bits 0, 4, 6 to 9, 11, 14 and 15 of FAULT_REQ were never seen. The kernel logs of
resgx545-data hold BIF fault words with bit 7: 0x90080 (ta/points, usse/output-room-rd,
render/hold-fault) and 0xd0080 (usse/output-room-rd); bit 8: 0x90100 (ta/mtile-fields,
ta/mtile-fields-risky, ta/te-psg, ta/te-words-repeat); bit 9: 0x90200 (zls/control-bits); and type-5
forms with bit 1, 0xd0002 (texture/sampler-bits), and bit 3, 0xd0008 (usse/output-room-vdm, S1's
g-e4 and S1b's g-e4w, the last two from a bit-25 index list header, E737, E756). So bits 7, 8 and 9
are seen. Which requestor each names is not established (the log line carries the word and the
address), and the statement that no ZLS access has faulted rests on zls/control-bits, whose jobs
faulted at 0x90200 with bits of the ZLS control word set (E411's data) and are not identified as a
ZLS fetch. Bits 0, 4, 6, 11, 14 and 15 are still not seen.

Narrowed in S3 (2026-11-10, laptop session S3 of the question-closing pass, dataset
render-closing-s3; one run each). Frozen verdict: `Q003 E1: partly: e1-tex HE, e1-xfer-ro HE, a6
(TA write) had no data` (a6 never ran). The two E444 controls reproduce word for word (E764), which
opened the gates. A held texture fault, S1's 16-page L2e2 job, reads `CR_BIF_INT_STAT` 0x90002 and
`CR_BIF_FAULT` 0x3e017001 and `CR_EVENT_STATUS` 0x20000000 with `CR_EVENT_STATUS2` 0x440 at 2.8 s
and 3.8 s, clear after the debugfs reset (E765); the transfer's write fault of E021 (debugfs
`xfer_ro`, no hold needed) reads 0x80020 and 0x32200001, writes nothing, and the same status 0x440
(E766). Neither fault raises a status bit of its own (the frozen HE), unlike the EDM's write fault,
which leaves 0x400 (E444). So of "whether a fault of another unit sets another status bit", the
texture unit's fetch and a transfer's write are answered: bit 6 and no other, no bit 7. Not
answered: the 3D's own stores, the ZLS, a held TA-write fault (a5 and a6 did not run), and the
type-1 transfer fault (0x90020).

Post hoc, from the timeline rows (not frozen, nothing was predicted): in the three held render
faults and the transfer's, `CR_EVENT_STATUS2` bit 7 (TA read) or bit 6 (background fetch, texture
fetch, transfer write) sets 121.1 to 124.1 us after the fault word appears, with `CR_EVENT_STATUS2`
0x400 in between (sampling about every 4.3 us), so the bit follows the fault and is not raised with
it (E764, E765, E766). What sets it, hardware or the firmware's reaction, is open, and bears on
Q082. Also post hoc and [infer]: at the kernel's reset of each of three held render faults
`CR_BIF_INT_STAT` and `CR_BIF_FAULT` read clear (0x80000 and 0) in the first row of the reset,
6.8 to 11.3 ms before the status registers are host cleared and before the kernel writes the clear
bit of `CR_BIF_CTRL` (E767); the kernel's order is halt (deinit script and soft reset), then the
clears. That reads as the halt leaving the fault reading zero, a lead for "what clears a latched
fault"; whether the latch is cleared or only reads zero while the block is in reset, and whether the
clear bit alone clears it without the halt (a kernel change), is not shown. Status: narrowed.
