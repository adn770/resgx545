+++
id = "Q003"
question = "which event (if any) does a bus-interface fault raise, and what do the fault-request bits of CR_BIF_INT_STAT name, and what clears a latched fault in CR_BIF_INT_STAT and CR_BIF_FAULT while leaving the bus usable?"
unit = "transfer"
kind = "hw"
value = "medium"
phase = 4
evidence = ["E021", "E024", "E317", "E318", "E319", "E320", "E354", "E355", "E357", "E444"]
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
