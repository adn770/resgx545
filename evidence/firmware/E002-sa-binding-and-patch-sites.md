+++
id = "E002"
claim = "The EDM reads sa0-sa2 as base pointers into TA3DCtl, HostCtl and the kernel CCB control, filled by PDS #11; 9 patched immediates"
unit = "firmware"
method = "the layout captures (base and every buffer moved) against the reference loader's images of the cut firmware; the cut ukernel disassembled with usse-dis (which arrives with the disassembly unit)"
tiers = ["CAP", "RE"]
date = "2026-10-30"
data = ["firmware-layout", "firmware-images"]
terms = ["ta3d_ctl", "host_ctl", "CR_EVENT_OTHER_PDS_EXEC", "CR_EVENT_OTHER_PDS_DATA"]
+++

**Who sets the base pointers.** Across the 6637 instructions of the cut ukernel, `sa0`, `sa1` and
`sa2` are never a destination; they are read as bases (194, 40 and 8 times). Their values come
from TA3DCtl, which PDS program #11 copies into the secondary attributes. The captured TA3DCtl
holds: `sa0` a pointer to TA3DCtl itself (so `[sa0, +#k]` reads its dword k), `sa1` to HostCtl,
`sa2` to the kernel CCB control (`+#0` the write offset, `+#1` the read offset), `sa22` to the
kernel CCB, `sa23` the page directory's physical address (a value, not a pointer), and
`sa43`-`sa45` pointers to the HWPerf circular buffer and the TA and 3D signature buffers. The
remaining dwords of the 0xec-byte (59-dword) block are 0 at boot.

**The patch sites.** In the template, 9 ukernel instructions hold the placeholder immediate
`0xDEADBEEF`. The loader patches the 32-bit immediate of each in three bit-fields; 52 bytes
differ between the template and the loaded image. It fills them with the `emitpds` control
words and `address >> 4` of PDS #11, #12 and #14, the TA3DCtl device address (at byte
`0xd78`), and PDS #13's address and data size, written to `CR_EVENT_OTHER_PDS_EXEC` and
`_DATA` (bytes `0xe40` and `0xe50`). With a
distinct device address for every buffer (the moved layout), each value resolves to one buffer,
and the reference loader reproduces both captures byte for byte from the cut firmware
(`tools/fwcutter/test_fwload.py`). The moved capture also shows that the initialiser leaves the
kick table alone when the ukernel moves within its heap, while the PDS code words move with it.

It does not show what the EDM does with each pointer beyond the reads counted, nor run PDS #11
itself.
