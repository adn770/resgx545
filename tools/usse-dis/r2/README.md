# radare2 `usse` arch plugin — PowerVR SGX Series-5 USSE

A radare2 `RArch` plugin that disassembles PowerVR SGX **USSE** code (Series-5 / SGX5xx). There
is no PowerVR/USSE architecture in upstream radare2 today — this is intended to be contributed.

All decoding lives in the standalone clean-room core (`../usse.c` / `../usse.h`); this directory
is just the radare2 adapter (`arch_usse.c`): it maps the decoder to `RAnalOp` — mnemonic, op
type, and branch targets (so r2's control-flow analysis and graphs work).

## Build & install (out-of-tree)

`R2_PREFIX`, the prefix of your radare2 install (its `include/libr` and `bin/radare2`), is a
required input; the Makefile stops without it.

```sh
make R2_PREFIX=<your radare2 prefix>            # -> arch_usse.{dylib,so}
make R2_PREFIX=<your radare2 prefix> install    # copies to $(radare2 -H R2_USER_PLUGINS)
```

## Use

```sh
radare2 -a usse -b 32 "$RESGX545_DATA_PRIVATE"/firmware/images/images/00_ukernel.bin
# then: pd 40      (disassemble), aa; agf   (analyze + graph — branches resolve)
```

`pd` prints the text of `usse-dis`; a word no form decodes shows as `invalid`.
`ba`/`br`/`ba.savelink` set `op->jump`/`fail` and type
(JMP/CJMP/CALL), so jump arrows and function graphs render. Every other instruction gets the
type of its class (`usse_classify` in `../usse.h`, pinned by `../test_usse_api.c`): in the
control and special class, the moves and the writes of the unit's state are `mov`, `ldr` and
`str` are `load` and `store`, the fences, mutexes, waits, cache control and `phas` are `sync`,
and the emits and the visibility tests, which send work to other units, are `io`.

## Assemble

The plugin also assembles, through the same form table: any text the
disassembler prints assembles back (`rasm2 -a usse -b 32 'ldr r0, #7, drc0'`, `pa`, `wa` in
radare2). r_asm lowercases what it assembles, so the form engine matches letters in either
case. The encoder is the form engine's (`usse_form_encode` in `../usse_form.c`), so the
plugin needs nothing beyond `tools/usse-dis`. `test_r2.py` round-trips several hundred random
decodable words through `rasm2` in both directions (needs `R2_PREFIX` set and the plugin
installed; it skips otherwise, naming what to set).

## In-tree: the radare2 fork

The radare2 fork (github.com/adn770/radare2, branch `resgx545`) carries this plugin in-tree, as
a few commits meant for upstream on a radare2 master of October 2026. `libr/arch/p/usse/` holds
`plugin.c` (this `arch_usse.c`, with local includes and `.author` set to resgx545) and the core
files unchanged: `usse.c`, `usse.h`, `usse_form.c`, `usse_form.h`, `usse_table.inc` and
`forms/*.inc`. The plugin is registered in both of radare2's build systems (meson, and make
through `libr/arch/p/usse.mk`), and `test/db/asm/usse` holds one r2r test per form, made from
the words of `../pinned.tsv`, and `test/db/anal/usse` the op types and branch targets of a
few made-up words.

The branch also carries what has no out-of-tree twin here:

- **a PDS plugin** (`arch pds`, `bits 32`), in `libr/arch/p/pds/`: `plugin.c` and the core
  files unchanged, `pds.c`, `pds.h`, `pds_table.inc` and `usse_form.h` (the PDS forms run on
  the USSE plugin's form engine). It disassembles and assembles PDS words as `pds-dis` prints
  them and sets their op types and branch targets (`pds_classify` and `pds_branch` in
  `../pds.h`); `bra`/`call` targets count 4-byte instructions from the first one after the
  data segment, so load the instructions at address 0. `test/db/asm/pds` holds one r2r test
  per PDS form from `../pinned.tsv`, `test/db/anal/pds` the types and targets;
- **a pseudo syntax for each** (`e asm.pseudo=true`; `pseudo.c` beside each plugin, registered
  as the `usse` and `pds` asm parsers, so radare2 no longer warns that it finds none): the
  instructions whose text says all they do, without flags, read as assignments and returns
  (`mov r1, r2` as `r1 = r2`, `and`/`or`/`xor`, `lapc` as `ret`; PDS `mov32` and `rtn`),
  under `if (p0)` when predicated; everything else keeps its text (`test/db/cmd/cmd_pseudo_*`).

Emulation (ESIL) joins the branch in a later phase.

```sh
git clone -b resgx545 https://github.com/adn770/radare2 && cd radare2
meson setup b --prefix=<prefix> && ninja -C b install
# or: ./configure --prefix=<prefix> && make install
cd test && PATH=<prefix>/bin:$PATH r2r -L db/asm/usse db/asm/pds db/anal/usse db/anal/pds \
    db/cmd/cmd_pseudo_usse db/cmd/cmd_pseudo_pds
```

A radare2 built from that branch has `usse` in-core, and the in-core plugin takes precedence
over this out-of-tree one: use one or the other. With `R2_PREFIX` set to that build's prefix,
`test_r2.py` round-trips its random words through the in-core plugin.

The plugin follows upstream's conventions (`const RArchPlugin r_arch_plugin_usse`,
`RLibStruct radare_plugin` guarded by `R2_PLUGIN_INCORE`). It was written independently; no
vendor source is copied or vendored.

## Licence

`arch_usse.c`, like the decoder core it wraps, is MIT. radare2 is LGPL-3.0; MIT code is
compatible with it, so the plugin can be loaded by, and contributed to, radare2.
