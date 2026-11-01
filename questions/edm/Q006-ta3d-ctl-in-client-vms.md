+++
id = "Q006"
question = "can a render client's VM do without a writable mapping of the device-wide TA/3D control block?"
unit = "edm"
phase = 6
evidence = ["E023"]
terms = ["ta3d_ctl"]
+++

While the EDM loads a render context's parameter buffer it runs through that context's page
directory, so the kernel maps every firmware buffer into each render VM at its own address:
read-only, except the TA/3D control block, which the EDM writes in that window (the loaded
parameter buffer). The renders of E023 run with this mapping.

A render client's own programs can therefore address the control block that all render
contexts share, and read the other firmware buffers. The render node treats its clients as
trusted until this is settled.

Open: whether the EDM can load a parameter buffer through the kernel's page directory, or
whether each VM can carry its own copy of the control block that the kernel keeps in step.
A run: map the block read-only (the debug option's switch) and see which render step faults;
then a render with a per-VM copy at the same address.
