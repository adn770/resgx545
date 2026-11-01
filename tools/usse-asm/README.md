# usse-asm — a clean-room SGX545 USSE and PDS assembler

`usse-asm` and `pds-asm` assemble text written the way our disassemblers print it
(`tools/usse-dis`: `usse-dis`, `pds-dis`) into raw little-endian words, so that

```
disasm(asm(text)) == text        asm(disasm(words)) decodes as words
```

With them the GPU programs of the 2D transfers no longer need to come from the closed
`libsrv_um.so`: `asm/transfer/` holds the nine transfer-queue templates as our own assembly
source, and assembled they equal the templates `tools/fwcutter` cuts from the library, bit for
bit (`doc/specs/fw_format.md` §11, checked by `tools/fwcutter/test_ours.py`).

## Usage

```sh
make                                      # builds usse-asm and pds-asm (needs ../usse-dis)
./usse-asm -o fill.bin ../../asm/transfer/use_fill.s   # 64-bit USSE words
./pds-asm -l -o prim.bin ../../asm/transfer/pds_prim.s # 32-bit PDS words; -l lists
../usse-dis/usse-dis prog.bin | ./usse-asm -o again.bin -    # listings assemble too
pytest -q                                 # from the repository root: tools/usse-asm
```

`crates/sgx-tools` builds Rust twins of both tools, with the same options, output and messages
(`crates/README.md`), and one option of their own: `--explain` follows each "cannot assemble"
with the forms that matched the most of the line and what each expected next, or says that no
form reads its mnemonic.

Options: `-o <file>` writes the binary, `-l` prints a listing in the disassembler's format,
`--core 540` follows the SGX540 reading of the load/store cache bits (default 545). `-` reads
standard input. Errors name the file and line; the exit status is 1.

## Source syntax

One statement per line:

| statement | meaning |
|-----------|---------|
| `mov.skipinv.end o0, #0xFF336699` | an instruction, as the disassembler prints it |
| `.long 0x...` / `.word 0x...` | raw words (USSE 64-bit / PDS 32-bit), comma-separated |
| `name:` | a label; may share the line with a statement |
| `; ...`, `/* ... */` | comments |
| `12: 0xFA44070000000000\tphas ...` | a disassembler listing line: the index and hex columns are ignored, except that a PDS `data` line takes its value from the hex column |

Instruction text is matched leniently around the exact disassembler spelling, letters in
either case (radare2 lowercases what it assembles; `test_case.py`): blanks may
vary (around commas too), numbers may be decimal or `0x` hex in any case (`#0` for
`#0x00000000`), and the `/* incp */`-style comments the disassembler prints are optional.
Mnemonics, flags and register names are exact.

**PDS**: the raw words before the first instruction are the data segment (the program's
constants, in the `ds0`/`ds1` banks by pairs of dwords: `SGX_FEATURE_PDS_DATA_INTERLEAVE_2DWORDS`,
`doc/specs/hw_spec.md` §2). `bra`/`call` take a label or a number; a label's value is its
instruction index counted from the first instruction after the data segment, as the branch
field counts. **USSE**: `ba #label` takes the label as an absolute instruction index; `br`
takes only a number (its offset base is not established here).

### Rust-only extensions

The Rust `usse-asm` and `pds-asm` also read these directives; the C tools do not (a source
without them assembles the same in both):

| statement | meaning |
|-----------|---------|
| `.include "file.s"` | read another source here; the name is relative to the including file (to the working directory from stdin) |
| `.equ NAME, expr` | a constant; defined once, before its use |
| `.macro name a, b=0` ... `.endm` | a macro; `\a` in the body is the argument, `\@` the call's number (for unique labels) |
| `name x, y` | a macro call; a missing argument takes its default |

Expressions use C operators and precedence (`- ~ + * / % << >> & ^ |`, parentheses) on
decimal, `0x` and `0b` numbers and `.equ` names. In an instruction, a `.equ` name and a
parenthesised expression (`#(BASE + 4)`, `ds0[(U0 + 1)]`) become their decimal value;
parentheses that are not an expression, such as the predicate in `(p0) bra`, stay. `.long` and
`.word` take expressions too, negative values in two's complement. Errors inside an included
file name that file; errors inside a macro name the line that called it.

### sgx-asm: several programs in one source

`sgx-asm` (Rust, `crates/sgx-tools`) reads the same syntax with sections and patch records,
for firmware and templates made of several USSE and PDS programs:

```sh
cargo run -p sgx-tools --bin sgx-asm -- -l -d out/ asm/transfer/transfer.s
```

`-d out/` writes each section's image as `out/<name>.bin` and `out/map.json`: the sections
(name, ISA, id, size, PDS data words), every label (section, value as branches count it,
byte offset) and the patch records. `-l` lists each section; `--core` and `--explain` as above.

| statement | meaning |
|-----------|---------|
| `.section name, usse\|pds\|data, id` | start a section; `id` is the buffer (or template) id its patches name; `data` holds `.word`s only |
| `kind(args)` in a `.word` | a `WORD32` patch on that word, which assembles as 0 |
| `kind(args)` in a USSE operand | a `USSE_LIMM` patch on that instruction (`mov rN, #kind(...)`), which assembles as 0 |
| `.patch encoding, kind(args)` | a patch on the next word or instruction, any encoding |
| `.patch encoding, kind(args), offset` | a patch at a byte offset in the section |

Encodings and kinds are the firmware format's (`doc/specs/fw_format.md` §4, §9.4):
`word32`, `usse_limm`, `code_base`, `emitpix_sb`; `const(value)`, `addr(target[, addend])`,
`addr_shr4`, `heap(heap id[, addend])`, `pd_phys([addend])`, `code_word(usse label[, addend])`,
`pds_ctl`, `pds_rows`, `param(n[, addend])`, `doutu`. A target is a section name (its id) or a
number. Records keep source order, a `.patch` before the inline patch of the same statement,
since the driver applies them in order. Labels are per section: a branch reaches only its own
section; other sections name a label only through `code_word`.

`tools/fwcutter/asmmap.py` reads the output as firmware-format records. `asm/transfer/transfer.s`
writes the nine transfer-queue templates as one source; `tools/fwcutter/test_asmmap.py`
checks that it gives `ours.py`'s templates and `facts.TQ_PATCHES` exactly.

## Design

The USSE decoder is a table of instruction forms (`../usse-dis/usse_form.h`): a text pattern,
the bits that identify the form, and fields printed by *kinds*. The assembler is the same
table read backwards, by the engine in `usse_form.c`:

1. Try the forms in table order. Match the pattern against the text: literal text exactly
   (blanks flexible); for each field, either parse it (numbers, the rotated immediate, branch
   offsets, movs operand lists) or search the field's values for one that prints the text.
   The search backtracks, so ambiguous prefixes (`r1` vs `r12`) resolve.
2. Build the word from the form's fixed bits, its preferred values for the bits it ignores
   (`dflt`), and the fields.
3. **Accept the word only if the decoder prints it with the form's text.** An earlier form
   may claim the word, or a value may not be printable; then the search goes on.

Step 3 makes the assembler unable to emit a word the disassembler would read differently.
PDS works the same way: `pds_forms.c` inverts the PDS form table, which `pds_decode()` walks
(both generated from `isa/pds/`).

**Canonical encodings.** Many words print the same text: bits an instruction ignores, an
unused operand, a mask that equals a repeat count of one. The assembler picks the first
form in table order and, within it, the form's preferred values (`dflt`): 0, or a convention of
our tables. Two are named in the form tables (`isa/usse/forms/`): an unused source 2 of a
class-5 `mov` or of a load without a range operand is written as immediate 0 (`UNUSED_SRC2`),
and the vertex-side emits write the operand they do not print as immediate 0
(`EMIT_UNUSED_SRC1`, `EMIT_UNUSED_SRC0`: source 1 of `emitvcbst` and `emitvcbvtx`, the
extension bit of source 0 of `emitmtest`). With them, the programs of the user's own firmware
file (the microkernel and the five EDM PDS programs) reassemble bit for bit from their
listings (`test_roundtrip.py`, when the private data repository is present), as do the nine
transfer templates (`tools/fwcutter/test_ours.py`).

## Coverage

Whatever `usse-dis` and `pds-dis` decode assembles. `usse-dis` decodes the whole SGX545 USSE
instruction set (`../usse-dis/README.md` lists the groups: moves, integer, float, formats,
memory and texture sampling, control and special, video), and `pds-dis` every PDS instruction
group (`movs`/`movsa` to the `dout*` ports, `mov16`–`mov128`, `load`/`store`, the integer
ALU, `tstz`/`tstn`, `bra`/`call`/`rtn`/`halt`, fences, `alum`, shifts). The assembler reads
the decoder's form table, so a form added there assembles too.

## Tests

`pytest -q tools/usse-asm` from the repository root (about 20 s):

- `test_usse_asm.py`, `test_pds_asm.py`: every form through its made-up word in
  `../usse-dis/pinned.tsv` (each text assembles to its pinned word or, for the ten USSE forms
  whose pinned word sets bits the form ignores, to the canonical word, which prints the same
  text), then every PDS group, lenient spelling, listings, labels, data segments, errors and
  refused values.
- `test_roundtrip.py`: random words, drawn per form of the decoder's table (1500 each, a third
  with flipped identifying bits) plus 50k uniform USSE words, the same on the SGX540 reading
  (fewer), and 4000 random PDS words per opcode. Every decoded word must reassemble to a word
  that decodes the same. A run prints the statistics:

  ```
  usse-asm: 378500 words, 314007 decoded, 0 failed, 94877 bit-identical, 219130 canonicalised (69.8%)
  usse-asm --core 540: 75700 words, 40421 decoded, 0 failed, 9905 bit-identical, 30516 canonicalised (75.5%)
  pds-asm: 128000 words, 84729 decoded, 0 failed, 8358 bit-identical, 76371 canonicalised (90.1%)
  ```

  Random words are mostly not canonical (their ignored bits are random), so most come back
  canonicalised: the bits they ignore are written the canonical way, and every one of them
  decodes to the same text. Then, read at run time from the private data repository
  (`$RESGX545_DATA_PRIVATE` or a sibling `resgx545-data-private`; skipped without it), the
  microkernel and the five EDM PDS programs must come back bit for bit. No word of theirs is
  stored here.
- `test_case.py`: every decoded instruction also assembles from its lowercase spelling, as
  radare2 hands it over.
- `test_tutorial.py`: the listings in `doc/specs/usse_tutorial.md` are the sources in `asm/`
  and what the assembler makes of them.

The Rust side (`cargo test`, `crates/README.md`) holds the Rust encoders to these tools on
random and respelled texts and runs both on every program in `asm/`.

## Programs

Our own GPU programs are in `asm/` at the repository root; `asm/README.md` lists them, and
`doc/specs/usse_tutorial.md` walks through the transfer programs instruction by instruction.

## Users

- `tools/fwcutter/ours.py` assembles `asm/transfer/` for `fwcutter.py cut <libsrv_init.so>
  --tq-from-source`, which writes them into the firmware file as origin `OURS` (format v4,
  `doc/specs/fw_format.md` §11), so 2D needs no `libsrv_um.so`; `tools/fwcutter/asmmap.py`
  reads `sgx-asm`'s output of `asm/transfer/transfer.s`.
- The radare2 fork's PDS plugin carries `pds_forms.c` and `pds_asm.h`
  (`../usse-dis/r2/sync-fork.sh` copies them with the decoders).
- The user-space library and the first triangle's programs, which assemble their sources from
  `asm/` too, arrive with the render path unit; the probe host, which assembles its probe
  programs with these tools, arrives with the probes unit.

## Next

- Let `br` take a label as `ba` does, once its offset base is measured.
