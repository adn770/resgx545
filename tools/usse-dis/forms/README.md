# USSE instruction families

The forms are described in `isa/usse/` (`isa/README.md`), one file per family, and
generated into `usse_table.inc`. What stays here, in `forms/*.inc`, is each family's **code
kinds**: the operand printers and parsers with logic, which `usse.c` includes before the
generated table (their Rust twins are in `crates/usse-isa/src/forms/`). A family owns opcode
classes (`enc[63:59]`):

| file | classes | instructions |
|------|---------|--------------|
| `float` | 0-4, 6, 7, 25, 27 | float ALU, transcendentals, `fdp`, `fminmax`, `efo`, `fpma` |
| `memctl` | 28, 29, 31 | `smp*` texture sampling, `eldd`/`eldq`, the rest of class 31 |
| `intpack` | 8, 14, 16-21, 24, 26 | `pck`/`unpck`, `sop2`/`sop3`, `ima*`, `idiv`, `u8dot` |
| `misc` | 5, 9, 15, 22, 23 | `movc`/`movmsk`, the test group, `firh`/`firv`/`bilin`/`adif` |

## Method

A form states an encoding: the bits that identify it and a field for each operand. Make the
fields as general as the encoding is known (an under-determined field is fixed in the mask
instead of guessed). Add or change the form in `isa/usse/forms/<group>.toml` (and any new kind
in `isa/usse/kinds/<family>.toml`), give it its made-up word in `../pinned.tsv`, then, from the
repository root:

```sh
python3 isa/gen.py && make -C tools/usse-dis    # regenerate the tables, build
.venv/bin/pytest -q tools/usse-dis tools/usse-asm  # pinned texts, assembler round trip
cargo test                                      # the Rust twin agrees
```

`test_roundtrip.py` draws words per form (its fixed bits, random elsewhere, plus one- and
two-bit flips) and uniformly: every word a form decodes must assemble back to a word that
decodes to the same text, so it must stay at 0 failed. What an instruction does is measured on
the GPU: the probe vectors, which the simulator (`crates/sgx-sim`) must match.

The pinned texts use made-up words; `test_firmware.py` decodes the user's own firmware and
transfer captures at run time and checks that every form they use is pinned.
