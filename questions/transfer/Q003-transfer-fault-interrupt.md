+++
id = "Q003"
question = "which event (if any) does a bus-interface fault raise, and what do the fault-request bits of CR_BIF_INT_STAT name?"
unit = "transfer"
phase = 4
evidence = ["E021", "E317", "E319", "E320", "E357", "E444"]
terms = ["CR_BIF_FAULT", "CR_BIF_INT_STAT"]
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

To settle it: the same enables over faults of the other requesters (a transfer to a read-only page,
a texture fetch from an unmapped page, a 3D store to one), the status registers read and the
interrupts counted for each.
