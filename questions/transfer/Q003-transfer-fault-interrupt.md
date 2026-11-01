+++
id = "Q003"
question = "which event (if any) does a bus-interface fault raise, and what do the fault-request bits of CR_BIF_INT_STAT name?"
unit = "transfer"
phase = 4
evidence = ["E021", "E317", "E319", "E320", "E357"]
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

Open: whether any host-enabled event follows a fault (our debug interface cannot write
`CR_EVENT_HOST_ENABLE`); which requester each of bits 15:0 names beyond those seen; bits 16 and 18.

To settle it: a kernel switch that enables one more host event at a time while a fault is held,
the host interrupt counted.

Not run in 11.16: debugfs kreg refuses CR_EVENT_HOST_ENABLE, so no host event can be enabled while
a fault is held. Kernel need: a debugfs switch that writes that register one bit at a time, with
the host interrupt count read, for faults of the TA, the 3D and the PDS (the hold_recovery faults
of E317, E319 and E363 are ready). Status: narrowed, not answered.
