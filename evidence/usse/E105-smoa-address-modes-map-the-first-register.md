+++
id = "E105"
claim = "smoa's address modes map an operand's first register once, and the iterations step on from it: with i the register plus the operand's smoa offset and M its smr range less one, none gives i, clamp min(i, M), mirror 2M - i and repeat i - (M + 1) when i is past M; this holds for the destination and for source 1 in all 70 cases (14 starting below r0), smr's field 0 goes with the destination and field 2 with source 1, and a first register below r0 drops writes and reads values from outside r0-r46"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/moe.toml, the twelve usse-moe-smoa-{all,hi}-{none,repeat,clamp,mirror,pred,src} probes (client fill on all_dump.s and all_dump_hi.s: r0-r46 preset to 0xE0E1E200 + k, then smr and smoa, a mov.repeat8 or a plain mov, the MOE state reset, every register r0-r46 read back), two runs (the second is the follow-up run)"
tiers = ["HW"]
date = "2026-11-01"
data = ["usse-moe", "usse-moe-followup"]
terms = []
+++

**What runs.** Each of the 70 cases sets `smr` (one range per field) and `smoa` (an offset and a
mode per operand), runs one move, and resets both. The fill dumps `r0` to `r31` in one table and
`r15` to `r46` in the other, so every register is read. A value read back names its source register.
The cases are: 46 in the four modes (none and repeat 9 each, clamp and mirror 14 each), mostly
`mov.repeat8 r20, r1` (ranges 2, 4 and 8 for none and repeat, 1 to 6, 8 and 16 for clamp and mirror,
offsets 0 and 2 on the destination, offsets 0 and 2 on source 1 at range 4, and a plain `mov` with
offset 6); 12 predictions on `mov.repeat8 r20, r30` (ranges 12, 24, 11, 14, 5, 10 and 16 with
offsets 0, 3 and 5); and 12 on source 1 above its range (`mov.repeat8 r40, r20`, four modes) and on
`smr` fields one at a time.

**Results.** One model fits all 70 cases and both runs, register for register over r0-r46: the first
register of the destination (and of source 1) is mapped once by the mode (none gives i, clamp min(i,
M), mirror 2M - i, repeat i - (M + 1) when i is past M; i is the register plus the smoa offset, M
the smr range less one), and iteration k then uses that register plus k. Examples: `smr` 16 clamp
writes from `r15` and mirror from `r10`; `smr` 8 mirror starts at -6, so only the last two
iterations land (in `r0` and `r1`); `smr` 8 repeat starts at `r12`, not `r4`; `smr` 24 in every mode
leaves `r20` as it is. In 14 cases the destination starts below `r0` (mirror with ranges 1 to 8, and
`smr` field 1, 2 or 3 at 4 with the destination clamped, where its own field 0 is 0 and M is -1):
the writes below `r0` vanish. With source 1 at `r20` and range 4, clamp reads `r3` to `r9` and
repeat `r16` to `r22`; mirror starts at -14 and reads values that are in no register of `r0`-`r46`:
`0x04040404` five times and `0x001c0029` and `0x001d0028` once each, the same in both runs. A source
clamped with `smr` field 0, 1 or 3 at 4 and its own field 2 at 0 starts at -1 and reads `0x04040404`
for its first iteration. Field 0 at 4 clamps the destination to `r3` and field 2 at 4 clamps source
1; fields 1 and 3 moved neither.

**What it shows.** The address modes bound where an operand's run of registers starts; they do not
wrap on each iteration. `smr` holds one range per operand in `smoa`'s order for at least the
destination (field 0) and source 1 (field 2); fields 1 and 3 are not shown to belong to the sources
0 and 2, which the table does not use. A register number below `r0` is not an error: writes there
are dropped and reads return values from some other storage.

**Not shown.** Source 0 and source 2 as moved operands; a mix with the base-offset instruction.
