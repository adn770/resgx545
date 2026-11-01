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

The fork (github.com/adn770/radare2, branch `arch-usse`) carries the same core in-core; run
its asm tests with `r2r test/db/asm/usse`. Its in-core `usse` plugin takes precedence over this
out-of-tree one, so keep them in sync.

## Upstreaming to radareorg/radare2

The plugin is structured to drop into the r2 tree with minimal change:

1. Create `libr/arch/p/usse/` containing `plugin.c` (this `arch_usse.c`, renamed), plus the core
   `usse.c` + `usse.h`. The core is already radare2-free and self-contained.
2. Add the build entries: a `usse` stanza in `libr/arch/p/meson.build` and the `arch.usse`
   entry in the plugin list (`libr/arch/meson.build` / `meson_options.txt`), mirroring an
   existing small arch (e.g. `chip8`).
3. The plugin already follows upstream conventions: `const RArchPlugin r_arch_plugin_usse`,
   `RLibStruct radare_plugin` guarded by `R2_PLUGIN_INCORE`.

Clean-room note for the PR: the decoder was written independently. No vendor source is
copied or vendored — only our own code is contributed.

## Licence

`arch_usse.c`, like the decoder core it wraps, is MIT. radare2 is LGPL-3.0; MIT code is
compatible with it, so the plugin can be loaded by, and contributed to, radare2.
