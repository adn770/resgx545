+++
id = "E015"
claim = "The EDM's TRANSFER handler only counts and queues the context; a later routine picks a ready context from the queue heads, skips suspended ones (flag bit 4), takes the dummy path for context flag bit 1 or command flag 0x20, applies updates through the context's directory, loads the command's 17 register words into fixed registers (the three coefficient groups only when their load words are set) and starts the render by writing 1 to 0x0428; completion reads the size word, writes the status values and raises SW_EVENT"
unit = "transfer"
method = "the EDM dataflow (firmware-edm-dataflow): every row of HWTRANSFERCONTEXT, TRANSFERCMD, CCB_CTL and the registers the transfer routines touch; checked against the laptop runs E018-E021; our disassembly of the firmware, for interoperability; facts only, no code"
tiers = ["RE", "HW"]
date = "2026-10-31"
data = ["firmware-edm-dataflow", "transfer-dummy", "transfer-fill", "transfer-isolation"]
terms = ["hw_transfer_context.submitted_commands", "hw_transfer_context.priority", "hw_transfer_context.fw_com_ctx_flags", "transfer_cmd.flags", "transfer_cmd.pds_exec_base", "transfer_cmd.bif_3d_req_base", "CR_BIF_BANK0", "CR_EVENT_STATUS"]
+++

Instruction indices below are the microkernel's (byte offset / 8).

**The handler (`0x103`-`0x11c`).** It reads the context's count (`+0x14`) and writes it back
plus one. Only if it was 0 does it link the context into a queue: it reads the priority
(`+0x04`), uses it to index the queue's head and tail (secondary attributes 13 + priority and
14 + priority) and writes the context's links (`+0xac`, `+0xb0`). It loads no register and
starts nothing.

**The pick and start (`0x12dc`-`0x1460`).** For a queued context: bit 4 of the context's flags
(`+0x00`) set skips it (`0x12e8`). The command is read from the CCB the context names
(`+0x0c`, typed as the client CCB). The command's flags (`+0xa8`) bits 0 and 1 steer the sync
handling, then:

- context flag bit 1 set: the EDM clears it (`+0x00 &= ~0x2`, `0x135f`) and goes to the dummy
  path at `0x14fa`;
- command flag bit 5 (`0x20`) set: the dummy path, with no register of the 3D pipe written;
- an update count (`+0x19c`) other than 0 runs an update loop (reading `+0x1a0`) with calls of
  `0x1864` before and after it; that routine read-modify-writes `BIF_BANK0`'s low nibble (the
  EDM's directory index). The completion routine has a second such loop (`0x1514`), which the
  dummy path reaches;
- otherwise the 17 words `+0x000`-`+0x040` go to registers `0x04c4`, `0x04bc`, `0x04b8`,
  `0x0404`, `0x0408`, `0x0414`, `0x0cac` (`BIF_3D_REQ_BASE`), `0x042c`, `0x04c8`, `0x0a5c`,
  `0x0a60`, `0x0a64`, `0x040c`, `0x0410`, `0x0400`, `0x0ab8` (`PDS_EXEC_BASE`) and `0x0148`, in
  that order of words; `+0x044`-`+0x06c` go to `0x0820`-`0x0848` only if `+0x188` is not 0,
  `+0x070`-`+0x078` to `0x0860`-`0x0868` only if `+0x18c` is not 0, `+0x07c`-`+0x0a0` to
  `0x0a9c`, `0x0a84`-`0x0a98` and `0x0b24`-`0x0b2c` only if `+0x190` is not 0; `+0x194` is
  ORed into a register value; `+0x198` is read with no use; the routine ends by writing 1 to
  `0x0428` (`0x145f`).

The context's words `+0xa0`, `+0xa4` are copied into the command at `+0x13c`, `+0x140`, and
`+0xa8` into TA3DCtl `+0xcc`.

**The directory list.** No instruction writes a `BIF_DIR_LIST_BASE` register at a constant
address. The routine at `0x17ec`-`0x184b` holds four of the 14 writes whose register address
is computed, and the next one (`0x184c`-`0x1857`) writes `BIF_BANK0`. On the laptop every
transfer leaves the context's directory in `BIF_DIR_LIST_BASE1` and `BIF_BANK0` `0x100f`
(E018, E021). **[infer]** Those computed writes put the directory in a list; the analysis
does not resolve which.

**Completion (`0x1461`-`0x1591`).** It reads the command's size (`+0xa4`) and flags and the
shared block's status entries, and writes `0x4000` (SW_EVENT) to `EVENT_STATUS` (`0x14f8`).
The read-offset store goes through a pointer the analysis does not resolve; on the laptop the
read offset advances by exactly the size (E018). The dummy path enters at `0x14fa`, past the
`EVENT_STATUS` write; how it raises its event is not resolved, though E018 shows it does.

**[infer]** Only one transfer renders at a time: the pick routine starts at most one render
and the next pick follows a completion. The runs show one SW_EVENT per transfer and never
two transfers in flight, but no run tries.
