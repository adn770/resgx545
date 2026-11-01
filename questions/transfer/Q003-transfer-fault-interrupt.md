+++
id = "Q003"
question = "which event (if any) does a bus-interface fault raise, and what do the fault-request bits of CR_BIF_INT_STAT name?"
unit = "transfer"
phase = 4
evidence = ["E021", "E317", "E319", "E320"]
terms = ["CR_BIF_FAULT", "CR_BIF_INT_STAT"]
+++

In E021 a fill aimed at a page the context's directory maps read-only writes nothing and never
completes. Afterwards `BIF_FAULT` reads `0x32200001` (the page, `CID` 1: the client directory's
list) and `BIF_INT_STAT` reads `0x80020`. No SGX interrupt came, neither for the fault nor as an
SW_EVENT; the host enables only SW_EVENT (`EVENT_HOST_ENABLE` `0x4000`, E006).

Held without recovery (E317, E319, one run each), render faults behave the same way: the
kernel's interrupt counters do not move, and `CR_BIF_INT_STAT` keeps the fault until a reset. Its
low bits differ by what faulted: bit 3 for the TA's read of an unmapped stream page (0x90008),
bit 10 for the EDM's write to a read-only control block (0x80400) and, in a fault the kernel
recovered at once (E320, one run; only its logged status is known), for its read of page 0
through its own directory list, 15 (0xd0400); bit 5 for E021's transfer write; bit 19 is set when
idle. A debugfs reset (halt, the
firmware's buffers rebuilt, boot) recovers each in place (render_uapi.md §10).

Open: which event a fault raises and whether the host must enable it to see one; which requester
each of bits 15:0 names, beyond the three seen; what bits 16 and 18 mean.

To settle it: a fault held with each event enabled in turn in `CR_EVENT_HOST_ENABLE`, the host
interrupt counted, and faults from each unit's requests.
