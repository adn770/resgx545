<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### Encoding bits no field maps

*Measured on the hardware (2026-11-02; `probes/usse/encoding-bits*.toml` and
`encoding-gaps.toml`, written by `tools/usse-asm/usse_bits.py`, recorded runs).* The 219 forms
leave 2,161 bits neither identifying nor in a field. Each probe runs one form's base instruction
as a raw word in a fill's pixel program (`dump.s`) and flips one such bit per case; a bit is read
if the readback differs from the base's, or the job fails **[HW]**. 761 bits of 73 forms ran:

- **Read: 4 bits.** `idiv`'s enc[47] changes every destination from r10 to r17, not only the
  quotient and the remainder (E295): it is the high bit of `idiv`'s repeat count, now a field
  (E367). enc[51] on `setfc` and on `imo` (the
  bit that selects the register forms of `smoa`, `smr`, `smlsi` and `smbo`) and enc[44] on
  `depthf` hang the job (E296).
- **Ignored: the other 757.** The moves, the bitwise group, integer multiply-add, `fsubflr`,
  `frcp`, the dot products and `fdsx` (f32 and f16 sources), `sop2wm`, the colour and integer
  dot products, `rlp` (with `p0` set first), `movc`, `movmsk`, the masked tests, `adif`,
  `adifsum`, `bilin`, `firv`, `firh`, `idiv`'s other 18, eleven dual-issue pairs, both `ldr`
  forms (E295); `nop`, `setfc`, `moest`, `setm`, `imo`, the immediate `smoa`, `smr`, `smbo`
  and `smlsi`, `pcoeff`, `depthf` and `atst8` (E296), each but the bits above.

The other 1,400 unmapped bits belong to forms with no base yet: the register forms of the MOE
group, `wop`, `lock`, `phas`, the emits, `str`, `ba`, `br`, `bexception`, `lapc`, the `pclink`
moves, the other dual-issue pairs and the forms whose words an earlier form decodes first.

**Words no form decodes.** About 4 percent of random words match no form's mask and value, all
of classes 2, 22, 26 and 31; the decoder rejects about a quarter, counting words that match a
mask but hold a reserved field value. Three words of each class that the decoder rejects ran in
place of an instruction: none hung or faulted; class 31's changed nothing, but three of class 2,
one of class 26 and one of class 22 (bilin's word with format 3, a reserved value rather than a
gap) left the program's later stores unwritten, and two of class 22 changed some pixels (E297,
Q080). The five that lost the stores are those of classes 2, 22 and 26 with enc[50] set, the
`.end` bit of mov, nop, fmad and bilin. Run again with a marker moved to the pixel after the
word, each of the nine words of classes 2, 22 and 26 with enc[50] set lost the stores and the
pixel's own write, the pixel keeping what the job before left, and each with it clear kept them,
or hung the job (three cases): with enc[50] set the program ends at the word. Of the other bits,
flipped one at a time on three of the words, none changes that; flips of bits 51 to 58 of a
class 2 and a class 26 word, and of bits 32, 33 and 51 of a class 22 word, change which pixels
the word writes **[HW]** (E368). The simulator stops on a word no form decodes, and on a word
with one of the three read bits that remain set.
