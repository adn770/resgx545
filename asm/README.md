# asm — our own GPU programs

USSE and PDS programs we wrote, in the syntax of `tools/usse-asm` (README there): the single-ISA
sources assemble with the C or Rust `usse-asm`/`pds-asm`, and `sgx-asm` sources (`.section`)
put several of them into one image set with their patch records.

| directory | what | used by |
|-----------|------|---------|
| `transfer/` | the nine transfer-queue templates; `transfer.s` = all of them for `sgx-asm` | `tools/fwcutter/ours.py`, `tools/fwcutter/asmmap.py` |
| `tutorial/` | the USSE tutorial's own cases (`doc/specs/usse_tutorial.md`) | `tools/usse-asm/test_tutorial.py` |

Every `.s` here without `.section` is cross-checked between the C and Rust assemblers
(`crates/sgx-tools/tests/asm_cli.rs`). The programs of the first triangle and the user-space
library that embeds these sources arrive with the render path unit.

Transfer-queue templates, `transfer/` (the firmware format, `doc/specs/fw_format.md` §9-§11;
the transfers they run, `doc/specs/transfer.md` §4):

| file | template | what it does |
|------|----------|--------------|
| `use_fill.s` | `USE_FILL` (0) | writes the fill colour (patched immediate) to `o0` |
| `use_sec.s` | `USE_SEC` (1) | the empty USE secondary program |
| `use_eot.s` | `USE_EOT` (2) | end of tile: the PBE state words to the pixel back end |
| `use_eor.s` | `USE_EOR` (3) | end of render |
| `pds_prim.s` | `PDS_PRIM` (4) | kicks the fill shader (`DOUTU`) |
| `pds_sec.s` | `PDS_SEC` (5) | kicks the USE secondary program |
| `pds_pixevent.s` | `PDS_PIXEVENT` (6) | dispatches pixel events: PTOFF, end of tile, end of render |
| `use_copy.s` | `USE_COPY` (7) | moves the fetched texel `pa0` to `o0` |
| `pds_prim_1src.s` | `PDS_PRIM_1SRC` (8) | kicks the copy shader, the iterator and the texture fetch |

The comments explain each instruction from the documented semantics. The programs keep the
values the driver patches (`doc/specs/fw_format.md` §9.4, §10.4) at 0, as the templates do, so
that the existing patch records apply unchanged; `use_eot.s` keeps its four `mov`s on `r0`
for the same reason (the patch adds the register number).

## Why they match the closed templates bit for bit

Assembled, the nine programs equal the transfer templates in the closed `libsrv_um.so` word
for word (`tools/fwcutter/test_ours.py`, by hash and, with the user's library, byte for
byte). That identity is the interoperability goal, not a copy of anyone's expression. Each
program is short (a few to a few dozen instructions) and its form is dictated by the hardware
and by the interface around it: the registers the PDS and the pixel back end read and write,
the instruction slots the driver patches through the existing patch records, and the
assembler's canonical choice for every bit an instruction ignores. For the same job on the
same hardware there is in practice one way to write each of them.

We wrote the source ourselves, instruction by instruction, from our own understanding of
what each program must do (the instruction set as our disassembler decodes it, and the
hardware behaviour the specifications under `doc/specs/` document), so that our driver and
firmware file interoperate with the EDM's transfer interface. The commented `.s` files are
the preferred form for modification. Being bit-identical lets one loader, one set of patch
tables (`tools/fwcutter/facts.py`) and one test serve both template origins, and shows the
programs equal to the templates the closed stack sends to the GPU. Should identity
ever stop being useful, the programs can be rewritten to be functionally equal without
being bit-identical.
