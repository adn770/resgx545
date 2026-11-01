+++
id = "E167"
claim = "The EDM tests bit 5 of a render context's flags word (dword 0) only in the render-context cleanup: with the bit set the cleanup clears the TA and 3D loaded-PB slots (TA3DCtl dwords 46 and 47) that hold the context's own PB; with it clear it leaves them to the PB cleanup, which clears them whenever they hold that PB"
unit = "edm"
method = "the ukernel of the cut firmware (00_ukernel.bin of firmware-images, 6637 instructions) disassembled with our usse-dis; a scan for every instruction that tests the value 32 or the bit-5 mask against a register and the origin of that register at each of the fifteen sites, with the render-context cleanup (0x39d-0x3bf) and the PB cleanup (0x475-0x485) read in full; our disassembly of the firmware, for interoperability; facts only, no code"
tiers = ["RE"]
date = "2026-11-01"
data = ["firmware-images"]
terms = ["CONTEXT_FLAGS.OWN_PB", "CLEANUP.RENDER_CONTEXT", "CLEANUP.PB", "ta3d_ctl.hw_pb_desc_ta", "ta3d_ctl.hw_pb_desc_3d", "hw_render_context.hw_pb_desc_dev_vaddr", "hw_render_context.submitted_commands"]
+++

**What was read.** Instruction numbers are indices in hex. TA3DCtl dword 46 is the PB loaded for the
TA and dword 47 the PB loaded for the 3D (E159, E163). The cleanup is the kernel CCB command
CLEANUP (E012), which reaches the render-context routine at `0x39d` with `r0` the context.

**Results.**

- *The routine at `0x39d`.* It reads context dwords 8, 10 and 5 (the pending list head, the ready
  list head and `submitted_commands`); if any is not zero it returns at `0x3c0` and the cleanup
  waits (the same routine runs again). Otherwise it reads the context's PB (dword 6), TA3DCtl dwords
  46 and 47, and the context's flags (dword 0). Then:
  1. if bit 5 of the flags is clear, nothing happens to the slots; if it is set and dword 46 equals
     the context's PB, dword 46 is cleared;
  2. the same two steps for dword 47.
  It then clears bit 18 of `sa8`, sets bit 0 of HostCtl dword 2 and clears bit 3 of `sa10`.
- *The PB cleanup (`0x475`, `r0` the PB descriptor).* It clears dword 46 if it equals `r0` and
  dword 47 if it equals `r0`, with no test of any flag, and sets bit 0 of HostCtl dword 2 and
  clears bit 6 of `sa10`.
- *Every test of bit 5.* Fifteen instructions test it; two are the ones above (`0x3aa`, `0x3af`).
  The other thirteen test: `sa8` (`0x358`, `0x496`, `0xb69`, `0x15c7`), `sa9` (`0xec7`), dword 13
  of an RT data, its state word (`0x41a`, `0x52e`, `0x1162`, `0x1791`, `0x17d7`), a status register
  (`0x1752`, `0x17d4`, bit 5 of `CR_EVENT_STATUS`, the DPM state load) and a word of the transfer
  command (`0x139c`, command dword 42). None tests dword 0 of a context.

**What it shows.** With bit 5 set, destroying a render context also unloads its PB from the TA and
3D slots, when they hold it; with it clear the slots keep the PB until the PB's own cleanup. That
fits a context that owns its PB, which is what the glossary term says, and it is the opposite of the
reading in which the bit marks a PB shared with other contexts **[RE]**.

**Not shown.** The scan looked for tests by an AND with 32 and by a shift left of 26 (the latter
found none); a flags word loaded by a fetch or through a computed address would not have been tied
to its test by it. What the bit does on the hardware (a context destroyed with and without it, the
two slots read before and after) is not in this record, and nothing here runs the firmware.
