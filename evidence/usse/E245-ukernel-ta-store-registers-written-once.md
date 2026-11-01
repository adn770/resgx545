+++
id = "E245"
claim = "The microkernel writes the TA command's context store and resume registers (0x0a04, 0x0aa0, 0x02b0, 0x02b4, 0x02d0, 0x02d4, 0x0324, 0x0364, 0x0368, 0x0370, 0x0374) at one site each, in one run of straight-line code that fetches the values from memory and stores them without computing on them, reads none of them at a statically named site, and its 6637 instructions use none of the instructions moest, setfc, bexception, setm, smoa and smbo and no mon or synce modifier"
unit = "usse"
method = "the cut microkernel image (firmware-images, 00_ukernel.bin) disassembled with usse-dis: every load and store with an immediate register index, as regtouch.py lists them, restricted to these registers, the code around the sites read, and the mnemonics and modifiers of all instructions counted; our disassembly of the firmware, for interoperability; facts only, no code"
tiers = ["RE"]
date = "2026-11-01"
data = ["firmware-images"]
terms = [
    "cmd_ta.use_reg_0a04", "cmd_ta.use_reg_0aa0", "cmd_ta.ta_reg_02b0", "cmd_ta.ta_reg_02b4",
    "cmd_ta.ta_reg_02d0", "cmd_ta.ta_reg_02d4", "cmd_ta.reg_0324", "cmd_ta.reg_0364",
    "cmd_ta.reg_0368", "cmd_ta.reg_0370", "cmd_ta.reg_0374",
]
+++

**What was read.** The microkernel image is 6637 instructions. The scan lists each load and store
whose immediate is a dword register index (E010) and keeps the accesses to the eleven registers
above. The same scan finds 421 write sites and 183 read sites over the image, as E010 does.

**Results.**

- Each of the eleven registers is written at exactly one site and read at none. The eleven
  stores are 11 of the 421 write sites. The 14 loads and stores through a register-supplied
  address are not resolvable statically; the scan does not say whether any of them reaches
  these registers.
- The eleven stores sit in one stretch of about fifty instructions, in the part of the
  microkernel that starts a TA job, among stores to other registers. The stretch fetches blocks
  of consecutive dwords from memory, at an address made from an immediate and a register, waits
  for each fetch, and stores the fetched dwords to the registers one by one, in an order that is
  not the registers' own. Nothing computes on a dword between its fetch and its store. This is
  the shape of a copy of a command block into registers; the command words involved are those
  of E054.
- Decoded, the image uses 31 mnemonics (and, ba, br, cfi, ci, emitpds, fmad, iaddu32, idf,
  ima16, ima32, imae, isub16, lapc, ldad, ldaw, ldr, lock, mov, nop, or, phas, rol, shl, shr,
  smlsi, stad, str, usub16, wdf, xor). None of them is moest, setfc, bexception, setm, smoa or
  smbo, no instruction carries a mon or a synce modifier, and the listing holds no word printed
  as undecoded.

**What it shows.** In the microkernel the registers of the TA's context store and resume state
get a value only from the command, once per TA job; no other statically named site writes or
reads them. The microkernel does not itself store or restore a TA context through these
registers. The six instructions never occur in the microkernel, so no firmware path of ours
could drive them.

**Not shown.** What the hardware does with the registers once written. Accesses through
computed register indices. What the compiled programs of the closed stack use. That the hardware
has no context switch to request: this record covers the microkernel's own code only, and the
command words' effect on images is in E054 and E056.
