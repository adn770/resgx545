+++
id = "E172"
claim = "The EDM tests dword 1 of the TA command with mask 0x5 at four places and mask 0x9 at three: at two of the 0x5 tests a non-zero result keeps the list-insertion stores that link the render details into the context, and a zero 0x9 result runs the cache, bank and DPM-context calls of the TA kick that a non-zero result skips"
unit = "ta"
method = "the cut ukernel (00_ukernel.bin of the firmware-images dataset) disassembled with our usse-dis, every immediate 0x5 and 0x9 searched, each hit followed to the load of the TA command's dword 1 and to what its branch skips; our disassembly of the firmware, for interoperability; facts only, no code"
tiers = ["RE", "infer"]
date = "2026-11-01"
data = ["firmware-images"]
terms = ["GEOM_FLAGS.FIRST_KICK", "GEOM_FLAGS.NO_DPM_CONTEXT_LOAD", "GEOM_FLAGS.LAST_KICK"]
+++

**What was read.** The TA command's flags are its dword 1 (byte 0x4). Instruction indices are
those of the stored image (byte offset = index times 8). Searching the image for the immediates
5 and 9 and keeping those applied to a value loaded from dword 1 of a command gives seven tests:
four with mask 0x5 and three with 0x9. The bits are bit 0 and bit 2 (0x5) and bit 0 and bit 3
(0x9); bit 0 is the first-kick flag (`GEOM_FLAGS.FIRST_KICK`) and bit 3 the flag whose glossary
row says it is tested together with it in mask 0x9 (`GEOM_FLAGS.NO_DPM_CONTEXT_LOAD`).

**Results.**

*Mask 0x5.* Where each test sits (instruction index, then the routine it is in), where a zero
result goes, and what that skips:

- 0x673, routine 0x643 to 0x6f4: zero goes to 0x695, skipping stores into dwords 8 and 9 of the
  structure at TA3DCtl dword 27 and into dwords 74 and 75 of another, the shape of a head and tail
  pointer and a previous and next link.
- 0x755, routine 0x6f5 to 0x7b0: zero goes to 0x771, skipping a block that tests dword 13 of the
  structure at TA3DCtl dword 25 and walks the other.
- 0x872, routine 0x80c to 0x8e8: zero goes to 0x892, skipping a block of the same shape as the
  first: it loads dwords 8 and 9 of a structure, then stores.
- 0xa77, routine 0x8e9 to 0xacd (the TA kick): zero goes to 0xa85, skipping a block that clears
  bits 11:4 of dword 13 of the structure at TA3DCtl dword 25 and zeroes a run of words.

So at the first and third tests a non-zero flags word runs the list-insertion block (the reading
that it links the render details into a pending list of the context is an inference [infer]: the
block's stores have the shape of an append to a doubly linked list, and nothing here follows the
list to its reader). At the other two the bit selects work this record does not follow.

*Mask 0x9.* The three tests:

- 0x24b, routine 0x1c4 to 0x599 (the general event routine): a zero result skips a store of the
  value 0x50 into dword 13 of the structure at TA3DCtl dword 25; non-zero runs it.
- 0x821, routine 0x80c to 0x8e8: a zero result runs three calls (to 0x187c, 0x17ec and 0x184c)
  before going on; non-zero skips them.
- 0x9fa, routine 0x8e9 to 0xacd (the TA kick): a zero result runs three calls (to 0x17ec, 0x184c
  and 0x17be) with the kick's context and the next context; non-zero skips them.

The glossary row of `GEOM_FLAGS.NO_DPM_CONTEXT_LOAD` describes the skipped calls of the TA kick
as the cache invalidates, the BIF bank set and the reload of the RT data's stored DPM context. The
routines at 0x17ec, 0x184c and 0x17be were not read for this record, so that description of
their work is the row's and not shown here.

**Not shown.** What the blocks behind the mask-0x5 tests at 0x755 and 0xa77 do beyond the shape
given. What bit 2 of the flags word is for: no run here sets it alone. The seven tests are all
the tests of those two masks on dword 1 that the immediate search finds; a test through another
immediate (a register loaded with a mask by arithmetic) would not be found. The branch senses
are read from the instruction forms (a branch on a zero test), not from a run.
