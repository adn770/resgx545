+++
id = "E128"
claim = "In a fill's PDS secondary program, bit 9 (.1) of a special source makes a mov16 read 0 (of ir0, pc and tim alike; ir1 reads 0 in any case) and a 16-bit 0 is all it writes, but in mov32 it reads the same register as .0; ir0 is the tile position, tile_y << 10 | tile_x, of the fill's 16x16 tiles and pc.0 reads 3 ahead of the reading instruction's index with a few irregular places; a second run agrees"
unit = "pds"
method = "probes of probes/pds/moves.toml (pds-moves-index-mov16, -index-mov32, -index-mov64, -index-alu, -index-mul, -index-shl, -mov-flag-write, -mov-flag-flags, -mov-flag-side, -mov-flag-cond, -mov-flag-pipes, -mov-pc, -mov32-spare) and probes/pds/alu.toml (pds-alu-specials, -specials-paths, -specials-paths2) on the laptop, linux fork with the debug option on: 64x32 fill whose secondary PDS program runs the operation and passes sixteen temporaries to the shader with douta, one run of each case, fresh context each; both tables ran twice (the second is the follow-up run)"
tiers = ["HW"]
date = "2026-11-01"
data = ["pds-moves", "pds-alu", "pds-load-store", "pds-moves-followup", "pds-alu-followup"]
terms = []
+++

**What runs.** The special registers are the PDS program's inputs `ir0`, `ir1` and `ir2`, the
program counter `pc` and the timer `tim`. A source is named by an index, and the assembler's `.0`
and `.1` set the bit 9 of the instruction word: the low bit of the index in `mov32`, the bit above
the half select in `mov16`. A move with `.1` is called a flagged move below, a move with `.0` a
plain one; this has nothing to do with the arithmetic flags (`aluz`, `alun`, the carry). The index
tables hand-encode one instruction per index and run 16 at a time into the 16 temporaries, which
hold a marker (0x5eed0000 plus the number) so a move that writes nothing shows. The other probes set
up the flags, a carry or the predicates, read specials back to back or after nops, or read one
special 200 times in a loop whose result is the OR of the reads, one value per pixel. The fill is
64x32, 8 tiles of 16x16; `ir1` reads 0 in it throughout, so `ir1.0` and `ir1.1` cannot be told apart
here.

**Results.**

- **mov16 `.1` reads 0.** Over indices 256 to 511 only the plain forms among the first 16 (256, 257,
  260, 261, 264, 265, 268 and 269: ir0, ir1, pc and tim, low and high half) read anything: ir0.l
  0x403, pc.l 0x1b, tim.l and tim.h (0x0100b343 as one dword); the others of these, ir1 and the high
  halves of ir0 and pc, read 0. The `.1` indices 258, 259, 262, 263, 266, 267, 270 and 271 read 0,
  and so do indices 272 to 511. Flagged and plain moves side by side: a `.1` `mov16` of `tim.l` puts
  0 into one half of the marked temporary (0x5eed0000) and the other half keeps its marker; a `.1`
  `tim.h` puts 0 into the high half and leaves the low one (0x00000003); `.1` `ir0.l` and `.1`
  `pc.l` give 0x5eed0000, where the plain `ir0.l` and `pc.l` of the same probes give 0x5eed0402 and
  0x5eed0019. So the move writes a 16-bit 0 into its half: nothing is extended or swapped.
- **mov32 `.1` reads the same register as `.0`.** Over indices 128 to 255 only the first 16 read
  anything: 128 and 129 both give 0x402 (ir0), 130 and 131 both 0 (ir1), 132 and 133 give 0x17 and
  0x18 (pc, one instruction apart), 134 and 135 give 0x01005b03 and 0x01005b02 (tim, one count
  apart); 136 to 255 read 0. A `.1` `mov32` of `tim` in the condition and flag probes gives a
  running count, never 0 (for example 0x01036515), and a `.1` `mov32` of `ir0` gives the tile
  position, 0x402 or 0x403.
- **Other forms have no `.1`.** The ALU sources (index 64 `ir0`, 65 `ir1`, 66 `tim`), `mul` (128
  and 129 `ir0.l` and `.h`, 130 and 131 `ir1`, 132 and 133 `tim.l` and `.h`) and `shl` (128, 129,
  130) read ir0 as 0x402 or 0x403 and tim as a count (0x0100a886, 0x620c with 0x103, 0x0103c31c);
  every other index of those ranges, up to 127 and 255, reads 0, so they say nothing about bit 9.
  `mov64` read 0 from all 64 pairs tried. The `specials` probe agrees with the `mov32` result:
  `mov32 ir0.0` and `mov32 ir0.1` both give 0x403.
- **No condition, no side effect.** The 7 setups of mov-flag-cond (as found, `aluz`, a carry, a
  borrow, `alun`, `p0` to `p2` true, false) give the flagged `mov16` of `ir0.l`, `tim.l`, `tim.h`
  and `pc.l` the value 0 every time. In mov-flag-flags the flagged moves leave `aluz`, `alun`
  and the carry as they were: after a nonzero `sub` a flagged move (which writes 0) does not set
  `aluz`, and an `add -1 + 1` keeps its carry. In mov-flag-side the flagged and plain reads of
  `ir0` give the same 0x402 four times and the `tim` reads count down by one an instruction,
  flagged or not.
- **mov32 spare bits.** Setting bit 0, bit 8 or any of bits 17 to 23 of the `mov32` word, one per
  case (9 cases), changes no read of `ir0`, `pc` or `tim`, and bits 17 to 23 do not change the
  `mov16` either.
- **Per tile.** The probe that ORs 200 reads of a flagged `mov16` of `pc.l`, `ir0.l` or `tim.l`
  gives 0 at all 2048 pixels; the plain `pc.l` gives 0x14 at all 2048. A plain `mov32 ir0`
  gives 0, 1, 2 and 3 on the 256 pixels of each tile of the top row and 0x400, 0x401, 0x402 and
  0x403 on the bottom row: `tile_y << 10 | tile_x`.
- **pc.0.** Sixteen reads back to back from instruction 16 give 19, 20, 21, 22, 23, 24, 25, 26,
  27, 28, 28, 29, 31, 32, 33, 34: the reading instruction's index plus 3, except at instructions
  26 and 27, which read one less. After four `mul`s the reads start at instruction 20 and give 23
  to 28, 28, 29: again index plus 3 except at instructions 26 and 27. After 0 to 7 `nop`s the
  reads are 17, 21, 24, 28, 33, 38, 46, 53 where index plus 3 is 19, 21, 24, 28, 33, 39, 46, 54.
  In a loop the first and second pass both read 0x14.
- **tim after a write.** After a `movs` of 0x00abcdef to `tim` every later read in that job
  (ALU, `mul` halves 0xcdef and 0xab, the other forms) gives 0x00abcdef; with no write the same
  reads count down.
- **Second run.** All 68 probes of the two datasets (16 of moves, 52 of alu) ran in both runs
  and agree value for value except for 151 values that are timer counts or the position of the
  tile that stored last (0x402 or 0x403). In the follow-up run of the moves dataset every `tim`
  read (49 values in 9 probes, from the first probe on) is 0x00abcdef or its halves, the value
  that the `specials-paths` probe writes to `tim`; the counter did not count in that dataset. In
  the follow-up run of the alu dataset the timer counts until that write (23 count values, for
  example 0x01022e15 in `specials` and 0x010252de in the first case of `specials-paths`) and reads
  the written value after it (28 values in `specials-paths` and `alum-spare`, the same in the first
  run). In the first run the moves dataset counts (48 count values, none frozen).

**Not shown.** The data does not say what bit 9 selects in other cores, or whether it names an
alternative path or unit: the 200-read OR of a `.1` move is 0 at every pixel, but no case here times
reads of the two forms against each other. The effect of a `.1` `mov32` of `ir1` is not known
because `ir1` is 0. Vertex programs are not in these tables, so `ir0` as a vertex index and the kick
conditions of vertex programs are not examined. Why the timer reads 0x00abcdef throughout the moves
dataset of the follow-up run was not tested. A reading is that the write of the alu follow-up's
`specials-paths` (16:03 in its env.toml) was still in effect when the moves dataset ran (16:07)
because no faulting job came between them in that run, while in the first run the `pds-load-store`
dataset (E127), whose jobs fault, ran between the same two datasets (07:29, 07:33 and 07:34). One
run of each case in each run.
