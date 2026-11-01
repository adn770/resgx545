+++
id = "Q003"
question = "why does a transfer render that faults on a read-only page raise no BIF-fault interrupt the host sees, and how does a host recover the EDM in place afterwards?"
unit = "transfer"
phase = 4
evidence = ["E021"]
terms = ["CR_BIF_FAULT", "CR_BIF_INT_STAT"]
+++

In E021 a fill aimed at a page the context's directory maps read-only writes nothing and never
completes. Afterwards `BIF_FAULT` reads `0x32200001` (the page, `CID` 1: the client directory's
list) and `BIF_INT_STAT` reads `0x80020`. Bit 5 is among the fault-request bits (15:0) the
kernel's SGX interrupt handler counts, but the handler counted none: no SGX interrupt came at
all, neither for the fault nor as an SW_EVENT. The host enables only SW_EVENT
(`EVENT_HOST_ENABLE` `0x4000`, E006). The EDM then did not answer a POWEROFF request; only a
halt, a reload of the firmware's buffers and a boot recovered it.

Open: which event (if any) the fault raises and whether the host must enable it; what bit 5 of
`BIF_INT_STAT` means; which state a recovery in place must rebuild (the DDK's hardware recovery
resets the core and reboots the EDM). Phase 9 (the render path, with its job recovery) is where
a run would settle it: fault with each event enabled, then a recovery without a reload.
