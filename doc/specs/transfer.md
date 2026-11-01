<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
# SGX545 transfer command: host contract and EDM behaviour

SGX545 has no 2D core (hw_spec.md §9.1): every blit, fill and copy is a *transfer*, a small 3D
render with no TA phase that the microkernel (the EDM) runs from a queue. This document gives
what a host must build to run one, what the EDM does with it, and how a host talks to the EDM
at all: the kernel command queue (§5).

Sources, as everywhere in resgx545: the GPL DDK of the Cedarview kernel (sgx545-ce, paths
relative to its tree), black-box captures of the closed user-space stack under the harness
(CAP), our disassembly of the firmware for interoperability (RE: facts only, no code), and runs
on the laptop through the linux fork (HW). Each section ends with its evidence. The firmware
file's transfer templates (formats v2 and v3) are specified in fw_format.md §9 and §10; this
document does not repeat them.

## 0. Build configuration

The Cedarview kernel is built with `TRANSFER_QUEUE` (sgx545-ce `Kbuild`:99), without
`SUPPORT_SGX_LOW_LATENCY_SCHEDULING`, `PDUMP` and `NO_HARDWARE`, so a client's transfer reaches
the kernel through the `SGX_SUBMITTRANSFER` bridge call. The SGX545 feature list has neither
`SGX_FEATURE_2D_HARDWARE` nor `SGX_FEATURE_FAST_RENDER_CONTEXT_SWITCH`
(`src/services4/srvkm/hwdefs/sgxfeaturedefs.h`:118-146), so the 2D command and the
context-switch transfer flag (`0x10`) do not exist here.

The structures, as the EDM reports their sizes (E001, E017): transfer command `0x4c8` bytes,
its kernel-written shared block `0xdc`, HW transfer context `0xb4`, kernel CCB command `0x20`.

Limits (sgx545-ce `src/include4/sgxapi_km.h`:89-92, 416-419;
`src/services4/include/sgx_mkif_km.h`:157): 8 source syncs, 1 destination sync,
`SGXTQ_MAX_STATUS` = 2 + 2 = 4 status values, 5 sync operations.

Evidence: E001, E017.

## 1. Objects and the submit path

A transfer involves four objects, all reached by the EDM through its own page directory (the
kernel data heap), except the memory the transfer itself renders to or updates (§4.4):

- **the HW transfer context** (`0xb4` bytes, KERNEL_DATA): one per client queue; names the
  queue's client CCB and its control block, the page directory the transfers run under, and
  holds the EDM's queue state (§2.2);
- **the client CCB**: a ring of transfer commands. The closed stack allocates it as
  `0x10000` + `0x4c8` bytes, so the last command may run past the 64 KiB ring (E016);
- **its control block** (8 bytes: write offset, read offset; sgx545-ce
  `src/services4/include/sgx_mkif_km.h`:62-67, `PVRSRV_SGX_CCB_CTL`), byte offsets into the
  ring;
- **the transfer command** (§2.3), written by the client at the write offset.

The submit, as sgx545-ce does it (`src/services4/srvkm/devices/sgx/sgxtransfer.c`):

1. the client writes the command into its CCB and advances its write offset by the command's
   size;
2. it calls `SGX_SUBMITTRANSFER` with the CCB, the command's shared-block offset, the
   context's address and its sync objects;
3. the kernel fills the shared block in the CCB (`sgxtransfer.c`:87-260): the TA and 3D syncs
   when the kick names them (their write-pending count always bumped), then the source and
   destination syncs with duplicates dropped (read-pending resp. write-pending bumped unless
   `KEEPPENDING`);
4. it sends `TRANSFER` on the kernel CCB with the context's address in data word 1
   (`sgxtransfer.c`:377-383; §5).

What the closed stack submits (E016): commands of `0x1c0` bytes laid back to back from offset
0, flags `0x8` (`3DTQ_SYNC`), no update, one status entry whose value is the context's fence
count plus one; the fence count (`+0x198`) counts the run's commands from 0 (each run has one
context).

Registering a context: the kernel copies the client's `0xb4`-byte image into KERNEL_DATA and
writes the page directory of the client's memory context at the offset the client names
(sgx545-ce `src/services4/srvkm/devices/sgx/sgxutils.c`:997-1052). Our kernel builds the
context itself (§4).

Evidence: E016, E018.

## 2. Structure layouts

### 2.1 Sync objects and the shared block

A device sync object is 16 bytes: read-pending value, read-complete address, write-pending
value, write-complete address (sgx545-ce `src/services4/include/servicesint.h`:163-169). The
addresses point at the complete counters of a `PVRSRV_SYNC_DATA`
(`src/include4/servicesext.h`:632-646).

The shared block (`SGXMKIF_TRANSFERCMD_SHARED`, `sgx_mkif_km.h`:168-192), at command offset
`0xac`:

| offset | field |
|---|---|
| `+0x00` | source sync count |
| `+0x04` | 8 source sync objects |
| `+0x84` | destination sync count |
| `+0x88` | 1 destination sync object |
| `+0x98` | TA sync: write pending, write-complete address, read pending, read-complete address |
| `+0xa8` | 3D sync: the same four words |
| `+0xb8` | status count |
| `+0xbc` | 4 status entries {address, value} |

Command flags (`sgx_mkif_km.h`:159-166): `NOSYNCUPDATE` `0x1`, `KEEPPENDING` `0x2`,
`TATQ_SYNC` `0x4`, `3DTQ_SYNC` `0x8`, `DUMMYTRANSFER` `0x20` (no render; E018).

### 2.2 The HW transfer context

The DDK kernel never defines this structure; its size is the EDM's (`0xb4`, E001). The words a
host sets, as our kernel sets them and the EDM uses them (E018, E021):

| offset | word |
|---|---|
| `+0x00` | flags (0 from a host that builds its own context) |
| `+0x04` | priority (0) |
| `+0x08` | page directory (physical) the context's transfers run under |
| `+0x0c` | client CCB base (device address) |
| `+0x10` | client CCB control block (device address) |
| `+0x14` | commands queued, kept by the EDM: 1 while one waits, 0 when done |

The rest is zero when a host creates the context; what the EDM keeps there is §3.

### 2.3 The transfer command

| offset | content |
|---|---|
| `0x000`-`0x040` | the register block, 17 words the EDM loads into the 3D pipe (§3) |
| `0x044`-`0x0a0` | coefficient groups, loaded only when their load words are set (§3) |
| `0x0a4` | size: the bytes the command occupies in the CCB, a multiple of 64 |
| `0x0a8` | flags (§2.1) |
| `0x0ac`-`0x187` | the shared block (§2.1) |
| `0x188`-`0x190` | the three load words; 0 in every captured command (E016) |
| `0x194` | pixel partitions word (`0x07c00000` in every capture and in our commands) |
| `0x198` | fence count |
| `0x19c` | update count |
| `0x1a0`-`0x4c7` | up to 101 updates {address, value} |

Our builders size a command as `0x1a0` + 8 per update, rounded up to 64: `0x1c0` for up to four
updates (`sgx_xfer_add_update()`; E021 runs one). The closed stack's commands, with none, are
`0x1c0` too (E016).

The register block's fixed words for a fill and a copy, and how the varying ones (background
tag, request base, pixel-event program, PDS execution base) follow the surface and the
templates, are fw_format.md §9.5 and §10.4 (E004). The two render-box words give the
rectangle in 32 x 16 tiles: `+0x030` = `y0 / 16 | (x0 / 32) << 16`, `+0x034` the inclusive
last tile in the same form (our kernel's builder; E019, E020 render with them).

Evidence: E001, E004, E016, E018, E019, E020, E021.

## 3. The EDM side

Our disassembly of the firmware, for interoperability (E013: facts only, no code); instruction
indices are the microkernel's (byte offset / 8). doc/specs/edm_dataflow.md lists every word
and register the firmware touches.

### 3.1 Queueing (the TRANSFER handler)

The handler (`0x0103`) adds one to the context's count (`+0x14`); only when it was 0 does it
link the context into the queue of its priority (`+0x04` indexes the head and tail kept in
secondary attributes 13 and 14; the links are `+0xac` and `+0xb0`). It starts nothing: a host
sees no effect of the command until the EDM's scheduler picks the context (E015).

### 3.2 Picking and starting

For each queued context the pick routine (`0x12dc`-`0x1460`):

1. takes a queued context from the queue heads (secondary attribute 13 + priority; which
   priorities it scans is Q004) and skips it if flag bit 4 is set;
2. reads the command at the client CCB's read offset; tests the command's sync flags and its
   sync objects (a command waits while a destination sync's counters are short: E018);
3. takes the dummy path (into the completion routine) if context flag bit 1 is set (clearing
   it) or command flag `0x20` is set: no 3D register is written;
4. otherwise, if the command has updates (`+0x19c`), runs an update loop that calls
   `0x1864` (which sets `BIF_BANK0`'s EDM index) before and after it; the completion routine
   has a second such loop, which the dummy path reaches. The updates land through the
   context's directory (E018, E021); which loop acts on a render the runs do not tell;
5. loads the 17 register words (§2.3) into fixed registers, in order: `0x04c4`, `0x04bc`,
   `0x04b8`, `0x0404`, `0x0408`, `0x0414`, `0x0cac` (`BIF_3D_REQ_BASE`), `0x042c`, `0x04c8`,
   `0x0a5c`, `0x0a60`, `0x0a64`, `0x040c`, `0x0410`, `0x0400`, `0x0ab8` (`PDS_EXEC_BASE`),
   `0x0148`; the coefficient groups `+0x044`-`+0x06c`, `+0x070`-`+0x078`, `+0x07c`-`+0x0a0`
   only when the load words `+0x188`, `+0x18c`, `+0x190` are not 0; `+0x194` ORed into a
   register value;
6. writes 1 to `0x0428`, which starts the render.

`PDS_EXEC_BASE` is written per transfer, so the command must carry the base the programs
were placed against (§4.2). The fence word `+0x198` is read and not used. No instruction
writes a BIF directory list at a constant address; after transfers the laptop reads the
context's directory in `BIF_DIR_LIST_BASE1` and `BIF_BANK0` `0x100f` (E018). **[infer]** The
computed-address writes of the routine at `0x17ec` put it there (E015).

### 3.3 Completion

At the end of the render the completion routine (`0x1461`-`0x1591`) reads the command's size
and flags and the shared block, and writes `0x4000` (`SW_EVENT`) to `EVENT_STATUS` at `0x14f8`;
the dummy path enters it at `0x14fa`, past that write, and how it raises its event the dataflow
does not resolve. The rest the runs show: once the interrupt arrives the sync counters and
status values are written, the client CCB's read offset has advanced by the size and the
context's count is 0, for renders and dummies alike (E018, E019). **[infer]** One transfer
renders at a time (E015).

Nothing completes while the EDM is stopped by a fault the kernel has not recovered: a fill
submitted while a render's fault is held never starts, its target untouched, and the EDM answers
no kernel command; the fill stays queued and runs after the reset, where it faults if its client
has gone and its memory with it (E317, one run; one such job).

Evidence: E013, E015, E018, E021, E317.

## 4. Transfers on the hardware

What our kernel does in the linux fork (commits 08-11), and what the laptop showed.

### 4.1 A dummy transfer

Recipe: in the kernel data heap, a 64 KiB client CCB (plus one command), its 8-byte control
block, a `0xb4`-byte context (priority 0, the EDM's own page directory, the CCB addresses) and
two target words U and F. The command: flags `0x20`, one status {F, value}, one update
{U, value}, size `0x1c0`. Write the write offset, then send `TRANSFER` with the context's
address; our kernel carries the `INVAL_DATA` cache-control bit (`0x8`) with each (no run
omits it).

Result (E018): one SW_EVENT per transfer; when the host reads after it, U and F hold their
values, the read offset has advanced by the size and the context's count is 0. Eleven in a row
work. A destination sync one write short keeps the command queued for the 50 ms the kernel
waits (count 1, read offset unmoved); once the host completes the sync and sends
`PROCESS_QUEUES` (no run tries without it) the EDM runs it and sets the write counter to
pending + 1, the read counter untouched. After the dummies `BIF_DIR_LIST_BASE1` holds the
context's page directory and `BIF_BANK0` reads `0x100f`; before any transfer they read 0 and
`0xf`.

### 4.2 A solid fill

The seven programs come from the firmware file (format v2, fw_format.md §9) placed at the PDS
heap base and the pixel-shader code base; the background object holds the PDS state of the
primary and secondary programs and the rectangle's three vertices (80 bits each: Y, X as 24-bit
fixed point with 8 fraction bits and an offset of 4096, then 32 zero bits); the command's
register block matches the file's TQ_CMD list word for word. Our kernel sends `INVAL_BIF` |
`INVAL_DATA` (`0xb`) with every fill and copy (no run omits it). At the REV1 layout the PDS
execution base is the PDS heap base `0x2e000000`, not the `0xe4000000` of the harness's
`layout_base` nor the SGX545 non-REV1 default `0xf0000000` (boot_sequence.md). Our commands
carry flags 0; the closed stack's carry `0x8` (E016); both render.

The background object, as our builders lay it out (`sgx_xfer.c`) and the renders of E019 and
E020 accept it; the captured objects of E004 have the same PDS state words:

| dword | fill (no layer) | copy (one layer) |
|---|---|---|
| 0 | secondary program: offset from the PDS code base in 16-byte units, data size in [31:26] (16-byte units) | same |
| 1 | the primary's attributes in dwords, rounded up to 4, divided by 4; 3 in [17:16] | same, one attribute (the texel) |
| 2 | primary program: offset and data size as dword 0 | same |
| 3-8 | 0 | texture coordinates U0 V0, U1 V0, U0 V1 (IEEE singles, normalised to the source) |
| 9-16 | the three vertices | 9: 0; 10: the layer format, 2 in [7:0] and in [15:8]; 11-14: 0 |
| 15-22 | | the three vertices |

Each vertex takes 80 bits from its first dword: Y, then X (24 bits each, fixed point with 8
fraction bits and an offset of 4096), then 32 zero bits; the order is top-left, top-right,
bottom-left. The command's tag word gives the object's offset in the request window in 16-byte
units and the layer count in [30:25].

Result (E019): four rectangles (whole 64x32, inset on a padded stride, across tiles, one pixel)
exact, three pages around them untouched, no BIF fault.

### 4.3 A linear copy

The programs come from format v3 (fw_format.md §10); the background object has one texture
layer with the source rectangle's normalised coordinates per vertex (U0 V0, U1 V0, U0 V1) and
the layer count is 1 in the tag word. Result (E020): whole, offset between padded strides and
tile-crossing rectangles exact.

Other values of the copy's words, read back pixel by pixel on the laptop:

- Word 0 (the background object tag) at 0, or with bit 24 or 30 flipped: every pixel is the
  source's last texel, over both sources (E272; Q011).
- Word 7 bit 1 (`CR_ISP_MSAA` mode 2): only the first 32 x 16 tile is written, pixel (x, y)
  taking texel (16 + x / 2, 8 + y / 2) (E272; Q011).
- T1 bit 28: the source read as YUYV and converted through colour-space set 0, whose words stay
  from the last job that loaded them (E271; Q010).
- T2 bits 12 to 14: reads of the page before the source and of the destination (E273; Q007).
- The luma key (T0 bit 31): bits 7:0 of its third word are the low end of a luma band whose high
  end is the threshold; a luma inside it takes alpha_below (E275; Q008).

### 4.4 Under a client page directory

A context may name a page directory other than the EDM's: fills and updates through it land
where only that directory maps (E021). With the EDM's own buffers also mapped at their
addresses (read-write or read-only) a fill and its update land; with none of them a fill
without updates lands. **[infer]** A command with updates needs those mappings. In the one run
that aimed a fill at a read-only mapping, the render faulted (`BIF_FAULT` `0x32200001`: the
page, `CID` 1, the client directory's list), wrote nothing and never completed; the EDM then
did not answer a power-off, and a halt, a reload and a boot recovered it (recovery in place
is phase 9).

Evidence: E018, E019, E020, E021, E271, E272, E273, E275.

## 5. The kernel command queue

The host gives the EDM work through the kernel CCB, one of the firmware's buffers (fw_format.md
§3):
256 commands of `0x20` bytes, `{handler, cache control, data[6]}` (sgx545-ce
`sgx_mkif_km.h`:49-54), and a control block {write offset, read offset}, both counted in
commands modulo 256. To send one (`SGXScheduleCCBCommandKM`, `sgxutils.c`:374-502): write the
command at the write offset, advance the write offset and the event-kicker word (`:483`), then
write 1 to `EVENT_KICK` (`:502`). The EDM advances the read offset as it consumes commands (E017:
1 and 1 after the first).

The handler is the command type's entry of the kick-address table in the boot payload,
recorded in the firmware file; this firmware has eight (E012):

| type | command | handler (instruction) | data |
|---|---|---|---|
| 0 | TA | `0x011d` | (phase 10) |
| 1 | TRANSFER | `0x0103` | word 1: the HW transfer context |
| 3 | POWER | `0x00d4` | word 1: 1 power off, 2 idle |
| 4 | CONTEXTSUSPEND | `0x00eb` | |
| 5 | CLEANUP | `0x013a` | |
| 6 | GETMISCINFO | `0x0173` | word 1: the misc-info buffer |
| 7 | PROCESS_QUEUES | `0x0156` | none |
| 9 | SETHWPERFSTATUS | `0x0157` | |

2D, DATABREAKPOINT and FLUSHPDCACHE have no handler in this build.

The cache-control word asks the EDM to invalidate before it handles the command: `INVAL_BIF_PT`
`0x1`, `INVAL_BIF_PD` `0x2`, `INVAL_BIF_SL` `0x4`, `INVAL_DATA` `0x8` (`sgx_mkif_km.h`:269-272).
The first command after the boot carries the init info's value (`0x2` here, E011).

**GETMISCINFO.** With `0x2` (struct sizes) in the misc buffer's first dword, the EDM sets bit 0
and returns seven identity words (core revision and id, DDK version and build, core id 545, the
revision it was built for, build options) and thirteen structure sizes (E017).

**POWER.** POWEROFF (1) and IDLE (2): the EDM sets HostCtl's power status bit 3 or bit 2, and
the clocks gate under the init info's idle mask (E017: about 0.2 ms). A boot after a power-off
works with the same buffers.

Evidence: E011, E012, E017.

## 6. Open questions

- Q003: the faulting transfer of E021 brought no interrupt to the host (whose enable mask is
  `0x4000`, SW_EVENT only), and neither do render faults held without recovery (E317, E319, one
  run each); which event a fault raises, and which requester each fault bit of `BIF_INT_STAT`
  names (bit 5 for E021's write, bit 3 and bit 10 for the render's), are open. A debugfs reset
  (halt, the firmware's buffers rebuilt, boot in place) recovers without a reload of the module.
- Q004: context flag bits 1 and 4 and priorities other than 0 are not run on the hardware.
- Q007: where the copy's buffers lie, which T2 bits 12 and 14 read.
- Q008: the rounding at the luma key's low cut.
- Q010: what clears the colour-space words between jobs.
- Q011: why a wrong background-object tag reads the source's last texel.
- The meanings of the register words without a name here (`0x042c`, `0x0400`, `0x0148`, the
  value `+0x194` adjusts) belong to the 3D state specs (phase 10); the transfer needs only
  the values fw_format.md §9.5 lists.
