# SGX545 PDS instruction set reference

The **PDS** (programmable data sequencer) of the SGX545 runs small programs that prepare and
start USSE tasks: they DMA vertex data and state into the USSE attribute registers, issue
iterator and texture work, and start a task on a code address with `doutu`. Every USSE task
starts this way, the microkernel's own included (`doc/specs/hw_spec.md`). The
USSE instruction set has its own reference, `doc/specs/usse_isa.md`.

This reference covers the PDS instruction set as our disassembler `tools/usse-dis/pds-dis`
decodes it and our assembler `tools/usse-asm/pds-asm` writes it. The decoder was derived
by black-box probing of the layouts and decodes every word of the firmware and the captures
(`tools/usse-dis/README.md`); the assembler describes the same layouts as forms in
`tools/usse-asm/pds_forms.c` and checks each word it builds against the decoder. The
generated parts of this document read those forms.

No simulator models the PDS and no hardware probe has been run on it: **[HW]** here means that
one of our own programs depends on the behaviour and works, as the transfer and fill paths do
(`doc/specs/transfer.md`).

> **Generated file.** This document is assembled by `doc/isa/build.py` from the snippet library
> in `doc/isa/` (see `doc/isa/README.md`). Edit the snippets, not this file, and rebuild; the
> test `doc/isa/test_build.py` fails while the committed copy is stale. Bit diagrams, field
> lists, form lists and encoding examples are generated from the form tables of our clean-room
> disassemblers and assemblers (`tools/usse-dis`, `tools/usse-asm`), so they cannot drift from
> the tools; the prose around them is handwritten.

## 1. Conventions

### 1.1 Where each fact comes from

This is a reconstruction, not a vendor document. Every statement about what an instruction
*does* carries a tag, as in `doc/specs/hw_spec.md`:

- **[HW]** measured on the laptop: our own programs or probes ran and behaved as stated.
- **[CAP]** captured from the closed driver running under the extraction harness (its
  programs, the words it writes), so exact for that build.
- **[RE]** read from the closed microkernel's code with our disassembler, or established by
  black-box probing of the layouts (bit flips and value sweeps). Encodings and assembler
  spellings are **[RE]** in this sense: our decoder decodes every word of the firmware and the
  captures, and nothing more is implied about behaviour.
- **[DDK]** read in the GPL DDK sources (register names, structure layouts).
- **[infer]** an inference from names, context or how the firmware uses an instruction;
  verify before relying on it.
- **[open]** not known. Said plainly rather than guessed.

Two tags joined by a slash (**[CAP/HW]**, **[RE/CAP]**) mean both kinds of evidence agree, the
first being the primary one. The design documents also use **[patent]** and **[decide]**
(HACKING.md).

**Names.** Most spellings are the decoder's **[RE]**; where a public
source (the Rogue ISR, Mesa, Rogue's register headers) spells the same thing, the tables take its
spelling. The rest keep their names when the hardware confirms what the name says or a public source
outside PowerVR uses the same word for the same thing, and carry a name of ours where the
name would mislead: `sop3c`, `lrp`, `alrp`/`alrpc`, `latch`, `usub8`, `usub16`, `.quadlead`
(a quad's first instance, E088) and `.twopart` (bit 42). Eight names stay without a measured
meaning, so
they are kept as printed and marked **[open]** where they appear: `bexception` (its bit 51), `setm`,
`.bypassl1`, `.dm_nomatch`, `moest`, `setfc`, `twosided` and `optdwd`. `perinstance` (E112) and
`.pcff16` (E116) have one.

Facts asked of the hardware with our probe programs are collected in one section, one snippet
per fact, marked *Measured on the hardware (2026-10-22)* (with what stays undecided) or *Not
probed yet*.

### 1.2 Clean room

Everything here was written from our own decoders, our own programs, the GPL DDK and our
hardware runs. No vendor ISA text is quoted. Examples are either our own programs
(`asm/`) or instructions assembled fresh for this document; no instruction
word of the closed firmware appears. Where the firmware's use of an instruction is described,
it is described in words and counts, not quoted.

### 1.3 Reading the encodings

The decoders are tables of **forms**. A form is an assembler pattern, the bits that identify
it (`(word & mask) == value`) and up to ten **fields**. A field is one or more bit ranges of
the word, concatenated lowest first into a field value `v`, and a printer that turns `v` into
text. The decoder tries the forms in table order and prints the first whose fields all print;
the assembler reads the same table backwards and accepts a word only if the decoder prints it
back. Form numbers (`#12`) are table indices; they change when the table grows.

In the generated parts:

- **Patterns** name each field `<name>`, as in `<pred>ba<flags> #<imm>`. Names are derived
  from what a field prints: `pred` for an execution predicate, `dst` and `src0`-`src2` for
  register operands (by where the operand sits in the word), a flag's own name such as `end`,
  `op` for an operation, `imm` for a number, `extra` for an optional trailing operand. A field
  after the `+` of a two-operation instruction gets an `s` prefix; repeated names are numbered.
- **Diagrams** draw the word as boxes, highest bit first, each box headed by its highest and
  lowest bit. A box holds a field name, the value of fixed bits (`?` where the forms sharing
  the diagram differ) or `-` for bits the instruction ignores. A field split over several
  places appears once per place.
- **Field lists** say where each field's bits are (`27:21 → v[6:0], 51 → v[9]`: word bits
  27-21 are value bits 6-0, word bit 51 is value bit 9) and what its values print. `(none)` is
  a value that prints nothing.
- **Mnemonics and modifiers** are collected from every value the fields can print; numbered
  families are written once (`.repeatN`, `.fetchN`, `.incsXYZ`).

## 2. Programs and the instruction word

A PDS program is a **data segment** followed by **instructions**, both 32-bit little-endian
words **[CAP/HW]**. The data segment holds the program's constants (code addresses, DMA control
words, masks); the hardware is told its size separately, in rows of four dwords (16 bytes):
in a `doutu`-started program's resource record, in the VDM state words, or in the
`EVENT_*_PDS_DATA` registers.
Branch targets count instructions from the first instruction after the data segment
**[RE/CAP]**.

An instruction word has the **opcode** in `w[31:27]` and, in most groups, the **predicate** in
`w[26:24]` (7 = always); the remaining 24 bits are the operands, laid out per group **[RE]**.
The opcodes and the mnemonics each one holds (the integer ALU group takes its operation from
the opcode field itself, so its single form spans several opcodes):

- Opcode 0 (`0x00`): `movs`
- Opcode 1 (`0x01`): `mov16`
- Opcode 2 (`0x02`): `mov32`
- Opcode 3 (`0x03`): `mov64`
- Opcode 4 (`0x04`): `mov128`
- Opcode 5 (`0x05`): `movsa`
- Opcode 6 (`0x06`): `load`
- Opcode 7 (`0x07`): `store`
- Opcode 8 (`0x08`): (none: no form decodes it)
- Opcode 9 (`0x09`): (none: no form decodes it)
- Opcode 10 (`0x0a`): (none: no form decodes it)
- Opcode 11 (`0x0b`): (none: no form decodes it)
- Opcode 12 (`0x0c`): `mul`
- Opcode 13 (`0x0d`): `abs`
- Opcode 14 (`0x0e`): (none: no form decodes it)
- Opcode 15 (`0x0f`): `rfence`, `rwfence`
- Opcode 16 (`0x10`): `tstz`
- Opcode 17 (`0x11`): `tstn`
- Opcode 18 (`0x12`): `bra`
- Opcode 19 (`0x13`): `call`
- Opcode 20 (`0x14`): `rtn`
- Opcode 21 (`0x15`): `halt`
- Opcode 22 (`0x16`): `nop`
- Opcode 23 (`0x17`): `alum`
- Opcode 24 (`0x18`): (none: no form decodes it)
- Opcode 25 (`0x19`): (none: no form decodes it)
- Opcode 26 (`0x1a`): (none: no form decodes it)
- Opcode 27 (`0x1b`): `not`
- Opcode 28 (`0x1c`): (none: no form decodes it)
- Opcode 29 (`0x1d`): (none: no form decodes it)
- Opcode 30 (`0x1e`): `shl`
- Opcode 31 (`0x1f`): `shr`
- With the opcode in a field: `adc`, `add`, `and`, `nand`, `nor`, `or`, `sbc`, `sub`, `xor`

## 3. Machine model

### 3.1 Data registers

The data segment is loaded into two banks, `ds0` and `ds1`, of 64 dwords each **[RE]**. It is
stored **in rows of four dwords, two per bank**: row `r` holds `ds0[2r]`, `ds0[2r+1]`,
`ds1[2r]`, `ds1[2r+1]` **[HW]** (*Hardware probes*). So data dwords 0-3 are `ds0[0]`,
`ds0[1]`, `ds1[0]`, `ds1[1]`, dwords 4-7 are `ds0[2]`, `ds0[3]`, `ds1[2]`, `ds1[3]`, and so on;
every one of our
PDS programs documents its data segment this way, and the hardware reads them so.

Only `ds0[48..63]` and `ds1[48..63]` can be written: the rows below are read-only, and a write
to `dsB[n]` lands in the temporary `dsB[48 + (n & 15)]` **[HW]**. Our programs compute in
`ds0[48]`, `ds1[48]` and `ds1[50]` **[HW]**, and `load`/`store` move memory to and from
`ds0[48]`/`ds1[48]` and up **[RE]**. The temporaries keep their values from one PDS task to the
next, and the read-only rows past the data segment hold what earlier tasks left **[HW]**: a
program must write a temporary before it reads it.

### 3.2 Input and special registers

- `ir0`, input word 0: the vertex index of a vertex program **[HW]**; the tile position
  `tile_y << 10 | tile_x` (16 x 16 tiles) of a fill's secondary program **[HW]** and of the
  pixel-event program, on every one of 41 tiles of a 128x128 triangle read back
  (`pds-pixel-event-pixev-grid16`) **[HW]**, and of the primary pixel program, per pixel, bit
  by bit (E262) **[HW]**; the request mask the microkernel passes to its PDS #14 **[RE]**.
- `ir1`, input word 1: the event bits of the pixel-event program **[CAP/infer]**: on the
  end-of-tile events of the render's last two 16 x 16 tiles, and on no other, bit 2 is set
  **[HW]** (a 128x128 and a 64x64 triangle: the events that have it, sent to the end-of-render
  task instead, leave the bottom-right 32 x 16 pixels unwritten; read back per tile, `ir1` is 6
  on tiles (6, 7) and (7, 7) of the 128x128 render and 2 on every other tile seen); bits 3 and
  8-11 are clear on every end-of-tile event **[HW]** (`tri-pixev-event-bit*`,
  `pds-pixel-event-pixev-grid16`, `probes/pds/pixel-event.toml`); in the
  microkernel's event program, `EVENT_STATUS` bits 22-0 in reverse order (bit k is status bit
  22 - k: all eight bits the handlers acknowledge fit) **[RE/infer]**. It reads 0 in a fill's
  secondary program and in the primary pixel program (every pixel, E262) **[HW]**. In the
  pixel-event program every path reads the event bits: the ALU, `shl`, `abs`, `mov32`'s `ir1.0` and
  `ir1.1` and `mov16`'s `ir1.0` alike on one tile, and per tile the ALU and `mov32`'s `ir1.0` and
  `ir1.1` (E263) **[HW]**. A test's source 65, which the decoder names `ir1`, tests zero exactly
  where `ir0` is 0: `tstz` of it is true on the pixels of tile (0, 0) and on a one-tile render,
  false on every other tile, while the ALU's `ir1` is 0 (primary pixel program) or never 0
  (pixel-event program) (E262, E263) **[HW]**; that it reads `ir0` fits every case **[infer]**, and
  `tstn` of it was not measured.
  Rogue's vertex programs get the vertex index in `IR0` and the instance ID in `IR1` (Mesa
  `pvr_pds.c`, MIT, Imagination); for SGX's vertex programs the second is **[infer]**.
- `ir2` **[open]**: in a `movs` it reads 0 in a fill's secondary program **[HW]**; the
  `mov16`/`mov32` fields do not reach it (the field once called `ir2` there is
  `pc.0`, *Hardware probes*) **[HW]**.
- `tim` is the SGX register **`EVENT_TIMER`** (`0xacc`): `VALUE` in bits 23-0, `ENABLE` in bit 24
  (`EUR_CR_EVENT_TIMER` in `sgx545defs.h`, GPL DDK) **[GPL/HW]**, the microkernel's tick. The
  firmware loads it with `HostCtl.ui32uKernelTimerClock | 1 << 24` (core clocks per tick, 400000 at
  400 MHz, for the DDK's 1000 Hz `SYS_SGX_PDS_TIMER_FREQ`); it counts down while enabled, and its
  expiry is `EVENT_STATUS.TIMER` (bit 29), which `EVENT_PDS_ENABLE` sends to the event program
  **[GPL/RE]**. Everything measured fits: a `movs tim` writes it (its first word's bits 24-0), for
  every later job, the firmware's included; reset reprograms it (`0x0102_0000`-`0x0106_1a7f` read
  back) and POWER IDLE writes 0 **[HW]**. The firmware writes it only at boot and on POWER resume,
  so it reloads itself with the period last written **[RE/infer]**; an enabled small count, which
  hung the job in runs by hand that no record holds (Q057), would then raise TIMER events back to
  back **[infer]**. The ALU, `shl`, `mul` and `movs` read it as `tim`, `mov16`/`mov32` as `tim.0`
  (*Hardware probes*) **[HW]**.
- `pc`, through `mov16`/`mov32` only (`pc.0`): the fetch pc, the reading instruction's index plus 3,
  or plus 1 to 2 where fetch fell behind; the same on every pass of a loop, so not a time (*Hardware
  probes*) **[HW]**. Over the 399 reads of 27 programs it was never more than 3 nor less than 1
  ahead (E261) **[HW]**. Where it lags is mostly a fixed place in a program: back to back, at
  instructions 26-27 (dwords 62-63, before a 64-dword boundary) in ten of twelve runs whatever the
  `nop`s before, with some runs lagging elsewhere **[infer]** (Q062). The simulator gives index + 3,
  which the hardware may give up to 2 below.
- `mr01`, `mr23`: 64-bit sources of `mov64`; they read 0 in a fill's secondary program, the
  pixel-event program on every tile and the primary pixel program on every pixel, also after
  a `movs mr` (E262, E263, E264) **[HW]**; what `mr` is for is **[open]** (Q057).

Some operand fields reach only a prefix of the specials (`ir0`, `ir1`; or `ir0`, `ir1`, `tim`):
the field descriptions below say which. `mov16`/`mov32` number theirs apart **[HW]**: special
index `k` (the field less 128, in dwords) is selector `k >> 1` over `ir0`, `ir1`, `pc`, `tim`
and the word's bit 9 (`k & 1`), spelled `.0`/`.1` (`mov32 ds0[48], tim.0`, `mov16 ds0[96],
ir0.1.l`); selectors 4 and up read 0 and stay undecoded. Through `mov16` a `.1` source reads 0
in every case tried; `mov32` does not decode the bit (`.1` reads as `.0`). What it is for is
**[infer]**: another PDS pipe's registers (SGX545 is the only core in the DDK with two,
`SGX_FEATURE_NUM_PDS_PIPES`), another core's on the MP parts, or 64-bit specials; SGX545
cannot tell (*Hardware probes*, 8.11). The
fields were once numbered `ir0`, `ir1`, `pc`, `tim`, `ir2` in dwords, which the hardware does
not follow; this reference spells them as above (8.9).

### 3.3 Predicates

The predicate field `w[26:24]` reads `p0`, `p1`, `p2`, `if0`, `if1`, `aluz`, `alun` or nothing
(7) **[RE]**:

- `p0`-`p2` are written by `tstz` (`pN = (src == 0)`) and `tstn` (`pN` = bit 31 of `src`)
  **[HW]**. `tstz` setting its predicate on zero is **[CAP/HW]**: our pixel-event program
  matches the captured one in what it tests and where it branches, skipping each case with
  `tstz p0, x; (p0) bra`, and the right task runs for each event.
- `if0` and `if1` are **[open]** on SGX. Our vertex program starts its shader under `(if0)`, as
  the closed driver's vertex programs do **[CAP]**, and in a fill's secondary program neither
  tests true **[HW]**. Rogue's PDS defines them as input predicates: `IF0` "Last Vertex In Task"
  for a vertex program and "End of Tile" for a pixel start/end program, `IF1` "First In Task"
  and "End Render" (Mesa `pvr_rogue_pds_defs.h`, MIT, Imagination); its vertex program issues
  `doutu` once, under `IF0`, on the last vertex (`pvr_pds.c`). Our vertex observations fit that
  reading **[infer]**. In pixel programs neither tests true anywhere: not in the primary pixel
  program of any pixel of a 64x64 and a 128x128 triangle, nor in the pixel-event program of any
  tile, the last ones included (E262, E263) **[HW]**, so Rogue's pixel readings ("End of Tile",
  "End Render") do not hold for these tasks (Q058).
- `aluz` tests a zero result of the last `add`, `sub`, `adc`, `sbc` or `mul`; `alun` a negative
  one, but only under `alum signed`; every other instruction keeps both **[HW]** (*Hardware
  probes*).

`load`, `store`, the fences and `nop` use `w[26:24]` for other purposes or not at all, and
carry no predicate.

### 3.4 The output ports

A `movs` (or `movsa`) writes four source words to a **port**; the `dout*` ports issue work to
other units **[RE]**. What each port does with its words, where we know it:

| port | words | known meaning |
|------|-------|---------------|
| `doutu` | U0, U1, U2 | start a USSE task **[HW]** |
| `doutd` | address, control | DMA memory into the USSE attributes **[HW]** |
| `douta` | value, control | write one secondary attribute **[HW]** |
| `douti` | two words | issue iterator work **[HW]** |
| `doutt` | T0-T3 | the state of a texture fetch **[HW]** |
| `tim` | value, (ignored) | load the counter `tim`: bits 24-0, bit 24 the run bit **[HW]** |
| `doutc` | | faults the job, from a fill's secondary or a primary pixel program **[HW]** |
| `douts`, `slc`, `mr`, `ir0` | | no effect seen (E264) **[open]** |

- **`doutu`** **[HW]**. U0 holds the code address: `CBASE` (`USE_CODE_BASE_n`) in bits 3-0 and
  the instruction index above it (`EXE`, bits 19-4 on this build's layout), plus the
  temporaries in fours (`TRC`) in bits 31-24. U1 holds flags: bit 2 `SDSOFT` for the pixel
  and secondary programs, bit 23 `PBENABLE` for the end-of-tile task, bit 22 `ENDOFRENDER`,
  bit 25 `TEXTUREDEPENDENCY` (wait for the texture result); U2 is 0 in all our programs
  (`doc/specs/transfer.md` §4.2, §4.4). A `movs` always names four sources; `doutu`
  uses three. The tile position the pixel-event program puts in the end-of-tile task's U1
  does not place the tile: flipping its lowest `tile_x` or `tile_y` bit changed no pixel of a
  64x64 render (2026-10-24, the triangle probe host) **[HW]**, so the PBE words place it.
  On the fill, read after the fact from the kept sweeps of every value of the x field (bits
  11:3) and the y field (bits 21:12) poked into the program's U1 word, the fields do place it,
  in half-tile units (16 pixels in x, 8 rows in y): each 32 x 16 tile t stores at
  (2t | f) >> 1 or (2t + f) >> 1 per axis and nothing is stored where that lies outside the
  target, which gives the tool's image hash in 1536 of 1536 jobs, XOR in place of OR in 1532
  (E876, post hoc). The lowest bit is half a tile, which is why its flip changed nothing. Held
  out on fills of 128 x 64 and 256 x 32, where OR and addition differ, OR gave every image hash
  (20 of 20 rows, 8 of 8 that separate the two) and addition failed 8 of 8, with nothing stored
  outside the target **[HW]** (E884): the program ORs the poked word into the tile's own field
  and the task stores the tile at the place the field names, field >> 1 in 32 x 16 tiles. E126's
  XOR flips on a 128 x 128 render move whole tiles the same way (19 of 19 pictures, post hoc).
  With both fields poked at once each axis is placed by its own field the same way, independently
  of the other: held out on a 128 x 64 fill, 8 of 8 image hashes, where only the x field acting or
  only the y field gave none **[HW]** (E909).
- **`doutd`** **[CAP/HW]**. The first word is the source address; the second is
  burst size − 1 (bits 3-0), lines − 1 (7-4), the destination attribute (19-8) and
  stride − 1 (29-22) With `movsa` the third source is added to
  the address: our vertex program fetches vertex `index × stride` this way.
- **`douta`** writes its first word to the secondary attribute named by bits 19-8 of the
  second **[HW]**: from a fill's secondary program the words reach `sa0`-`sa15` of its pixel
  tasks, given room for them in the PDS state's secondary attribute size; from the primary
  program nothing reached the USE task. Attributes 0-63 arrive at their own `sa` with the size
  word (the background object's dword 1, bits 24:18, echoed as sent) at 0, 1, 2, 3, 4, 6 and 8
  rows (E391, E1096, E1104); what the size limits is open (Q019).
  Our pixel-event program uses it before starting the
  end-of-tile task. Secondary attributes keep their values from one job to the next **[HW]**:
  a task reads what an earlier one left in any it was not given.
- **`douti`** and **`doutt`** **[HW]**: our copy's primary program issues one iterator word pair
  (one texture fetch from the first layer, no USE issue) and the four texture state words
  T0-T3, and the texel arrives in `pa0` of the task `doutu` started
  (`doc/specs/transfer.md` §4.4).
  The task waits for its iterations with U1 bit 24 and for its fetches with U1 bit 25, and
  the program's last iteration of each kind ends the wait: `DOUTI0` bit 29 (`LAST_ITER`) and
  bit 30 (`LAST_FETCH`); a wait no word ends, or an end no wait takes, hangs the job. The word
  pair's other fields are in the glossary's `DOUTI0` rows (E047, E048).

## 4. Operand encodings

The PDS has no single operand encoding: each group lays out its own fields **[RE]**. The
recurring ones:

- **Seven-bit destination** (`w[6:0]`): `ds0[0]`-`ds0[63]`, then `ds1[0]`-`ds1[63]`.
- **Seven-bit first source** (`w[23:17]`): `ds0[0]`-`ds0[63]`, then the first two or three of
  `ir0`, `ir1`, `tim`; the second source of the ALU group is always `ds1[n]` (`w[15:10]`). Past
  `tim` the field reads 0 **[HW]**.
- **Halves** (`.l`, `.h`): `mov16` and `mul` read 16-bit halves of a register. The `movs`
  sources' `.l`/`.h` on a special are not halves: a special is a pair of words, as a `ds0`
  pair is, and `.l` passes a whole 32-bit word **[HW]**.
- **The `movs` source list** (`w[23:5]`): a `ds1` pair (`w[17:13]` × 2) and either a `ds0`
  pair (`w[22:18]` × 2) or, with `w[23]` set, the input register numbered by `w[22:18]`;
  then four two-bit selectors, one per slot (`w[12:5]`), each picking the `ds1` pair or the
  other one, and its first or second dword (`.l` or `.h` of a special). So
  the four sources of one `movs` come from at most two `ds0` and two `ds1` dwords.

`movsa doutd, ds0[0], ds0[1], ds1[50], ds1[50]` assembles with form #1: the word is `0x2F032343`; in
memory (little endian) `43 23 03 2F`.

| field | value | prints |
|---|---|---|
| `pred` | 0x7 | (none) |
| `dst` | 0x3 | `doutd` |
| `srcs` | 0x191a | `ds0[0], ds0[1], ds1[50], ds1[50]` |

## 5. Assembler syntax

`pds-asm` reads the syntax `pds-dis` prints, with the rules of the USSE assembler (comments,
labels, lenient blanks and number bases, listings; `tools/usse-asm/README.md`) and two of its
own:

- **The data segment** is the raw words (`.word 0x...`) before the first instruction, in file
  order: dword 0 first, so `ds0[0]`, `ds0[1]`, `ds1[0]`, `ds1[1]`, `ds0[2]`, ... by the row
  layout above. In a listing, a `data` line takes its value from the hex column.
- **Labels** count instructions from the first one after the data segment, as `bra` and `call`
  do, so `(p0) bra not_eot` works without counting data words.

A predicate is written in parentheses before the mnemonic: `(p0) bra done`, `(if0) movs ...`.

From `asm/transfer/pds_prim.s`:

```
; pds_prim.s -- the PDS primary program of a fill, KICKONLY (template
; PDS_PRIM, id 4).
;
; The background object names this program; the PDS runs it per pixel batch
; and it only starts the fill shader (use_fill.s) as a USE task: a DOUTU
; issue of the three words U0-U2 (doc/specs/fw_format.md §9.4).
;
; Data segment (the first 4 dwords; banks interleave by pairs of dwords,
; doc/specs/hw_spec.md §2). The driver patches dwords 0-2
; (doc/specs/fw_format.md §9.4): U0 = the DOUTU word of USE_FILL (EXE [19:4], CBASE [3:0], TRC
; [31:24]), U1 = 4 (SDSOFT), U2 = 0.

        .word 0         ; dword 0 = ds0[0]: U0 (patched)
        .word 0         ; dword 1 = ds0[1]: U1 (patched)
        .word 0         ; dword 2 = ds1[0]: U2 (patched)
        .word 0         ; dword 3 = ds1[1]: unused

        ; Issue U0, U1, U2 to the USE through the DOUTU port. A movs always
        ; names four sources; DOUTU takes three, the fourth repeats ds0[0].
        movs doutu, ds0[0], ds0[1], ds1[0], ds0[0]
        halt
```

## 6. Instruction groups

One section per group: what it does and what is known of it, how the microkernel's five PDS
programs and ours use it, examples, then the generated forms, mnemonics, diagrams and field
lists. The microkernel's programs (event dispatch, boot, deferred work) are described in
`doc/specs/hw_spec.md`; they are counted here, not quoted.

### 6.1 Port writes: `movs`, `movsa`

Opcodes 0 (`movs`) and 5 (`movsa`) write four source words to a port (`w[3:0]`, *The output
ports*); ports 10-14 do not decode **[RE]**.

- **`movs port, a, b, c, d`** issues the four words **[HW]**; every program we run ends its
  work with one or more (`doutd` the data, then `doutu` the task).
- **`movsa`** adds its third source to the DMA address of a `doutd` **[CAP/HW]**: our vertex
  program fetches the vertex at `base + index × stride` with
  `movsa doutd, ds0[0], ds0[1], ds1[50], ds1[50]`, where `ds1[50]` holds `index × stride`.
  What `movsa` does on other ports is **[open]**.

**In the microkernel's programs [CAP].** Every path through the five programs ends in a
`movs doutu` that starts a USSE task, then `halt`: one in the boot programs, four in the
event program (one per case), three in the deferred-work program. The program that starts
`edm.task.pds11` first `doutd`s the TA/3D control block into the secondary attributes; the
event and deferred-work programs pass their inputs on with `douta` (an input register or the
timer, written `ir0.l`, `ir1.l`, `tim.l` in every slot: the whole low word **[HW]**).

From `asm/tri/pds_vtx.s`:

```
        movsa doutd, ds0[0], ds0[1], ds1[50], ds1[50]
        (if0) movs doutu, ds0[2], ds0[3], ds1[1], ds1[1]
```

Forms (generated from the decoder's table; `<name>` is a field):

```
#0    opcode 0       mask F8000000  value 00000000  movs
      <pred>movs <dst>, <srcs>
#1    opcode 5       mask F8000000  value 28000000  movsa
      <pred>movsa <dst>, <srcs>
```

Mnemonics: `movs`, `movsa`.

Layout (forms #0, #1):

```
 31   27 26  24 23   5 4   3   0
+-------+------+------+---+-----+
| 00?0? | pred | srcs | - | dst |
+-------+------+------+---+-----+
```

- `pred`: bits 26:24. Values: 0-2 `(p0)`…`(p2)`, 3 `(if0)`, 4 `(if1)`, 5 `(aluz)`, 6 `(alun)`, 7
  (none).
- `dst`: bits 3:0. Values: 0 `mr`, 1 `slc`, 2 `douti`, 3 `doutd`, 4 `doutt`, 5 `doutu`, 6 `douta`, 7
  `tim`, 8 `doutc`, 9 `douts`, 15 `ir0`. Other values do not decode.
- `srcs`: bits 23:5. An operand list (see *Operand encodings*), for example 0 `ds0[0], ds0[0],
  ds0[0], ds0[0]`, 1 `ds0[0], ds0[0], ds0[0], ds0[1]`, 2 `ds0[0], ds0[0], ds0[0], ds1[0]`.

Simulator (`crates/sgx-sim`, from `doc/isa/sim-coverage.json`): 2 of 2 forms have semantics. The
probe vectors that test them: 54 match the hardware (18 with near values: 2 each within the bound
the hardware was measured to, 16 with a value the task does not know, the timer, accepted as any
value of its width and so not checked), 36 stop unsupported, 0 mismatch (`pds-alu-carry-movs` 4/0/0,
`pds-alu-flags-movs` 4/0/0, `pds-alu-specials` 12/0/0, `pds-alu-specials-paths` 2/0/0,
`pds-fetch-pc-kinds` 0/3/0, `pds-load-store-ports` 1/6/0, `pds-mov128-bit15-companions` 0/3/0,
`pds-mov128-bit15-mr` 3/24/0, `pds-timer-tim-count` 4/0/0, `pds-timer-tim-host` 2/0/0,
`pds-timer-tim-period` 2/0/0, `pds-timer-tim-restore` 2/0/0, `pds-timer-tim-words` 18/0/0);
unsupported mostly for the port is open (32); reads dsN[N] before the program writes it (3); movsa
to Douta is open (1).

Confirmed on the hardware (a passing vector): #0; not yet confirmed (as decoded; no passing vector
yet): #1.

### 6.2 Data moves: `mov16`, `mov32`, `mov64`, `mov128`

Opcodes 1-4 **[RE]**: `mov16 dsB[n], src.h|l` moves a 16-bit half (sources: `ds0`, `ds1`, then
`ir0`, `ir1`, `pc`, `tim`, each `.0` or `.1` (3.2), each `.l` or `.h`); `mov32 dsB[n], src` a
dword (the same sources, whole); `mov64 dsB[2k], src` an aligned pair (from a `ds0`/`ds1`
pair, `mr01` or `mr23`); `mov128 ds[2k], ds[2j]` four dwords, optionally `, swap`.

- **Semantics [HW].** Copies of the named width. `mov16`'s destination index names a 16-bit half:
  `dsB[n]` is the high half of `dsB[n >> 1]` for odd `n`, the low half for even `n`, and the other
  half is kept (so `ds0[96]` is the low half of `ds0[48]`). `mov128 ds[2k]` is the row `ds0[2k]`,
  `ds0[2k+1]`, `ds1[2k]`, `ds1[2k+1]` and `swap` exchanges its two pairs; its source field is five
  bits, rows 0-31 (`ds[0..62]`), rows 24-31 the temporaries (rows 24 and 27 read back, E261)
  **[HW]**. With `lastpair` (bit 15) set it writes to both halves of its destination row the
  `ds0` pair the last `mov32` or `movs` read from a data row (rows 0-23): a `mov32` from `ds0[9]`
  or `ds0[2]` and a `movs` to `mr` or `douta` from the pair `ds0[2]`, `ds0[3]` or `ds0[6]`,
  `ds0[7]` name that pair, whatever the `mov128`'s source row, `swap` and other unmapped bits
  (23:16, 9, 7, 1:0); a `mov32` from `ds1[9]`, a `not` of a temporary (`ds0[48-55]` or
  `ds1[48-55]`), a `movs` from the temporary pair `ds0[50]`, `ds0[51]` and a `mov64` from `mr01`
  leave it (E261, E379) **[HW]**. These are the instructions the runs placed before it; others
  (another row or pair, `movsa`, a `not` of a data row, `mr23`) were not run, so the pair after
  them is not known. Since the data rows are read-only, the pair named is its value. The decoders
  print the bit as `, lastpair` after `, swap`; the simulator writes the pair after the
  instructions measured and stops otherwise.
- **In the microkernel's programs:** not used; nor in ours.

`mov16 ds0[3], ds1[2].h` assembles with form #2: the word is `0x0F008503`; in memory (little endian)
`03 85 00 0F`.

| field | value | prints |
|---|---|---|
| `pred` | 0x7 | (none) |
| `ds` | 0x0 | `0` |
| `idx` | 0x3 | `3` |
| `src` | 0x85 | `ds1[2].h` |

Forms (generated from the decoder's table; `<name>` is a field):

```
#2    opcode 1       mask F8000000  value 08000000  mov16
      <pred>mov16 ds<ds>[<idx>], <src>
#3    opcode 2       mask F8000000  value 10000000  mov32
      <pred>mov32 ds<ds>[<idx>], <src>
#4    opcode 3       mask F8000000  value 18000000  mov64
      <pred>mov64 ds<ds>[<idx>], <src>
#5    opcode 4       mask F8000000  value 20000000  mov128
      <pred>mov128 ds[<idx1>], ds[<idx2>]<extra1><extra2>
```

Mnemonics: `mov128`, `mov16`, `mov32`, `mov64`.

Layout 1 of 4 (form #2):

```
 31   27 26  24 23 17 16  8 7    6   0
+-------+------+-----+-----+----+-----+
| 00001 | pred |  -  | src | ds | idx |
+-------+------+-----+-----+----+-----+
```

- `pred`: bits 26:24. Values: 0-2 `(p0)`…`(p2)`, 3 `(if0)`, 4 `(if1)`, 5 `(aluz)`, 6 `(alun)`, 7
  (none).
- `ds`: bit 7. A 1-bit number, printed in decimal.
- `idx`: bits 6:0. A 7-bit number, printed in decimal.
- `src`: bits 16:8. A register operand, v = bank·128 + number (the bank bits may carry modifiers).
  By bank: 0 `ds0[0].l`…`ds0[63].h`, 1 `ds1[0].l`…`ds1[63].h`, 2 `ir0.0.l`.

Layout 2 of 4 (form #3):

```
 31   27 26  24 23 17 16  9 8   7    6   1 0
+-------+------+-----+-----+---+----+-----+---+
| 00010 | pred |  -  | src | - | ds | idx | - |
+-------+------+-----+-----+---+----+-----+---+
```

- `pred`: as in layout 1.
- `ds`: as in layout 1.
- `idx`: bits 6:1. A 6-bit number, printed in decimal.
- `src`: bits 16:9. A register operand, v = bank·128 + number (the bank bits may carry modifiers).
  By bank: 0 `ds0[0]`…`ds1[63]`, 1 `ir0.0`.

Layout 3 of 4 (form #4):

```
 31   27 26  24 23 17 16 10 9 8 7    6   2 1 0
+-------+------+-----+-----+---+----+-----+---+
| 00011 | pred |  -  | src | - | ds | idx | - |
+-------+------+-----+-----+---+----+-----+---+
```

- `pred`: as in layout 1.
- `ds`: as in layout 1.
- `idx`: bits 6:2. A 5-bit number, printed in decimal, times 2.
- `src`: bits 16:10. A register operand, v = bank·128 + number (the bank bits may carry modifiers).
  By bank: 0 `ds0[0]`.

Layout 4 of 4 (form #5):

```
 31   27 26  24 23 16 15       14  10 9   8        7   6    2 1 0
+-------+------+-----+--------+------+---+--------+---+------+---+
| 00100 | pred |  -  | extra2 | idx2 | - | extra1 | - | idx1 | - |
+-------+------+-----+--------+------+---+--------+---+------+---+
```

- `pred`: as in layout 1.
- `idx1`: bits 6:2. A 5-bit number, printed in decimal, times 2.
- `idx2`: bits 14:10. Values: 0 `0`, 1 `2`, 2 `4`, 3 `6`, 4 `8`, 5 `10`, 6 `12`, 7 `14`, 8 `16`, 9
  `18`, 10 `20`, 11 `22`, 12 `24`, 13 `26`, 14 `28`, 15 `30`, 16 `32`, 17 `34`, 18 `36`, 19 `38`, 20
  `40`, 21 `42`, 22 `44`, 23 `46`, 24 `48`, 25 `50`, 26 `52`, 27 `54`, 28 `56`, 29 `58`, 30 `60`, 31
  `62`.
- `extra1`: bit 8. Values: 0 (none), 1 `, swap`.
- `extra2`: bit 15. Values: 0 (none), 1 `, lastpair`.

Simulator (`crates/sgx-sim`, from `doc/isa/sim-coverage.json`): 4 of 4 forms have semantics. The
probe vectors that test them: 123 match the hardware (65 with near values, each within the bound the
hardware was measured to), 46 stop unsupported, 0 mismatch (`pds-alu-after-mov128` 4/0/0,
`pds-alu-after-mov16` 12/0/0, `pds-alu-after-mov64` 4/0/0, `pds-alu-constants` 2/0/0,
`pds-alu-flags-mov128` 4/0/0, `pds-alu-flags-mov64` 4/0/0, `pds-alu-inputs` 2/0/0,
`pds-alu-specials-paths` 2/2/0, `pds-alu-specials-paths2` 0/2/0, `pds-alu-uninit` 0/2/0,
`pds-encoding-bits-flow-bra` 6/0/0, `pds-encoding-bits-flow-nop` 28/0/0,
`pds-encoding-bits-followup-nop` 10/0/0, `pds-fetch-pc-back-to-back` 12/0/0, `pds-fetch-pc-kinds`
0/9/0, `pds-fetch-pc-nop-gaps` 6/0/0, `pds-fetch-pc-pad-back-to-back` 5/25/0, `pds-load-store-ports`
0/1/0, `pds-mov128-bit15-mr` 0/3/0, `pds-moves-mov-flag-cond` 0/2/0, `pds-moves-mov-flag-pipes`
2/0/0, `pds-moves-mov-wide` 10/0/0, `pds-moves-mov16` 2/0/0, `pds-moves-mov16-constants` 8/0/0);
unsupported mostly for (pN) before it is known (25); reads dsN[N] before the program writes it (11);
scratch[NxN] is computed from a near value (4).

Confirmed on the hardware (a passing vector): #2, #3, #4, #5.

### 6.3 Memory: `load`, `store`

Opcodes 6 and 7 **[RE]**: `load addr, dsB[48+i ... ]` and `store addr, dsB[48+i ...]` move one to
eight dwords between memory and the registers from `ds0[48]` or `ds1[48]` up. The address is an
18-bit dword index (printed as a byte address, `× 4`); the count reuses the predicate bits
`w[26:24]` (1-8, 0 meaning 8), so these instructions cannot be predicated.

- **Semantics.** The address is absolute in the program's GPU address space, so these reach
  its first 1 MiB **[HW]** (a fill client's loads from 0, `0x1000` and `0x10000` faulted on
  those pages, under the PDS's own `BIF_INT_STAT` requestor bit 13).
- **Timing [HW]** (E143, with the probe's scratch mapped at `0x10000` through the kernel's
  debugfs `sgx/vm_low`). A `load`'s dwords land in its registers only at the next `rfence` or
  `rwfence`. Without one, the registers keep their old values through four `nop`s and up to
  the program's `douta`. A `store` writes the registers as they are at once, so a `load` not
  yet fenced is not in what it stores. A `load` after a `store` of the same dword reads the
  stored value.
- **Store faults [HW]** (E144). A program whose stores total 2, 3 or 4 dwords faults once
  they have landed. That holds for one store of that size or several smaller ones (1 + 1,
  2 + 1, also with an `rfence` between), on any page. A total of 1 or of 5 and more (4 + 1,
  five of 1, 8 + 2, 8 + 8 + 2) completes. `CR_BIF_FAULT` names the first store's page; its low
  bits are the context's directory slot (`CID`) and `SB`, 2 for totals of 2 and 3 for totals of
  3 or 4 (E145). Why these totals fault, and what `SB` encodes, are **[open]**.
- **In the microkernel's programs:** not used; nor in ours.

`load 0x00001000, ds0[48-51]` assembles with form #6: the word is `0x34000400`; in memory (little
endian) `00 04 00 34`.

| field | value | prints |
|---|---|---|
| `imm` | 0x400 | `0x00001000` |
| `ds` | 0x0 | `0` |
| `idx` | 0x40 | `48-51]` |

Forms (generated from the decoder's table; `<name>` is a field):

```
#6    opcode 6       mask F8000000  value 30000000  load
      load <imm>, ds<ds>[<idx>
#7    opcode 7       mask F8000000  value 38000000  store
      store <imm>, ds<ds>[<idx>
```

Mnemonics: `load`, `store`.

Layout (forms #6, #7):

```
 31   27 26 24 23  22   21 18 17  0
+-------+-----+---+----+-----+-----+
| 0011? | idx | - | ds | idx | imm |
+-------+-----+---+----+-----+-----+
```

- `imm`: bits 17:0. An 18-bit number, printed in hex, times 4.
- `ds`: bit 22. A 1-bit number, printed in decimal.
- `idx`: bits 21:18 → v[3:0], 26:24 → v[6:4]. 128 distinct texts, for example 0 `48-55]`, 1
  `49-56]`, 2 `50-57]`, 3 `51-58]`, 4 `52-59]`, 5 `53-60]`.

Simulator (`crates/sgx-sim`, from `doc/isa/sim-coverage.json`): 2 of 2 forms have semantics. The
probe vectors that test them: 229 match the hardware (3 with near values, each within the bound the
hardware was measured to), 0 stop unsupported, 0 mismatch (`pds-encoding-bits-memory-fence` 27/0/0,
`pds-fetch-pc-load` 3/0/0, `pds-load-store-addressing` 8/0/0, `pds-memory-mem` 40/0/0,
`pds-memory-mem2` 36/0/0, `pds-memory-mem3` 28/0/0, `pds-memory-mem4` 20/0/0, `pds-memory-mem5`
24/0/0, `pds-memory-mem6` 10/0/0, `pds-store-totals-runs` 33/0/0).

Confirmed on the hardware (a passing vector): #6, #7.

### 6.4 Integer ALU: `add`, `sub`, `adc`, `sbc`, `and`, `or`, `xor`, `nor`, `nand`

Opcodes 8-11 (`add`, `sub`, `adc`, `sbc`) and 24-26, 28-29 (`or`, `and`, `xor`, `nor`, `nand`)
share one layout: `op dst, src, ds1[n]` with a seven-bit destination, a first source from
`ds0` or `ir0`/`ir1`/`tim`, and `ds1[n]` **[RE]**. Opcode 27 is `not` (*`abs`, `not`*) and
opcode 14 does not decode.

- **Semantics [HW].** `dst = src op ds1[n]` on 32 bits, as named, `add` and `sub` modular
  (our pixel-event program also builds the end-of-tile task's `U1` with `and`/`or` masks).
  `add` and `sub` leave the high dword of the exact result (+1 carry, -1 borrow, else 0),
  which `adc` and `sbc` both add: `a + b + c`, `a - b + c`. All four set `aluz`, and `alun`
  under `alum signed`; the logic ops set neither, and keep the carry (*Hardware probes*).
- **In the microkernel's programs [CAP].** The event program masks the event bits of `ir1`
  with `and` and compares groups of them with `xor` before its tests; the deferred-work
  program masks the request bits of `ir0` with `and`.

From `asm/transfer/pds_pixevent.s`:

```
        and ds1[48], ir1, ds1[2]
        and ds1[48], ir1, ds1[3]
        and ds1[48], ds0[4], ds1[48]                    ; ~ir1 & 0x100: zero if bit 8 set
        and ds1[48], ds0[5], ds1[48]                    ; tile_x
        or ds0[48], ds0[6], ds1[48]                     ; base | tile_x
        and ds1[48], ds0[7], ds1[48]                    ; tile_y
        or ds0[48], ds0[48], ds1[48]
        and ds1[48], ds0[8], ds1[48]                    ; ENDOFRENDER
        or ds0[48], ds0[48], ds1[48]
        and ds1[48], ir1, ds1[4]
```

Forms (generated from the decoder's table; `<name>` is a field):

```
#8    any opcode     mask 00000000  value 00000000  adc add and nand nor or sbc sub xor
      <pred><op> <dst>, <src>, ds1[<idx>]
```

Mnemonics: `adc`, `add`, `and`, `nand`, `nor`, `or`, `sbc`, `sub`, `xor`.

Layout (form #8):

```
 31 27 26  24 23 17 16  15 10 9 7 6   0
+-----+------+-----+---+-----+---+-----+
|  op | pred | src | - | idx | - | dst |
+-----+------+-----+---+-----+---+-----+
```

- `pred`: bits 26:24. Values: 0-2 `(p0)`…`(p2)`, 3 `(if0)`, 4 `(if1)`, 5 `(aluz)`, 6 `(alun)`, 7
  (none).
- `op`: bits 31:27. Values: 8 `add`, 9 `sub`, 10 `adc`, 11 `sbc`, 24 `or`, 25 `and`, 26 `xor`, 28
  `nor`, 29 `nand`. Other values do not decode.
- `dst`: bits 6:0. A register operand, v = bank·128 + number (the bank bits may carry modifiers). By
  bank: 0 `ds0[0]`…`ds1[63]`.
- `src`: bits 23:17. A register operand, v = bank·128 + number (the bank bits may carry modifiers).
  By bank: 0 `ds0[0]`.
- `idx`: bits 15:10. A 6-bit number, printed in decimal.

Simulator (`crates/sgx-sim`, from `doc/isa/sim-coverage.json`): 1 of 1 forms have semantics. The
probe vectors that test them: 442 match the hardware (60 with near values: 6 each within the bound
the hardware was measured to, 54 with a value the task does not know, the timer, accepted as any
value of its width and so not checked), 17 stop unsupported, 0 mismatch (`pds-alu-adc-carry` 8/0/0,
`pds-alu-adc-sbc` 8/0/0, `pds-alu-add-sub` 6/0/0, `pds-alu-after-abs` 12/0/0, `pds-alu-after-adc`
8/0/0, `pds-alu-after-alum` 4/0/0, `pds-alu-after-and` 4/0/0, `pds-alu-after-mov128` 4/0/0,
`pds-alu-after-mov16` 12/0/0, `pds-alu-after-mov32` 4/0/0, `pds-alu-after-mov64` 4/0/0,
`pds-alu-after-mul` 12/0/0, `pds-alu-after-nand` 12/0/0, `pds-alu-after-nop` 4/0/0,
`pds-alu-after-nor` 12/0/0, `pds-alu-after-not` 4/0/0, `pds-alu-after-or` 12/0/0,
`pds-alu-after-sbc` 8/0/0, `pds-alu-after-shl` 4/0/0, `pds-alu-after-shr` 12/0/0,
`pds-alu-after-tstn` 12/0/0, `pds-alu-after-tstz` 4/0/0, `pds-alu-after-xor` 4/0/0,
`pds-alu-alum-spare` 48/0/0, `pds-alu-bitwise` 6/0/0, `pds-alu-call` 14/0/0, `pds-alu-carry-movs`
4/0/0, `pds-alu-flags` 48/0/0, `pds-alu-flags-alum` 4/0/0, `pds-alu-flags-mov128` 4/0/0,
`pds-alu-flags-mov64` 4/0/0, `pds-alu-flags-movs` 4/0/0, `pds-alu-flags-signed` 36/0/0, `pds-alu-if`
2/0/0, `pds-alu-loop` 6/0/0, `pds-alu-signed-adc` 10/0/0, `pds-alu-signed-carry` 14/0/0,
`pds-alu-specials-paths` 2/2/0, `pds-alu-specials-paths2` 0/2/0, `pds-alu-tst` 10/0/0,
`pds-fetch-pc-kinds` 0/3/0, `pds-moves-mov-flag-cond` 0/8/0, `pds-moves-mov-flag-flags` 12/0/0,
`pds-moves-mov-flag-pipes` 8/0/0, `pds-moves-mov-flag-write` 0/2/0, `pds-moves-mov-pc` 2/0/0,
`pds-timer-tim-count` 6/0/0, `pds-timer-tim-host` 2/0/0, `pds-timer-tim-period` 2/0/0,
`pds-timer-tim-restore` 2/0/0, `pds-timer-tim-words` 18/0/0); unsupported mostly for (pN) before it
is known (8); scratch[NxN] is computed from a near value (6); reads dsN[N] before the program writes
it (3).

Confirmed on the hardware (a passing vector): #8.

### 6.5 Multiply: `mul`

Opcode 12 **[RE]**: `mul dst, a.l|h, ds1[n].l|h` multiplies two 16-bit halves (the first from
`ds0` or `ir0`/`ir1`/`tim`) into a 32-bit destination.

- **Semantics [HW].** Our vertex program computes the vertex offset `ir0.l × stride` with it,
  and the vertices are fetched from the right place. It multiplies unsigned, and signed under
  `alum signed` **[HW]**.
- **In the microkernel's programs:** not used.

From `asm/tri/pds_vtx.s`:

```
        mul ds1[50], ir0.l, ds1[0].l
```

Forms (generated from the decoder's table; `<name>` is a field):

```
#9    opcode 12      mask F8000000  value 60000000  mul
      <pred>mul <dst>, <src1>, <src2>
```

Mnemonics: `mul`.

Layout (form #9):

```
 31   27 26  24 23  16 15   9 8 7 6   0
+-------+------+------+------+---+-----+
| 01100 | pred | src1 | src2 | - | dst |
+-------+------+------+------+---+-----+
```

- `pred`: bits 26:24. Values: 0-2 `(p0)`…`(p2)`, 3 `(if0)`, 4 `(if1)`, 5 `(aluz)`, 6 `(alun)`, 7
  (none).
- `dst`: bits 6:0. A register operand, v = bank·128 + number (the bank bits may carry modifiers). By
  bank: 0 `ds0[0]`…`ds1[63]`.
- `src1`: bits 23:16. A register operand, v = bank·128 + number (the bank bits may carry modifiers).
  By bank: 0 `ds0[0].l`…`ds0[63].h`, 1 `ir0.l`.
- `src2`: bits 15:9. A register operand, v = bank·128 + number (the bank bits may carry modifiers).
  By bank: 0 `ds1[0].l`…`ds1[63].h`.

Simulator (`crates/sgx-sim`, from `doc/isa/sim-coverage.json`): 1 of 1 forms have semantics. The
probe vectors that test them: 22 match the hardware (4 with near values, each within the bound the
hardware was measured to), 7 stop unsupported, 0 mismatch (`pds-alu-after-mul` 12/0/0, `pds-alu-mul`
6/0/0, `pds-alu-specials-paths` 2/2/0, `pds-alu-specials-paths2` 0/2/0, `pds-fetch-pc-kinds` 0/3/0,
`pds-moves-mov-pc` 2/0/0); unsupported mostly for scratch[NxN] is computed from a near value (4);
reads dsN[N] before the program writes it (3).

Confirmed on the hardware (a passing vector): #9.

### 6.6 `abs`, `not`

Opcodes 13 and 27 **[RE]**: one source, either `ds1[n]` (`w[8]` set) or a first source (`ds0`,
then `ir0`, `ir1`, and for `not` also `tim`).

- **Semantics [HW].** `not` is the bitwise complement (our pixel-event program also tests
  "bit 8 clear" as `not` then `and` then `tstz`). `abs` is the identity unless `alum signed`,
  then the two's complement absolute value, with `abs(0x80000000)` itself. The `ds1[n]` forms
  of both take `n` from bits 15:10, `ds1[0..63]`: `abs`'s bit 15, once unmapped, reads
  `ds1[n + 32]` (E259, E261) **[HW]**.

From `asm/transfer/pds_pixevent.s`:

```
        not ds1[48], ir1
```

Forms (generated from the decoder's table; `<name>` is a field):

```
#10   opcode 13      mask F8000100  value 68000100  abs
      <pred>abs <dst>, ds1[<idx>]
#11   opcode 13      mask F8000100  value 68000000  abs
      <pred>abs <dst>, <src>
#12   opcode 27      mask F8000100  value D8000100  not
      <pred>not <dst>, ds1[<idx>]
#13   opcode 27      mask F8000100  value D8000000  not
      <pred>not <dst>, <src>
```

Mnemonics: `abs`, `not`.

Layout 1 of 2 (forms #10, #12):

```
 31   27 26  24 23 16 15 10 9   8   7   6   0
+-------+------+-----+-----+---+---+---+-----+
| ?1??1 | pred |  -  | idx | - | 1 | - | dst |
+-------+------+-----+-----+---+---+---+-----+
```

- `pred`: bits 26:24. Values: 0-2 `(p0)`…`(p2)`, 3 `(if0)`, 4 `(if1)`, 5 `(aluz)`, 6 `(alun)`, 7
  (none).
- `dst`: bits 6:0. A register operand, v = bank·128 + number (the bank bits may carry modifiers). By
  bank: 0 `ds0[0]`…`ds1[63]`.
- `idx`: bits 15:10. A 6-bit number, printed in decimal.

Layout 2 of 2 (forms #11, #13):

```
 31   27 26  24 23 17 16 9 8   7   6   0
+-------+------+-----+----+---+---+-----+
| ?1??1 | pred | src | -  | 0 | - | dst |
+-------+------+-----+----+---+---+-----+
```

- `pred`: as in layout 1.
- `dst`: as in layout 1.
- `src`: bits 23:17. A register operand, v = bank·128 + number (the bank bits may carry modifiers).
  By bank: 0 `ds0[0]`.

Simulator (`crates/sgx-sim`, from `doc/isa/sim-coverage.json`): 4 of 4 forms have semantics. The
probe vectors that test them: 318 match the hardware, 64 stop unsupported, 0 mismatch
(`pds-alu-abs-not` 16/0/0, `pds-alu-abs-signed` 24/0/0, `pds-alu-after-abs` 12/0/0,
`pds-alu-after-not` 4/0/0, `pds-alu-flags` 6/0/0, `pds-alu-flags-signed` 6/0/0,
`pds-alu-specials-paths2` 0/4/0, `pds-encoding-bits-followup-mov128` 70/0/0,
`pds-encoding-bits-mov128-dst` 24/0/0, `pds-fetch-pc-kinds` 0/6/0, `pds-mov128-bit15-companions`
120/6/0, `pds-mov128-bit15-markers2` 30/0/0, `pds-mov128-bit15-mr` 6/48/0); unsupported mostly for
the port is open (54); reads dsN[N] before the program writes it (6); scratch[NxN] is computed from
a near value (4).

Confirmed on the hardware (a passing vector): #10, #11, #12, #13.

### 6.7 Shifts: `shl`, `shr`

Opcodes 30 and 31 **[RE]**: `shl dst, src, n` and `shr dst, src, n` with a source from `ds0`,
`ds1`, `ir0` or `ir1` (and, at 130, which the decoder does not name, `tim` **[HW]**) and a
seven-bit amount, which the decoder prints as a signed number widened to 32 bits (so the field
125 prints `4294967293`).

- **Semantics.** `shl` shifts left **[HW]**: our pixel-event program places the tile position with
  `shl` by 3 and the end-of-render bit with `shl` by 20. The amount is the field taken unsigned:
  32-127 give 0, whatever the decoder prints **[HW]**. `shr` is logical, and arithmetic under
  `alum signed`, where 32-127 fill with the sign **[HW]**.

From `asm/transfer/pds_pixevent.s`:

```
        shl ds1[48], ir0, 3
        shl ds1[48], ir0, 3
        shl ds1[48], ir1, 20
```

Forms (generated from the decoder's table; `<name>` is a field):

```
#25   opcode 30      mask F8000000  value F0000000  shl
      <pred>shl <dst>, <src>, <n>
#26   opcode 31      mask F8000000  value F8000000  shr
      <pred>shr <dst>, <src>, <n>
```

Mnemonics: `shl`, `shr`.

Layout (forms #25, #26):

```
 31   27 26  24 23 16 15  14 8 7   6   0
+-------+------+-----+---+----+---+-----+
| 1111? | pred | src | - | n  | - | dst |
+-------+------+-----+---+----+---+-----+
```

- `pred`: bits 26:24. Values: 0-2 `(p0)`…`(p2)`, 3 `(if0)`, 4 `(if1)`, 5 `(aluz)`, 6 `(alun)`, 7
  (none).
- `dst`: bits 6:0. A register operand, v = bank·128 + number (the bank bits may carry modifiers). By
  bank: 0 `ds0[0]`…`ds1[63]`.
- `src`: bits 23:16. A register operand, v = bank·128 + number (the bank bits may carry modifiers).
  By bank: 0 `ds0[0]`…`ds1[63]`, 1 `ir0`.
- `n`: bits 14:8. Values: 0-63 `0`…`63`, 64-127 `4294967232`…`4294967295`.

Simulator (`crates/sgx-sim`, from `doc/isa/sim-coverage.json`): 2 of 2 forms have semantics. The
probe vectors that test them: 90 match the hardware, 5 stop unsupported, 0 mismatch
(`pds-alu-after-shl` 4/0/0, `pds-alu-after-shr` 12/0/0, `pds-alu-alum-shr` 4/0/0, `pds-alu-ashr-big`
10/0/0, `pds-alu-flags` 6/0/0, `pds-alu-flags-signed` 6/0/0, `pds-alu-shifts` 48/0/0,
`pds-alu-specials-paths2` 0/2/0, `pds-fetch-pc-kinds` 0/3/0); unsupported mostly for reads dsN[N]
before the program writes it (3); scratch[NxN] is computed from a near value (2).

Confirmed on the hardware (a passing vector): #25, #26.

### 6.8 Tests: `tstz`, `tstn`

Opcodes 16 and 17 **[RE]**: `tstz pN, src` and `tstn pN, src` set predicate `p0`-`p2`
(`w[2:0]`; other values print an empty predicate) from a source that is `ds1[n]` (`w[8]` set)
or `ds0`, `ir0`, `ir1`. The test itself can be predicated.

- **Semantics.** `tstz` sets `pN` when the source is zero **[CAP/HW]** (*Predicates*); `tstn`
  when bit 31 is set **[HW]**; a predicated test obeys its predicate **[HW]**.
- **In the microkernel's programs [CAP].** The event program runs ten `tstz` (some of them
  predicated, some on `ir0` directly) and branches past the cases that do not apply, as our
  pixel-event program does; the deferred-work program picks its task with two. Neither uses
  `tstn`.

From `asm/transfer/pds_pixevent.s`:

```
        tstz p0, ds1[48]
        tstz p0, ds1[48]
        tstz p0, ds1[48]
        tstz p0, ds1[48]
```

Forms (generated from the decoder's table; `<name>` is a field):

```
#15   opcode 16      mask F8000100  value 80000100  tstz
      <pred>tstz <pdst>, ds1[<idx>]
#16   opcode 16      mask F8000100  value 80000000  tstz
      <pred>tstz <pdst>, <src>
#17   opcode 17      mask F8000100  value 88000100  tstn
      <pred>tstn <pdst>, ds1[<idx>]
#18   opcode 17      mask F8000100  value 88000000  tstn
      <pred>tstn <pdst>, <src>
```

Mnemonics: `tstn`, `tstz`.

Layout 1 of 2 (forms #15, #17):

```
 31   27 26  24 23 16 15 10 9   8   7 3 2    0
+-------+------+-----+-----+---+---+---+------+
| 1000? | pred |  -  | idx | - | 1 | - | pdst |
+-------+------+-----+-----+---+---+---+------+
```

- `pred`: bits 26:24. Values: 0-2 `(p0)`…`(p2)`, 3 `(if0)`, 4 `(if1)`, 5 `(aluz)`, 6 `(alun)`, 7
  (none).
- `pdst`: bits 2:0. Values: 0-2 `p0`…`p2`, 3 (none), 4 (none), 5 (none), 6 (none), 7 (none).
- `idx`: bits 15:10. A 6-bit number, printed in decimal.

Layout 2 of 2 (forms #16, #18):

```
 31   27 26  24 23 17 16 9 8   7 3 2    0
+-------+------+-----+----+---+---+------+
| 1000? | pred | src | -  | 0 | - | pdst |
+-------+------+-----+----+---+---+------+
```

- `pred`: as in layout 1.
- `pdst`: as in layout 1.
- `src`: bits 23:17. A register operand, v = bank·128 + number (the bank bits may carry modifiers).
  By bank: 0 `ds0[0]`.

Simulator (`crates/sgx-sim`, from `doc/isa/sim-coverage.json`): 4 of 4 forms have semantics. The
probe vectors that test them: 126 match the hardware (4 with near values, each within the bound the
hardware was measured to), 9 stop unsupported, 0 mismatch (`pds-alu-after-tstn` 12/0/0,
`pds-alu-after-tstz` 4/0/0, `pds-alu-flags` 6/0/0, `pds-alu-loop` 6/0/0, `pds-alu-specials-paths2`
0/2/0, `pds-alu-tst` 30/0/0, `pds-encoding-bits-tstn` 14/0/0, `pds-encoding-bits-tstn-ds1` 15/0/0,
`pds-encoding-bits-tstz` 14/0/0, `pds-encoding-bits-tstz-ds1` 15/0/0, `pds-fetch-pc-kinds` 0/3/0,
`pds-moves-mov-flag-cond` 0/4/0, `pds-moves-mov-flag-pipes` 8/0/0, `pds-moves-mov-pc` 2/0/0);
unsupported mostly for (aluz) before it is known (4); reads dsN[N] before the program writes it (3);
scratch[NxN] is computed from a near value (2).

Confirmed on the hardware (a passing vector): #15, #16, #18; not yet confirmed (as decoded; no
passing vector yet): #17.

### 6.9 Flow control: `bra`, `call`, `rtn`, `halt`, `nop`

Opcodes 18-22 **[RE]**: `bra` and `call` take a 24-bit target (bits 23:0: a target with any
of bits 19-23 set sent the fetch 2 MiB and more past the program, where the job faulted, E260)
**[HW]**, `rtn` and `halt` none, `nop` has no predicate.

- **`bra`** jumps to an instruction index counted from the first instruction after the data
  segment **[RE/CAP]**: the captured programs' control flow only makes sense that way, and our
  pixel-event program, assembled with labels on that basis, works **[HW]**.
- **`halt`** ends the program **[HW]**: every program of ours ends with it.
- **`call`** and **`rtn`**: one return register, not a stack: a nested call's return loops
  **[HW]**. Neither is used by our programs.
- **`nop`** takes one instruction slot and does nothing else: the fetch pc reads one more after
  each (E261), and none of its 27 other bits changed a result (E260) **[HW]**.

From `asm/transfer/pds_pixevent.s`:

```
        (p0) bra not_ptoff
        halt
        (p0) bra not_eot
        (p0) bra eor
        halt
        (p0) bra done
        halt
```

Forms (generated from the decoder's table; `<name>` is a field):

```
#19   opcode 18      mask F8000000  value 90000000  bra
      <pred>bra <imm>
#20   opcode 19      mask F8000000  value 98000000  call
      <pred>call <imm>
#21   opcode 20      mask F8000000  value A0000000  rtn
      <pred>rtn
#22   opcode 21      mask F8000000  value A8000000  halt
      <pred>halt
#23   opcode 22      mask F8000000  value B0000000  nop
      nop
```

Mnemonics: `bra`, `call`, `halt`, `nop`, `rtn`.

Layout 1 of 3 (forms #19, #20):

```
 31   27 26  24 23  0
+-------+------+-----+
| 1001? | pred | imm |
+-------+------+-----+
```

- `pred`: bits 26:24. Values: 0-2 `(p0)`…`(p2)`, 3 `(if0)`, 4 `(if1)`, 5 `(aluz)`, 6 `(alun)`, 7
  (none).
- `imm`: bits 23:0. A 24-bit number, printed in hex.

Layout 2 of 3 (forms #21, #22):

```
 31   27 26  24 23 0
+-------+------+----+
| 1010? | pred | -  |
+-------+------+----+
```

- `pred`: as in layout 1.

Layout 3 of 3 (form #23):

```
 31   27 26 0
+-------+----+
| 10110 | -  |
+-------+----+
```


Simulator (`crates/sgx-sim`, from `doc/isa/sim-coverage.json`): 5 of 5 forms have semantics. The
probe vectors that test them: 183 match the hardware (30 with near values, each within the bound the
hardware was measured to), 5 stop unsupported, 0 mismatch (`pds-alu-banks` 4/0/0, `pds-alu-call`
42/0/0, `pds-alu-loop` 6/0/0, `pds-alu-readback` 4/0/0, `pds-encoding-bits-flow-call` 12/0/0,
`pds-encoding-bits-flow-halt` 25/0/0, `pds-encoding-bits-flow-rtn` 50/0/0, `pds-encoding-bits-movs`
2/0/0, `pds-encoding-bits-movsa` 0/2/0, `pds-fetch-pc-back-to-back` 9/0/0, `pds-fetch-pc-branches`
9/0/0, `pds-fetch-pc-kinds` 0/3/0, `pds-fetch-pc-nop-gaps` 6/0/0, `pds-memory-fence` 2/0/0,
`pds-moves-mov-flag-pipes` 8/0/0, `pds-moves-mov-pc` 4/0/0); unsupported mostly for reads dsN[N]
before the program writes it (3); movsa to Douta is open (2).

Confirmed on the hardware (a passing vector): #19, #20, #21, #23; not yet confirmed (as decoded; no
passing vector yet): #22.

### 6.10 Fences and ALU mode: `rfence`, `rwfence`, `alum`

Opcode 15 is a fence, `rfence` or `rwfence` by `w[0]`, without a predicate; opcode 23 is
`alum signed` or `alum unsigned` (`w[0]`) **[RE]**.

- **Fences [HW]** (E142, E143). Both make earlier `load`s land in their registers: a load's
  dwords appear only at a fence. On their own, or after loads only, both are harmless.
  `rwfence` after a `store` faults on page 0, whatever the store's size and with an `rfence`
  or eight `nop`s between; `rfence` does not, and `rwfence` before a `store` completes. After
  a job faults, `rwfence` faults on page 0 in the jobs after it, even with no `store`, until
  a job without it completes (E144). What the write half of `rwfence` waits for, and why that
  touches page 0, is **[open]**.
- **`alum` [infer].** By the name, a mode switch for the ALU's signedness. Neither the
  microkernel's programs nor ours use the fences or `alum`.

Forms (generated from the decoder's table; `<name>` is a field):

```
#14   opcode 15      mask F8000000  value 78000000  rfence rwfence
      <op>
#24   opcode 23      mask F8000000  value B8000000  alum
      <pred>alum <op>
```

Mnemonics: `alum`, `rfence`, `rwfence`.

Layout 1 of 2 (form #14):

```
 31   27 26 1 0
+-------+----+----+
| 01111 | -  | op |
+-------+----+----+
```

- `op`: bit 0. Values: 0 `rfence`, 1 `rwfence`.

Layout 2 of 2 (form #24):

```
 31   27 26  24 23 1 0
+-------+------+----+----+
| 10111 | pred | -  | op |
+-------+------+----+----+
```

- `pred`: bits 26:24. Values: 0-2 `(p0)`…`(p2)`, 3 `(if0)`, 4 `(if1)`, 5 `(aluz)`, 6 `(alun)`, 7
  (none).
- `op`: bit 0. Values: 0 `unsigned`, 1 `signed`.

Simulator (`crates/sgx-sim`, from `doc/isa/sim-coverage.json`): 2 of 2 forms have semantics. The
probe vectors that test them: 431 match the hardware (51 with near values: 3 each within the bound
the hardware was measured to, 48 with a value the task does not know, the timer, accepted as any
value of its width and so not checked), 13 stop unsupported, 0 mismatch (`pds-alu-abs-signed` 6/0/0,
`pds-alu-adc-carry` 8/0/0, `pds-alu-after-abs` 12/0/0, `pds-alu-after-adc` 8/0/0,
`pds-alu-after-alum` 4/0/0, `pds-alu-after-and` 4/0/0, `pds-alu-after-mov128` 4/0/0,
`pds-alu-after-mov16` 12/0/0, `pds-alu-after-mov32` 4/0/0, `pds-alu-after-mov64` 4/0/0,
`pds-alu-after-mul` 12/0/0, `pds-alu-after-nand` 12/0/0, `pds-alu-after-nop` 4/0/0,
`pds-alu-after-nor` 12/0/0, `pds-alu-after-not` 4/0/0, `pds-alu-after-or` 12/0/0,
`pds-alu-after-sbc` 8/0/0, `pds-alu-after-shl` 4/0/0, `pds-alu-after-shr` 12/0/0,
`pds-alu-after-tstn` 12/0/0, `pds-alu-after-tstz` 4/0/0, `pds-alu-after-xor` 4/0/0,
`pds-alu-alum-shr` 4/0/0, `pds-alu-alum-spare` 48/0/0, `pds-alu-ashr-big` 10/0/0,
`pds-alu-carry-movs` 4/0/0, `pds-alu-flags-alum` 4/0/0, `pds-alu-flags-mov128` 4/0/0,
`pds-alu-flags-mov64` 4/0/0, `pds-alu-flags-movs` 4/0/0, `pds-alu-flags-signed` 36/0/0,
`pds-alu-mul` 6/0/0, `pds-alu-signed-adc` 10/0/0, `pds-alu-signed-carry` 14/0/0,
`pds-encoding-bits-abs` 10/0/0, `pds-encoding-bits-abs-ds1` 11/1/0,
`pds-encoding-bits-followup-abs-ds1` 6/2/0, `pds-encoding-bits-memory-load` 2/0/0,
`pds-fetch-pc-kinds` 0/6/0, `pds-fetch-pc-load` 3/0/0, `pds-load-store-addressing` 1/0/0,
`pds-memory-fence` 6/0/0, `pds-memory-mem` 12/0/0, `pds-memory-mem2` 12/0/0, `pds-memory-mem3`
6/0/0, `pds-memory-mem4` 14/0/0, `pds-memory-mem5` 6/0/0, `pds-memory-mem6` 10/0/0,
`pds-moves-index-mul` 14/2/0, `pds-moves-mov-flag-cond` 0/2/0, `pds-moves-mov-flag-flags` 2/0/0,
`pds-store-totals-runs` 2/0/0); unsupported mostly for reads dsN[N] before the program writes it
(9); (pN) before it is known (2); scratch[NxN] is computed from a near value (2).

Confirmed on the hardware (a passing vector): #14, #24.

## 7. Open questions

1. **The ports** `doutc`, `douts`, `slc`, `mr` and `ir0` as destinations, and `movsa` on ports other
   than `doutd`: what they do (*Hardware probes* lists what was seen). `tim` loads the counter the
   ALU reads, `EVENT_TIMER` (its first word, bits 24-0, bit 24 the run bit; settled); whether and
   why an enabled small count hangs the job, seen only in runs by hand with no record, is open
   (Q057). In a primary pixel program `doutc` faults the job and `mr`, `slc`, `douts` and `ir0`
   change nothing seen (E264); `mr01`/`mr23` read 0 after a `movs mr`.
2. **`if0`/`if1`** in pixel programs: neither tests true in any pixel of the primary pixel
   program nor on any tile of the pixel-event program (E262, E263), so Rogue's pixel readings
   (end of tile, end of render) do not hold there; whether anything sets them outside a vertex
   program is open (Q058); with the triangle drawn twice and five times over itself neither tests
   true on any pixel either (E389). *(`adc`/`sbc` setting the flags: settled, they do.)*
3. **`load`/`store`**: why stores totalling 2-4 dwords fault, and why `rwfence` after a store
   (or after a faulted job) touches page 0 (their timing and the fences: E143; which
   programs fault: E144) (Q025). Totals of 11, 13, 14, 15 and 17 dwords complete (one total-11
   run in three faulted), 1 and 10 complete in five runs each, and 2 faults with an `rfence`
   between the stores too (E395).
4. **`mr01`/`mr23`** read 0 in a fill, the primary pixel and the pixel-event programs; `ir1` reads 0
   in the primary pixel program and the event bits in the pixel-event program by every path,
   `mov32`'s `ir1.0` included; a test's source 65 tests zero exactly where `ir0` is 0, so that it
   reads `ir0` **[infer]** (E262, E263; `tstn` of it unmeasured). Open: the vertex-side programs
   (Q060); a `douta` from the vertex program does not reach the vertex task's `sa`, so that route
   does not read them (E390). *(settled: the numbering, selector and bit 9; selector 2 is the fetch
   pc; `ir0` in a fill is the tile position; 8.9, 8.11.)*
5. *(settled: the ALU details, `mov128` and `swap`.)*
6. *(settled: one return register.)*
7. *(settled: bits 21:20 of the word are address bits, so the 18 PC bits reach bit 21 (a word with
   only bit 21 set starts a program 1 MiB up), and `CBASE` adds multiples of 512 KiB (8 starts
   one 4 MiB up); E428.)*

8. *(settled: `nop` takes one slot and reads none of its other bits, E260, E261.)*
9. **The specials in a `movs`**, mostly settled: `.l` passes a whole word and `ir0.l` is all of
   `ir0` (*Hardware probes*); in the microkernel's event program `ir1.l` reads what the ALU reads as
   `ir1`, since its fast paths depend on it, and `tim.l` goes to a word the firmware never reads. In
   our pixel-event program `ir1.l` reads what the ALU's `ir1` does, the event bits, and `.h` reads 0
   for `ir0`, `ir1` and `tim` (*Hardware probes*), on every tile of a 128x128 render too, `ir2.l` 0
   there and `ir2.h` 0 on a one-tile render (E263). Still open: `.h` in the vertex-side programs
   (Q060).
10. *(settled: the flags and the carry after every instruction.)*
11. *(settled: a `mov16` into a read-only row keeps its temporary's other half.)*
12. **Bit 9 of the `mov16`/`mov32` specials (`.1`)** on the rest of the family: on SGX545 it
    only makes `mov16` read 0 (8.11). The other pipe's registers (SGX545 alone has two PDS
    pipes), another core's, or 64-bit specials are the readings left **[infer]**. A one-pipe
    core (SGX540 on a PandaBoard, SGX530 on an N950) shows whether its special fields run at
    stride 1, the bit then new with the second pipe; an MP part (SGX544MP2) tests the cores
    (Q063).
13. **The fetch pc's offset**: `pc.0` reads the index plus 3, or 1 or 2 below it (E261). Back
    to back the lag sits at instructions 26-27 in ten of twelve runs whatever the `nop`s before,
    dwords 62-63 after the 36-dword data segment, the last two before a 64-dword boundary; with 1
    to 4 leading instructions more a pair sits at instructions 24-25 (dwords 60-61) in 14 of 20
    runs and among the first four reads in 19 (E384) **[infer]** for the place. The back-to-back
    baseline varies: E384's five runs with no leading words put the pair at 26-27 in two, at
    19-20 in two and nowhere in one, so the ten of twelve above stands as E261 counted it and was
    not repeated. What sets it, a model of the PDS fetch, is open (Q062).
14. *(settled: `mov128`'s bit 15 writes the `ds0` pair the last `mov32` or `movs` read from a data
    row, E379.)*

## 8. Hardware probes

The questions of *Open questions* are put to the GPU by PDS probes: our own PDS program runs
as the PDS secondary program of a client fill, copies its preset data words to the
temporaries, does the operation under test there and passes the results to the fill's shader
`sa_dump.s` with `douta` (into `sa0`-`sa15`), which stores them where the host reads them
(the probe runner and the tables under `probes/pds/` of the data repository, each probe
listing the readings it tests). The first,
`pds-alu-readback`, checks that path itself. Each fact
is one snippet in `doc/isa/content/pds/probe/`, measured on 2026-10-24; the vectors are in the data
repository's
`vectors/` directory, one set per series of probes:

- §8.1 Data rows, and the banks past the data segment **[HW]**
- §8.2 Bitwise ops, `add` and `sub` **[HW]**
- §8.3 `aluz`, `alun`, `tstn` and predicated tests **[HW]**
- §8.4 Shift amounts and the `shr` fill **[HW]**
- §8.5 `mul` signedness and the `adc`/`sbc` carry **[HW]**
- §8.6 `abs` and `not` **[HW]**
- §8.7 `mov16`, `mov64`, `mov128` and `swap` **[HW]**
- §8.8 Loops, `call` and `rtn` **[HW]**
- §8.9 `ir0`-`ir2`, `tim` and `pc` as sources **[HW]**
- §8.10 `load`, `store`, the fences and the other ports **[HW]**
- §8.11 Bit 9 of the `mov16`/`mov32` specials, the fetch pc, `ir0` and the two PDS pipes **[HW]**
- §8.12 The pixel-event program's inputs and its attribute room **[HW]**
- §8.13 Encoding bits no field maps **[HW]**
- §8.14 The fetch pc, read everywhere **[HW]**
- §8.15 The inputs of the primary pixel and pixel-event programs **[HW]**

### 8.1 Data rows, and the banks past the data segment

*Measured on the hardware (2026-10-24).* Sixteen data words come back unchanged through `douta`
(`pds-alu-readback`), and different words in the two banks follow the row rule for every dword of
the
segment (`pds-alu-banks`) **[HW]**. The rows `ds0[0..47]`, `ds1[0..47]` are read-only: a write to
`dsB[n]` lands in the temporary `dsB[48 + (n & 15)]`, so each bank has sixteen writable registers,
`dsB[48..63]`, and the destination's low four bits pick one (`pds-alu-constants`: a write to
`ds1[1]`
appears in `ds1[49]`, one to `ds0[36]` in `ds0[52]`, one to `ds1[19]` in `ds1[51]`) **[HW]**. Past
the data segment the read-only rows hold what earlier tasks left, not zeros. The temporaries are not
cleared between runs: `pds-alu-uninit` read `ds0[60]` and `ds1[60]` as the value an earlier run of
the
same probe had written there **[HW]**.

### 8.2 Bitwise ops, `add` and `sub`

*Measured on the hardware (2026-10-24).* `xor`, `nor`, `nand`, `and` and `or` are as named, on 32
bits (`pds-alu-bitwise`), and `add` and `sub` are modular with `dst = src - ds1[n]`
(`pds-alu-add-sub`)
**[HW]**.

### 8.3 `aluz`, `alun`, `tstn` and predicated tests

*Measured on the hardware (2026-10-24).* `add`, `sub`, `adc`, `sbc` and `mul` set the flags from
their result; `and`, `xor`, `shl`, `not`, `mov32` and `tstz` (`pds-alu-flags`), and `or`, `nor`,
`nand`,
`shr`, `abs`, `mov16` and `tstn` (`pds-after-*`, in both `alum` modes), and `mov64`, `mov128`,
`alum` and a `movs` (`pds-flags-*`) leave them **[HW]**. `aluz` is a zero result. `alun` is a
negative result, but only under `alum signed`: in the default unsigned mode it never tests true,
even after a result with bit 31 set (`pds-alu-flags`, `pds-alu-flags-signed`) **[HW]**. `tstn` sets
its
predicate from bit 31, and a predicated test obeys its predicate (`pds-alu-tst`) **[HW]**. In a
fill's
secondary program neither `if0` nor `if1` tests true (`pds-alu-if`, recorded) **[HW]**; what they
mean
in a primary program, whose results `douta` cannot pass on, is still open.

### 8.4 Shift amounts and the `shr` fill

*Measured on the hardware (2026-10-24).* The amount is the seven-bit field taken unsigned: 0-31
shift, 32-127 (which includes what the assembler writes for a negative amount) give 0; `shr` is
logical (`pds-alu-shifts`), and arithmetic under `alum signed` (`pds-alu-alum-shr`) **[HW]**, where
32-127
fill the result with the sign bit (`pds-alu-ashr-big`) **[HW]**.

### 8.5 `mul` signedness and the `adc`/`sbc` carry

*Measured on the hardware (2026-10-24).* `mul` multiplies its halves unsigned, and signed under
`alum signed` (`pds-alu-mul`) **[HW]**. `add` and `sub` leave the high dword of their exact result:
+1
after a carry out, -1 after a borrow, 0 otherwise; `adc` adds it (`a + b + c`) and so does `sbc` (`a
- b + c`), which is what chains a multiword add or subtract (`pds-alu-adc-sbc`) **[HW]**. Every
  other
instruction tried keeps that carry for a later `adc`: `and`, `or`, `xor`, `nor`, `nand`, `shl`,
`shr`, `not`, `abs`, `mul`, `mov16`, `mov32`, `mov64`, `mov128`, `tstz`, `tstn`, `alum` and
`nop` (`pds-after-*`, the carry measured in the default unsigned mode) **[HW]**. `adc` and
`sbc` leave the high dword of their own exact result, as `add` and `sub` do, so the carry chains
through a multiword add (`pds-alu-adc-carry`, unsigned) **[HW]**. Under `alum signed` the carry of
`add` and `sub` is the signed overflow: the `c` for which the exact sum is `signed(r) + c × 2³²`,
so `0x7fffffff + 1` carries +1, `0x80000000 - 1` -1 and `-1 + 1` nothing; read unsigned, the same
rule is the unsigned rule (`pds-alu-signed-carry`; the reading was fitted to its first four cases
and confirmed by three more) **[HW]**; `adc` and `sbc` leave the same signed overflow of their
own result (`pds-alu-signed-adc`) **[HW]**. A port write keeps the carry too (`pds-alu-carry-movs`)
**[HW]**.

### 8.6 `abs` and `not`

*Measured on the hardware (2026-10-24).* `not` is the bitwise complement from both source forms
(`pds-alu-abs-not`) **[HW]**. `abs` is the identity in the default unsigned mode (`pds-alu-abs-not`:
`abs(-5)` is `-5`), and the two's complement absolute value under `alum signed`, with
`abs(0x80000000)` itself (`pds-alu-abs-signed`), from both source forms **[HW]**.

### 8.7 `mov16`, `mov64`, `mov128` and `swap`

*Measured on the hardware (2026-10-24).* `mov16`'s destination index names a 16-bit half: `dsB[n]`
is the high half of `dsB[n >> 1]` when `n` is odd, the low half when even, and the other half is
kept (`pds-moves-mov16`) **[HW]**. `mov64` moves an aligned pair across the banks as named; `mov128
ds[2k]` is the row `ds0[2k]`, `ds0[2k+1]`, `ds1[2k]`, `ds1[2k+1]`, and `swap` exchanges its two
pairs (`pds-moves-mov-wide`) **[HW]**. A `mov16` into a half of a read-only row `dsB[0..47]` lands,
as any write there, in the temporary `dsB[48 + ((n >> 1) & 15)]`, whose other half is kept: the
constant row's other half plays no part (`pds-moves-mov16-constants`, rows inside and past the data
segment) **[HW]**.

### 8.8 Loops, `call` and `rtn`

*Measured on the hardware (2026-10-24).* `bra` goes to the label's instruction index both ways, and
predicated (`pds-alu-loop`) **[HW]**. There is one return register, not a stack: a single
`call`/`rtn`
returns, a nested one loops and the job fails (`pds-alu-call`) **[HW]**.

### 8.9 `ir0`-`ir2`, `tim` and `pc` as sources

*Spelling.* This section was measured with the earlier names of the
`mov16`/`mov32` special sources, which the probes' program texts and the published vectors
keep (their words are the record). The tools now spell them by
selector and bit 9 (*Input and special registers*):

| field (mov32; mov16 is twice it, plus the half) | earlier name | spelled now | reads (SGX545) |
|---|---|---|---|
| 128 | `ir0` | `ir0.0` | `ir0` |
| 129 | `ir1` | `ir0.1` | `ir0` (mov32), 0 (mov16) |
| 130 | `pc` | `ir1.0` | the ALU's `ir1`, 0 in a fill (E262, E263) |
| 131 | `tim` | `ir1.1` | 0 |
| 132 | `ir2` | `pc.0` | the fetch pc |
| 133 | (none) | `pc.1` | as `pc.0` (mov32), 0 (mov16) |
| 134 | (none) | `tim.0` | `EVENT_TIMER` |
| 135 | (none) | `tim.1` | the timer (mov32), 0 (mov16) |
| 136-255 | (none) | (undecoded) | 0 |

*Measured on the hardware (2026-10-24).* In a 64x32 fill's secondary program, `mov32` reads `ir0`
and `ir1` equal, `0x402` or `0x403`, and `ir2` from `0x15` to `0x1f`, varying from run to run;
`tim` and `pc` read 0, twice each (`pds-alu-inputs`, `pds-alu-specials`, recorded) **[HW]**. What
the
values mean is still open.

As `movs` sources (`pds-alu-specials`, recorded) the four specials are pairs of words, as a `ds0`
pair is: `.l` passes a whole 32-bit word and `.h` read 0 for all four, whatever the other
slots hold **[HW]**. Special 0 (`ir0.l`) is `ir0`, equal to the `mov32` copy in every run.
The others do not read what `mov32` reads under the same reference names: `ir1.l` and `ir2.l`
read 0, and `tim.l` a 32-bit down-counter (`0x0100_0000`-`0x0105_0000` at the start of the
program, different each run) that drops by 1 between back-to-back `movs` and by nearly the same
amounts across runs after the same `nop` gaps (3-6, 4-17, 7, 11-23, 31-40, 58-59 and 115-117
across 0, 1, 2, 4, 8, 16, 32 and 64 `nop`s, through `movs` and the ALU alike) **[HW]**: core
clocks, since the counter is `EVENT_TIMER` (*Input and special registers*) **[GPL]**.

The datapaths number the specials two ways (`pds-alu-specials-paths`, recorded) **[HW]**. The ALU's
first source, `mul`'s halves and `movs` agree: `ir0` is the input word, `ir1` reads 0 and `tim` is
the down-counter (`or ds0[n], tim, ...` reads it whole, `mul` with `tim.l`/`tim.h` its 16-bit
halves). `mov32` and `mov16`, with `pc` inserted in their numbering, read only `ir0` the same: their
`ir1` reads what `ir0` does, their `pc` and `tim` read 0 (`mov16` of `tim.l`/`tim.h` and `pc.l`
too), and their `ir2` the varying `0x15`-`0x1f`. `shl` and `abs` read `ir0` and `ir1` as the ALU
does (`ir1` 0), `not tim` the counter's complement; `tstz` of `ir1` tests nonzero, unlike the ALU's
`ir1` (it tests zero where `ir0` is 0, E262, so that it reads `ir0` **[infer]**), and `mov16` reads
`ir1.l` as 0 where `mov32` reads `ir1` as `ir0`'s value (`pds-alu-specials-paths2`, recorded)
**[HW]**.

Every special index of the source fields, swept with hand-encoded words (`pds-x-index-*`,
recorded; none hung) **[HW]**. The ALU's first source reads `ir0`, `ir1` (0 here) and the counter
at 64-66 and 0 above; `shl` reaches the counter too, at 130 after `ir0` and `ir1`, which the
decoder does not name; `mul`'s halves follow the ALU (`ir0`, `ir1`, the counter). `mov32` and
`mov16` number them their own way: special 0 is `ir0`, 2 reads 0, 4 a small count near the
instruction's own index (two `mov32`s in a row at instructions 20 and 21 read 23 and 24; what
the reference calls `ir2`), 6 the counter (which the reference does not name), and 8 and up 0;
`mov32` ignores the index's low bit (its `ir1` is `ir0` again), while `mov16` reads 0 at every
odd one. So of the reference's names for these fields only `ir0` matches the hardware: the
fields hold the reference's list in its order at every other index, the low bit (the word's
bit 9) apart, which is how the tools spell them now. The count is the fetch pc (8.11)
**[HW]**.

A `movs tim` loads the counter and stops it: the value written reads back unchanged through 64
`nop`s, and in every later job, of any client, until the GPU is reset; after a reboot it counts
again (`pds-timer-tim-count`, recorded) **[HW]**. Between probes, by hand through debugfs: the
driver's in-place reset (`sgx/reset`: halt, soft reset, firmware boot) restarts it, from
`0x0102_0000`-`0x0105_0000` as after power-on, while a POWER IDLE through the CCB (`sgx/idle`)
leaves it reading 0, in that job and the next ones, until a reset **[HW]**. The first word
printed (`movs tim, a, b, c, d`: `a`) loads it and the others do nothing; it keeps the word's
bits 24-0 (`pds-timer-tim-words`; the 25-bit reading was fitted to its first run and confirmed by a
case added for it) **[HW]**. Bit 24 is a run bit: a value with it set counts down from the
value less one, one with it clear stays where it was put; the counter that resets and power-on
leave has it set (`0x0102_0000`-`0x0105_0000`) **[HW]**. In runs by hand that no table or record
holds, an enabled count that reaches 0 hung the job: loads of `0x0100_0002`, `0x0100_0020` and
`0x0100_0040` each lost their job to the driver's recovery (Q057 asks for the recorded run). The
counter is the microkernel's tick timer, `EVENT_TIMER`
(GPL DDK, *Input and special registers*), so a probe that writes it stops or speeds up the
firmware's tick. It is not a PDS watchdog.

### 8.10 `load`, `store`, the fences and the other ports

*Measured on the hardware (2026-10-24).* From the table `probes/pds/load-store.toml`
(recorded). `load` and `store` address the
program's GPU address space from 0: the field is the byte address divided by 4, so they reach the
first 1 MiB, and a fill client has nothing mapped there; every case faulted on the page it named (0,
`0x1000`, `0x10000`), with `BIF_INT_STAT` requestor bit 13, the PDS's own, set
(`pds-load-store-addressing`)
**[HW]**. Their timing and the fences need a mapping there. A `movs` to `mr` leaves `mr01`/`mr23`
reading 0, to `tim` leaves it reading 0, to `ir0` does not change it; `slc` and `douts` show
nothing; after `doutc` the fill's USE task faults storing to page 0 (`pds-load-store-ports`)
**[HW]**. The
`doutu` `EXE` width (*Open questions* 7) needs USE code above 512 KiB of its heap, which the driver
cannot place yet.

### 8.11 Bit 9 of the `mov16`/`mov32` specials, the fetch pc, `ir0` and the two PDS pipes

*Measured on the hardware (2026-10-25; the table `probes/pds/moves.toml`, recorded runs).* What bit
9 of the special index (`.1`) does, each reading
put to the hardware in turn **[HW]**:

- **It writes a 16-bit 0, nothing else.** A `.1` `mov16` into one half of a marked temporary
  leaves the other half's mark (`pds-moves-mov-flag-write`): no extension, swap, packing or
  saturation; `tim.1` gives 0 where `tim.0` gives the counter (`0x0102c45a`), so not another
  16-bit select either.
- **No condition and no side effect.** It reads 0 after setups that set `aluz`, `alun`, the
  carry, a borrow, or `p0`-`p2` true or false (`pds-moves-mov-flag-cond`); it leaves the flags and
  the carry (`pds-moves-mov-flag-flags`); the register it reads is unchanged before and after
  (`pds-moves-mov-flag-side`).
- **Not `if0`/`if1`.** In a vertex program, a kick under "a `.1` `mov16` of `pc.l` is
  nonzero" never starts a vertex (the render hangs with nothing stored), where the plain
  `pc.0.l` kicks every vertex (`pds-vertex-programs-flag-pc`, `-plain-pc`, `-zero`); `if0` holds on
  the
  last vertex (`pds-vertex-programs-if0`).
- **`mov32` has no other select.** Its unused bits (0, 8, 23-17) and `alum`'s (23-1) change
  no read (`pds-moves-mov32-spare`, `pds-alu-alum-spare`); `mov64`'s sources 64-127 read 0
  (`pds-moves-index-mov64`).
- **Not the other pipe's live registers, in a fill.** SGX545 has two PDS pipes
  (`SGX_FEATURE_NUM_PDS_PIPES`, the `PDS0`/`PDS1` clock gates, GPL DDK), and runs two PDS
  programs at once: the same four-instruction loop runs in aggregate at 3.14 ns an instruction
  over a fill's 8 tiles and at 6.28 over a triangle's 3 vertices, which fits tiles two at a
  time and vertices one at a time (predicted time ratio 1.50, measured 1.497). With every tile
  sampling a `.1` `mov16` of `pc`, `ir0` and `tim` 50000 times while two of them ran, every
  sample was 0 (`pds-moves-mov-flag-pipes` lengthened). (Timed by hand: `CLKGATESTATUS` polled
  read-only through `/dev/mem`; `PDS0` and `PDS1` gate together,
  so the status bits do not tell the pipes apart.)

So on SGX545 the bit has no observable meaning beyond "`mov16` reads 0". It is kept apart
in the spelling (`.0`/`.1`) because it likely means more elsewhere **[infer]**: the other
pipe's registers (SGX545 is the only core in the DDK with two PDS pipes, so the bit may have
come with the second one), another core's on the MP parts, or 64-bit specials. The one-pipe
cores can test the first: if their special fields run at stride 1, as the reference
disassembler numbers them, the bit arrived with SGX545's second pipe (*Open questions*).

The other results of the round **[HW]**:

- `pc.0` is the fetch pc: the reading instruction's index plus 3 back to back and after
  `mul`s, plus 1 or 2 at some places (instructions 26-27 here, and after some `nop` gaps), and
  the same on both passes of a loop (`pds-moves-mov-pc`).
- `ir0` in a fill's secondary program is the tile position `tile_y << 10 | tile_x` for 16 x 16
  tiles: 0-3 on the top row of the 64 x 32 fill, `0x400`-`0x403` on the bottom
  (`pds-moves-mov-flag-pipes`, per pixel). The `0x402`/`0x403` of the earlier rounds was whichever
  bottom-right tile stored its readback last.
- In a vertex program, `(if1)` and `(if0)` kicks together, a kick on every vertex and a kick
  only where `if0` is false each hang the render; an `(if1)` kick alone works as `(if0)` does,
  one task of the three vertices (`probes/pds/vertex-programs.toml`).

### 8.12 The pixel-event program's inputs and its attribute room

*Measured on the hardware (2026-10-27; the triangle probes of
`probes/pds/pixel-event.toml`, recorded runs).* The probe replaces the
triangle's pixel-event program with `pixev_dump.s` and passes what it reads to the end-of-tile
task with `douta` **[HW]**:

- **The attribute room.** `douta` reaches the task's `sa0`-`sa15` only when bits 2:0 of the
  render's pixel-event info word (`EVENT_PIXEL_PDS_INFO`, `cmd:20` of our render command, 1 in
  every closed capture) are zero: with any of them set (1, 2, 4, 0x101, 0x102, 0x104) the task
  reads the tile's colours there, with 0, 0x80, 0x100-0x8000 or 0x10000 it reads the values
  passed on (a one-tile render, poked through the kernel's `rd:25`). On the 128x128 render
  bits 3, 4 and 5 stop it as well (0x8, 0x10, 0x20: no tile's values arrive), and every value
  from 0x40 up with bits 5:0 clear delivers as 0 does: the gate is bits 5:0. With them set
  (1, on a one-tile render) no `douta` value is in `sa0`-`sa127`: they hold the pixels of the
  task's 16 x 8 block, in 2 x 2 quads taken in raster order across it, `sa(4q + i)` pixel `i`
  of quad `q` (top left, top right, bottom left, bottom right). All 128 match that order and no
  other tried (raster, column, 4 x 4 or 8 x 8 blocks, quads across the 32-pixel target). They
  are the tile buffer itself: an end-of-tile task that writes `sa0`-`sa3` before its emit
  changes pixels (0, 0), (1, 0), (0, 1), (1, 1) of every 16 x 8 block of the target, at (0, 0),
  (16, 0), (0, 8), (16, 8), with either info value. With bits 5:0 clear, `douta` writes into
  that buffer: the markers come out as pixels, `sa4`-`sa15` at x 2-7 of rows 0-1. So the
  gate picks where `douta` lands, the tile buffer or elsewhere; a 16 x 16 tile's event runs the
  task once for each 16 x 8 half. The probes write 0.
- **The primary attributes** (the `pa-dump` runs: the 16-marker program, the
  end-of-tile task storing `pa0`-`pa15` instead): with info 0 they hold the 16 markers in
  order, as `sa` does; with info 1, `pa0`-`pa3` hold markers 12-15 (the last four attributes)
  and `pa4` on other values; with info 4 nothing recognisable; with 0x10 the background
  colour throughout. So the info word moves where the passed attributes and the tile sit
  against `pa` and `sa`; no one offset fits the four readings: open.
- **A whole tile pass** (the `sa-tile` runs): an end-of-tile task that writes
  `0xa0000000 | k` into every `sak`, `k` 0-127, before its emit turns all 512 pixels of a
  32x16 target into exactly the values that order predicts. On larger targets it does not
  hold: on 64x64 (info 1) only the 32x16 tiles (0, 0) and (0, 2) come out written, the
  other six as the triangle renders them, the same in three runs (128x128: 3968 of 16384
  pixels); with info 0 the pixel-event program's markers land in the other tiles. Where those
  tiles' `sa` writes go is open.
  On a 128x128 render the same layout races: some tiles' tasks get colours in `sa15` (the
  fault address was the scratch base plus `0xff20 × 0x3040`), a different set each run. The
  per-tile store (`eot_tile.s`) now clamps its slot word to the buffer, so such a tile only
  loses its record: 34 or 35 of the 64 tiles come back per run, 41 in three runs.
- **Per tile** (`pds-pixel-event-pixev-grid16`, 128x128, 8 x 8 tiles of 16 x 16): on every tile read
  back
  `ir0` is `tile_y << 10 | tile_x`, as `ir0.l` and through the ALU, and `ir1` is 2 (the end of
  the tile), except on tiles (6, 7) and (7, 7), where it is 6: the last tile's bit comes with
  the last two 16 x 16 tiles, the bottom-right 32 x 16 pixels.
- **`ir0`, `ir1`, `tim` on a one-tile render**, twice alike: `ir0` is 0 (tile 0, 0) as `ir0.l`,
  through the ALU and through `mov32` `.0` and `.1`; `ir1` is 6 as `ir1.l` and through the ALU:
  bit 1, the end of the tile, and bit 2, the render's last tile (*Machine model*); `.h` reads 0
  for all three. `tim` reads `0x0104xxxx`, `ENABLE` and a count that falls through the program:
  the ALU's read first, a `movs` nine lower, a later `movs` another 0x74 lower. `mov32 pc.0`
  reads 0x1a.
- **Past bit 16** (`pds-pixel-event-pixev-tall`, 32x4096, two 16 x 16 tiles a row): of the 47
  records
  that come back whole (`ir1` 2 by both paths, `.h` 0), the 29 whose `ir0` passes bit 15
  (tile rows 66-127, `ir0` up to `0x1fc01`) read the same word as `ir0.l`, through the ALU and
  through `mov32` `.0` and `.1`: `.l` passes all of `ir0`. Rows from 128 share their slots
  with lower ones in that probe's layout, so none is read.
- **The plain task of `pds-pixel-event-readback`** (started with U1 0, no PBE) passes the 16
  markers, but
  every second run of it hangs: something it leaves is cleared only by the reset after a hang.
  Ending it with `ptoff.end` instead of `nop.end` changes nothing (hang, ok, hang, ok). It
  ends without the `.freep` emit that the end-of-tile tasks free their tile buffer with
  [infer: what it holds on to].

### 8.13 Encoding bits no field maps

*Measured on the hardware (2026-11-02; `probes/pds/encoding-bits*.toml`, written by
`tools/usse-asm/pds_bits.py`, recorded runs).* Before this round the 27 forms left 281 bits
neither identifying nor in a field. Each probe runs one form's base instruction as a fill's
secondary program and flips one such bit per case; a bit is read if the readback differs from
the base's, or the job fails (E259, E260) **[HW]**:

- **Read: 12 bits.** `bra` and `call` bits 19-23 are target bits: each flip sent the fetch
  `4 << k` bytes past the program (the fault addresses 0x2e200000 up to 0x30000000) and the job
  faulted, so the target is 24 bits (E260). `abs`'s `ds1[n]` form reads bit 15 as the sixth bit
  of `n`, as `not`'s does: `abs ds0[52], ds1[16]` with it set gives the absolute value of
  `ds1[48]` (E261). `mov128`'s bit 15 makes it write `ds0[8]`, `ds0[9]` (the data's row 4 `ds0`
  pair) to both halves of its destination, from every source row into `ds[52]`, and at four
  destinations from rows 2 and 31 and from row 2 with `swap` (E261): row 4's pair is the one the
  template's last `mov32` from a data row read, `ds0[9]`; the bit makes `mov128` write the `ds0`
  pair the last `mov32` or `movs` read from a data row (E379), and the tables name it `lastpair`.
- **Ignored: every other bit.** `movs`, `movsa` bit 4; `mov16` 23:17; `mov64` 23:17, 9:8, 1:0;
  `mov128` 23:16, 9, 7, 1:0; the ALU group 16, 9:7; `mul` 8:7; `abs` 23:16, 9, 7 and 16:9, 7;
  `not` 23:16, 9, 7 and 16:9, 7; `tstz`, `tstn` 23:16, 9, 7:3 and 16:9, 7:3; `shl`, `shr` 15,
  7; `load`, `store` 23; the fences 26:1; `rtn`, `halt` 23:0; `nop` 26:0, which also leaves the
  fetch pc as the plain `nop` does (E260, E261). `mov32`'s 23:17, 8, 0 and `alum`'s 23:1 were
  measured before (*`mov16`/`mov32` specials*, `pds-moves-mov32-spare`, `pds-alu-alum-spare`).

So 270 bits were unmapped after this round (bra and call 0, abs 10 where it had 11), and 269 of
them change nothing the probes can see; `mov128`'s bit 15 was the one read that no field described,
and 11.14 names it `lastpair`, which leaves 269 unmapped bits, none of them read.

### 8.14 The fetch pc, read everywhere

*Measured on the hardware (2026-11-02; `probes/pds/fetch-pc.toml`, recorded runs).* `pc.0` read
by `mov32` into a temporary of its own, 16 reads a program, each case three times (E261)
**[HW]**:

- **Back to back**, after 0-3 `nop`s: index + 3 at every read but two consecutive ones at
  index + 2, at instructions 26-27 in ten of twelve runs, whatever the `nop`s before, and at
  19-20 in two.
- **After 0-14 `nop`s** between reads, rising and falling: index + 3, with lags of one at a
  few reads, and + 1 once (the first read of a long program in one run). A `nop` takes one slot.
- **After each kind of instruction** (`mov16`, `mov64`, `mov128`, `add`, `mul`, `shl`, `not`,
  `abs`, `tstz`, `alum`, `rfence`, `rwfence`, `movs douta`, `mov32`, `bra` to the next):
  index + 3, + 2 after `add` and `mov32` in every run, and in one run also after `mov64` and
  `alum`, with + 1 at its first read.
- **Across branches and a call**, the three runs alike: + 2 at the first read, at the targets
  of branches over 1 and 3 `nop`s, in the called routine, after its return and at the target
  past it; + 3 at the target of a branch to the next instruction (the read after it + 2) and
  of one over 7 `nop`s (and the read after it).
- **After a load** with `nop`s instead of a fence, and after `rfence` and `rwfence`: + 1 to + 3.

No read was more than 3 or less than 1 ahead. Where the fetch falls behind is mostly a fixed place
in the program: the back-to-back lag stays at instructions 26-27 whatever the `nop`s before it,
which with the 36-dword data segment are dwords 62-63, the last two before a 64-dword boundary; the
branch program gives the same values in all three runs, and the `nop`-gap programs do but at their
first read and one read of one run. Some runs differ (two of twelve back to back, some first reads,
the third kinds run and the loads) **[infer]**.

With 1, 2, 3, 4 and 8 words of 0 (`(p0) movs mr, ds0[0], ...`) as the first instructions
(`probes/pds/fetch-pc-pad.toml`, five runs each, E384) **[HW]** every read is its index + 3, the
leading words counted, or 1 below at a pair of reads: for 1 to 4 leading words at instructions
24-25 (dwords 60-61) in 14 of 20 runs and among the first four of the sixteen reads in 19; with
none at 26-27 (two runs), 19-20 (two) or nowhere (one); with 8 at 35-36 in all five. The simulator
models `pc.0` as index + 3, matched by a hardware value up to 2 below (*Input and special
registers*; Q062).

### 8.15 The inputs of the primary pixel and pixel-event programs

*Measured on the hardware (2026-11-02; `probes/pds/task-inputs.toml`, recorded runs).*

- **The primary pixel program** (E262, E264) **[HW]**. `pds_iter_if.s` starts the triangle's shader
  with the iteration wait and then issues one iteration: of the coordinate set, or of the pixel's
  `x + 0.5` where the case's condition held, so every pixel shows the condition in the program that
  served it. On a 64x64 and a 128x128 triangle: `if0` and `if1` hold nowhere; `ir0` is 0 only on
  tile (0, 0); the ALU's `ir1`, `mov32`'s `ir1.0`, `mr01` and `mr23` read 0 on every pixel; `tim`
  and `pc.0` are never 0; `tstz` of `ir1` is true exactly where `ir0` is 0. Bit by bit, on the 64x64
  triangle only: `ir0` is the 16 x 16 tile's position `tile_y << 10 | tile_x` (bits 0, 1, 10 and 11
  follow the tile, all others are clear), and the ALU's `ir1` has bits 0-11 clear. `movs` to `mr`,
  `slc`, `douts` and `ir0` leave the image as the control's, `mr01` reading 0 and `ir0` the tile
  after them; `movs doutc` faults the job (BIF status 0xd0400, the address 0x0401f030).
- **The pixel-event program** (E263) **[HW]**. `pixev_dump.s` with the reads passed to the
  end-of-tile task, three runs each. On a one-tile render `ir1` reads 6 through the ALU, `shl`,
  `abs`, `mov32` (`ir1.0` and `ir1.1`) and `mov16`; `tstz` of `ir1` is true (`ir0` is 0); `if0`,
  `if1`, `mr01`, `mr23`, `ir2.l`, `ir2.h` and `tim.h` read 0 or false. Per tile of a 128x128 render
  (61 or 62 of 64 slots a run come back; slots 0 and 1 never): 18 to 24 slots a run hold a slot word
  that is not their own, mostly 2 above it, among them slot 61 (tile (5, 7)'s `ir0`, word 63) and
  slot 60 in one run, whose `ir1` reads disagree. On the 38 to 44 slots whose word names the tile of
  their `ir0`: `ir0.l` the tile, `ir1` by the ALU and by `mov32` (`ir1.0`, `ir1.1`) alike, 2, or 6
  on tiles (6, 7) and (7, 7); `if0`, `if1` false and `mr01`, `mr23`, `ir2.l`, `.h` of `ir0`, `ir1`
  and `tim` 0. Per tile only those were read.

## 9. Appendix: every instruction form

Every form of the assembler's PDS table (`tools/usse-asm/pds_forms.c`), which describes the
decoder's layouts, in table order within each opcode: its index, its identifying mask and
value, its mnemonics and its pattern with named fields.

**Opcode 0**

```
#0    opcode 0       mask F8000000  value 00000000  movs
      <pred>movs <dst>, <srcs>
```

**Opcode 5**

```
#1    opcode 5       mask F8000000  value 28000000  movsa
      <pred>movsa <dst>, <srcs>
```

**Opcode 1**

```
#2    opcode 1       mask F8000000  value 08000000  mov16
      <pred>mov16 ds<ds>[<idx>], <src>
```

**Opcode 2**

```
#3    opcode 2       mask F8000000  value 10000000  mov32
      <pred>mov32 ds<ds>[<idx>], <src>
```

**Opcode 3**

```
#4    opcode 3       mask F8000000  value 18000000  mov64
      <pred>mov64 ds<ds>[<idx>], <src>
```

**Opcode 4**

```
#5    opcode 4       mask F8000000  value 20000000  mov128
      <pred>mov128 ds[<idx1>], ds[<idx2>]<extra1><extra2>
```

**Opcode 6**

```
#6    opcode 6       mask F8000000  value 30000000  load
      load <imm>, ds<ds>[<idx>
```

**Opcode 7**

```
#7    opcode 7       mask F8000000  value 38000000  store
      store <imm>, ds<ds>[<idx>
```

**Any opcode (in a field)**

```
#8    any opcode     mask 00000000  value 00000000  adc add and nand nor or sbc sub xor
      <pred><op> <dst>, <src>, ds1[<idx>]
```

**Opcode 12**

```
#9    opcode 12      mask F8000000  value 60000000  mul
      <pred>mul <dst>, <src1>, <src2>
```

**Opcode 13**

```
#10   opcode 13      mask F8000100  value 68000100  abs
      <pred>abs <dst>, ds1[<idx>]
#11   opcode 13      mask F8000100  value 68000000  abs
      <pred>abs <dst>, <src>
```

**Opcode 27**

```
#12   opcode 27      mask F8000100  value D8000100  not
      <pred>not <dst>, ds1[<idx>]
#13   opcode 27      mask F8000100  value D8000000  not
      <pred>not <dst>, <src>
```

**Opcode 15**

```
#14   opcode 15      mask F8000000  value 78000000  rfence rwfence
      <op>
```

**Opcode 16**

```
#15   opcode 16      mask F8000100  value 80000100  tstz
      <pred>tstz <pdst>, ds1[<idx>]
#16   opcode 16      mask F8000100  value 80000000  tstz
      <pred>tstz <pdst>, <src>
```

**Opcode 17**

```
#17   opcode 17      mask F8000100  value 88000100  tstn
      <pred>tstn <pdst>, ds1[<idx>]
#18   opcode 17      mask F8000100  value 88000000  tstn
      <pred>tstn <pdst>, <src>
```

**Opcode 18**

```
#19   opcode 18      mask F8000000  value 90000000  bra
      <pred>bra <imm>
```

**Opcode 19**

```
#20   opcode 19      mask F8000000  value 98000000  call
      <pred>call <imm>
```

**Opcode 20**

```
#21   opcode 20      mask F8000000  value A0000000  rtn
      <pred>rtn
```

**Opcode 21**

```
#22   opcode 21      mask F8000000  value A8000000  halt
      <pred>halt
```

**Opcode 22**

```
#23   opcode 22      mask F8000000  value B0000000  nop
      nop
```

**Opcode 23**

```
#24   opcode 23      mask F8000000  value B8000000  alum
      <pred>alum <op>
```

**Opcode 30**

```
#25   opcode 30      mask F8000000  value F0000000  shl
      <pred>shl <dst>, <src>, <n>
```

**Opcode 31**

```
#26   opcode 31      mask F8000000  value F8000000  shr
      <pred>shr <dst>, <src>, <n>
```
