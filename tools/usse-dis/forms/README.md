# USSE instruction families

The forms are described in `isa/usse/` (`isa/README.md`): the definitions of each family in
`isa/usse/kinds/<family>.toml`, the forms in `isa/usse/forms/<group>.toml`, one file per
encoding group. Both are generated into `usse_table.inc`. What stays here, in `forms/*.inc`,
is each family's **code kinds**: the operand printers and parsers with logic, which `usse.c`
includes before the generated table (their Rust twins are in `crates/usse-isa/src/forms/`). A
family owns opcode classes (`enc[63:59]`):

| file | classes | instructions |
|------|---------|--------------|
| `float` | 0-4, 6, 7, 25, 27 | float ALU, transcendentals, `fdp`, `fminmax`, `efo`, `fpma` |
| `memctl` | 28, 29, 31 | `smp*` texture sampling, `eldd`/`eldq`, the rest of class 31 |
| `intpack` | 8, 14, 16-21, 24, 26 | `pck`/`unpck`, `sop2`/`sop3`, `ima*`, `idiv`, `u8dot` |
| `misc` | 5, 9, 15, 22, 23 | `movc`/`movmsk`, the test group, `firh`/`firv`/`bilin`/`adif` |

Classes 10-13 (the bitwise group) and 30 (`ld`/`st`) need no code kinds of their own: their
forms use the kinds of `isa/usse/kinds/main.toml` and `usse.c`.

## Method

A form states an encoding: the bits that identify it and a field for each operand. Make the
fields as general as the encoding is known (an under-determined field is fixed in the mask
instead of guessed). Add or change the form in `isa/usse/forms/<group>.toml` (and any new kind
in `isa/usse/kinds/<family>.toml`), then, from the repository root:

```sh
python3 isa/gen.py                          # regenerate the C and Rust tables
make -C tools/usse-dis
.venv/bin/pytest -q tools/usse-dis          # the pinned texts, one made-up word per form
cargo test                                  # the Rust twin agrees, word for word
```

Every form has one made-up word in `../pinned.tsv`, with the text the decoder prints for it;
`test_pinned.py` fails when a form has none, so a new form needs its line. The fields of the
word take values distinct from each other and from the form's `dflt`, so that a field moved
or resized changes the text. `test_firmware.py` decodes the user's own firmware and transfer
captures at run time and checks that every form they use is pinned.
