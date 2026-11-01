# SGX545 firmware container (`sgx545_ukernel.fw`), formats v1 to v4

`tools/fwcutter/` builds this file from the user's own copy of the closed Cedarview
`libsrv_init.so`. The kernel driver (in the linux fork) loads it with `request_firmware()`.
This is the b43-fwcutter model: the tool ships no Imagination bytes, only offsets, sizes,
hashes and our own reconstructed tables. The user supplies the blob.

The file carries everything srvinit contributes to an SGX545 boot: the code images, how to
patch them for the device addresses the driver picks, the register init scripts, and the
initial contents of the control blocks. The reference loader (`tools/fwcutter/fwload.py`)
reproduces the harness captures byte for byte from it, at two different address layouts
(§6). That is the evidence that the format is complete.

The format has four versions. A writer emits the lowest version that holds the content.

| version | content | template ids | parameters |
|---------|---------|--------------|------------|
| v1 | buffers, patches, init scripts | n/a | n/a |
| v2 | adds transfer-queue (TQ) sections and `VALUES` list 4 | 0-7 | 0-5 |
| v3 | the same sections | 0-15 | 0-8 |
| v4 | adds the `OURS` origin | 0-15 | 0-8 |

§1-§8 describe v1 and hold for every version. §9 describes the transfer-queue templates of a
solid fill (v2, cut from the user's `libsrv_um.so`), §10 the two templates of a copy (v3) and
§11 the templates of our own (v4).

## 1. Two kinds of content

(The hardware spec, `doc/specs/hw_spec.md` (arrives with the firmware boot unit), the transfer
spec, `doc/specs/transfer.md` (arrives with the host protocol unit), `asm/transfer/` and the
assembler `usse-asm`/`pds-asm` (arrive with the assembler unit), and the disassemblers
`usse-dis` and `pds-dis` (arrive with the disassembly unit) are later units. They are pointers
for further reading: nothing here rests on a section of them. Each fact rests on the evidence
records E001 to E004, on the captures they cite, or on the text that states it.)

Every section is tagged with its origin, so the two never mix:

| origin | what | where it comes from |
|--------|------|---------------------|
| `CUT` | the ukernel and the five PDS programs, as stored in `libsrv_init.so` | the user's blob |
| `FACT` | everything else | `facts.py`, reconstructed from the captures (E001-E004) |
| `OURS` | transfer-queue templates written by us (v4, §11) | `asm/transfer/`, assembled |

Item by item:

| item | origin | notes |
|------|--------|-------|
| ukernel template (`0x2080`, `0xCF68` bytes) | CUT | 9 placeholder immediates, unpatched |
| PDS programs #10–#14 (`0x1ea0`–`0x2070`) | CUT | code and data; the data is mostly zero |
| patch table for the ukernel and PDS data | FACT | which field, which value (§4) |
| PDS data-segment constants | FACT | the layout captures hold them, the blob does not (E003) |
| buffer sizes, alignments, heaps | FACT | the allocations srvinit requests |
| init scripts part 1, part 2, deinit | FACT | the layout captures (§6) |
| `asInitDevData` | FACT | the layout captures (§6) |
| TA3DCtl initial image (the `sa` binding) | FACT | the layout captures (E002) |
| TA / 3D signature register lists | FACT | register offsets the EDM samples |
| kick table, MKIF sizes, EDM task regs, clock gating, cache | FACT | layout captures (§6, E001) |
| HostCtl layout, CCB protocol | n/a | not in the file: driver source (`ccb.py` is the reference) |

The fact sections are the values the layout captures hold and the cut code does not (§6; E002,
E003). They are build-specific, because the PDS programs index specific data slots and the
ukernel expects specific `sa` values. That is
why they travel with the cut code in one file, instead of being compiled into the driver: a
driver that reads them from the file supports any build the cutter knows, without changes.

## 2. Container

Little-endian throughout. The file is a 32-byte header, a section table, then the section
payloads, each 8-byte aligned.

```
header (32 bytes)
  +0   char[8] magic           "SGX545FW"
  +8   u16     format_version  1 to 4 (§9.1, §10.1, §11.1)
  +10  u16     section_count
  +12  u8      ddk_major       1
  +13  u8      ddk_minor       7
  +14  u16     reserved        0
  +16  u32     ddk_build       862890
  +20  u32     build_options   0x60218 (the client build options srvinit reports)
  +24  u32     file_size
  +28  u32     crc32           CRC-32 (zlib) of bytes [32, file_size)

section table entry (16 bytes)
  +0   u16     type
  +2   u16     origin          0 = CUT, 1 = FACT, 2 = OURS (v4 templates, §11)
  +4   u32     offset          from the start of the file
  +8   u32     size
  +12  u32     arg             type-specific
```

A loader must reject a wrong magic, an unknown `format_version`, a size or CRC mismatch, and
an unknown section type.

| type | name | origin | arg | payload |
|------|------|--------|-----|---------|
| 1 | `IMAGE` | CUT | buffer id | the buffer's template bytes |
| 2 | `BUFFERS` | FACT | 0 | buffer records (§3) |
| 3 | `PATCHES` | FACT | 0 | expression records, applied to buffer images (§4) |
| 4 | `VALUES` | FACT | list id | expression records evaluated to a list of values (§5) |
| 5 | `EDM_META` | FACT | 0 | 31 × u32 (§5) |
| 6 | `TQ_TEMPLATE` | CUT, OURS | template id | v2+: a transfer-queue program template (§9) |
| 7 | `TQ_PATCHES` | FACT | 0 | v2 only: expression records, applied to templates (§9.4) |
| 8 | `TQ_META` | FACT | 0 | v2 only: template records (§9.3) |

## 3. Buffers

The driver allocates one device buffer per record and places it where it likes, within the
constraints below. Buffer ids:

| id | buffer | heap | size | align |
|----|--------|------|------|-------|
| 0 | ukernel | KERNEL_CODE | `0xcf68` | 8 |
| 1–5 | PDS #10–#14 | KERNEL_CODE | `0x18 0x38 0x18 0x100 0x68` | 16 |
| 6 | kernel CCB | KERNEL_DATA | `0x2000` | `0x1000` |
| 7 | CCB control | KERNEL_DATA | `0x8` | `0x1000` |
| 8 | event kicker | KERNEL_DATA | `0x4` | 16 |
| 9 | TA3DCtl | KERNEL_DATA | `0xec` | 32 |
| 10 | HostCtl | KERNEL_DATA | `0x44` | 32 |
| 11 | misc | KERNEL_DATA | `0x54` | 32 |
| 12 | HWPerf circular buffer | KERNEL_DATA | `0x640c` | 32 |
| 13 | TA signature buffer | KERNEL_DATA | `0x620` | 32 |
| 14 | 3D signature buffer | KERNEL_DATA | `0x2088` | 32 |

Heap ids are `sgxapi_km.h`'s: 2 KERNEL_CODE, 3 KERNEL_DATA, 4 PIXELSHADER, 5 VERTEXSHADER,
6 PDSPIXEL_CODEDATA.

```
buffer record (16 bytes)
  +0   u8      id
  +1   u8      heap
  +2   u8      pds_rows        PDS data-segment size in rows of 4 dwords (0 if not PDS)
  +3   u8      reserved
  +4   u32     size            allocation size
  +8   u32     align
  +12  u32     reserved
```

A buffer starts as its `IMAGE` section (zero-padded to `size`) or, without one, as zeros.
Then the patches are applied.

**Placement constraint.** The EDM code base (`USE_CODE_BASE_15`) is the KERNEL_CODE heap base. PDS
code words name the ukernel by instruction index from that base, so the ukernel's offset `uk_off =
(addr[0] − heap_base[2]) / 8` enters every code word. **For the firmware to run, `uk_off` must be
0**: the ukernel's own branch targets and the CCB service addresses (the kick table) are also
instruction indices from the code base, and nothing relocates them (the moved layout shows the
kick table unchanged while the PDS code words move; E002). The two layout captures place the
ukernel at `+0x1000` (`uk_off = 0x200`) and `+0x5000` of the heap, not at its base, so they do not
show where srvinit's own allocator would put it. The PDS words in both captures are patched
consistently with the ukernel's offset, which is why the loader accepts any `uk_off`. That a
ukernel at a nonzero offset faults on its first absolute branch is what the rule above predicts,
not something the captures show: no GPU ran. The measurement on hardware belongs to the firmware
boot unit.

## 4. Expressions and patches

A 16-byte expression record computes one 32-bit value and says how to store it:

```
expression record (16 bytes)
  +0   u8      buffer          target buffer id (PATCHES); 0xff in VALUES
  +1   u8      encoding
  +2   u8      kind
  +3   u8      param           encoding parameter
  +4   u32     offset          byte offset in the buffer (PATCHES); register or index (VALUES)
  +8   u32     target
  +12  u32     addend
```

| kind | value |
|------|-------|
| 0 `CONST` | `addend` |
| 1 `ADDR` | `addr[target] + addend` |
| 2 `ADDR_SHR4` | `(addr[target] + addend) >> 4` (the `emitpds` address operand) |
| 3 `HEAP` | `heap_base[target] + addend` |
| 4 `PD_PHYS` | `pd_phys + addend` (the EDM page directory's physical address) |
| 5 `CODE_WORD` | `addend \| ((target + uk_off) << 4)`, with `target` a ukernel instruction index |
| 6 `PDS_CTL` | `(pds_rows[target] << 23) \| addend` (an `emitpds` control word) |
| 7 `PDS_ROWS` | `pds_rows[target]` |

| encoding | store |
|----------|-------|
| 0 `WORD32` | the value as a dword at `offset` |
| 1 `USSE_LIMM` | the 32-bit immediate at `offset`: `e[20:0]`, `e[40:36]`, `e[49:44]` |
| 2 `CODE_BASE` | `USE_CODE_BASE_n` form: `(value >> 7) & 0x1ffffff \| param << 25`; `param` = DM |

`USSE_LIMM` patches only the immediate bits. All other bits of the instruction (opcode,
destination) come from the template, whose immediate at each patch site is the placeholder
`0xDEADBEEF` (Evidence: E002).

The `PATCHES` table for 1.7.862890 has 81 records (Evidence: E003):

- **ukernel, 9 `USSE_LIMM`**, the 9 placeholder immediates of the template; the loader patches the
  32-bit immediate of each in three bit-fields, which changes 52 bytes (Evidence: E002):

  | insn | byte | value | used as |
  |------|------|-------|---------|
  | 428 | `0xd60` | `PDS_CTL` #11, `0x1000` | `emitpds` control, PDS #11 |
  | 430 | `0xd70` | `ADDR_SHR4` PDS #11 | `emitpds` address, PDS #11 |
  | 431 | `0xd78` | `ADDR` TA3DCtl | boot task reads TA3DCtl |
  | 438 | `0xdb0` | `PDS_CTL` #12, `0x100` | `emitpds` control, PDS #12 |
  | 440 | `0xdc0` | `ADDR_SHR4` PDS #12 | `emitpds` address, PDS #12 |
  | 456 | `0xe40` | `ADDR` PDS #13 | → `EVENT_OTHER_PDS_EXEC` |
  | 458 | `0xe50` | `PDS_ROWS` #13 | → `EVENT_OTHER_PDS_DATA` |
  | 5983 | `0xbaf8` | `PDS_CTL` #14, `0x100` | `emitpds` control, PDS #14 |
  | 5986 | `0xbb10` | `ADDR_SHR4` PDS #14 | `emitpds` address, PDS #14 |

- **PDS data segments, 24 `WORD32`**: the code words of every USSE entry (addend
  `0x0800000f`, except PDS #11's `0xf`; E003), PDS #11's TA3DCtl DMA source address and DMA
  control word `0x03c0003f`, and constants (`2`, `0x100`, `0x200`, the PDS #14 request masks
  `0x4000f` and `0x120080`).
- **TA3DCtl, 8 `WORD32`** (the base pointers the EDM reads; Evidence: E002):
  `sa0` TA3DCtl, `sa1` HostCtl, `sa2` CCB control, `sa22` CCB, `sa23` `PD_PHYS`,
  `sa43`–`sa45` HWPerf / TA signature / 3D signature buffers.
- **Signature buffers, 40 `WORD32` `CONST`**: 7 records for TA and 33 for 3D: the register
  count (offset 0), then 6 (TA) or 32 (3D) register offsets from offset 8. The zero word
  at offset 4 is not a record.

## 5. Values and EDM metadata

`VALUES` sections, by list id: 0 init script part 1, 1 part 2, 2 deinit (record `offset` = the
register, in write order), 3 `asInitDevData` (record `offset` = the index; absent entries are
0). Address-valued entries are expressions: `USE_CODE_BASE_0–9` = `HEAP` PIXELSHADER
`+ n·0x80000`, data master 1; `10–13` = `HEAP` VERTEXSHADER, data master 0; `15` = `HEAP`
KERNEL_CODE, data master 3; `PDS_EXEC_BASE` = `HEAP` PDSPIXEL_CODEDATA; `EVENT_KICKER` =
`ADDR` kicker; `EVENT_OTHER_PDS_EXEC` = `ADDR` PDS #10; `EVENT_OTHER_PDS_DATA` = `PDS_ROWS`
#10; dev data 12 and 13 = `HEAP` PDSPIXEL_CODEDATA and PIXELSHADER.

`EDM_META` is 31 dwords: the 11 host kick addresses (`SGXMKIF_CMD_*` order, 0 = no handler),
the 13 MKIF struct sizes (in the order of E001), the two EDM task
registers, clock gating (`ctl`, `ctl2`, status register, status mask) and the cache-control
word.

The kick addresses are **not relocated**. They stay the same when the ukernel moves within
the heap (§6), unlike the PDS code words (Evidence: E002).

## 6. Verification

`tools/fwcutter/test_fwload.py` runs the loader with the addresses of two harness captures,
both taken with `harness/ukernel-extract/`. The capture table is
`captures/firmware/layout.toml` and the dataset manifest `datasets/firmware-layout.toml`; the
bytes are in resgx545-data-private:

| capture | heap bases | first allocation | PD address |
|---------|-----------|------------------|------------|
| `layout_base` | `sgxconfig.h` | heap + `0x1000` | `0x1000` |
| `layout_moved` | each heap + 1 MiB | heap + `0x5000` | `0x2345000` |

For both, the loader output equals the capture: all 15 buffers (the rest of each captured
page is zero), the three init scripts, dev data, kick table, struct sizes and EDM values.
`layout_moved` exercises every expression kind with values that differ from `layout_base`
(Evidence: E002).

`test_fwcutter.py` checks that the static carve equals the harness's extracted template, and
that the cutter refuses an unknown input.

## 7. Known inputs

The hash cells are truncated; the full hashes are in `facts.KNOWN_INPUTS`.

| file | SHA-256 | size | DDK |
|------|---------|------|-----|
| `libsrv_init.so.1.7.862890` | `8c5a59c4…e327869a` | 63524 | 1.7.862890 |
| `libsrv_um.so.1.7.862890` | `2b2c0986…11988a44` | 196152 | 1.7.862890 (v2, §9) |
| `libsrv_init.so.1.7.862890` | `4d3df850…effe53b6d` | 66976 | 1.7.862890 (Ubuntu) |
| `libsrv_um.so.1.7.862890` | `e19402fc…19ad0dce` | 198204 | 1.7.862890 (Ubuntu) |

The first two come from `cdv-gfx-drivers-1.0.3_bee.tar.bz2`: the
`cedarview-userspace-v1.0.3_bee` tarball inside it, `usr/lib/`. The Ubuntu pair comes from
`cedarview-graphics-drivers_20120717.orig.tar.gz` (Ubuntu 12.04 multiverse), `usr/lib/`. It
is a different link of the same code: every `libsrv_init.so` section sits 0x80 bytes lower
(the ukernel at 0x2000), and in `libsrv_um.so` the code immediates sit 0x1d0 and the whole
programs 0x200 bytes higher. The cut sections and templates hash the same, so both pairs give
the same file, byte for byte.

Each cut section is also checked against its own SHA-256, so an entry whose offsets do not
yield the expected bytes is refused. fwcutter takes only the libraries;
`tools/fwcutter/get-firmware.sh` fetches either package, checks it and extracts them.

## 8. Out of scope

This document specifies the file. Kernel-side loading, a C header generated from `facts.py` and
anything on hardware are not part of it. The C loader in `tools/sgx_fw/` ports §2–§5 and
§9–§11 (`tools/sgx_fw/README.md`).

## 9. Format v2: transfer-queue templates

A solid fill (the transfer spec, `doc/specs/transfer.md`, arrives with the host protocol unit)
runs seven small programs on the GPU. Their bytes are Imagination's, stored in `libsrv_um.so`
(E004), so they travel in this file the way the ukernel does: `CUT` sections carved at run
time from the user's library, plus `FACT` tables saying how to place and patch them (§9.2 to
§9.6).

### 9.1 Versions and the cutter

- `fwcutter.py cut <libsrv_init.so>` writes a **v1** file. `fwcutter.py cut <libsrv_init.so>
  <libsrv_um.so>` writes a **v3** file (§10); with `--format-version 2` it writes the v2 file
  described here. Both libraries must be known inputs (§7) of the same DDK build, or the
  cutter refuses.
- The writer sets `format_version` to 1 when the file has no transfer-queue content
  (sections 6–8 or `VALUES` list 4), and otherwise to the lowest version whose limits hold
  it (§10.1): 2 for the seven fill templates. A v1 loader loads every file cut from
  `libsrv_init.so` alone and rejects a v2 file on its version.
- A v2 loader reads both versions. It rejects sections 6–8 and `VALUES` list 4 in a v1 file.
  A v2 file without them is valid (the cutter never writes one).
- In a v2 file, every `TQ_TEMPLATE` and every `TQ_PATCHES` record names a template that has a
  `TQ_META` record, and a template's image is at most its size.

### 9.2 Templates (`TQ_TEMPLATE`, CUT)

Template ids are a namespace of their own, 0–7 in v2 (0–15 in v3), separate from buffer
ids. Each template is assembled from pieces of `libsrv_um`, `(source offset, length,
destination offset)`, into a zeroed array, and the result is checked against its SHA-256. A
template assembled from small pieces is thus no different from one copied whole.

| id | name | pieces | size | SHA-256 |
|----|------|--------|------|---------|
| 0 | `USE_FILL` | `0x22218`+8 → 0; `0x1d1cc`+4 → 12 | `0x10` | `7727cde6…a7a400b0` |
| 1 | `USE_SEC` | `0x223d8`+16 → 0 | `0x10` | `74c3e748…1847cece` |
| 2 | `USE_EOT` | 9 × 4 bytes, below | `0x38` | `d03fa3dc…5a6667be` |
| 3 | `USE_EOR` | 4 × 4 bytes, below | `0x18` | `dfbb3b5d…a4ccddaa` |
| 4 | `PDS_PRIM` | `0x227e0`+24 → 0 (`KICKONLY`) | `0x18` | `0963b59a…55005092` |
| 5 | `PDS_SEC` | `0x229a0`+24 → 0 (`BASIC`) | `0x18` | `0963b59a…55005092` |
| 6 | `PDS_PIXEVENT` | `0x23080`+196 → 0 | `0xc4` | `65e78fa8…19881671` |

`USE_EOT` takes the 4-byte pieces at `0x2001e` → byte 4, `0x20062` → 12, 20, 28 and 36,
`0x2007c` → 40, `0x20083` → 44, `0x20092` → 48 and `0x200b3` → 52. `USE_EOR` takes
`0x1fd9d` → 4, `0x1fdab` → 12, `0x1fdb2` → 16 and `0x1fdb9` → 20.
`USE_FILL`'s 4-byte piece at `0x1d1cc` is the high dword of its second instruction; the
template's colour immediate is 0 until patched (§9.4).
Templates 4 and 5 are byte-identical in this build (and equal to PDS #10), as are the two
pixel-event copies at `0x23080` and `0x23160`; they keep separate ids because other builds may
differ.

Captures of the closed stack show each piece's bytes at its offset (Evidence: E004). Searching
the library for the bytes the GPU receives, with the bits a patch writes as don't-care, finds
`USE_FILL`'s piece at `0x1d1cc`, `USE_EOT`'s at `0x20083`, `0x20092` and `0x200b3`,
`USE_EOR`'s at `0x1fdb2` and `0x1fdb9` (and `PDS_PRIM_1SRC`, §10.2) in one place only; the
other 4-byte pieces of `USE_EOT` and `USE_EOR` are the candidates nearest those (5 to 57 places
hold their bytes). `USE_FILL`'s first piece (53 places), `USE_SEC`, `PDS_PRIM`, `PDS_SEC`,
`PDS_PIXEVENT` (2 places each) and `USE_COPY` (§10.2) are one of several equal copies: any of
them cuts the same bytes, and which one the library itself reads is not shown. The bits under
patched fields never reach the GPU unpatched, so the SHA-256 column holds for these offsets
and the captures confirm every other bit.

Read with our disassemblers (`usse-dis`, `pds-dis`), each cut template decodes in full and
ends on its last instruction. The instruction counts, and what the captures show of each
template (E004: the fields that vary between copies, and which program each `DOUTU` word
starts), are:

| template | instructions | patched fields; data |
|----------|--------------|----------------------|
| `USE_FILL` | 2 | the colour immediate (0 in the template) |
| `USE_SEC` | 2 | none |
| `USE_EOT` | 7 | the four immediate loads (PBE words, destinations `r0`-`r3`) and the sideband |
| `USE_EOR` | 3 | none |
| `PDS_PRIM`, `PDS_SEC` | 2 | the `DOUTU` words `U0`-`U2`; 4 data dwords, 0 in the template |
| `PDS_PIXEVENT` | 29 | `DOUTU` and constant dwords 0-5 and 12; 20 data dwords, 0 in the template |

In the cut `USE_EOT` the low dwords of the four immediate loads are zero, which is destination
`r0` (bits 21 and up). The captured loads have destinations `r0` to `r3` (`1 << 21`, `2 << 21`,
`3 << 21` for the last three), and the library holds no run of two consecutive such loads, with
the immediates as don't-care (E004), so the destinations are FACT patches (§9.4).

### 9.3 Template records (`TQ_META`, FACT)

```
template record (16 bytes)
  +0   u8      id
  +1   u8      heap            4 PIXELSHADER (USE code), 6 PDSPIXEL (PDS programs)
  +2   u8      temps           USE temporaries; enters the DOUTU word
  +3   u8      pds_attrs       attributes the PDS program's task receives
  +4   u32     size            allocation size
  +8   u32     align
  +12  u16     pds_data        PDS data segment in bytes (0 for USE code)
  +14  u8      flags           bit 0 NO_STRADDLE: must not cross a 4 KiB page
  +15  u8      reserved        0
```

| id | heap | temps | attrs | size | align | data | flags |
|----|------|-------|-------|------|-------|------|-------|
| 0 `USE_FILL` | 4 | 0 | 0 | `0x10` | 8 | 0 | 1 |
| 1 `USE_SEC` | 4 | 0 | 0 | `0x10` | 8 | 0 | 1 |
| 2 `USE_EOT` | 4 | 4 | 0 | `0x38` | 8 | 0 | 1 |
| 3 `USE_EOR` | 4 | 1 | 0 | `0x18` | 8 | 0 | 1 |
| 4 `PDS_PRIM` | 6 | 0 | 0 | `0x18` | 16 | `0x10` | 1 |
| 5 `PDS_SEC` | 6 | 0 | 0 | `0x18` | 16 | `0x10` | 1 |
| 6 `PDS_PIXEVENT` | 6 | 0 | 1 | `0xc4` | 16 | `0x50` | 1 |

The captures show each record's heap, size and PDS data segment, and the `DOUTU` words'
`TRC` = `(temps + 3) >> 2` (Evidence: E004). They show the temporaries and attributes only
through those values, and the alignment and `NO_STRADDLE` only as rules every captured
placement keeps (each address a multiple of 16, of 64 for `PDS_PRIM_1SRC`, none across a
page), not as the closed allocator's minimum. The driver places each template where it
likes, with its address **aligned**, **at or above its heap's base** and, with `NO_STRADDLE`,
inside one page. `DOUTU` (§9.4) adds one more constraint for USE code.

The background object needs `pds_data` and `pds_attrs` of `PDS_PRIM` and `PDS_SEC`; it stays
in driver code (the transfer spec describes it), like the PBE words (§9.6), because both are
SGX545 data formats, not build facts.

### 9.4 Patches (`TQ_PATCHES`, FACT)

The 16-byte expression record of §4, with `buffer` = the template id (one `TQ_PATCHES`
section for all templates, as v1 has one `PATCHES` section for all buffers). The driver copies
each template into its placed copy (zero-padded to `size`) and applies the records **in file
order**; order matters where a `WORD32` and a `USSE_LIMM` share a dword. In transfer-queue records,
`param` is 0 and these kinds are allowed:

| kind | value |
|------|-------|
| 0 `CONST` | `addend` |
| 1 `ADDR` | `tq_addr[target] + addend`: `target` is a **template** id here |
| 3 `HEAP` | `heap_base[target] + addend` |
| 8 `PARAM` | `param[target] + addend`, a per-transfer parameter (§9.6) |
| 9 `DOUTU` | the `DOUTU` word 0 of template `target`, below |

`DOUTU` takes `off = tq_addr[target] + addend − heap_base[heap of target]`, which must be a
multiple of 8 in `[0, 0x80000)`, and yields

```
((off << 1) & 0xffff0) | ((off >> 19) & 0xf) | ((temps[target] + 3) >> 2) << 24
```

(`EXE` [19:4], `CBASE` [3:0], `TRC` [31:24]; E004 names the fields). Keeping USE code in the
first 512 KiB of the heap makes `CBASE` 0, as it is in every capture; what `CBASE` selects is
not shown (E004). Encodings are `WORD32`, `USSE_LIMM` and one new one:

| encoding | store |
|----------|-------|
| 3 `EMITPIX_SB` | the 14-bit sideband of the `emitpix2` at `offset`, other bits kept |

`EMITPIX_SB` scatters value bits [5:0] to `e[27:22]`, [11:6] to `e[40:35]` and [13:12] to
`e[55:54]`.

Why the set is this small: there is no destination-register encoding, because the destination
registers are `CONST` `WORD32` patches written before the immediates (`USSE_LIMM` keeps every
non-immediate bit). There is no PDS-pointer kind, because no template holds a PDS state
pointer; the background object, which does, is driver code. `DOUTU` takes the temporaries from
`TQ_META` rather than from a parameter. The fixed command words are a `VALUES` list (§9.5)
rather than part of `TQ_META`. Tile size, PBE `COUNT` and the state-size word stay in driver
code with the formats they belong to (§9.6).

v1 sections (`PATCHES`, `VALUES` 0–3) may not use kinds 8 and 9 or encoding 3; v2 records
may not use kinds 2 and 4–7 or encoding 2. For 1.7.862890 there are 22 records:

| template | byte | encoding | value | what |
|----------|------|----------|-------|------|
| `USE_FILL` | 8 | `USSE_LIMM` | `PARAM` 0 | the colour |
| `USE_EOT` | 16, 24, 32 | `WORD32` | `CONST` `1 << 21`, `2 << 21`, `3 << 21` | dest `r1`–`r3` |
| `USE_EOT` | 8, 16, 24, 32 | `USSE_LIMM` | `PARAM` 1–4 | PBE words 0–3 into `r0`–`r3` |
| `USE_EOT` | 48 | `EMITPIX_SB` | `PARAM` 5 | the PBE sideband |
| `PDS_PRIM` | 0, 4, 8 | `WORD32` | `DOUTU` `USE_FILL`, `CONST` 4, `CONST` 0 | `U0`, `U1`, `U2` |
| `PDS_SEC` | 0, 4, 8 | `WORD32` | `DOUTU` `USE_SEC`, `CONST` 4, `CONST` 0 | `U0`, `U1`, `U2` |
| `PDS_PIXEVENT` | 0, 4 | `WORD32` | `DOUTU` `USE_EOT`, `CONST` `0x00800000` | dwords 0, 1 |
| `PDS_PIXEVENT` | 8, 12 | `WORD32` | `CONST` 0, `DOUTU` `USE_EOT` | dwords 2, 3 |
| `PDS_PIXEVENT` | 16, 20 | `WORD32` | `DOUTU` `USE_EOR`, `CONST` `0x00c00000` | dwords 4, 5 |
| `PDS_PIXEVENT` | 48 | `WORD32` | `CONST` `0x00800000` | dword 12 |

Every record is backed by the captures (Evidence: E004). The 11 `PARAM` and `DOUTU` records
are the only fields that vary between the captured copies of the fill's templates, each with
this encoding and value. Eight `CONST` records write values the cut templates lack, which the
captures hold; the three `CONST` 0 at byte 8 of the PDS programs write the template's own 0
and cannot be seen. `CBASE` was 0 and only sideband bits [1:0] varied in every capture, so
those parts of the `DOUTU` and `EMITPIX_SB` encodings rest on their definitions above.

The seven patched pixel-event dwords are dwords 0 to 5 and 12. Our disassembler's operand
notation `dsB[i]` names data dword `4 × (i div 2) + 2 × B + i mod 2`, so they are `ds0[0]`,
`ds0[1]`, `ds1[0]`, `ds1[1]`, `ds0[2]`, `ds0[3]` and `ds0[6]`. `LINESTRIDE` (§9.6) counts
pixel pairs.

### 9.5 Command words (`VALUES` list 4, `TQ_CMD`, FACT)

The fixed `SGXMKIF_TRANSFERCMD` words of a fill, as `WORD32` expression
records evaluated like §9.4 (template ids, parameters). `offset` is the byte offset in the
command: a multiple of 4, with `offset + 4` at most the `TRANSFERCMD` size in `EDM_META`.

| offset | field | value |
|--------|-------|-------|
| `0x004` | `ISPBgObj` | `0x200` |
| `0x008` | `ISPBgObjDepth` | `0x3f800000` |
| `0x00c` | `ISPRender` | 3 |
| `0x014` | `ISPIPFMisc` | `0x100` |
| `0x01c` | `3DAAMode` | `0x80000000` |
| `0x020` | `ISPMultiSampCtl` | `0x88` |
| `0x024` | `EDMPixelPDSExec` | `ADDR` `PDS_PIXEVENT` |
| `0x028` | `EDMPixelPDSData` | 5 (`pds_data >> 4`) |
| `0x02c` | `EDMPixelPDSInfo` | 1 (`(4 × pds_attrs + 15) >> 4`) |
| `0x038` | `PixelBE` | `0x80` |
| `0x03c` | `PDSExecBase` | `HEAP` PDSPIXEL |
| `0x194` | `num_pixel_partitions` | `0x07c00000` |

Every captured command holds these 12 words, `PDSExecBase` following a moved PDSPIXEL heap
(Evidence: E004).

The word names are the glossary's where it has one: `EDMPixelPDSExec` is
`transfer_cmd.event_pixel_pds_code` (+0x24), `PDSExecBase` `transfer_cmd.pds_exec_base`
(+0x3c) and `Bif3DReqBase` `transfer_cmd.bif_3d_req_base` (+0x18, the GPL DDK's
`EUR_CR_BIF_3D_REQ_BASE`). `ISPBgObjTag` (+0x00) is our label, defined by what E004 shows:
its bits [23:0] locate the background object above `Bif3DReqBase` in 16-byte units and
`TSPDATASIZE` [30:25] counts its layers. The other names in the table are labels of the same
kind, for the words at those offsets.

The driver zeroes the command, writes these, then the fields that depend on its own memory
and queue: `ISPBgObjTag`, `Bif3DReqBase`, `ISPRenderBox1/2`, `ui32Size`, `ui32Flags`, the
status values and `fence_id`.

### 9.6 Parameters of a fill

The `PARAM` values come from the fill, in driver code (`fwload.fill_params()`,
`sgx_fw_tq_fill_params()`). An ARGB8888 fill of the `width` × `height` rectangle at (`x`, `y`)
of a linear surface whose pixel (0, 0) is at `dest`, `stride` bytes per line, with colour
`colour` (`x` and `y` default to 0, a whole-surface fill):

| param | value |
|-------|-------|
| 0 | `colour` (pack mode 0 stores the `o0` dword unchanged) |
| 1 | PBE word 0: `x \| y << 16` (`XMIN`, `YMIN`) |
| 2 | PBE word 1: `(x + width − 1) \| (y + height − 1) << 16` (`XMAX`, `YMAX`) |
| 3 | PBE word 2: `0x8000 \| (stride / 8 − 1) << 16` (`COUNT` `0x80`, `LINESTRIDE`) |
| 4 | PBE word 3: `dest` |
| 5 | sideband: `0x200` (`TILERELATIVE`, pack mode 0) |

Accepted: `width, height ≥ 1` with `x + width` and `y + height` at most 8192 (13-bit
`XMAX`/`YMAX`), `stride` a multiple of 8 (an even pixel stride) with `4 × (x + width) ≤ stride
≤ 0x8000` (12-bit `LINESTRIDE`), `dest` a multiple of 4, and the surface below 4 GiB. The
driver's render box and background object must cover the same rectangle.

With these parameters, computed from each captured request, and the captured placements, the
records of §9.4 rebuild every captured ARGB8888 program byte for byte (Evidence: E004). The
closed OpenVG stack pads each surface line to 8 pixels; it fills XRGB8888 and RGB565 surfaces
with the same ARGB8888 colour immediate and the sidebands `0x200` and `0x203`, formats this
table does not cover.

What the PBE makes of these words, measured by varying each in a triangle's end-of-tile program
(3d.md §12.3): `XMIN`/`YMIN` and `XMAX`/`YMAX` bound the stored rectangle, inclusive, in bits
12:0 and 28:16 (E267); `COUNT` (`0x80`) is the number of four-pixel units stored of each 32 x 16
tile, an even value below it storing part of the tile and an odd one hanging the job (E266);
`LINESTRIDE` + 1 is the row pitch in 8-byte units and `FBADDR` a byte address whose bits 1:0
are ignored (E267); EMIT2 bits 6:0, the bits below `COUNT`, must stay 0, since they move where
the colours are read from (E267; Q040). Sideband `0x203` stores RGB565 (E030); bit 10 added
dithers it (E269).

### 9.7 Verification

`tools/fwcutter/test_fwload.py` cuts both libraries, places the templates at the addresses of the
fill recipe (a layout chosen in the test) and checks every patched field (the colour, the PBE
words and destination registers of `USE_EOT`, the sideband, the `DOUTU` words and the pixel-event
constants), that every other dword is the template's, the SHA-256 of each patched program and the
command words. It stores no program words. With the same layout it disassembles the patched
programs with `usse-dis` and `pds-dis`: every instruction decodes, the instruction counts are
those above, the listing shows the patched immediates (the fill shader's `#0xFF336699` for that
colour), and each `doutu` of the pixel-event program reads the dwords its patches wrote.

`test_tqcapture.py` reads the transfer captures (`captures/firmware/transfer.toml`, E004)
with `tqcapture.py`: the records of §9.3, the pieces of §9.2 in the library, the varying
fields of §9.4, the command words of §9.5, the CCB, the rings and allocations, the ring of the
copy's primaries, the library search for `USE_EOT`'s destination registers and the rebuild of
every captured program. It skips (and says so, naming `RESGX545_DATA_PRIVATE` or
`RESGX545_CDV_LIBS`) without the private data repository or `libsrv_um.so`.

`test_fwcutter.py` checks the seven hashes and that a `libsrv_um` with another SHA-256 is
refused. `test_cloader.py` runs the C port on the real v2 file with random layouts and fill
parameters and requires the same images and command words as `fwload.py`.


## 10. Format v3: the copy templates

A linear ARGB8888 copy (the transfer spec, `doc/specs/transfer.md`, arrives with the host
protocol unit) runs seven programs: five of the
fill's (`USE_SEC`, `USE_EOT`, `USE_EOR`, `PDS_SEC`, `PDS_PIXEVENT`) and two of its own, the
copy shader and a PDS primary that fetches the texel. v3 carries those two the §9 way. It adds
no section type, kind or encoding; it raises two limits that v2 loaders enforce, so it needs
its own version (§10.1).

### 10.1 Versions and limits

| version | content | template ids | parameters |
|---------|---------|--------------|------------|
| 1 | §2–§5 | — | — |
| 2 | + sections 6–8, `VALUES` list 4 (§9) | 0–7 | 0–5 |
| 3 | the same sections | 0–15 | 0–8 |

- The writer picks the **lowest version that holds the content**: 1 without transfer-queue
  content; 2 when every template id (in `TQ_META`, `TQ_TEMPLATE` and `TQ_PATCHES`) is below 8
  and every `PARAM` target (in `TQ_PATCHES` and `TQ_CMD`) below 6; 3 otherwise. A cut from
  both libraries holds template 8 and parameters 6–8, so it is v3.
- `fwcutter.py cut <libsrv_init.so> <libsrv_um.so> --format-version 2` leaves out templates
  7 and 8 and their patches, which gives the v2 file of §9 byte for byte. A v2-only loader
  rejects a v3 file on its version, so this is the file for such a loader.
- A v3 loader reads all three versions and applies the limits of the file's version: a v2 file
  with template 8 or parameter 6 is rejected, like a v1 file with transfer-queue content. A v3
  file without transfer-queue content is valid (the cutter never writes one).

### 10.2 Templates

| id | name | pieces | size | SHA-256 |
|----|------|--------|------|---------|
| 7 | `USE_COPY` | `0x21d60`+16 → 0 | `0x10` | `9d0dfd83…5a78b297` |
| 8 | `PDS_PRIM_1SRC` | `0x22960`+64 → 0 | `0x40` | `e3f3a906…13da3758` |

`USE_COPY` is the copy's USE program, which the closed stack keeps in an allocation of its
own, at one address for the whole run: 16 bytes, at `0x21d60` and again at `0x223a8`, either of
which cuts them. `PDS_PRIM_1SRC` is the copy's PDS primary, which the stack places in the
64-byte slots of a ring of 16: 64 bytes, found only at `0x22960` (Evidence: E004). Read with
our disassemblers:

| template | instructions | patched fields; data |
|----------|--------------|----------------------|
| `USE_COPY` | 2 | none |
| `PDS_PRIM_1SRC` | 4 | the `DOUTU`, `DOUTI` and texture words (§10.4); 12 data dwords |

### 10.3 Placing a subset of the templates

The copy's two templates take the slots of the fill's `USE_FILL` and `PDS_PRIM` in the transfer
recipes (the recipes of `test_fwload.py` put a USE program at the PIXELSHADER base and a PDS
primary at the PDSPIXEL base, for the fill and for the copy). So a v3 loader does not require
every template to be placed. This applies to v2 files too:

- The driver places the templates it will run. The loader checks each **placed** template
  (aligned, in its heap, within a page with `NO_STRADDLE`), copies it and applies the
  `TQ_PATCHES` records that target it. Templates without an address are left out, with their
  patches.
- A patch into a placed template, or a command word, that names (`ADDR`, `DOUTU`) a template
  without an address is an error.
- Each operation names the templates it runs, and they must be placed if the file has them:
  a fill runs ids 0–6, a copy runs ids 1, 2, 3, 5, 6, 7 and 8 (`fwload.FILL_TEMPLATES`,
  `COPY_TEMPLATES`; `SGX_FW_TQ_FILL_SET`, `SGX_FW_TQ_COPY_SET` with `sgx_fw_tq_need()` in C).
  A copy also needs templates 7 and 8 in the file, i.e. a v3 file.

A driver that places all seven fill templates can run a fill from a v2 or a v3 file. The
one-slot rule holds for the shared slots as well: a fill and a copy that reuse the same memory
must not be in flight together, so the driver must wait for the earlier one to complete (the
transfer spec describes the queue).

### 10.4 Records, patches and the parameters of a copy

| id | heap | temps | attrs | size | align | data | flags |
|----|------|-------|-------|------|-------|------|-------|
| 7 `USE_COPY` | 4 | 0 | 0 | `0x10` | 8 | 0 | 1 |
| 8 `PDS_PRIM_1SRC` | 6 | 0 | 1 | `0x40` | 16 | `0x30` | 1 |

The copy shader is never patched. The PDS primary takes nine
`WORD32` records, all of existing kinds; with the §13.8 interleave its data dwords 0–11 are
`ds0[0]`, `ds0[1]`, `ds1[0]`, `ds1[1]`, `ds0[2]`, `ds0[3]`, `ds1[2]`, `ds1[3]`, `ds0[4]`,
`ds0[5]`, `ds1[4]`, `ds1[5]`:

| byte | value | what |
|------|-------|------|
| 0, 4, 8 | `DOUTU` `USE_COPY`, `CONST` `0x02000004`, `CONST` 0 | `U0`–`U2` |
| 16, 20 | `CONST` `0x40012001`, `CONST` 0 | `DOUTI` words 0, 1 |
| 24, 28 | `PARAM` 8, `CONST` `0xa0800000` | T2 (`TEXADDR`), T3 |
| 32, 36 | `PARAM` 6, `PARAM` 7 | T0, T1 |

So `doutt` reads T0, T1, T2, T3 from dwords 8, 9, 6, 7. In the captures (Evidence: E004) the
four `PARAM` and `DOUTU` records are the fields that vary between the copies, `CONST` 4, 16
and 28 write values the cut template lacks, and `CONST` 8 and 20 write its own 0. The command
words are the fill's (`VALUES` list 4, §9.5) unchanged; only `ISPBgObjTag` differs
(`TSPDATASIZE`: 0 for a fill, 1 for a copy in all 67 commands, E004), and the driver writes
that field itself.

The parameters come from the copy in driver code (`fwload.copy_params()`,
`sgx_fw_tq_copy_params()`). The **source** is the linear `width` × `height` texture whose first
texel is at `src`, `src_stride` bytes per line: to copy a sub-rectangle of a larger surface,
`src` is that rectangle's top-left pixel (so T1 holds the copy's size and the texture
coordinates are 0 and 1.0). It lands 1:1 on the `width` × `height` rectangle at
(`x`, `y`) of the **destination**, a linear surface whose pixel (0, 0) is at `dst`,
`dst_stride` bytes per line:

| param | value |
|-------|-------|
| 0 | 0 (unused) |
| 1–5 | the PBE words and sideband of the destination rectangle, as `fill_params()` (§9.6) |
| 6 | T0: `s = src_stride / 4 − 1`; `(s & 7) << 9 \| (s >> 3) << 17` (`STRIDELO`, `STRIDEHI`) |
| 7 | T1: `0xcc000000 \| (width − 1) << 12 \| (height − 1)` (`NP2_STRIDE_EXT`, `B8G8R8A8`) |
| 8 | T2: `src` |

Accepted: `1 ≤ width, height ≤ 4096` (12-bit `WIDTH`/`HEIGHT`, no extension bits), `src_stride`
a multiple of 4 with `4 × width ≤ src_stride ≤ 0x8000` (13-bit stride in dwords), `src` a
multiple of 4 and the source below 4 GiB, and the destination as for a fill (§9.6). Source and
destination must not overlap: the command's scan order is fixed top-left to bottom-right.
Because the texture is exactly the copied rectangle, the background object's texture
coordinates are always (0, 0), (1.0, 0), (0, 1.0): 0 and 1.0 are exact in floating point, for
every size. The closed stack does not do this. In its copies the texture words describe the
whole source surface (its base, size and stride), not the copied rectangle (E004); with T0-T2
computed from that surface and the PBE words from the destination rectangle, the records
rebuild every captured copy. Both are inputs of these parameters. The captures do not show
how the closed stack selects the rectangle within the surface; that is in the background
object, which stays driver code, as for the fill.

Other values of the texture words, measured in a copy on the laptop: T1 bit 28 is `TEXFORMAT`'s
top bit, and flipped the copy reads the source as YUYV (`TEXFORMAT` 28) through colour-space set
0 (E271); T2 is an address in every bit from 2 up, its bits 12 and 14 reading the buffers around
the source (E273); in T3 `0xa0800000` bits 7:0 are a texel offset, left at 0 (E274).

### 10.5 The reference API

```python
fwload.copy_params(src, dst, width, height, src_stride, dst_stride, x=0, y=0) -> list[int]
fwload.copy(fw, layout, src, dst, width, height, src_stride, dst_stride, x=0, y=0) -> TQBuild
```

`copy()` checks that the file has the copy templates (`FormatError` otherwise) and that the
`COPY_TEMPLATES` are placed, then returns the nine parameters, the patched programs of every
placed template by id, and the command words. `fill()` returns a parameter list of nine
entries (6–8 are 0 for a fill). `fwload.py --copy src,dst,w,h,src_stride,dst_stride[,x,y]`
is the command-line form. The C equivalents are `struct sgx_fw_tq_copy`,
`sgx_fw_tq_copy_params()` and `sgx_fw_tq_need()`, with `sgx_fw_tq_build()` and
`sgx_fw_tq_cmd()` unchanged in signature (`tools/sgx_fw/README.md`).

### 10.6 Verification

`test_fwcutter.py` checks the two new hashes and pieces, that the v3 cut is v3 and that the v2 cut
is the v3 cut minus templates 7 and 8. `test_fwload.py` places the templates at the addresses of
the copy recipe (a layout chosen in the test) and checks every patched field (the data segments of
the PDS primary, secondary and pixel-event program, the `DOUTU` words and the command words), that
the rest of each program is its template, the SHA-256 of each patched program, the T0 cross-checks
(source stride to T0), and, with `usse-dis` and `pds-dis`, that the cut and patched copy programs
decode in full, with the instruction counts above, and that each `doutu`, `douti` and `doutt`
operand reads the dword its patch wrote. `test_fwformat.py` checks the version rule and rejects v3
content under v1 or v2 and records past the v3 limits. `test_cloader.py` runs the C port on the
synthetic `tiny_v3()` and on the real v3 file with random copy-only layouts and random copies, and
on the real v2 file, and requires the same output as `fwload.py`. `test_tqcapture.py` checks §10.2
and §10.4 against the copies of the transfer captures (E004), as §9.7 says for the fill.


## 11. Format v4: templates of our own

`asm/transfer/` holds the nine templates as our own assembly source; assembled, each
equals the cut template bit for bit (same SHA-256, §9.2, §10.2). They are our code, not
Imagination's, so a file that carries them needs no `libsrv_um.so` and must not call them
`CUT`. v4 adds one origin and nothing else.

### 11.1 Versions and the cutter

| version | content | template ids | parameters |
|---------|---------|--------------|------------|
| 4 | v3, and `TQ_TEMPLATE` sections may have origin 2 `OURS` | 0–15 | 0–8 |

- `fwcutter.py cut <libsrv_init.so> --tq-from-source` assembles the nine programs
  (`tools/fwcutter/ours.py`, which runs `usse-asm`/`pds-asm`) and writes them as `OURS`
  templates, with the same `TQ_META`, `TQ_PATCHES` and `VALUES` list 4 as a cut: the sources
  keep each patched field where the template has it. It takes neither `libsrv_um.so` nor
  `--format-version`.
- `OURS` is valid only on `TQ_TEMPLATE` and only from v4. The writer's rule of §10.1 gains a
  first case: a file with an `OURS` template is v4; otherwise v1–v3. A v4 file
  without one is valid (the cutter never writes one).
- A v4 loader reads all four versions; v4 has the v3 limits. A v3 loader rejects a v4 file on
  its version, which says more than an unknown origin would.
- The origin changes nothing in loading: an `OURS` template is placed, copied and patched
  like a `CUT` one. Loaders report it (`fwformat.Firmware.tq_ours`, `sgx_fw_tq.origin`).

### 11.2 Why an origin and not a new section type

The bytes, records and rules are those of §9–§10; only where the bytes come from differs, and
the origin field exists to say exactly that. Keeping the type lets every loader path stay
one path. A template's origin is per section, so a file could mix cut and assembled
templates; the cutter writes all of one kind.

### 11.3 Verification

`test_ours.py` assembles the nine programs and checks their SHA-256 against §9.2 and §10.2
(always: no closed input is needed) and, with `libsrv_um.so`, against the cut bytes.
`test_fwformat.py` checks the version rule and rejects `OURS` before v4 or on another section.
`test_fwcutter.py` checks that the source cut is v4, all `OURS`, with the fact tables of a
cut, and that its fill and copy builds equal the cut file's. `test_cloader.py` runs the C
port on a synthetic `tiny_v4()` and on the real v4 file (cut from `libsrv_init.so` alone)
with the recipe layouts and random fills and copies, and requires `fwload.py`'s output,
origins included.

### 11.4 Firmware tasks of ours (no section yet)

A section type for tasks of ours (an `FW_TASK`, `OURS`-origin like the templates) stays for later:
phase 11.29 ran with the loader and the container unchanged. Its tasks (`asm/fwtask/`) are blobs
the kernel's debug group loads (`own_code`) and places in the EDM's code heap at heap + 0x20000,
index 0x4000; the only difference from the stock buffers is the start dword of each armed slot of
PDS #13 (the `CODE_WORD` records of buffer 4, §4, E003), which the kernel evaluates again with
`sgx_fw_patch_word()`: `addend | (index << 4)`, the addend 0x0800000f (CBASE 15, TRC 8), the index
counting from the code base. A blob's `limm` patch sites take the results address and the
instruction index of the task the replaced record started (a jump target the record states,
E146); `tools/fwtask/test_overlay.py` checks on the real file that, unarmed, the 15 buffers are
the loader's and, armed, only the start dwords of the armed slots differ (HACKING.md, "Firmware
tasks of our own").
