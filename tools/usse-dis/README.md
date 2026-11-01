# usse-dis — SGX Series-5 USSE disassembler

A from-scratch disassembler for the PowerVR SGX **USSE** instruction set (Series-5 / SGX5xx),
built to read the SGX545 microkernel (the firmware `tools/fwcutter` cuts from the user's own
libraries). The same core is a **radare2 architecture plugin** (`r2/`, `r2/README.md`; no
PowerVR/USSE arch exists in r2 today, and the plugin is structured to be upstreamed).

The instruction sets it decodes are described once, as form tables, in `isa/usse/` and
`isa/pds/` (`isa/README.md`).

## Design

- **C decoder core** (`usse.c` / `usse.h`): pure `decode(enc) -> {text}`, no radare2 dependency,
  so it is regression-tested standalone, and the r2 `RArch` plugin (`r2/`) wraps the *same*
  source (one source of truth).
- **The form table** (`usse_form.h`, engine in `usse_form.c`; the table itself, `usse_table.inc`,
  is generated from `isa/usse/`, see `isa/README.md`): every instruction form is a text
  pattern, the bits that identify it (`(word & mask) == val`) and up to ten fields, each a set
  of bit ranges plus a *kind* that prints it (an enumeration, a number, a register operand, a
  rotated immediate...). `usse_decode()` walks the table in order and prints the first form
  whose fields all print. The encoders (`usse_form_encode` in C, `crates/usse-isa` and
  `crates/pds-isa` in Rust) invert the same table, so the two directions cannot drift apart; a
  form's `dflt` is the value our encoder writes in the bits an instruction ignores.
- **Rust twin** (`crates/usse-isa`, CLI `crates/sgx-tools` `usse-dis`): the same table,
  generated from the same description, with the code kinds written in Rust. `cargo test`
  holds the two identical: the same `--forms` listing, and the same text and form for every
  word, on both cores.
- **CLI** (`main.c` → `usse-dis`): decodes a raw little-endian USSE blob, one 64-bit word per
  line, easy to diff. `--forms` lists the table (index, mask, value, bits read, pattern),
  `--which` appends the index of the form that decoded each word, `--core 540` follows the
  SGX540 where it differs (the load/store cache bits are swapped there).
- **Scope**: grown group by group. The opcode space (major class = `enc[63:59]`) is fully
  enumerated; see `isa/usse/`.

## How it is checked

**Invariant: a form decodes a word only when every one of its fields prints.** A word no form
takes stays undecoded (its class name and `; TODO operands`, or `.long 0x...`): we'd rather
leave a word undecoded than print a plausible lie.

- **Pinned texts**: `pinned.tsv` holds one made-up word for every USSE and PDS form, with the
  text the decoder prints for it; `test_pinned.py` (and the Rust `tests/pinned.rs`) decodes
  each with its form to its text and fails naming any form without a word. The word's fields
  take values distinct from each other and from the form's defaults, so a field moved or
  resized fails. `pingen.c` writes the file (`make pinned`, from a fixed seed) and
  `test_pingen.py` checks the committed file is its output: when a form changes on purpose,
  regenerate it and review the lines that change. `test_forms.py`, `test_ldst.py` and `test_pds.py` pin variants of the fields
  of the commonest forms.
- **The user's firmware**: `test_firmware.py` decodes the microkernel, the five EDM PDS
  programs and the captured transfer programs from the private data repository
  (`$RESGX545_DATA_PRIVATE`, or a sibling `resgx545-data-private`): every instruction must
  decode, and every form they use must be pinned. It stores no word of theirs, and skips
  without the data.
- **Two decoders**: the Rust twin (`crates/usse-isa`) must print the same text and pick the
  same form for every word (`cargo test`, `crates/README.md`). The cross-checks run the C
  binaries and fail without them (`make -C tools/usse-dis` first); `SKIP_C_CROSSCHECK=1` skips
  them.

## Build & test

```sh
make                 # builds ./usse-dis and ./pds-dis
../../.venv/bin/pytest -q
./usse-dis "$RESGX545_DATA_PRIVATE"/firmware/images/images/00_ukernel.bin | less
```

## Status

**The whole SGX545 USSE instruction set decodes**, in all 32 opcode classes. The forms are
described once in `../../isa/usse/` (kinds/ and forms/) and generated into `usse_table.inc`
(`isa/README.md`); `usse.c` and `forms/` hold the code kinds that decode their fields
(`forms/README.md` for the classes each owns):

- **moves**: `limm`, class-5 `mov`, `movc`, `movmsk`, `pclink` moves;
- **integer**: the bitwise group (`and`/`or`/`xor`/shifts/rotates), the test group in both its
  predicate (class 9) and mask (class 15) forms with every operation and format,
  `imae`/`ima8`/`ima16`/`ima32`, `idiv`, `sop2`/`sop3`/`sop2wm`/`lrp`/`sop3c`, `rlp`,
  `u8dot`/`u16dot`;
- **float**: `fmad`/`fadm`/`fmsa`/`fsubflr`, `frcp`/`frsq`/`fsqrt`/`fexp`/`flog`/`fsin`/`fcos`,
  `fdp`/`fddp` and their clamped forms, `fminmax`, `fdsx`/`fdsy`, `fmad16`, `efo`, `fpma`, the
  class-27 dual-issue group;
- **formats**: every `pck`/`unpck` conversion, `statomic`;
- **memory**: `ld`/`st` in every addressing and cache mode, `eldd`/`eldq`, texture sampling
  `smp1d`/`smp2d`/`smp3d` with bias, replace and gradients;
- **control and special**: `ba`/`br`/`lapc`, `phas`, `nop`, `ldr`/`str`, `idf`/`wdf`,
  `lock`/`release`, `setm`/`setfc`/`wop`, `smoa`/`smr`/`smlsi`/`smbo`/`imo`/`moest`,
  `emitpix`/`emitpds`/`emitmt*`/`emitvcb*`, `pcoeff`/`ptoff`/`atst8`/`depthf`, `ci`/`cf`/`cfi`;
- **video**: `firh`/`firv`/`bilin`/`adif`/`adifsum`.

On the user's firmware, `test_firmware.py` checks at run time that every word of the SGX545
microkernel decodes. The SGX540 reads the float classes differently, so those forms refuse to
print under `--core 540` and its float words stay undecoded rather than wrong.

## radare2 plugin

`r2/` wraps the core (`usse.c` and `usse_form.c`) as a radare2 `RArch` plugin (`arch usse`,
`bits 32`): `make -C r2 R2_PREFIX=<your radare2 prefix> install`, then
`radare2 -a usse -b 32 <blob>`. In r2 it prints the text of `usse-dis` (op types and branch
targets wired so jump arrows and function graphs work) and assembles that text back. See
`r2/README.md` for the build and the upstream path to radareorg/radare2. The radare2 fork's
`resgx545` branch carries it in-tree, with a PDS plugin on the same form engine (`pds.c`) and
a pseudo syntax for both (`r2/README.md`, "In-tree").

## Next

1. Open the radare2 PR (`r2/README.md`): the plugin disassembles and assembles through the
   form table.

## Load/store addressing — what the immediate means

usse-dis prints the encoded offset field of `ldad`/`ldaw`/`stad`/`staw` (`test_ldst.py` pins
this). The text is right. What it means depends on the form. Offsets count elements of the data
size (4 bytes for `d`, 2 for `w`):

| form | elements accessed | base writeback |
|------|-------------------|----------------|
| `[b,+#k]` / `[b,-#k]` | `b+k` / `b-k` | none |
| `[b,++#k]` (pre) | `b+k` | `b += k` |
| `[b,#k++]` (post) | `b` | `b += k` |
| `.fetchN [b,+#k]` | **`b+k+1` … `b+k+N`** | none |
| `.fetchN [b,#k++]` | `b+k` … `b+k+N-1` | `b += N` |

So a fetch with a base+offset address starts **one element after** the printed offset:
`ldad.fetch4 r8, [r5,+#3]` loads dwords 4–7 into `r8`–`r11`. Stores behave the same way.
`.fetchN` is printed when the encoding's MOE-expand bit is clear, `.fetch1` included. Plain
forms (no `.fetch`) never add the extra element.

The rules the table states:
- **Plain forms** (no `.fetch`) access exactly the element they print, never an extra one.
- **A post-increment fetch** accesses `N` elements from `b+k` and writes back `b += N`: `k`
  offsets the access and is not part of the increment.
- **A base+offset fetch** starts one element after the printed offset, at `b+k+1`.

Left unmodelled: `.fetchN` with pre-increment or a negative offset, and register offsets
(`[b,+rN]`). The radare2 plugin follows this table.

## regtouch — the firmware's register map

`regtouch.py` lists every SGX register a USSE program touches directly: the EDM uses
`ldr rD, #idx` / `str #idx, src` with a dword register index (offset = idx × 4). It runs on
usse-dis output and can emit radare2 comments for each access site. Register names come from
the GPL DDK's `sgx545defs.h`, which you supply: `$RESGX545_REGDEFS` names it (several headers
joined by `:`), or `--defs <header>`; without one, registers print as offsets.

```sh
./usse-dis ukernel.bin > uk.txt
RESGX545_REGDEFS=<path>/sgx545defs.h ../../.venv/bin/python regtouch.py uk.txt --r2 regs.r2
../../.venv/bin/pytest -q test_regtouch.py
```

`--r2-flags out.r2` also writes a flag per register, `sgx.` and the header's name for it, at
`0x100000000 + offset`, a window above the 32-bit device address space (the radare2 emulation
that uses it arrives with the simulator unit).

## pds-dis — the PDS (data sequencer) decoder

The EDM is entered through small **PDS programs**. `pds.c` / `pds.h` decode the PDS
words by walking the PDS form table (`pds_table.inc`, generated from `isa/pds/`), the same
engine as USSE. The 32-bit PDS instruction word: opcode `w[31:27]`, predicate `w[26:24]`
(`p0`–`p2`, `if0`/`if1`, `aluz`/`alun`, 7 = always), and a 24-bit operand body per group
(`movs`/`movsa` to the `dout*` issue ports, `mov16`–`mov128`, `load`/`store`, integer ALU,
`tstz`/`tstn`, `bra`/`call`, fences). `pds-dis <program.bin> <data_dwords>` prints the data
segment as `data` and decodes the rest. Three options, as `usse-dis` has: `--forms` lists the
form table (index, mask, value, the bits each form reads, pattern), `--which` appends `#<n>`,
the form that decoded each instruction, and `--regs` names the register each data dword loads
(`data ds0[2]`; rows of `ds0[2r]`, `ds0[2r+1]`, `ds1[2r]`, `ds1[2r+1]`). The Rust `pds-dis`
prints the same.

`test_pinned.py` pins one made-up word for every PDS form, `test_pds.py` variants of the
fields of each group, and that reserved encodings print as `.word`, never as a guess;
`test_firmware.py` checks at run time that every instruction of the user's five EDM programs
decodes.

```sh
make pds-dis
./pds-dis "$RESGX545_DATA_PRIVATE"/firmware/images/images/04_pds13.bin 24
./pds-dis --regs --which "$RESGX545_DATA_PRIVATE"/firmware/images/images/04_pds13.bin 24
../../.venv/bin/pytest -q test_pds.py
```
