<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
# Writing USSE by hand

This tutorial walks through the USSE programs that run our transfer queue on the real SGX545:
a solid fill, a copy, the end-of-tile and end-of-render programs and the secondary program.
Each chapter shows the program as it is in `asm/`, explains it line by line, and assembles
it, or a variant of it with values of our own, with `usse-asm`. `tools/usse-asm/test_tutorial.py`
checks that every program quoted here is the file in `asm/` and every listing what the
assembler prints, so the text cannot drift from the sources and the tools.

The tools are those of `tools/usse-asm` and `tools/usse-dis` (`make` in each), or their Rust
twins in `crates/sgx-tools` (`cargo build --release -p sgx-tools`): `usse-asm` assembles a
source into raw words and, with `-l`, lists them as `usse-dis` prints them back. The syntax is
the disassembler's (`tools/usse-asm/README.md`).

Sources, as everywhere in resgx545: the firmware file's transfer templates
(`doc/specs/fw_format.md` §9-§11), which these programs reproduce bit for bit, the transfers
our kernel runs with them on the laptop (`doc/specs/transfer.md` §4; HW), and the readings
we infer from both, marked **[infer]**. The machine model behind each instruction (register
banks, predicates, phases, repeats) and what the hardware was measured to do arrive with the
probes and the simulator, with a reference of every instruction group; this tutorial uses
only what the transfers need.

## 1. A solid fill

A transfer fill draws a rectangle in one colour. The ISP covers the rectangle with a
background object, and the pixel shader runs for every pixel of it (`doc/specs/transfer.md`
§4.2). Its job is a single write: the colour, into output register `o0`, which the end-of-tile
program later packs into the surface.

From `asm/transfer/use_fill.s`:

```
; use_fill.s -- the solid-fill pixel shader (transfer template USE_FILL, id 0).
;
; The ISP background object covers the fill rectangle, and this program runs
; once per pixel of it (doc/specs/transfer.md §4.2). It writes the fill
; colour to output register o0; the end-of-tile program (use_eot.s) then packs
; o0 into the surface with pack mode 0, so the colour is the 0xAARRGGBB dword.
;
; Per transfer, the driver patches the colour into the immediate of the second
; instruction (doc/specs/fw_format.md §9.4: PARAM 0, a USSE_LIMM patch at byte 8).
; Each colour therefore needs its own copy of the program. The template keeps
; 0 there.

        ; The phase marker, the first instruction of every pixel program
        ; here: next-phase program #0 with #0 temporaries, pixel rate, wait
        ; condition "end", instances in parallel. [infer] "end" with #0 means
        ; no further phase follows.
        phas #0, #0, pixel, end, parallel

        ; o0 = the colour. A long immediate: the 32 bits are scattered over
        ; the word (the USSE_LIMM split). .skipinv runs it for every
        ; instance, .end ends the program.
        mov.skipinv.end o0, #0x00000000
```

Two instructions:

- **`phas`** opens the program's only phase. Every pixel program here starts with one; its
  operands name the next phase's program and temporaries (none), the rate (`pixel`), what the
  next phase would wait for (`end`: **[infer]** there is none) and that instances run in
  `parallel`.
- **`mov.skipinv.end o0, #imm`** writes the colour. A 32-bit immediate does not fit one field:
  the encoder scatters it over the word. `.skipinv` is set as on every instruction of these
  programs (**[infer]** it runs the instruction whatever the instance's coverage), and `.end`
  makes it the program's last.

The driver writes each fill's colour into that immediate before it submits the program
(`doc/specs/fw_format.md` §9.4), so every colour needs its own copy. With a colour of our own
in place of the template's 0, the listing shows where the immediate goes: `0xFF00FF00` lands
as `0xFF00` in the low half of the word and the rest in fields of the high half.

```
$ cat prog.s
phas #0, #0, pixel, end, parallel
mov.skipinv.end o0, #0xff00ff00
$ usse-asm -l -o prog.bin prog.s
     0: 0xFA44070000000000	phas #0, #0, pixel, end, parallel
     1: 0xFCA7F1810000FF00	mov.skipinv.end o0, #0xFF00FF00
```

The source may spell numbers in either case and in decimal; the listing is the
disassembler's canonical text. On the laptop, fills built from the firmware file's templates,
which these programs equal bit for bit, colour every pixel of their rectangle and nothing
outside it (E019).

## 2. Reading what the PDS fetched

A copy reads a source surface. The task's data comes from the PDS, the data sequencer that
starts every USSE task: for a copy its program (`pds_prim_1src.s`) has the texture unit fetch the
source texel of each pixel into primary attribute `pa0` and makes the task wait for it
(`doc/specs/fw_format.md` §10.4 lists the words it is patched with). The shader only passes
the texel on (`doc/specs/transfer.md` §4.3):

From `asm/transfer/use_copy.s`:

```
; use_copy.s -- the copy pixel shader (template USE_COPY, id 7).
;
; For a copy, the PDS primary program (pds_prim_1src.s) has the texture unit
; fetch the source texel of each pixel into primary attribute pa0, and makes
; this task wait for it (DOUTU U1 TEXTUREDEPENDENCY). The shader passes the
; texel on to o0; the end-of-tile program packs it as for a fill
; (doc/specs/transfer.md §4.3). Never patched: one copy serves every blit.

        phas #0, #0, pixel, end, parallel       ; the phase marker, as in use_fill.s
        mov.skipinv.end o0, pa0                 ; o0 = the fetched texel; end
```

The primary attributes `pa0`, `pa1`, ... are per instance and filled before the task runs.
Copies built from the templates these programs equal reproduce their source texel for texel
on the laptop (E020).

## 3. Leaving a tile

The pixel programs above only fill output registers. When a tile is finished, the end-of-tile
program hands those registers to the pixel back end (PBE), with the five state words that say
where and how to write them (`doc/specs/fw_format.md` §9.6 lists them for a fill):

From `asm/transfer/use_eot.s`:

```
; use_eot.s -- the end-of-tile program (template USE_EOT, id 2).
;
; Runs when a tile is finished and hands the tile's output registers to the
; pixel back end (PBE) with the five PBE state words of the destination
; (doc/specs/fw_format.md §9.6): emitpix1 sends words 0 and 1, emitpix2
; words 2 and 3 plus the sideband word 4 as an immediate. The task gets four
; temporaries (TQ_META temps 4) for words 0-3.
;
; Per transfer the driver patches (doc/specs/fw_format.md §9.4):
;   - the destination register of the movs at bytes 16, 24 and 32 to r1, r2
;     and r3 (CONST 1 << 21, 2 << 21, 3 << 21 added to the word): the cut
;     template's four movs all name r0 (doc/specs/fw_format.md §9.2) and so do ours, to
;     reproduce it bit for bit;
;   - their immediates to PBE words 0-3 (PARAM 1-4, USSE_LIMM patches);
;   - the sideband of the emitpix2 (PARAM 5, EMITPIX_SB: value bits [5:0]
;     to e[27:22], [11:6] to e[40:35], [13:12] to e[55:54]).

        phas #0, #0, pixel, end, parallel       ; the phase marker, as in use_fill.s

        ; Load words 0-3 into r0-r3 (the last three r0 until patched).
        mov.skipinv r0, #0x00000000             ; r0 = word 0: XMIN [12:0], YMIN [28:16]
        mov.skipinv r0, #0x00000000             ; -> r1 = word 1: XMAX, YMAX (inclusive)
        mov.skipinv r0, #0x00000000             ; -> r2 = word 2: COUNT [15:8], LINESTRIDE [27:16]
        mov.skipinv r0, #0x00000000             ; -> r3 = word 3: FBADDR [31:2]

        ; Emit to the PBE: incp #0, sources r0 and r1 (words 0 and 1).
        ; [infer] .freep frees the task's resources once the emit is done.
        emitpix1.freep #0 /* incp */, r0, r1

        ; Words 2 and 3 from r2 and r3, the sideband word as an immediate
        ; (PACKMODE [5:0], TILERELATIVE [9]: 0x200 for ARGB8888), and end.
        ; The third source (r0) is not used for this emit.
        emitpix2.end.freep #0 /* incp */, r2, r3, r0, #0x00000000
```

- The four `mov`s load PBE words 0-3 into temporaries. The task is given four temporaries
  (its `temps` in the template's `TQ_META` record, `doc/specs/fw_format.md` §9.3).
- **`emitpix1`** and **`emitpix2`** send the words to the PBE: the first words 0 and 1, the
  second words 2 and 3 and, as its last immediate, the sideband word 4 (the pack mode and
  `TILERELATIVE`). **[infer]** `.freep` frees the task's resources once the emit is done;
  the `.end` of the second ends the program.
- The driver patches this program per transfer: the immediates become the PBE words, and the
  destination registers of the last three `mov`s, `r0` in the template, become `r1`-`r3`
  (`doc/specs/fw_format.md` §9.2, §9.4). Ours keeps `r0` there so that its words are the
  template's, bit for bit.

Patched by hand, with made-up PBE words for a 64 x 32 rectangle, the program reads as the
driver would submit it:

From `asm/tutorial/eot_patched.s`:

```
; eot_patched.s -- use_eot.s as the driver patches it for one transfer, with made-up PBE
; words (doc/specs/usse_tutorial.md, "Leaving a tile"): the movs load r0-r3, the emits send them.

        phas #0, #0, pixel, end, parallel
        mov.skipinv r0, #0x00000000             ; word 0: XMIN 0, YMIN 0
        mov.skipinv r1, #0x001f003f             ; word 1: XMAX 63, YMAX 31
        mov.skipinv r2, #0x01001000             ; word 2: COUNT, LINESTRIDE
        mov.skipinv r3, #0x12340000             ; word 3: FBADDR
        emitpix1.freep #0 /* incp */, r0, r1
        emitpix2.end.freep #0 /* incp */, r2, r3, r0, #0x00000200
```

```
$ usse-asm -l -o eot.bin asm/tutorial/eot_patched.s
     0: 0xFA44070000000000	phas #0, #0, pixel, end, parallel
     1: 0xFCA0000000000000	mov.skipinv r0, #0x00000000
     2: 0xFCA00000003F003F	mov.skipinv r1, #0x001F003F
     3: 0xFCA0008000401000	mov.skipinv r2, #0x01001000
     4: 0xFCA0411000740000	mov.skipinv r3, #0x12340000
     5: 0xFB20010000200080	emitpix1.freep #0 /* incp */, r0, r1
     6: 0xFB24004000208180	emitpix2.end.freep #0 /* incp */, r2, r3, r0, #0x00000200
```

The destination register sits at bit 21 of the low half (`r1` adds `0x00200000` to it, which is
the `CONST 1 << 21` patch), and the sideband's bits are scattered over the `emitpix2` word as
the `EMITPIX_SB` encoding says.

## 4. Ending a render, and the secondary program

Two more programs complete a transfer. After the last tile of a render, the end-of-render
program sends one more `emitpix2`, with zero words and the sideband `0x200` (**[infer]** it
closes the render); the secondary program, which the PDS kicks once per transfer, has
nothing to do and ends:

From `asm/transfer/use_eor.s`:

```
; use_eor.s -- the end-of-render program (template USE_EOR, id 3).
;
; Runs once after the last tile of a render: an emitpix2 to the PBE with zero
; words and sideband 0x200; [infer] it closes the render. One temporary
; (TQ_META temps 1).
; Never patched.

        phas #0, #0, pixel, end, parallel       ; the phase marker, as in use_fill.s
        mov.skipinv r0, #0x00000000             ; r0 = 0
        ; Emit r0 (0) and the immediate #0 as words 2 and 3, sideband 0x200; end.
        emitpix2.end.freep #0 /* incp */, r0, #0, r0, #0x00000200
```

From `asm/transfer/use_sec.s`:

```
; use_sec.s -- the USE secondary program of a transfer (template USE_SEC, id 1).
;
; The PDS secondary program (pds_sec.s) kicks this once; a transfer has no
; per-tile secondary work ([infer]), so it only ends (doc/specs/fw_format.md §9.2).

        phas #0, #0, pixel, end, parallel       ; the phase marker, as in use_fill.s
        nop.end                                 ; nothing to do: end the program
```

`nop.end` is the shortest program there is: one phase marker, then an instruction that only
ends. Every program here ends on an instruction with `.end`.

## 5. Where to go next

- **`asm/README.md`** lists every program, the PDS programs that start these tasks
  (`asm/transfer/pds_*.s`) among them, and why they equal the closed templates bit for bit.
- **`tools/usse-asm/README.md`** gives the whole syntax: listings as input, PDS data segments
  and labels, and the Rust tools' `.include`, `.equ` and `.macro`, and `sgx-asm`, which
  assembles the nine programs and their patch records as one source (`asm/transfer/transfer.s`).
- **`tools/usse-dis/README.md`** describes the form tables both directions read.
- The programmer's guide and the instruction reference, with what the hardware was measured to
  do, a vertex shader in two phases and a template for testing an instruction on the GPU, arrive
  with the probes and the simulator.
