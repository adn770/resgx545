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
(JMP/CJMP/CALL), so jump arrows and function graphs render.

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
the words of `../pinned.tsv`. The branch disassembles and assembles USSE only; the PDS and
emulation join it in later phases.

```sh
git clone -b resgx545 https://github.com/adn770/radare2 && cd radare2
meson setup b --prefix=<prefix> && ninja -C b install
# or: ./configure --prefix=<prefix> && make install
cd test && PATH=<prefix>/bin:$PATH r2r -L db/asm/usse
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
