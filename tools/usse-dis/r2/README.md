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

Both plugins also carry a register profile and ESIL ("Emulation" and "PDS emulation"
below).

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

## Emulation (ESIL, fork only)

The fork's in-core plugin also carries a register profile (`regs.h`) and ESIL, so `aes`/`aesu`/
`aae` emulate; this out-of-tree plugin decodes and assembles only. The ESIL is built from the
decoded text (`libr/arch/p/usse/plugin.c`) and is deliberately conservative: an instruction gets
ESIL only when every operand is a register of the profile or an immediate, every modifier has a
pinned meaning and every flag is a scheduling flag (`.skipinv`, `.syncs`, `.nosched`, `.end`)
that does not change what one instance computes. Tests: `test/db/esil/usse` in the fork. What an
instruction does is the hardware's: items marked **[HW]** were measured on the GPU with our own
programs (`tools/usse-asm/probe.py`, the tables in `probes/`, "Hardware probes" below), and the
simulator (`crates/sgx-sim`) holds the same vectors.

Modelled:

- `mov`, `and`/`or`/`xor` (also with an inverted `~src2`), `shl`/`shr`/`rol`/`asr` by an
  immediate or by a register: **[HW]** an amount of 32 and over gives 0 for `shl`/`shr` and
  the sign for `asr`, and `rol` takes it mod 32; `~` complements the amount first;
- the **test group** on `chan0`: `<op>.test<S><a|o><Z>.chan0 dst, pN, src1, src2` computes the
  result, sets `pN` and writes `dst` unless it is `!reg`. Sign test `n` is bit 31 (the firmware
  tests flag bits by shifting them to the top and testing the sign), **[HW]** `p` is its
  complement (`>= 0`) and `t` is true, so an `o` join with a `t` side is always true; zero tests
  `z`/`nz`. For the bitwise group, the shifts, `iadd32` and `iaddu32` on the 32-bit result:
  **[HW]** the adds take src1's low 16 bits, sign-extended (`iadd32`) or zero-extended
  (`iaddu32`), plus the 32-bit src2 (the firmware's increment is an `iaddu32` of an immediate 1
  and the counter), and `iaddu32` is unsigned: `n` is never and `p` always true. The lane
  operations, `isub16`, `usub16`, `iadd16`, `uadd16`, `imul16` and `umul16` on 16-bit lanes and
  `iadd8`, `isub8` and `imul8` on bytes: **[HW]** each lane's result wraps (an immediate stands
  in both 16-bit lanes; the byte forms take none), but the test sees the lane unwrapped, signed
  or not by the operation, and a multiply its whole product; 16-bit lanes are channels 0 and 2,
  bytes 0-3; `usub16` only with the sign test `t`. The float tests `fadd`, `fsub` and `fmul`:
  **[HW]** the result's sign and zero at channel 0 (a zero tests positive), `fmul` giving +0 for
  -0; with a discarded result (`!c0`) a test of both the sign and zero gets no ESIL;
- **[HW]** `ima16.{s,u} d, a, b, c[.neg], u16, u16`: `a * b + c` (or `- c`) in each 16-bit lane,
  wrapping; an immediate `b` or `c` is in both lanes;
- `imae.{u,s} d, a.{low,high}, b.{low,high}, c, u32` (`d = a16 * b16 + c`, halves zero- or
  sign-extended; the firmware uses it as an add) and `ima32.{u,s} d, a, b, c` (low 32 bits of
  `a * b + c`);
- `fmad d, a, b, c`, `frcp`, `frsq`, `fsqrt`, with
  `.neg`/`.abs`/`.neg.abs` (`-|x|`) source modifiers acting on the sign bit. **[HW]** `fmad`
  rounds `a * b` to binary32, then the sum, both to nearest even (it is not fused), and flushes
  denormal inputs, product and result to a zero of their sign; the float sources of `frcp`,
  `frsq` and `fsqrt` are flushed too (`frcp` of a denormal is `+inf` on the hardware);
- `ba`/`br`, `.savelink` and `lapc`: `pclink` holds an **instruction index**, the next
  instruction's (the firmware builds a return address as an index, moves it into `pclink`, and
  the return goes to that instruction), so `lapc` jumps to `pclink * 8`;
- loads and stores as in `../README.md` (immediate offsets), and **[HW]** with a
  register offset (`ldad d, [b,+o]`, `[b,-o]`, `ldad.fetchN d, [b,+o]`, `stad [b,+o], s`):
  the offset register holds two unsigned 16-bit halves whose product is the offset in bytes
  (the firmware ORs a stride of 4 into the top half of a dword index), added modulo 2^32; a
  fetch starts one element after it, as with immediates; a load from an address that is not
  a multiple of 4 reads those bytes, a store there does not land;
- **SGX register-file accesses**: `ldr rD, idx, drcN` and `str idx, src`, with the dword index
  `idx` an immediate or a register (offset = idx × 4). ESIL places the register file in a
  window above the USSE's 32-bit address space, at `0x100000000 + offset`
  (`USSE_CR_ESIL_BASE`; `esil.addr.size` must stay 64, the default). Pinned by the hardware
  (index 7 returns the core id, index 801 the page-directory base register) and by the
  firmware, which programs its registers this way (`../regtouch.py`) and, for the register
  forms, loads the index into a register first. **[HW]** `ldr` masks a register index to 14
  bits (`0x4007`, `0x10007`, `0x40007` read the core id);
- **[HW]** **write masks** (`d.xyzw` and every other mask on `mov`, the bitwise group and the
  shifts, `frcp`/`frsq`/`fsqrt`, `movc` and the packs): component k writes `d + k` from every
  register source `+ k` (an immediate stays), a repeat of four with gaps; mask 0 (`d.`) writes
  nothing and gets no ESIL;
- **[HW]** **float repeats with `.incsXYZ`**: `fmad`, `fminmax` and `fmaxmin` `.repeatN`; X, Y
  and Z let source 0, 1 and 2 advance, the destination always advances, and without `.incs`
  every source does; the iterations run one after the other, the order measured on `mov`
  repeats [infer for the floats];
- **[HW]** **dot products**: `fdp.repeatN d, a, b` writes the `N`-term dot product to `d + N -
  1` only, each product rounded to binary32 and flushed, then the sums in order, each rounded;
  `fddp.repeatN d, iM, s0, s1, s2` writes `s0·s1` there and `s0·s2` to `i0`/`i1` (none when `d +
  N - 1` is one of the sources the second product reads);
- **[HW]** **`fminmax d, a, b, c` = `min(max(a, b), c)`** and **`fmaxmin` = `max(min(a, c),
  b)`**, IEEE minNum/maxNum (a NaN loses, `-0 < +0`) on the flushed bit patterns, through `d`
  (none when `d` is the operand the second step reads);
- **[HW]** **`movc.<i8|i16|i32|i10|flt>.<tz|tnz|tn|tp|z> d, s0, s1, s2`**: a select per lane
  of `s0` (`.i10`: three 10-bit lanes, bits 30-31 cleared; `.flt`: the float with denormals as
  zero, a NaN failing all but `tnz`); **`movmsk.<mask|u8|flt|flt16> d, s1, s2.c`**: `s1` into
  `d` when bit 0 or 7 of byte `c`, the float or the half `c` (bits 0-15, 8-23, 16-31) is at
  least 0.5;
- **[HW]** **packs** `pck<u8|s8|o8|u16|s16|c10>f32[.scale]` with byte masks, and **unpacks**
  `unpckf32<u8|s8|o8|u16|s16>[.scale]` and `unpck<u8|s16|u16><s8|u8>`: lanes s1, s2, s1, s2
  (bytes) or s1, s2 (halves), the measured byte-mask rule, saturation, `.scale` factors
  (255, 127 clamped to ±127, 127 + 128 clamped to 1..255, 65535, 32767 clamped to ±32767,
  `c10` 255 clamped to ±510), the rounding mode unscaled and nearest even scaled, correctly
  rounded scaled unpacks with -1 clamped, `unpcku8s8` turning a negative into `0x7f`;
- `mov.repeatN d, s`: `d+i = s+i` for `i < N`, the increments a task starts with. Our vertex
  and state-copy programs (`asm/tri/use_vtx.s`, `use_mtest*.s`) copy their attributes to the
  outputs this way and render correctly on the hardware. **[HW]** The iterations run one after
  the other in ascending order, so overlapping ranges propagate (`mov.repeat3 r2, r1` copies
  `r1` to `r2`-`r4`), and a predicate is tested once for the whole instruction;
- **[HW]** the index register: `mov i.l, src`, and moves through `r[il + #n]` and `sa[il + #n]`
  (the firmware reads a secondary attribute this way): the register is the bank's `i.l + n`-th,
  and bits 10 and up of `i.l` are ignored. ESIL cannot name a register from a value, so these
  are chains of conditionals over the bank's registers in the profile (`r0`-`r63`,
  `sa0`-`sa31`, plus the profile registers `il`/`ih`); an index outside them moves nothing;
- **[HW]** the **colour operations** on 8-bit operands (`sop2`, `sop3`, `lrp`, `sop3c`,
  `sop2wm`): bytes 0-2 colour, byte 3 alpha, `x` standing for `x/255`; `add`/`sub` sum the
  exact products, divide by 255 once, round and saturate; `min`/`max` compare the sources;
  `asat`, `s2scale` (doubles the result), `zeros` (a signed `s2`), `comp`, `neg`, the lerps by
  `s0`/`s0a` and `sop2wm`'s byte mask as measured;
- **[HW]** the **integer dot products** `u8dot3`/`u8dot4`/`u16dot3`/`u16dot4` and their `off`
  forms: byte products summed (`off`: `(x - 128)(y - 128)`), scaled by `Cx`/`Ax`, rounded and
  saturated, `u16` as a 15-bit fraction in both halves; `u8dot3`'s `aadd`/`asub`/`alrp`/
  `alrpc` alpha;
- **[HW]** `fpma` = `c0 + c1 × c2` on 8-bit channels; `efo` (the printed dataflow, every
  product and sum rounded to binary32, the destination's `i0`/`i1` read before the writes; not
  `.gpiext`, see below); `fadm` = `a·c + b·c`, `fmsa` = `a·a + b·c`, `fsubflr` =
  `a - floor(b)`; `statomic`; `movmsk.<fmt>.smsk` (bit 0 of `s0` too, except for `.mask`).
  These helpers evaluate each operand once with `DUP`/`SWAP`: ESIL keeps the strings it stacks
  in a ring (32 bytes per stack slot), so a value left on the stack while hundreds of others are
  pushed is overwritten and the expression fails;
- **[HW]** the **test channels**: one result per channel, the 32-bit result as channel 0 and a
  16-bit op's halves as channels 0 and 2, a channel without a lane testing as a positive
  non-zero value; `chan0`-`chan3`, `andall`/`orall` (all four), `and02`/`or02` (0 and 2);
- **[HW]** `rlp d, s, pN` = `s << 1 | pN`, then `pN` = bit 31 of `s`, `p4` and up aliasing
  `p0`-`p3`; `adif` (`|a - b|` per byte) and `adifsum` (their sum plus a 16-bit half of `s0`);
  `unpcku16c10`/`unpcks16c10`, which put lane 0's bits 4, 6 and 8 into bits 15, 1-14 and 0
  whatever the selects; `sop2`, `fpma` and the integer dot products with `.repeatN` (every
  operand advances);
- **[HW]** `idiv` (the unsigned quotient to `d`, the remainder to `d + 1`, all ones for a zero
  divisor); `imae` with `.usat`/`.ssat`, `.rsN`, `u16` (sign-extended) and `z16` sources and
  `coe`/`cie` carries through `iN`; `ima32`'s `cie`; `ima16` with `u8`/`s8`/`o8` sources; `ima8`
  (`x + y * z` per byte, `.sat`); shift immediates of 32 and over and `~` amounts; the `Pn`
  predicate (never runs); bank-7 numbers past `i3` lose their ESIL, as they read the other
  pixels of the quad;
- **[HW]** **dual issue** (`fmad r10, r1, r2, r3+fadd i0, i1, i2`) for the pairs that
  co-issue cleanly (a `mov`, `fmad`, `ima32`, `fadm`, `fmsa`, `fssq` or `fminmax` primary with
  a secondary that needs no unit the primary uses): both operations read before either
  writes, the secondary wins a shared destination, `.repeat2` runs both (the primary's
  operands advance), and the predicate covers both; a word where each operation writes what
  the other reads gets no ESIL. Pairs that share a unit mix their results; the ones measured
  (a second product, the primary's result, `fminmax`'s `max(a, b) - c`, `ima32` as a secondary
  with two 16-bit lanes) are modelled, `fmad` with `fmad16` or `fmaxmin` is not.

The window is plain memory. Map some to emulate the firmware, and load the register names as
flags (`harness/ukernel-extract/make_r2.sh` writes a script that adds one per register the
firmware touches, `../regtouch.py --r2-flags`; the script is generated and not tracked):

```sh
UK="$RESGX545_DATA_PRIVATE"/firmware/images/images/00_ukernel.bin
radare2 -a usse -b 32 -i sgx545_ukernel.r2 "$UK"
[0x00000000]> o malloc://0x10000 0x100000000
[0x00000000]> wv4 0x01150000 @ sgx.EUR_CR_CORE_ID
[0x00000000]> s edm.getmiscinfo; aei; aeim; aeip; aes 3; ar r3     # 0x01150000
```

Registers with side effects (status, clear-on-read, the kick and event registers), the `drc`
wait of `ldr` and `str`, and register indexes of 0x4000 and over are not modelled. The MOE state
that `smlsi`/`smoa`/`smbo`/`smr` set (other increments for repeats) is not tracked either; no
repeat of the microkernel follows one. **[HW]** `smlsi #I0, #I1, #I2, #I3, ...`: `I0` is the
destination's increment and `I2` the source's for a following `mov.repeatN` (`I1`, `I3` do not
affect it), so tracking it is possible once a program needs it.

Floats are IEEE binary32 bit patterns in the 32-bit registers, computed through ESIL's doubles
(`F2D` ... `D2F`, round to nearest even). The rounding and the flushing above are the
hardware's **[HW]**; what is left approximate: `fmad`'s sum goes through a double, so a sum of
very different magnitudes can round twice; `frcp`/`frsq`/`fsqrt` are correctly rounded in the
ESIL but only within one ulp on the hardware (**[HW]**: 46, 42 and 44 of 48 random inputs
exact, the others one ulp off, at most 0.65 ulp from the true value); and special values are
not modelled, because r2's `D2F` returns the low half of a double for an infinite or NaN
result (the hardware gives `+inf` for `frcp` of 0 and `frsq` of 0, `-inf` for `frcp` of -0,
and the NaN `0x7fffffff` for `frsq`/`fsqrt` of -1).

On the SGX545 microkernel (6637 words), the ESIL covers about 84% of the words, and every
word with a register effect but three; `esil_check.py survey` prints it per base mnemonic. Of
the rest, 1043 words have no register effect to model (the data fences and cache flushes, the
`nop`s, `smlsi`, `phas`, `ci`/`cfi`, `lock`, `emitpds`). The other three are two fetches of
two registers whose base register is also a destination, and a store whose data is an indexed
register. Our own pixel and vertex programs (`asm/*/use_*.s`) are covered the same way, except
for a predicated fetch that never runs and whose base is also its destination.

`esil_check.py` measures this and checks the ESIL (tests: `test_esil_check.py`); point
`R2_PREFIX` at an install of the fork:

```sh
R2_PREFIX=/path/to/fork-prefix ../../../.venv/bin/python esil_check.py survey uk.bin  # table
R2_PREFIX=... esil_check.py tokens uk.bin       # every token an operator, number or register
R2_PREFIX=... esil_check.py cross --count 3000  # random modelled instructions vs a Python model
```

`esil_vectors.py` holds the ESIL to the hardware itself: it runs the instruction vectors (the
probe tables' readbacks in `$RESGX545_DATA`, decoded by `crates/pysgx` for the `--only` filter,
with the simulator's skip list and its exclusion of the triangle-host runs applied) under the
fork's emulation, in the probe harness's scratch buffer, and compares
`o0` and the stored dwords with the readback; a program with a register-changing word that has
no ESIL counts as "no ESIL" for that mnemonic (`test_esil_vectors.py`). The vectors of the test
group, with the lane and float tests, all match. Of the words in the vectors the simulator
matches, some change registers without ESIL: the half-float and `c10` arithmetic (`fmad16`,
`sop2`/`fpma` with `.c10` operands, the f16/c10 packs), and what one instance cannot compute
(`fdsx`/`fdsy`, `efo.gpiext`, the near-value functions, sampling); the table the script
prints counts them per mnemonic under "no ESIL".

```sh
R2_PREFIX=... ../../../.venv/bin/python esil_vectors.py --only iadd8,fadd --show
```

Deliberately not modelled, because the semantics are not pinned by the text, the firmware or
probing (an instruction's text does not say what it does):

- **repeats** other than those of `mov`, `fmad`, `fminmax`/`fmaxmin` and `fdp`/`fddp`: of the
  other operations, after `smlsi`/`smoa`/`smbo`, and `.partial` / `.quadlead`; the repeats of
  `frcp`/`frsq`/`fsqrt`, `movc` and `.c10` operands too;
- write mask 0, write masks on the test group;
- **`i3`** and the bank-7 numbers past it, which read other pixels of the 2x2 quad and drop
  writes **[HW]**, and everything else that reads another pixel: `fdsx`/`fdsy` (coarse
  derivatives over the quad) and `efo.gpiext` (writes funnelled into the top-right pixel's
  `i0`) **[HW]**; ESIL emulates one instance;
- through the **index registers**, the `o` and `pa` banks and indexed operands of anything but
  `mov` (a store whose data is an indexed register);
- register-offset **word** loads and stores (`ldaw`/`staw`), with pre/post increments, and the
  negative fetch (`ldad.fetchN d, [b,-o]`);
- `usub16`'s sign tests, the mask forms (`.bmsk`/`.wmsk`/`.dmsk`), and every 8-bit, float
  and 16-bit multiply/add test not listed above (**[HW]** their channels are bytes, the value,
  or the lanes before they are cut to 16 bits);
- `ima32` with modifiers or a second destination; `.usat` with a `u16` source 2;
- floats with immediates, `.flt16`/`.c10`/swizzled sources, `.tpres`, `fmad16` (half-float
  arithmetic in ESIL is not cheap), `fdpc`/`fddpc` (where the clip-plane result goes is not
  known) and `fexp`/`flog`/`fsin`/`fcos` (no ESIL operation; the hardware computes `log2`,
  `2^x` and quarter turns);
- `.c10` operands of the colour operations, the dot products and `fpma` (pinned for every
  colour operation but `sop3c`, not modelled: each lane needs its own clamp);
- the **pack/unpack** forms with `f16` results or sources and `c10` sources, and `.scale` on
  the integer-to-integer unpacks; NaN and infinite pack inputs; `bilin`, `firv`, `firh`;
- sampling (**[HW]**: filters, address modes, layouts, formats, conversions and PCF follow
  the four state words, but ESIL would have to walk the texture layout), `eldd`/`eldq`
  and the special class.

Registers outside the profile (`r64`+, `pa32`+, `sa32`+, ...) never appear in the ESIL, so most
random words get none: on a uniform sample of 200k words, under 0.5% of the decodable ones do.

### Hardware probes

What the text left open was asked of the GPU: `tools/usse-asm/probe.py` runs a table of probes
(`probes/`), each a client fill on the render node whose pixel program, assembled from our own
source, presets its inputs with `mov rN, #imm`, runs the instruction under test and writes one
result to `o0` (a predicate as `mov r30, #0` then `pN mov r30, #1`); the host reads the surface
back, and a 64 KiB scratch buffer for loads and stores. Every case runs as its own fill and its
own process. A probe is settled when exactly one of its hypotheses predicts every case; all
were, except where noted. The readbacks are in the data repository, and `probe.py eval
raw.txt` re-reads one. **[HW]** throughout:

- **Test sign `p`** is `>= 0`: `shl.testpat`/`and.testpat` set `p0` for 0, 1 and 0x7fffffff,
  not for 0x80000000.
- **`t` in a join** is true: `and.testnot`, `.testtoz`, `.testtonz` set `p0` for every input.
- **The adds** (`iadd32`, `iaddu32`) add src1's low 16 bits, sign- or zero-extended, to the
  32-bit src2: `0x12345678 + 0x11111111` gives `0x11116789`, `iadd32 0xffff + 1` gives 0, while
  `#1 + r` is the plain increment the firmware uses. Their tests look at that 32-bit result;
  `iaddu32`'s `n` is never and its `p` always set (also for `0x80000000`).
- **`isub16`/`usub16`** subtract both 16-bit lanes, wrapping, with no saturation: `0x12340005 -
  #1` is `0x12330004`, `0 - #1` is `0xffffffff`, `0x00050007 - 0x00010002` is `0x00040005`, and
  `usub16 0 - #1` is `0xffffffff`. `chan0` tests the low lane: `z` from its 16 bits, `n` from
  bit 15 (not bit 31), `p` is `>= 0` on it.
- **`ima16 ..., u16, u16`** computes `a * b + c` (`- c` with `.neg`) in each lane, wrapping:
  `0x00020005 * #3 - 0x00010007` is `0x00050008`, `0x0000ffff * #3` is `0x0000fffd`; immediates
  are in both lanes, a register `b` or `c` lane by lane.
- **Shifts by a register:** `shl`/`shr` by 32, 33, 64, 0x100 or 0xffffffff give 0, `asr` gives
  the sign, `rol` takes the amount mod 32; `shl.testnat` the same.
- **The index register:** `mov r30, r[il + #n]` reads register `i.l + n` counted from `r0`
  (unit one register; `#n` adds), and `mov r[il + #n], r21` writes it. Bits 10 and up of `i.l`
  are ignored (`0x401`, `0x40001`, `0xfffffc02` index `r1`, `r1`, `r2`); indexes 0x21 to 0x201
  past the program's 32 temporaries read the next instances' registers [infer: the share of
  pixels with other values grows with the index]. `sa[il + #n]` is the same on the
  secondaries, measured by writing `sa0`-`sa7` from the pixel program; about 1% of the pixels
  read another secondary there, as expected when 2048 instances write shared registers.
- **Register offsets of loads and stores:** the offset register `o` gives `(o >> 16) * (o &
  0xffff)` bytes, both halves unsigned: `0x00040003` is +12, `0x00010001` +1 (an unaligned load
  reads those bytes), `0x01000001` +256, `0x00000005` +0; with a top bit set the address leaves
  the buffer and faults at base + the unsigned product, modulo 2^32 (`0xffffffff` faults at base
  - 0x1ffff). `[b,-o]` subtracts; `ldad.fetch2 [b,+o]` starts one element after, as the
  immediate forms do. `stad` matches, but a store at a byte offset of 1, 2 or 3 lands nowhere in
  the buffer and does not fault.
- **`ldr rD, rI`** masks the index to 14 bits: 0x4007, 0x8007, 0x10007 and 0x40007 read the core
  id like 7.
- **Repeats:** `mov.repeat2 r2, r1` leaves `r3 = r1`, so iterations run one after the other,
  ascending (`mov.repeat3 r1, r2` gives `r1 = r2`, `r2 = r3`, `r3 = r4`); `p0 mov.repeat2` with
  `p0 = 1, p1 = 0` writes both registers and with `p0 = 0, p1 = 1` neither: one predicate.
  `smlsi #I0, #I1, #I2, #I3, ...` before `mov.repeat2 r20, r10`: `I0` is the destination's
  increment, `I2` the source's (0 repeats a register, 2 skips one), `I1`/`I3` change nothing.
- **Floats:** `fmad` rounds to nearest even (`(1+2^-12)^2` and `(1+2^-12)(1+3*2^-12)`, both
  ties, round to even, also when negative), and rounds the product before adding:
  `(1+2^-12)^2 - (1+2^-11)` is 0, not 2^-24; 48 random triples agree with that model. Denormal
  results and inputs become zeros of their sign (`2^-70 * 2^-70` is 0, `-2^-70 * 2^-70 + -0`
  is -0, `2^-140 * 2^100` is 0). `frcp`, `frsq`, `fsqrt` are within one ulp but not correctly
  rounded (46, 42, 44 of 48 random normals exact); `1/3`, `1/5`, `1/sqrt(2)`, `sqrt(3)` are
  exact. Specials: `frcp(0) = +inf`, `frcp(-0) = -inf`, `frcp` of a denormal `+inf`,
  `frsq(0) = +inf`, `fsqrt(0) = 0`, and `frsq`/`fsqrt` of -1 give the NaN `0x7fffffff`.
- **Other channels:** `and.testtaz.chan1`..`chan3` and `isub16.testtaz.chan1` clear `p0` (and
  leave `p1`-`p3`) whatever the input, even when the tested value is zero; what they test is
  not known.

Masks, repeats, dot products, min/max, movc and packs (mostly through a template that stores
sixteen registers to the scratch buffer, so that a case sees every register it writes; all
settled but `movmsk-smsk`, which is recorded). **[HW]** throughout:

- **Write masks:** all 16 masks on `mov`, `or`, `and #0xff` and `frcp`, and masks on `movc` and
  a pack: `mov r10.xz, r1` writes `r10 = r1`, `r12 = r3`; `frcp r10.y, r1` writes `r11 =
  1/r2`; mask 0 writes nothing. A component is a register of a group of four, not a byte.
- **`.incsXYZ`:** `fmad.repeat2.incs001 d, a, b, c` gives `d = a·b + c`, `d+1 = a·b + (c+1)`;
  `incs010` advances `b`, `incs100` `a`; without `.incs` all three advance; `.incs000` repeats
  the first operation into `d+1`. The same for `fdp` (no source 0), `fddp`, `fminmax`.
- **`fdp`:** `fdp.repeatN r10, r1, r5` over `(1, 2, 4, 8)·(1, 16, 256, 4096)` writes 1, 33,
  1057, 33825 to `r10`, `r11`, `r12`, `r13` for N = 1-4 and leaves the others; 6 crafted and
  42 random cases fit "products rounded, added in order, each sum rounded" and no other order
  (`(1+2^-12)^2 - (1+2^-12)(1+2^-11)` is `-2^-12(1+2^-11)`); `inf·0` gives `0x7fc00000`,
  products of denormals or into the denormal range give 0, `-0 + -0` is -0. `fdpc` gives the
  same values and leaves `p0`-`p3` as they were. `fddp d, iM, s0, s1, s2` writes `s0·s1` and
  `s0·s2`; `fddpc` does not advance its sources.
- **Internal registers:** `mov i0..i2, ...` then `mov r, i0..i2` reads them back, and the next
  case, another process, reads the same values; `i3` always read what `i0` held, and a write to
  it changed nothing.
- **`fminmax`/`fmaxmin`:** the six orders of 1, 2, 3 give 2, 2, 2, 1, 2, 1 and 2, 3, 2, 3, 2, 2,
  and 10 random triples agree: `min(max(a, b), c)` and `max(min(a, c), b)`. 22 triples with
  NaN, zeros, infinities and denormals fit minNum/maxNum (NaN loses, `-0 < +0`) and no
  compare-and-select order.
- **`movc`:** per lane by type, as above, over 12 values per test and type (the 10-bit lanes'
  bits 30-31 come out 0 whatever `s1` and `s2` hold there). `.flt` treats `0x00000001` and `-0`
  as zero and a NaN as failing `tz`, `tn` and `tp|z`.
- **`movmsk`:** `.mask` moves for bytes 0x01, 0x03, 0x0f, 0xff, not 0x02, 0x04, 0x10, 0x80;
  `.u8` for 0x80, 0x81, 0xfe, not 0x7f, 0x40, 0x01; `.flt` for 0.5, 0.75, 2.0, `+inf`, not
  0.49999997, -0.5, NaN, -0; `.flt16` the same threshold on its half.
- **Packs:** `pcku8f32` with each of the 16 byte masks (source 1 = 1.0, source 2 = 2.0) fits
  only the rule above; saturation of 300, -5, 65536, -40000; `.scale` of 0.75, 0.3, 1.5, 0.1,
  1.0, 0.2 and their negatives; `.scale` rounding ignoring the mode; 96 random `[0, 1)` values;
  `c10` lanes and clamps; `pckf16f32` truncating, keeping a denormal (1e-7 gives `0x0001`) and
  saturating 70000 to `0x7bff`, and with `.renable` rounding 1.0005 to 1.0 (nearest) or 2.0
  (up). Every byte value through `unpckf32{u8,s8,o8}.scale` and 16 halves through the 16-bit
  forms give the correctly rounded quotient.

Colour, integer dot products, fpma, efo and fmisc (all settled but `efo-gpiext-instances` and
`unpack-c10-int`, which are recorded; models fitted on about 2500 exploration fills first).
**[HW]** throughout:

- **Colour operations:** 1872 `sop2` results (factor isolation, every operation, 24 random
  forms) fit `op(s1 × f1, s2 × f2)` with one rounding of the exact sum over 255; `(40c02080,
  12345678)` through `s1, s2, add` gives `0x79` in byte 0, not the `0x78` of rounding each
  product. `min`/`max` compare the sources (`s1, s2, min` equals `zero.comp, zero.comp, min`);
  `s2scale` doubles the result, also of `min`/`max`; `zeros.comp` turns `s2` into `s2 - 0.5`
  (0xff gives 0x7f) in `add`/`sub`; a leading `comp` complements `s1`; `asat.comp` is
  `min(1 - s1a, s2a)` (not `1 - asat`). `sop3`'s `neg` gives `-op(s1 × f2, s2 × f1)`, its
  `arsop` `-op(s1a × f2, s2a × a)` (an `add` is then always 0), `alrp` and `lrp` lerp by `s0a`
  and `s0`, `sop3c` adds two selected products; `sop2wm` writes byte N with mask bit N. `.c10`
  operands read signed 10-bit lanes, clamped to ±510, the alpha from lane 0.
- **Integer dot products:** `u8dot4` of `0x01ff00fe` and `0xff00ff01` is `0x02020202` (509/255
  rounded, in every byte); `off` subtracts 128 from every byte (`(0x40c02080, 0x12345678)` gives
  `0x18`); `u16dot4` gives `0x7f7f` for `127 × 510 / 255²` of 32767; `Cx`/`Ax` scale before
  rounding; the `u8dot3` alpha forms read the sources' own alphas, also with `.comp` sources.
- **Floats:** `fmad16` is fused per half (20 random cases, half denormals kept), `.swzf32` reads
  the binary32 exactly (`8209.25 × 1.5 + 3` gives `0x7204`); `efo` with 3, 5, 7 and `i0`, `i1`
  = 11, 13 gives every printed sum (`m0 + m1` = 56, `i1 + i0` = 24, ...), `d = i0` is the old
  11, and 24 random cases round every product and sum; `.gpiext` left `i0`, `i1` alone and
  wrote `i2`, its multipliers reading `i2` and `i0` for the dumping instance, but whenever its
  multipliers or `d` read `i0`/`i1`, 512 of the 2048 pixels got another instance's value
  (`d = i0`: 56 instead of 11), every run; `fadm` of 3, 5, 7 is 56 and `fmsa` 44, and
  24 random cases each fit `a·c + b·c` and `a·a + b·c` with every product rounded; `fsubflr` of
  0.5 and 2.75 is -1.5. `flog` is `log2` (one ulp, or 2^-22 near 1), `fexp` `2^x` (two ulps),
  `fsin`/`fcos` take quarter turns with 15 fraction bits (96 random inputs each).
- **Leftovers:** min/max steps of two NaNs return the second (payload kept);
  `movmsk.<fmt>.smsk` needs bit 0 of `s0` too for `.u8`, `.flt`, `.flt16` but not `.mask` (16
  values of `s0`); `statomic` packs two signed bytes, negatives as 0, into both halves. No
  driver fault, hang, warning or memory growth in the runs, nor in repeated runs of the whole
  table.

Channels, rlp, dual issue, cache, video, the sampler and bank 7. `sgxfive-test probe --coords
--pixels` runs a probe as the shader of a copy whose source texel is the pixel's coordinates
and reads all 2048 pixels back, so a coordinate template gives every pixel its own inputs and a
result names the pixel it came from. **[HW]** throughout:

- **Internal registers:** with `i0`-`i2` = `(2048 + p) · 2^(12k)` per pixel `p`, every pixel
  reads its own back; `i3` reads the next pixel's `i0` in the 2x2 quad (top-left reads
  top-right, top-right bottom-left, bottom-left bottom-right, bottom-right top-left). A later
  task without writes sees whole quads of the earlier task's values, quad positions kept.
- **`efo.gpiext`:** the multipliers read the pixel's `i2` and `i0` for `i0` and `i1`, an `i0`
  write lands in its `i2`, and after an `i1` write only the top-right pixel's `i0` changed, to
  the bottom-right pixel's value; during such an instruction the top-right pixel's `i0` reads
  give the top-left pixel's `i0`, and in 11 of 40960 reads the value the top-left pixel was
  writing. 300 jobs of two clients run concurrently never mixed their values.
- **Dual issue:** 144 primary/secondary pairs on 1.5, 2.25, 3 and `i0`-`i2` = 5, 7, 11; the
  clean pairs give both results as if alone; `fmad i0, ...+fadd i1, i0, i2` reads the old
  `i0`, `fmad i1, ...+fadd i1, ...` keeps the secondary's 16; `.repeat2 ...+fadd i0, i0, i1`
  gives 19; `fadm`+`fmul` gives the primary's second product 6.75, `fminmax`+`fadd` the
  comparison's -0.75. The two-bit predicate, 12 states, acts as printed on both. `ima32`
  secondaries and the pairs that share a unit were measured on integer and float inputs.
- **Derivatives:** marks of the quad's pixels through `fdsx d, mark, 0` and `fdsx d, 0,
  -mark` give the top-right and top-left marks in all four pixels (`fdsy`: bottom-left).
- **Sampling:** a 16x16 texture in the scratch buffer, state words in `r20`-`r23`: texel
  `(3, 5)` at `(3.5, 5.5)/16` and at `(3.0, 5.0)/16`, `(2, 4)` just below, `(15, 15)` and the
  edge rows/columns outside `[0, 1)`; `.repeat2` and `.xy` fault at the fourth state word.
  Bilinear weights are truncated to 1/64, channels rounded to nearest; stride textures clamp,
  twiddled ones repeat, mirror, clamp or mirror once; Morton order `y` first; the formats' raw
  readings and the c10/f16/f32 conversions; PCF `texel OP reference`.
- **Test channels:** 360 cases (`iadd8`, `iadd16`, `iadd32`, `fadd`; `taz`, `nat`, `pat`);
  `rlp` over every predicate and value pattern; `adif`/`adifsum` on random bytes; every lane
  value of the `c10` to 16-bit unpacks; cache operations with each pixel on its own dword.
- **Integers:** `idiv` 100/7 gives 14 and 2, `x/0` all ones twice; `imae.usat` of
  `0xffff·0xffff + 0xfffffff0` is `0xffffffff`, `.ssat` of `-1·-1 - 16` is `-15`, `.rs4`
  shifts, `coe` sets `i0` to 1, `cie` adds it; `ima16` u8/s8/o8 bytes; `ima8` `x + y·z`.
- **Others:** `br #k` counts from the `br`; `Pn` never runs; shift immediates and `~`; the
  16-bit tests see the unwrapped lane; bank 7 per pixel; `i.h`; `.syncs` hangs a fill.

Not probed: `ldaw`/`staw` and pre/post-increment register offsets, the clip-plane output of
`fdpc` (it is in no register a pixel task can read), mipmaps and LOD, and the visibility
group. The video filters `bilin`/`firv`/`firh` are measured (`doc/specs/usse_isa.md`, *Video*)
but not yet modelled in ESIL. The register-file writes stay a host-side question: a client
`str` was not seen to land, so probe them, if at all, only from the EDM's own task, with
registers that are safe to write.

## PDS emulation (ESIL, fork only)

The fork's `pds` plugin has a register profile and ESIL too (`libr/arch/p/pds/plugin.c`), with
the semantics of the PDS ISA reference (`doc/specs/pds_isa.md`) as the hardware probes settled
them. The registers: `ds0_0`-`ds0_63` and `ds1_0`-`ds1_63` (the data banks), the inputs
`ir0`-`ir2` and `tim` (set them as the program's starter would), `lr` (the one return
register), `p0`-`p2`, `if0`/`if1`, `aluz`/`alun`, `c` (the high dword `add`/`sub` leave: 1, 0 or
`0xffffffff`) and `alum` (1 signed). Map the code, not the data segment, at 0 (branch targets
count from the first instruction) and load the segment into the registers by the row rule, which
`pds-dis --regs` prints (`ar ds0_2=...`).

- A write to `dsB[n]` lands in `dsB_(48 + (n & 15))`; a wide move pushes every source before it
  writes, so overlapping rows (`mov128` with `swap`) come out right.
- `add`/`sub` set `aluz`, `alun` (a negative result under `alum signed` only) and, in the
  unsigned mode, `c`; `adc`/`sbc` add `c`. Every other instruction leaves the three as they
  were, which the probes measured for `and`, `xor`, `shl`, `not`, `mov32` and `tstz` and which is
  untried for the rest (the simulator calls them unknown instead).
- `mul`, `abs` and `shr` follow `alum`, selected arithmetically (a body under a predicate holds
  no nested condition); shift amounts are the 7-bit field, 32 and up giving 0.
- `mov16`/`mov32` spell their specials by selector and bit 9 (`ir0.0`, `tim.1.h`): `ir0` and
  `tim` read as the ALU's, `mov32` reads a `.1` as the `.0`, and a `.1` `mov16` writes 0.
- No ESIL, as open: the ports (`movs`, `movsa`), `load`/`store`, the fences, `mr01`/`mr23`, `ir1`
  and `pc` as `mov16`/`mov32` sources, `mov16` into a half of a read-only row and an arithmetic
  `shr` by 32 or more (which leaves its destination). `halt` has none: it ends the program, so
  emulate with `aesu <its address>`.

`pds_esil_check.py` runs a program in the simulator (`sgx-sim --pds`) and under the fork's ESIL
and compares every register the simulator knows at the end: `fixed` (one program through every
modelled form) and `random` (straight-line programs kept inside what the simulator models).
Both run with 0 differences. Tests: `test_pds_esil_check.py` and, in the fork,
`test/db/esil/pds`.

```sh
R2_PREFIX=/path/to/fork-prefix ../../../.venv/bin/python pds_esil_check.py random --count 300
```

## Licence

`arch_usse.c`, like the decoder core it wraps, is MIT. radare2 is LGPL-3.0; MIT code is
compatible with it, so the plugin can be loaded by, and contributed to, radare2.
