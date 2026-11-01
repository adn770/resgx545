+++
id = "E152"
claim = "The EDM's only access to register 0x0e80 (CR_HWPERF_PULSE) is a write of 1 then a write of 0 in the routine at 0x1ea, which also writes CR_HWPERF_CTRL; it is reached from the boot path at 0x1c4 and from the SET_HWPERF_STATUS handler, never read, and no instruction that takes its register number from a register can name it"
unit = "edm"
method = "the ukernel of the cut firmware (00_ukernel.bin of firmware-images, 6637 instructions) disassembled with our usse-dis; every instruction that reads or writes a register by number was listed, with the register number of each, and the fourteen that take the number from a register were read one by one; our disassembly of the firmware, for interoperability; facts only, no code"
tiers = ["RE"]
date = "2026-11-01"
data = ["firmware-images"]
terms = ["CR_HWPERF_PULSE", "CR_HWPERF_CTRL", "host_ctl.perf_group"]
+++

**What was read.** Instruction numbers are indices in hex. A register number is the register's
address divided by 4, so `0x0e80` is register number `0x3a0`. A direct `str` or `ldr` names the
number in the instruction; the other form takes it from a register.

**Results.**

- Exactly two instructions name `0x0e80`: a write of 1 at `0x1ee` and a write of 0 at `0x1ef`,
  in this order, with nothing between them. No instruction reads it.
- They are inside the routine at `0x1ea`, which E150 describes. Just before them the routine
  writes `CR_HWPERF_CTRL` = `0x1ff`; just after them, when the status word `sa19` is not zero,
  it writes `CR_HWPERF_CTRL` again with `host_ctl.perf_group` shifted left 9 and masked with
  `0x1e00`. These are the only two instructions that write `CR_HWPERF_CTRL` (`0x0040`).
- The routine has two callers: the boot path that starts at `0x1c4` (at `0x1ce`, after a
  comparison of a register with itself that always selects the writes) and the SET_HWPERF_STATUS
  handler (at `0x15f`, which selects them by bit 0 of the command data, E150). The routine sits
  inside the range `0x1c4` to `0x599` that the dataflow of E013 calls the general routine.
- Not every register access names its register in the instruction. The ones that take the number
  from a register are at `0x2c8`, `0x17ed`, `0x17fc`, `0x1846`, `0x184a` and, in the HWPerf routine,
  `0x19a9`, `0x19ba`, `0x19bf`, `0x19c4`, `0x19c9`, `0x19ce`, `0x19d3`, `0x19d8` and `0x19dd` (14 in
  all, 13 reads and one write: the 14 that the dataflow of E013 leaves unresolved). The HWPerf
  routine's numbers are the constants `0x11` to `0x19` and `0x3a1` to `0x3a4`, `0x3ad` to `0x3b0`
  (E149); `0x3a0` is not among them. The callers of `0x2c8` load nine constants and none is `0x3a0`;
  the code at `0x17ec` to `0x184b` uses `0x321` and `0x30d` plus a count.

**Not shown.** What the pulse does, and which of the writes it follows has an effect: the pulse
is written twice in a row and nothing is read back. Whether the hardware has any other way
to reach the register is not shown, only that the firmware does not.
