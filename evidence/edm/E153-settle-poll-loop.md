+++
id = "E153"
claim = "The routine at 0x15bc-0x1664 waits for a running TA or 3D to go quiet before a parameter buffer is swapped or a render is kicked: when told to settle the 3D it reads CR_SETTLE_POLL0 and CR_SETTLE_POLL1 (0x0308, 0x030c) together after the four ISP signature registers, then waits 1000 loop counts and reads each set again, and loops until the xor of each set is the same on both reads; when told to settle the TA it does the same with CR_PPP_SIGNATURE and the two TE diagnostic registers instead and does not read 0x0308 or 0x030c; nothing in the firmware writes any of them"
unit = "edm"
method = "the ukernel of the cut firmware (00_ukernel.bin of firmware-images, 6637 instructions) disassembled with our usse-dis and read by hand: the routine at 0x15bc to 0x1664, its three callers (0x932, 0x11a0, 0x18fb), the paired release at 0x15ad and the list of registers the firmware writes (the dataflow of E013); our disassembly of the firmware, for interoperability; facts only, no code"
tiers = ["RE"]
date = "2026-11-01"
data = ["firmware-images", "firmware-edm-dataflow"]
terms = ["CR_SETTLE_POLL0", "CR_SETTLE_POLL1", "CR_PPP_SIGNATURE", "CR_TE_DIAG2", "CR_TE_DIAG5", "CR_ISP_SIGNATURE0", "CR_ISP_SIGNATURE1", "CR_ISP_SIGNATURE2", "CR_ISP_SIGNATURE3", "CR_DMS_CTRL"]
+++

**What was read.** Instruction numbers are indices in hex. The routine takes one argument, `r16`;
only its low two bits are used. The callers pass 1 from the TA kick before it swaps the TA's
parameter buffer (`0x932`) and from the code at `0x18f0` that does the same swap (`0x18fb`), and
2 from the 3D kick before it swaps the 3D's (`0x11a0`). An argument of 1 selects the 3D side
of the state words (`sa9`), anything else the TA side (`sa8`).

**Results.**

- *Entry.* It increments TA3DCtl dword 52 (a nesting count). For the 3D side it goes on only if
  bit 0 of `sa9` (3D running) is set; for the TA side only if bit 5 of `sa8` is clear and bit 0
  (TA running) is set; otherwise it returns at once. The release at `0x15ad` decrements the count
  and, when it reaches 0, clears bits 3:0 of `CR_DMS_CTRL` (`0x0a74`).
- *Gate.* It sets bits 2:0 of `CR_DMS_CTRL`. They are cleared again (`0x165d`) on the timeout
  path below, after which the routine starts over from the top.
- *3D side (argument 1).* It reads the four ISP signature registers `0x04d4`, `0x04d8`,
  `0x0518` and `0x051c` and xors the four values together, waits 1000 loop counts (a counted
  loop), reads the four again and xors them, and loops back while the two results differ. Then
  it does the same with `CR_SETTLE_POLL0` (`0x0308`) and `CR_SETTLE_POLL1` (`0x030c`): the xor
  of the two reads, a 1000-count wait, the xor of two more reads, loop while different.
- *TA side (any other argument).* It reads `CR_PPP_SIGNATURE` (`0x026c`), waits 1000 counts, reads
  it again and loops while the two reads differ; then it does the xor of `CR_TE_DIAG2`
  (`0x0284`) and `CR_TE_DIAG5` (`0x0290`) the same way. It does not read `0x0308` or `0x030c`.
- *After either side* it polls the USE service registers, up to 25 tries 500 counts apart: for
  the 3D side the AND of the four vertex service registers (`0x0b10`, `0x0b1c`, `0x0b8c`,
  `0x0b98`), for the TA side the AND of the four pixel service registers (`0x0b0c`, `0x0b18`,
  `0x0b88`, `0x0b94`), until bit 16 of the AND is set; then, up to 25 tries, until `0x0aa8`,
  `0x0b80` and `0x0b84` each read `0xaaaaaaaa` and `0x0aa4` reads that pattern with the two-bit
  field numbered by the global register `g22` set to 3. A try that fails sets a flag; if any
  try failed the whole sequence runs again from the gate, and a try limit reached ends in the
  timeout path (clear the gate bits, wait 1000 counts, start over).
- *Writes.* No instruction of the firmware writes `0x0308`, `0x030c`, `0x026c`, `0x0284`,
  `0x0290`, `0x04d4`, `0x04d8`, `0x0518` or `0x051c` (the register list of E013). The other
  registers the routine reads are service and data-master slot registers.

**Not shown.** What the two words at `0x0308` and `0x030c` measure inside the core, and what
the signature registers hold; that the routine waits for the TA or 3D to be idle is a reading
of where it is called and what it polls, not something a run shows. How long the wait takes is
not shown, nor whether any of the polls ever fails on the hardware.
