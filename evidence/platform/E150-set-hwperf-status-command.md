+++
id = "E150"
claim = "The kernel CCB command 9 (SET_HWPERF_STATUS) handler at 0x157 writes 0xffffffff to dword 2 of the HWPerf buffer, stores command data dword 0 with bit 0 cleared as the HWPerf status word, and, only if bit 0 of the data was set, writes CR_HWPERF_CTRL = 0x1ff and pulses CR_HWPERF_PULSE; when the status is not zero it then writes HostCtl's group, shifted left 9 and masked with 0x1e00, to CR_HWPERF_CTRL"
unit = "platform"
method = "the ukernel of the cut firmware (00_ukernel.bin of firmware-images) disassembled with our usse-dis and read by hand: the handler at 0x157, the routine it calls at 0x1ea, and every test of the status word; our disassembly of the firmware, for interoperability; facts only, no code"
tiers = ["RE"]
date = "2026-11-01"
data = ["firmware-images"]
terms = ["CR_HWPERF_CTRL", "CR_HWPERF_CTRL.GROUP", "CR_HWPERF_PULSE", "CMD.SET_HWPERF_STATUS", "host_ctl.perf_group", "CR_DPM_OUTOFMEM"]
+++

**What was read.** Instruction numbers are indices in hex. The handler is the one E012 lists for
the command (kick address `0x157`); a kernel CCB handler gets the command's words in `r4` to
`r11` (E013), so command data dword 0 is `r6`.

**Results.** In order:

- It writes `0xffffffff` to dword 2 of the HWPerf buffer (TA3DCtl dword 43), the dword the
  HWPerf routine uses as its record counter (E149).
- It tests bit 0 of data dword 0 and keeps the result in a predicate; the branch that follows the
  test goes to the next instruction either way. It stores data dword 0 with bit 0 cleared in
  `sa19`, the HWPerf status word, and calls the routine at `0x1ea`.
- The routine at `0x1ea` does the first part only if the predicate from bit 0 is set: it writes
  `CR_HWPERF_CTRL` (`0x0040`) = `0x1ff` and then writes `CR_HWPERF_PULSE` (`0x0e80`) = 1 and = 0.
  It then, in every case, reads `sa19`; if that is not zero it reads HostCtl dword 15
  (`host_ctl.perf_group`, written by the host, E005), shifts it left by 9, masks the result with
  `0x1e00` and writes it to `CR_HWPERF_CTRL`.
- The handler then goes to the tail the kernel CCB handlers share (`0x161`): if bit 6 of `sa8` is
  set it clears the bit and writes register `0x069c` (`CR_DPM_OUTOFMEM`) = 1, it posts the
  3D and TA scheduler requests (E154) when their queues hold work, and it ends the task.

The same routine at `0x1ea` is also called at boot, from the main path that begins at `0x1c4`
(with the predicate set by comparing a register with itself, so it always writes `0x1ff` and the
pulse). The status word's other readers test bit 1 (mask 2), bit 2 (mask 4), bit 3 (mask 8) or
bits 1 to 3 (mask 14) before each HWPerf record (E149), so a status that is non-zero but has those
bits clear selects the group without any record being written, for example the value 0x10.

The test of bit 0 does not decide whether the status is stored: it is stored in both cases, but
the register writes of `0x1ea` that reset `CR_HWPERF_CTRL` and pulse `0x0e80` happen only with bit
0 set.

**Not shown.** What the group field of `CR_HWPERF_CTRL` selects, what the pulse does, and what
the reset value `0x1ff` enables. The published hardware data for this unit (platform-hwperf) is a
single read of the HWPerf registers from a shader (E149); no run sends the command or sets a
group, so there is no hardware half here: that a non-zero status puts the group in
`CR_HWPERF_CTRL` bits 12:9 and zeroes the counters at `0x0044`-`0x0064` is not shown. This
record shows only the writes the firmware makes.
