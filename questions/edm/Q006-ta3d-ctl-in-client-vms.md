+++
id = "Q006"
question = "can a render client's VM carry its own copy of the TA/3D control block at the shared address, which the kernel keeps in step, instead of a writable mapping of the device's?"
unit = "edm"
phase = 6
evidence = ["E023", "E319"]
terms = ["ta3d_ctl"]
+++

While the EDM loads a render context's parameter buffer it runs through that context's page
directory, so the kernel maps every firmware buffer into each render VM at its own address:
read-only, except the TA/3D control block, which the EDM writes in that window. The renders of
E023 run with this mapping.

The first part is answered (E319, one run): with the block mapped read-only (debugfs
`alias_ta3d_ro`) the first kick faults on the block's page (bus status 0x80400) before the PB
load writes dword 46 and before the DPM slot is taken; the job stalls and the EDM answers no
command until a reset. So a render client's VM cannot do without a writable view of the block
while the EDM loads parameter buffers through the client's directory, and the render node keeps
treating its clients as trusted.

Open: whether each VM can carry its own copy of the block at the same address, kept in step by
the kernel, or the EDM can load a parameter buffer through the kernel's directory.

To settle it: a render with a per-VM copy mapped at the block's address (a kernel switch that maps
a private page there and copies the block in and out around each kick).
