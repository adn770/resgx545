+++
id = "E155"
claim = "In every handler of the EDM event tasks that acknowledges an event, the pa1 bit it tests and the CR_EVENT_HOST_CLEAR value it writes are related by acknowledged status bit = 22 minus the pa1 bit, for the seven pa1 bits 22, 21, 20, 10, 9, 7 and 4; pa1 bit 8 (the kernel CCB) writes no acknowledgement, and the timer tick arrives in pa0 bit 1; the reading that pa1 is CR_EVENT_STATUS bits 22-0 in reverse order fits all of these"
unit = "edm"
method = "the ukernel of the cut firmware (00_ukernel.bin of firmware-images, 6637 instructions) disassembled with our usse-dis and read by hand: every test of pa0 and pa1 (17 instructions), the EVENT_HOST_CLEAR (0x0134) and EVENT_TIMER (0x0acc) writes that follow them, and PDS #13's dispatch masks (E146); our disassembly of the firmware, for interoperability; facts only, no code"
tiers = ["RE", "infer"]
date = "2026-11-01"
data = ["firmware-images"]
terms = ["CR_EVENT_STATUS", "CR_EVENT_HOST_CLEAR", "CR_EVENT_TIMER", "CR_EVENT_STATUS.PIXELBE_END_RENDER", "CR_EVENT_STATUS.BREAKPOINT", "CR_EVENT_STATUS.TA_FINISHED", "CR_EVENT_STATUS.TA_TERMINATE", "CR_EVENT_STATUS.DPM_OUT_OF_MEMORY_GBL", "CR_EVENT_STATUS.DPM_OUT_OF_MEMORY_MT", "CR_EVENT_STATUS.DPM_3D_MEM_FREE", "CR_EVENT_STATUS.DPM_REACHED_MEM_THRESH", "CR_EVENT_STATUS.SW_EVENT", "CR_EVENT_STATUS.TIMER", "CR_EVENT_KICK"]
+++

**What was read.** Instruction numbers are indices in hex. Every event runs PDS #13 (E146), which
hands two input words to its task as `pa0` and `pa1` (and a third, `pa2`, that no instruction of
the firmware reads). The general event task starts at `0x6`; the three fast-path tasks at
`0xe0a`, `0x59a` and `0xace` repeat its handlers for exact groups of bits. The firmware reads
`pa1` in 16 instructions and `pa0` in 14 (the request tasks, E154, and the timer).

**Results.** Each test of a `pa1` bit is followed by an acknowledgement, a write of a value to
`CR_EVENT_HOST_CLEAR`, and the value is a single status bit, or two:

| `pa1` bit | acknowledgement written | status bit | event it fits | tests at |
|---|---|---|---|---|
| 22 (`0x400000`) | `0x1` | 0 | `DPM_3D_MEM_FREE` | `0x1d`, `0xe1a` |
| 21 and 20 (`0x300000`) | `0x6` | 1 and 2 | `DPM_OUT_OF_MEMORY_MT`, `_GBL` | `0x64`, `0xad1` |
| 10 (`0x400`) | `0x1000` | 12 | `TA_TERMINATE` | `0x68`, `0xadd` |
| 9 (`0x200`) | `0x2000` | 13 | `TA_FINISHED` | `0x6f`, `0x5aa` |
| 7 (`0x80`) | `0x8000` | 15 | `BREAKPOINT` | `0x57`, `0xe5a` |
| 4 (`0x10`) | `0x40000` | 18 | `PIXELBE_END_RENDER` | `0x21`, `0xe21` |

In all seven rows, status bit = 22 minus the `pa1` bit (22 gives 0, 21 and 20 give 1 and 2, 10
gives 12, 9 gives 13, 7 gives 15, 4 gives 18). The acknowledgements of the request tasks (E154)
are the same values. The out-of-memory handler records in `sa8` bit 19 whether `pa1` bit 20 (the
global one) was set, which also fits.

- *Other `pa1` bits.* Bit 19 is tested with the out-of-memory bits (mask `0x380400` at `0x60`)
  and posts nothing; the rule would make it status bit 3, `DPM_REACHED_MEM_THRESH`. Bit 8
  (`0x100`, test at `0x98`) starts the kernel CCB reader: it takes the read offset from `sa2`,
  fetches the 32-byte command at that offset, advances the offset (modulo 256) and branches to
  the address in the command's first dword (E012). It writes no acknowledgement. The rule would
  make it status bit 14, the bit the firmware itself raises as `SW_EVENT` with a write of
  `0x4000` to `CR_EVENT_STATUS` (E156), so the host's kick may be the same bit seen from the
  other side **[infer]**.
- *Dispatch.* PDS #13's masks (E146) are `0x400090` (bits 22, 7, 4), `0x200` (bit 9) and
  `0x300400` (bits 21, 20, 10), and the fast-path tasks test exactly those bits; they test `pa1`
  with the same layout as the general task. PDS #13 passes its `ir1` input on to the task as
  `pa1` with a plain move (E146), so `ir1` has this layout too.
- *Timer.* The tick is `pa0` bit 1, tested at `0x8c`: it adds 1 to HostCtl dword 12 (E005,
  `host_ctl.edm_ticks`) and continues at `0x486` (a HWPerf record if enabled, then the periodic
  checks of the TA and 3D states). The firmware programs `CR_EVENT_TIMER` (`0x0acc`) from
  HostCtl dword 6 with bit 24 set at `0x1fc`, called from the boot path (`0x1d6`) and the POWER
  handler (`0xd6`), and writes it with 0 at `0x50a`; no instruction runs per tick writes it.

**What this does and does not show.** The pairing of each `pa1` test with its acknowledgement is
what the code does **[RE]**. That `pa1` is the status register reversed, rather than a
word that merely has a fixed relation to the status bits the handlers clear, is a reading
**[infer]**: no run feeds the firmware an event. The reading differs from the one in E146, which
took `ir1` to carry `CR_EVENT_STATUS` bits at their own positions; at those positions bit 22 would
be `DPM_INIT_END` and bit 4 `DPM_STATE_STORE`, yet the handlers for these bits acknowledge status
bits 0 and 18. Which hardware events set the bits is not shown. That the timer reloads itself on
expiry is not shown either: the code programs the timer only at those two sites.

**Correction 2026-11-10:** (an offline reading of our disassembly, made before the round 3 runs; not a
measurement; facts only). The ukernel has 16 instructions that read `pa1`; the table above names 14
of them. The two it does not: 0x17, `and r0, pa1, r0` with r0 = 0x00400090 (set at 0x16), the mask
of bits 22, 7 and 4 together, the first gate of the general task (when none is set, 0x1b skips their
handlers and goes to the test at 0x60); and 0x73, `and r0, pa1, #0x200` (bit 9), a second test of
the bit tested at 0x6f, whose skip at 0x75 to 0x88 cannot be taken after the first test passed with
`pa1` unchanged [infer]. The union of the masks tested anywhere in the ukernel is 0x00780790 (bits
22, 21, 20, 19, 10, 9, 8, 7 and 4): every other `pa1` bit has no code, including the tick's bit 25
and the SW_EVENT mirror at bit 14 (0x4000). Bit 19 is tested (at 0x60, with the out-of-memory bits)
and posts and acknowledges nothing; with bit 8 (the CCB reader, 0x98) it is one of the two groups of
handlers that do not acknowledge.
