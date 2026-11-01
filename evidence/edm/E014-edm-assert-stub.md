+++
id = "E014"
claim = "The EDM writes HostCtl dword 14 (assert_fail) only with constants: 0xad002600 at instruction 1, on the instruction-0 path that no normal boot takes, and 0xad001a07 at instruction 0x55c of the event routine, taken when the kernel CCB's write and read offsets differ; it never reads the word"
unit = "edm"
method = "the EDM dataflow (firmware-edm-dataflow): every row of HOST_CTL+0x038; HostCtl's host-written words from E005 for comparison; our disassembly of the firmware, for interoperability; facts only, no code"
tiers = ["RE", "HW"]
date = "2026-10-31"
data = ["firmware-edm-dataflow", "platform-boot"]
terms = ["host_ctl.assert_fail"]
+++

**The writes.** The dataflow finds two writes of `HOST_CTL+0x038` and no read:

- instruction 1, in the routine at instructions 0-5, writes `0xad002600`. Instruction 0 is
  where the code base starts; the boot enters through the PDS programs at the handlers'
  addresses (E002, E003), not there, so this path runs only if execution falls to the code
  base;
- instruction `0x55c`, in the event routine at `0x1c4`-`0x599`, writes `0xad001a07` on the
  branch taken when `CCB_CTL+0x000` (the host's write offset) differs from `CCB_CTL+0x004`
  (the EDM's read offset) at that point (test at `0x559`).

**On the laptop.** After every boot and every phase-4 run HostCtl dword 14 reads 0 (E008 and
the register dumps of E017-E021), so neither path ran there.

**[infer]** Both constants mark a firmware assertion (`0xad00....` with a location code):
dword 14 is the host's view of a firmware failure, which no run has produced.
