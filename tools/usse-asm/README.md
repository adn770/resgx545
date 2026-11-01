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
- `test_probe.py`: the probe host, `probe.py`: the tables under `probes/`, their programs,
  the parser of `sgxfive-test probe` output and the verdicts (an end-to-end run goes through
  `sgxfive-test --mock`).
- `test_vectors.py`: `vectors.py`, the converter of probe readbacks into vector files.
- `test_vec_tables.py`, `test_bank_probes.py`, `test_filter_probes.py`, `test_lock_probes.py`,
  `test_arch_guides_probes.py`: the tables of `probes/usse/` that hold generated or
  structured cases, as their cases and pokes (not their results).
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
- The user-space library and the first triangle's programs assemble their sources from `asm/`
  too, and the probe host (below) assembles its probe programs with these tools.

## Hardware probes

A table entry with host = "tri" takes, besides its program words, per case (case_set) the words of
the state block, the render command and the VDM stream as `blk`, `cmd` and `vdm` (replacing the
probe's) and `vdm_xor` (flipped: `--vdm N^=V`, the only word space the tool flips), the kernel's
render details and TA words as `kpoke = ["rd:N^=V"]`; the state block's and the render command's
words are set by absolute values, as the tool flips neither.
`output_room.py` reads the output-room probes (usse/output-room*.toml): which register of a
tagged shader reached each pixel (11.15).

`probe.py` runs our own short programs on the GPU to pin down what the instruction set does where
the text alone does not say. A table is `probes/<unit>/<feature>.toml` (`--table FILE` picks
one); per probe it names a template in the table's `templates/` directory, its parameters, the
input cases and, per hypothesis, the readback every case should give. Each case is assembled into
its own program, which `sgxfive-test probe` (`userspace/libsgxfive`) runs as the shader of a
client fill on the render node; the host reads back `o0` and a 64 KiB scratch buffer. A probe is
settled when exactly one hypothesis predicts every case. The campaign runner (`tools/campaign`)
runs the tables probe by probe on a clean GPU and keeps each run with its programs.

```sh
../../.venv/bin/python probe.py --table ../../probes/usse/integer.toml list
../../.venv/bin/python probe.py --table T build ../../debug/b 'usse-integer-isub16-*'
../../.venv/bin/python probe.py --table T run --out ../../debug/probes/run 'usse-integer-*'
../../.venv/bin/python probe.py --table T eval ../../debug/probes/run/raw.txt   # a saved run
../../.venv/bin/python probe.py --table T local --mock  # the mock: only checks the plumbing
../../.venv/bin/pytest -q test_probe.py
```

`run` needs the laptop booted with the render node on (`gma500_gfx.sgx_render=1`), its address
in `SGX_TARGET_HOST` (or `kernel/scripts/local.env`) and an i686 `sgxfive-test` in its home
directory (`SGX_PROBE_TOOL` overrides the path): build it with `make CC='cc -m32'` in
`userspace/libsgxfive` on a Linux host, or on the laptop itself, and copy `build/sgxfive-test`
there. `local` needs `make -C userspace/libsgxfive` first. A run's readbacks become vector files
with `vectors.py convert`, which finds the run's table and templates under `probes/`.
Every case runs in its own process, because a faulting probe gets its file banned after three
faults; a fault shows as `failed`, with the scratch dwords changed before it (or `scratch
unchanged`). A hypothesis expects a failure as `"fail"`, or as `{fail = true}` with a `dwords`
list (the first scratch dwords, as a plain list gives them) and/or a `scratch` set: what ran
before the job hung or faulted. A new probe is a table entry, plus a template when none of
`pred.s` (a predicate as the pixel), `value.s` (a register), `dump.s` (sixteen registers to
the scratch buffer), `index.s`, `index_sa.s`, `index_sa2.s`, `memoff.s`, `repeat.s`, `moe.s`,
`pred4.s` or `coords.s` fits (they sit in the templates of the tables that use them).

A table entry with `isa = "pds"` probes the PDS: its template (`pds_dump.s`) is assembled with
`pds-asm` and runs as the fill's PDS secondary program (`sgxfive-test probe --pds N --use
sa_dump.bin`, N its data dwords). It copies its inputs to the temporaries `ds0/ds1[48..55]` (the
only writable registers) and passes its results with `douta` into `sa0`-`sa15`, which the fill's
shader `sa_dump.s` stores to scratch dwords 0-15, so the hypotheses expect the same lists as
`dump.s` ones. A table entry may name its USE program (`use = "sa_pixel.s"`: `sa0` as the pixel,
with `pixels = true`).

A table entry with `coords = true` runs as the shader of a copy whose source texel is the
pixel's coordinates (`sgxfive-test probe --coords`), so that every pixel computes its own
inputs (`coords.s` derives a value per pixel and register), and with `pixels = true` every
pixel is read back. A hypothesis then expects `{pixels = [...]}`, all 2048 in raster order, or
`{quad = [[k, n], ...]}`: per 2x2 quad position (top-left, top-right, bottom-left,
bottom-right), the `coords.s` value `k` of the pixel at position `n` of the same quad.

A table entry with `host = "tri"` runs inside the first triangle's render instead of a fill
(`sgxfive-test probe --tri SLOT[:N] --slot SLOT=FILE[:N] --width W --height H`): its cases
replace the program `slot` (`pixev` the pixel-event PDS program, `eot` the end-of-tile task,
`vtxpds` and `vtxuse` the vertex programs, `pixel` the triangle's shader; a PDS slot makes the
entry a PDS one), `slots = { eot = "eot_dump.s" }` names fixed helpers for other slots, and
`size = [W, H]` (default 64 x 64) and `max_size` the target and its render context, and
`vertices = N` (3 to 15, whole triangles) draws copies of the triangle after it, copy `c` moved
`c`/16 pixel, so that the vertex programs run for more vertices than one task's. The host
patches each replacement as it does the default (libsgxfive's `sgxfive_tri_probe.h` lists
the rules: a `pixev` keeps `pds_pixevent.s`'s data dwords 0-5 and 12, an `eot` `use_eot.s`'s four
PBE movs and final `emitpix2`). `pixev_dump.s` is the default pixel-event program with `{OP}` on
the end-of-tile event, passing values with `douta` to the end-of-tile task's `sa0`-`sa15`,
which `eot_dump.s` stores to scratch dwords 0-15 (one tile: the hypotheses are lists as for
`dump.s`) or `eot_tile.s` to 16 dwords per tile.

A tri entry also takes `vtx_coords`, `copy_depth`, `blk`, `cmd` and `vdm` (state block, render
command and VDM stream words set by index), `sideband`, `kpoke` (words of the kernel-built
firmware command, set through the kernel's debugfs) and `case_set` (more pokes or words per
case). With `dump_render = true` the probe saves what the TA wrote (the kernel's debugfs
`render_param` and `render_tadata`) after each case, to the run's `dumps/NAME.{param,tadata}.bin`.

## Next

- Let `br` take a label as `ba` does, once its offset base is measured.
