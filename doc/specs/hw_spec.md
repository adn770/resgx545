# SGX545 hardware specification

This document describes the PowerVR SGX545 in the Intel Cedarview (Atom N2600/N2800) as a driver
sees it: what the core is, its registers and memory model, how the GPL DDK resets and starts it,
what the closed initialiser hands the kernel for the microkernel's boot, and what the boot
looks like on the hardware. It is a reconstruction, not a vendor document. The architecture
behind the unit names is in `doc/specs/tbdr_primer.md`; the host's register-level boot, step by
step, is in `doc/specs/boot_sequence.md`; the firmware file the driver loads is in
`doc/specs/fw_format.md`.

This part covers the platform and the firmware boot. The host protocol, the probes and the
render units add their parts.

**Sources.** The DDK is Intel's GPL DDK 1.7.862890 for Cedarview, cited as sgx545-ce with its
path from the repository root (`src/services4/...`). Other sources are the Linux v7.3 gma500
driver, public documents and patents by name, and the evidence records under `evidence/`
("Evidence: E002"), which name the captures and the runs on the laptop behind them. A value
read from a run is the value that run gave; an inference is marked `[infer]`.

**Conventions.** Registers are 32-bit, at offsets from the SGX register base. Register names
drop the `EUR_CR_` prefix where the context is clear. Names the DDK's `sgx545defs.h` does not
define come from other public trees; `glossary/registers/` lists each with its source. A
register no source names is given by its offset. Dwords of a control block are numbered from 0.

## 1. Core identity

| property | value | source |
|---|---|---|
| friendly name | `SGX545` | `sgxfeaturedefs.h:119` |
| core id constant | `SGX_CORE_ID_545` | `sgxfeaturedefs.h:120` |
| register header | `sgx545defs.h`, chosen by `#if defined(SGX545)` | `sgxdefs.h:58` |
| family | Series 5XT, USSE instruction set | Imagination's architecture guides |

The silicon reports its identity in two registers, `CORE_ID` at `0x001C` and `CORE_REVISION` at
`0x0020` (`sgx545defs.h:181,188`). Their fields are in §5.1 and the values our laptop reads are
in §8.

*Based on sgx545-ce `src/services4/srvkm/hwdefs/sgxfeaturedefs.h`, `sgxdefs.h`,
`sgx545defs.h`; imgtec-series5-arch-guide-2019.*

## 2. Feature set

The DDK's `#if defined(SGX545)` block (`sgxfeaturedefs.h:118-146`) defines:

| feature macro | value | meaning |
|---|---|---|
| `SGX_FEATURE_ADDRESS_SPACE_SIZE` | 32 | 32-bit (4 GB) GPU virtual address space |
| `SGX_FEATURE_NUM_USE_PIPES` | 4 | four USSE shader pipes |
| `SGX_FEATURE_NUM_PDS_PIPES` | 2 | two programmable data sequencer pipes |
| `SGX_FEATURE_BIF_NUM_DIRLISTS` | 16 | 16 MMU page-directory bases |
| `SGX_FEATURE_MULTIPLE_MEM_CONTEXTS` | defined | hardware multi-context MMU |
| `SGX_FEATURE_MONOLITHIC_UKERNEL` | defined | one monolithic microkernel (the EDM) |
| `SGX_FEATURE_USE_NO_INSTRUCTION_PAIRING` | defined | no paired-instruction slotting |
| `SGX_FEATURE_USE_UNLIMITED_PHASES` | defined | unlimited shader phases |
| `SGX_FEATURE_VOLUME_TEXTURES` | defined | volume textures |
| `SGX_FEATURE_TEXTURESTRIDE_EXTENSION` | defined | strided textures |
| `SGX_FEATURE_PDS_DATA_INTERLEAVE_2DWORDS` | defined | PDS data layout |
| `SGX_FEATURE_ZLS_EXTERNALZ` | defined | external depth load/store |
| `SGX_FEATURE_MAX_TA_RENDER_TARGETS` | 512 | render targets per tiling pass |
| `SGX_FEATURE_NATIVE_BACKWARD_BLIT` | defined | backward blit in hardware |
| `SGX_FEATURE_WRITEBACK_DCU` | defined | write-back data-cache unit |
| `SGX_FEATURE_BIF_WIDE_TILING_AND_4K_ADDRESS` | defined | wide tiling and 4K addressing |
| `SGX_FEATURE_HOST_ALLOC_FROM_DPM` | defined | host allocation from the DPM pool |
| `SGX_FEATURE_SECONDARY_REQUIRES_USE_KICK` | defined | a secondary needs a USE kick |
| `SGX_FEATURE_MULTI_EVENT_KICK` | defined | several event kick registers |
| `SGX_FEATURE_EDM_VERTEX_PDSADDR_FULL_RANGE` | defined | full-range vertex PDS address |
| `SGX_FEATURE_AUTOCLOCKGATING` | defined | automatic clock gating |

Absent: `SGX_FEATURE_2D_HARDWARE` (the SGX545 has no dedicated 2D block),
`SGX_FEATURE_36BIT_MMU` (the MMU is plain 32-bit), `SGX_FEATURE_SYSTEM_CACHE`, `SGX_FEATURE_MP`.

`sgxfeaturedefs.h:186-219` removes features when an erratum is set: `FIX_HW_BRN_27266` drops the
36-bit MMU, `FIX_HW_BRN_27456` wide tiling, `FIX_HW_BRN_31620` multiple memory contexts,
`FIX_HW_BRN_22934` and `FIX_HW_BRN_25499` the multi-event kick. The errata follow the core
revision. `sgxerrata.h` lists the SGX545 revisions 100, 109, 1012, 1013, 10131, 1014 and 10141;
revision 10131 sets only `FIX_HW_BRN_SAMPLE_CACHE` (`sgxerrata.h:634`), so none of the
removals above applies to it. Which revision this firmware was built for is in §8.

*Based on sgx545-ce `src/services4/srvkm/hwdefs/sgxfeaturedefs.h`, `sgxerrata.h`.*

## 3. Register map

`sgx545defs.h` defines 92 register offsets, plus the array macro `USE_CODE_BASE(X)` over the 16
code-base registers it also defines one by one. (Method: the `#define EUR_CR_<name> <offset>`
lines whose name does not end in `_MASK`, `_SHIFT` or `_SIGNED`.) By block:

| block | offsets | role |
|---|---|---|
| `BIF` | 49 | bus interface and MMU: control, faults, 16 directory lists, tiling ranges |
| `USE` | 16 | the USSE code bases `USE_CODE_BASE_0..15` |
| `EVENT` | 12 | event status, host enable and clear (two banks), kicks, kicker, timer |
| `PDS` | 5 | PDS execution base and invalidates |
| clock gating | 4 | `CLKGATECTL`, `CLKGATECTL2`, `CLKGATESTATUS`, `CLKGATECTLOVR` |
| `CORE`, `DESIGNER` | 4 | identity and designer revision |
| `TIMER`, `SOFT_RESET` | 2 | free-running timer, per-block reset |

The header is a subset: the microkernel reaches many registers it does not define (§10).

Key registers:

| register | offset | role |
|---|---|---|
| `CLKGATECTL` | `0x0000` | clock gating control |
| `CLKGATECTL2` | `0x0004` | clock gating control 2 |
| `CLKGATESTATUS` | `0x0008` | clock gating status |
| `CLKGATECTLOVR` | `0x000C` | clock gating override |
| `CORE_ID` | `0x001C` | core identity |
| `CORE_REVISION` | `0x0020` | silicon revision |
| `SOFT_RESET` | `0x0080` | per-block reset |
| `EVENT_HOST_ENABLE2` | `0x0110` | event enable, bank 2 |
| `EVENT_HOST_CLEAR2` | `0x0114` | event clear, bank 2 |
| `EVENT_STATUS2` | `0x0118` | event status, bank 2 |
| `EVENT_STATUS` | `0x012C` | event status |
| `EVENT_HOST_ENABLE` | `0x0130` | event enable |
| `EVENT_HOST_CLEAR` | `0x0134` | event clear |
| `TIMER` | `0x0144` | timer |
| `USE_CODE_BASE_0..15` | `0x0A0C + 4n` | USSE code base per data master |
| `PDS_EXEC_BASE` | `0x0AB8` | PDS code base |
| `EVENT_KICKER` | `0x0AC4` | device address of the kicker word |
| `EVENT_KICK` | `0x0AC8` | doorbell |
| `EVENT_TIMER` | `0x0ACC` | event timer |
| `EVENT_KICK1..3` | `0x0AE4..0x0AEC` | further doorbells (multi-event kick) |
| `BIF_CTRL` | `0x0C00` | MMU control |
| `BIF_INT_STAT` | `0x0C04` | MMU fault status |
| `BIF_FAULT` | `0x0C08` | faulting directory list and page |
| `BIF_DIR_LIST_BASE1..15` | `0x0C38 + 4(n - 1)` | page directories of lists 1 to 15 |
| `BIF_BANK0` | `0x0C78` | directory list per requestor |
| `BIF_DIR_LIST_BASE0` | `0x0C84` | page directory of list 0 |

*Based on sgx545-ce `src/services4/srvkm/hwdefs/sgx545defs.h`.*

## 4. Memory model: MMU and BIF

- **Two levels, 4 KB pages.** A virtual address splits 10 / 10 / 12: page directory index
  (`SGX_MMU_PD_SHIFT` 10, mask `0xFFC00000`), page table index (`SGX_MMU_PT_SHIFT` 10, mask
  `0x003FF000`), page offset (`SGX_MMU_PAGE_SHIFT` 12).
- **PDE** (`sgxmmu.h:45-52`): bit 0 `VALID`; bits 1-3 the page size (4K, 16K, 64K, 256K, 1M,
  4M); address mask `0xFFFFF000`. The 36-bit layout does not apply (§2). No record shows a run
  with a size other than the smallest (Q109).
- **PTE** (`sgxmmu.h:65-69`): `VALID` `0x1`, `WRITEONLY` `0x2`, `READONLY` `0x4`,
  `CACHECONSISTENT` `0x8`, `EDMPROTECT` `0x10`; address mask `0xFFFFF000`. Only `READONLY` is
  run in a record (a write to a read-only page faults, E021, E319); what the other flags do is Q108.
- **BIF.** The bus interface is the MMU's front end. With 16 directory lists and multiple
  memory contexts, `BIF_DIR_LIST_BASE0..15` hold up to 16 page directories at once, and
  `BIF_BANK0` says which list each requestor translates through (§5.5).
- **Tiling.** `BIF_TILE0..n` describe tiled address ranges (start, end, stride); the DDK
  programs them in `sgxinit.c:1476-1529`. No record touches them (Q110).

*Based on sgx545-ce `src/services4/srvkm/hwdefs/sgxmmu.h`, `sgx545defs.h`,
`src/services4/srvkm/devices/sgx/sgxinit.c`.*

## 5. Register fields for the boot

All fields from `sgx545defs.h`.

### 5.1 `CORE_ID` (0x1C) and `CORE_REVISION` (0x20)

- `CORE_ID`: `ID` [31:16], `CONFIG` [15:0].
- `CORE_REVISION`: `DESIGNER` [31:24], `MAJOR` [23:16], `MINOR` [15:8], `MAINTENANCE` [7:0].

The DDK writes a revision as its digits run together: 1.0.13 is `SGX_CORE_REV` 1013, and the
revisions of §2 are spelled the same way.

### 5.2 `SOFT_RESET` (0x80)

One bit per block, 1 holds it in reset and 0 releases it:

| bit | field | block |
|---|---|---|
| 0 | `BIF_RESET` | bus interface and MMU |
| 1 | `DPM_RESET` | parameter memory manager |
| 2 | `TA_RESET` | tile accelerator |
| 3 | `USE_RESET` | USSE |
| 4 | `ISP_RESET` | image synthesis processor |
| 5 | `TSP_RESET` | texture and shading processor |

(`sgx545defs.h:209-225`.) The bits name the pipeline blocks of the primer.

### 5.3 `CLKGATECTL` (0x00)

Two bits per unit: `ISP` [1:0], `ISP2` [3:2], `TSP` [5:4], `TE` [7:6], `MTE` [9:8], `DPM`
[11:10], `VDM` [13:12], `PDS0` [15:14]; `AUTO_MAN_REG` [24] = 1 selects automatic gating.
`CLKGATECTL2` does the same for `PBE`, `CACHEL2`, `UCACHEL2`, `USE0`, `ITR0`, `TEX0`, `MADD0`,
`USE1`, `ITR1`, `TEX1`, `MADD1` and `PDS1`, from bit 0 up.

### 5.4 `BIF_CTRL` (0xC00)

`NOREORDER` [0], `PAUSE` [1], `FLUSH` [2], `INVALDC` [3] (invalidate the directory cache),
`CLEAR_FAULT` [4]; per-requestor MMU bypass: `CACHE` [8], `VDM` [9], `TE` [10], `PBE` [11],
`TSPP` [12], `ISP` [13], `USE` [14], `HOST` [15].

The SGX545 header has no `BIF_CTRL_INVAL` register. The DDK's reset therefore invalidates the
directory cache by writing `INVALDC` to `BIF_CTRL` and then 0 (`SGXResetInvalDC`,
`sgxreset.c:272-300`).

### 5.5 Faults and directory lists

- `BIF_INT_STAT` (0xC04): `FAULT_REQ` [15:0], one bit per faulting requestor; `FAULT_TYPE`
  [18:16]; `FLUSH_COMPLETE` [19].
- `BIF_FAULT` (0xC08): `CID` [3:0], the directory list the faulting access went through; `SB`
  [8:4]; `ADDR` [31:12], the faulting page.
- `BIF_DIR_LIST_BASE0` (0xC84) and `BASE1..15`: the page directory of each list.
- `BIF_BANK0` (0xC78): the list each requestor uses: `INDEX_EDM` [3:0], `INDEX_TA` [7:4],
  `INDEX_HOST` [11:8], `INDEX_3D` [15:12], `INDEX_2D` [19:16].

So `CID` and `BIF_DIR_LIST_BASE<CID>` name the page directory, hence the address space, of a
fault.

During the renders of a context on a freshly reset GPU `BIF_BANK0` takes `INDEX_TA` = 1 and
`INDEX_3D` = 1 (12 of 12 runs; `INDEX_EDM` = 1 as well in 5), and a fault of the first job names
`CID` 1, so the render's TA and 3D reach memory through list 1 (E457). In the client directory the
aliases of the EDM's buffers 6, 7, 8, 10 and 11 are not needed for a 64 x 64 render (each left out
alone, 10 of 10 runs exact); TA3DCtl is, writable (Q076).

On the laptop the EDM keeps its own directory in `BASE15` and gives each render context's
directory one of lists 0 to 14 at its first kick, in turn after a reset (1, 2, ... 14, then 0),
recording the last in TA/3D control block dword 49; our kernel reads a fault's directory back from
the list `CID` names (E360). A fault raises no bit of `EVENT_STATUS` or `EVENT_STATUS2` of its
own (E357).

A 4x multisampled render of our stack (mode 2, `CR_TE_AA` 0xe0000000, the unpoked macrotile words)
at 320 x 160 and up faults the job with `BIF_FAULT` reading 0x90004 at the page 0x20006 (320 x 160
to 512 x 256), 0x20008 (512 x 384) and 0x2000a (640 x 480) (6 of 6 jobs, E507); the script's health
check, a plain 64 x 64 triangle, failed after each of the last three in a row and stopped it (five
`SGX recovery failed: -110` kernel lines in the run). The cause is open (Q140, a kernel
question).

### 5.6 Unit names

`BIF` bus interface and MMU; `DPM` parameter memory manager; `TA` tile accelerator; `VDM`
vertex data master; `TE`, `MTE` tiling engine and macro-tiling engine; `PDS` programmable data
sequencer; `USE` the USSE shader core; `ISP` hidden-surface processor; `TSP`, `TSPP` texture
and shading processor and its pre-processor; `PBE` pixel back end (tile write-out).

*Based on sgx545-ce `src/services4/srvkm/hwdefs/sgx545defs.h`,
`src/services4/srvkm/devices/sgx/sgxreset.c`; E357, E360, E507.*

## 6. How the DDK resets and starts the core

### 6.1 Outline

1. Map the registers at the SGX register base (`pvRegsBaseKM`).
2. Reset the blocks through `SOFT_RESET`, then release them.
3. Configure clock gating through `CLKGATECTL` and `CLKGATECTL2`.
4. Bring up the MMU: page directories into `BIF_DIR_LIST_BASE0..15`, tiling ranges into
   `BIF_TILE*`, the directory cache invalidated as in §5.4.
5. Enable host events through `EVENT_HOST_ENABLE` and `EVENT_HOST_ENABLE2`; read and clear
   them through `EVENT_STATUS`, `EVENT_STATUS2`, `EVENT_HOST_CLEAR` and `EVENT_HOST_CLEAR2`.
6. Start the microkernel (§6.3).

The debug dump (`sgxinit.c:1031-1038`) reads `BIF_CTRL`, `BIF_BANK0`, `BIF_INT_STAT`,
`BIF_FAULT`, `BIF_MEM_REQ_STAT` and `CLKGATECTL`: the registers the DDK itself checks first.

### 6.2 The init scripts

The register-level boot is data. An init script is an array of `SGX_INIT_COMMAND`
(`include4/sgxscript.h`) that `SGXRunScript` (`sgxinit.c:242`) replays:

| operation | effect |
|---|---|
| `SGX_INIT_OP_WRITE_HW_REG` | write one register (offset, value) |
| `SGX_INIT_OP_PDUMP_HW_REG` | record a register (PDUMP builds only) |
| `SGX_INIT_OP_HALT` | end of script |
| `SGX_INIT_OP_ILLEGAL` | error |

There are three: `asInitCommandsPart1` and `asInitCommandsPart2` (up to 64 commands each) and
`asDeinitCommands` (up to 16). The kernel does not build them. The user-space initialiser
(srvinit) builds them, together with the EDM task registers (`ui32EDMTaskReg0/1`,
`sgxinit.c:214`), from the heap table and page-directory address the kernel gives it through
`SGXGetInfoForSrvinitKM` (`sgxinit.c:591`). The values srvinit produces for this core are in
§9.

### 6.3 `SGXInitialise`

`SGXInitialise` (`sgxinit.c:286-413`):

1. `SGXInitClocks`: program clock gating.
2. Run init script part 1.
3. `SGXReset(psDevInfo, bFirstTime || bHardwareRecovery)`: the first boot after load passes
   the hardware-recovery flag, so it takes the full reset path (`sgxinit.c:292,316`).
4. Zero the kernel CCB's event-kicker word.
5. Run init script part 2.
6. Write `HostCtl.ui32HostClock`, then `HostCtl.ui32InitStatus = 0`.
7. Write barrier, then kick the microkernel: with `SGX_FEATURE_MULTI_EVENT_KICK` the DDK writes
   `EVENT_KICK2` `NOW` and leaves the kicker word alone; otherwise it bumps the kicker and
   writes `EVENT_KICK` (`sgxinit.c:373-384`).
8. Poll `HostCtl.ui32InitStatus` for `PVRSRV_USSE_EDM_INIT_COMPLETE` (bit 0,
   `sgx_mkif_km.h:222`) (`sgxinit.c:413`); on timeout dump the debug state and fail.

The DDK's `EUR_CR_POWER` write between steps 3 and 4 is compiled only where the header defines
that register; `sgx545defs.h` does not. The full sequence, with every register write and its
value, is `doc/specs/boot_sequence.md`.

### 6.4 Event bits

`EVENT_STATUS` (`0x012C`) is the host's view of the pipeline. Its bits, high to low:
`MASTER_INTERRUPT` 31, `TIMER` 29, `TA_DPM_FAULT` 28, `MADD_CACHE_INVALCOMPLETE` 26,
`DPM_OUT_OF_MEMORY_ZLS` 25, `DPM_TA_MEM_FREE` 24, `ISP_END_TILE` 23, `DPM_INITEND` 22,
`ISP2_ZLS_CSW_FINISHED` 21, `OTPM_INV` 20, `OTPM_FLUSHED` 19, `PIXELBE_END_RENDER` 18,
`ISP_VISIBILITY_FAIL` 16, `BREAKPOINT` 15, `SW_EVENT` 14, `TA_FINISHED` 13, `TA_TERMINATE` 12,
`TPC_CLEAR` 11, `TPC_FLUSH` 10, `DPM_CONTROL_CLEAR` 9, `DPM_CONTROL_LOAD` 8,
`DPM_CONTROL_STORE` 7, `DPM_STATE_CLEAR` 6, `DPM_STATE_LOAD` 5, `DPM_STATE_STORE` 4,
`DPM_REACHED_MEM_THRESH` 3, `DPM_OUT_OF_MEMORY_GBL` 2, `DPM_OUT_OF_MEMORY_MT` 1,
`DPM_3D_MEM_FREE` 0 (`sgx545defs.h:367-451`; the debug dump decodes them, `sgxinit.c:907`).
`TA_*` is the geometry and tiling front end, `ISP` the hidden-surface stage, `PIXELBE` the tile
write-out, `DPM` the parameter memory manager. Which event sets which bit in an ordinary job is
partly known, and for how long a bit is set is open (Q111, Q166). Seen on the hardware (E547, E548):
PIXELBE_END_RENDER, DPM_3D_MEM_FREE and MADD_CACHE_INVALCOMPLETE show in a triangle, TA_FINISHED,
TPC_FLUSH and the DPM state and control bits in the 256-pixel and partial jobs, a fill shows
PIXELBE_END_RENDER and a copy only SW_EVENT, which comes with MASTER_INTERRUPT (41 of 41 jobs);
armed one at a time through the host enables, bits 0, 6, 9, 18, 20 and 26 of CR_EVENT_STATUS and bit
1 of CR_EVENT_STATUS2 raised an extra host interrupt in a 64 x 64 triangle, bit 26 in a fill, and
for TA_FINISHED and TA_TERMINATE the host saw none, which does not show that they cannot. What
depends on the firmware or on a race with it is [infer]: the short pulses of PIXELBE_END_RENDER,
DPM_3D_MEM_FREE and TA_FINISHED are 4.2 to 6.1 microseconds, at most a few samples wide (sampling
intervals averaging 1.06 to 5.58 microseconds), the time to the firmware's acknowledgement; SW_EVENT
is the firmware's own event and its pulse (4.3 to 87.5 microseconds) the host's handling of it; and
which armed bit raised an interrupt is read from the enable written, not from the status the handler
saw.

`EVENT_STATUS2` (`0x0118`) reads 0x400 (`DCU_INVAL_COMPLETE`) when the core is idle;
OTPM_MEM_CLEARED (bit 12) and DPM_TA_FREE_LOAD (bit 0) pulse in some depth-store, 256-pixel and
partial jobs (E547). Its
`TRIG_TA` (bit 7) and `TRIG_3D` (bit 6) latch on the laptop: bit 7 within 0.2 ms of the PB load of
a TA that hangs or faults, bit 6 about 0.1 ms into a fill whose pixel program loops 128 times or
more; neither sets in the renders, fills and copies of our stack, and each stays set until the
core is reset (E357). A vertex program of our own that loops on a backward `br` (8 instructions an
iteration) left bit 7 clear through 880 iterations and set it at 1760, so bit 7 does not follow the
pixel latch's 53 to 55 iterations (E784). Both are host events: written alone into
`CR_EVENT_HOST_ENABLE2` they raise the host interrupt once set (E444), as do `TIMER`
(`CR_EVENT_STATUS` bit 29) and `DCU_INVAL_COMPLETE`, which an idle core has set; the EDM's write
fault sets no bit beyond the idle ones. `CLKGATESTATUS` (`0x0008`) reads 0x20 idle and the same
values under a floating-point and an integer pixel loop with the gates as the boot leaves them
(E365), and with seven two-bit fields of `CR_CLKGATECTL2` at 0, 1 and 3, the MADD fields among
them, written in turn while idle (E445; Q048). Writing both MADD fields during a loop ten times as
long hung all six jobs, and the same loops with no write hung in 6 of 7 runs, so that half is
untested (E445).

*Based on sgx545-ce `src/services4/srvkm/devices/sgx/sgxinit.c`, `sgxreset.c`,
`src/services4/include4/sgxscript.h`, `src/services4/include/sgx_mkif_km.h`,
`src/services4/srvkm/hwdefs/sgx545defs.h`; E357, E365, E784.*

## 7. Where the microkernel comes from

The SGX545's microkernel (the EDM, the Event-Driven Microkernel, running on the USSE) is not a
kernel firmware file in the DDK. The GPL kernel module has no SGX `request_firmware()` and holds
no microkernel image; it only allocates the buffers and replays the scripts. srvinit, a closed
user-space library, uploads the image into the KERNEL_CODE heap through the device-memory calls
and passes the init scripts and control-block handles down through `SGXDevInitPart2`.

resgx545's driver keeps the kernel side and replaces the upload: `tools/fwcutter` cuts the
microkernel, the five PDS programs and srvinit's tables from the user's own copy of the
Cedarview library into one file, which the driver loads with `request_firmware()`
(`doc/specs/fw_format.md`). The PowerVR firmware in linux-firmware is for the Rogue cores the
mainline `imagination` driver supports and does not apply to the SGX545.

*Based on sgx545-ce `src/services4/srvkm/devices/sgx/sgxinit.c`; `doc/specs/fw_format.md`;
linux-imagination.*

## 8. The platform

The target is a Cedarview laptop: Atom N2600, 2 GB, i686, running Arch Linux 32 with Linux 7.3
and our gma500, whose debug option exposes the SGX state in debugfs (`sgx/status`,
`sgx/regs`). Everything below is read through those files and through the PCI sysfs, before the
firmware is loaded.

| item | value |
|---|---|
| GPU | Cedarview, PCI `8086:0be1` rev 09 at `00:02.0`, subsystem `8086:1999` |
| driver | gma500 (display and KMS) |
| register BAR | BAR0 at `0x80000000`, 1 MB, non-prefetchable; I/O ports at `0x7100` |
| SGX register base | `0x80080000` = BAR0 + `SGX_REGS_OFFSET` (`0x80000`) |
| host bridge | `00:00.0`, `8086:0bf1` rev 03 |
| `CORE_ID` | `0x01150000`: ID `0x0115`, config 0 |
| `CORE_REVISION` | `0x0001000d`: 1.0.13 |
| `CLKGATECTL`, `SOFT_RESET` | 0 and 0 before the load: idle, no block held in reset |
| interrupt | MSI (IRQ 25 on this boot) |
| BAR2 | none: gma500 takes its fallback aperture, `0x40000000`, 128 MB `[infer]` |

(Evidence: E007.) The aperture follows from Linux v7.3's `gtt.c` (`psb_gtt_init`) given no
BAR2; the run does not read it back, nor the stolen-memory and GTT sizes.

The SGX shares the display's PCI function and BAR: the DDK's unified Cedarview path places its
registers at `SGX_REGS_OFFSET` into BAR0 (`sysconfig.h:43`, applied in `sysconfig.c:202`).
gma500 binds the function in Linux v7.3 (`drivers/gpu/drm/gma500/psb_drv.c`, the Cedarview
device ids), so the SGX driver lives inside gma500 rather than beside it.

**Which build the firmware is.** The microkernel's HostCtl is 0x44 bytes (Evidence: E001). The
DDK's `SGXMKIF_HOST_CTL` (`sgx_mkif_km.h:70-112`) gains `ui32BRN31939Mem` under
`FIX_HW_BRN_31939`, which revision 1013 sets and 10131 does not (`sgxerrata.h:630-635`). With
`SUPPORT_HW_RECOVERY` on, a 1013 build's HostCtl is 0x48, so the firmware was built for revision
10131, which reports itself as 1.0.13 and carries only `FIX_HW_BRN_SAMPLE_CACHE` `[infer]`. The
silicon's 1.0.13 matches (Evidence: E007).

**The sample-cache workaround applies.** The Cedarview system layer enables it when the host
bridge's revision is below 4 (`sysconfig.c:98`); ours is revision 3 (Evidence: E007).
`doc/specs/boot_sequence.md` describes what the workaround changes (the heap layout).

*Based on sgx545-ce `src/services4/system/unified/sysconfig.h`, `sysconfig.c`,
`src/services4/include/sgx_mkif_km.h`, `src/services4/srvkm/hwdefs/sgxerrata.h`; E001, E007;
linux-gma500.*

## 9. The boot payload

srvinit's contribution to a boot reaches the kernel as one buffer, the 2068-byte input of
`SGX_DEVINITPART2`, which is the complete `SGX_BRIDGE_INIT_INFO`. Its layout depends on build
`#ifdef`s; it is pinned by running the closed srvinit to completion under the extraction
harness (`harness/ukernel-extract/`) and decoding the buffer with `initinfo.py`: every handle
field lands on one of the harness's allocations and the field table consumes the buffer
exactly (Evidence: E001, E011). The values below are what `doc/specs/fw_format.md`
carries in the firmware file.

To read the microkernel itself, with its handlers, boot path and register-access sites
labelled, run `harness/ukernel-extract/make_r2.sh` on your own firmware; it writes a radare2
script for the `usse` plugin.

### 9.1 Build configuration

- **No 2D hardware.** The misc-info structure sizes have 13 fields, the two 2D command sizes
  absent (Evidence: E001), and the kick-address table has no 2D entry (Evidence: E011). 2D
  work goes through the transfer queue.
- `SUPPORT_SGX_HWPERF` is on (a HWPerf circular buffer is allocated); there is no
  `SGX_FEATURE_MP`. The client build options are `0x60218` (Evidence: E011).

### 9.2 Control blocks

srvinit allocates, in this order (Evidence: E001, E002; `doc/specs/fw_format.md` §3):

| init-info field | size | contents |
|---|---|---|
| `hKernelCCBMemInfo` | `0x2000` | kernel CCB: 256 `SGXMKIF_COMMAND` of `0x20` bytes |
| `hKernelCCBCtlMemInfo` | `0x8` | write offset (+0, host), read offset (+4, EDM) |
| `hKernelCCBEventKickerMemInfo` | `0x4` | event-kicker word |
| `hKernelSGXTA3DCtlMemInfo` | `0xec` | TA/3D control (TA3DCtl) |
| `hKernelSGXHostCtlMemInfo` | `0x44` | host control (HostCtl) |
| `hKernelSGXMiscMemInfo` | `0x54` | misc info |
| `hKernelHWPerfCBMemInfo` | `0x640c` | HWPerf circular buffer |
| `hKernelTASigBufferMemInfo` | `0x620` | TA signature buffer |
| `hKernel3DSigBufferMemInfo` | `0x2088` | 3D signature buffer |
| `asInitMemHandles[0..5]` | | KERNEL_CODE: the microkernel (`0xCF68`) and five PDS programs |

The control blocks live in the KERNEL_DATA heap, the code in KERNEL_CODE (Evidence: E011).

**HostCtl** (`SGXMKIF_HOST_CTL`) has 17 dwords in this build: `SUPPORT_HW_RECOVERY` (build
option bit 3) is on and EDM breakpoints are off. Dword 0 is `ui32InitStatus`; 1-2 the power and
cleanup status; 3-5 the hardware-recovery fields; 6 `ui32uKernelTimerClock`; 7 the active-power
sample rate; 8-9 the interrupt flags; 10-12 the breakpoint signal, the power-event count and the
EDM tick count (`ui32TimeWraps` in the DDK; Evidence: E005); 13 `ui32HostClock`; 14
`ui32AssertFail`; 15 `ui32PerfGroup`; 16 the OpenCL delay count. The size, `0x44`, is the one
srvinit reports (Evidence: E001). Which side writes each dword is in
`doc/specs/boot_sequence.md`.

### 9.3 MKIF structure sizes

The microkernel was built against these sizes (Evidence: E001): `CMDTA 0x2b0`,
`CMDTA_SHARED 0x1e0`, `TRANSFERCMD 0x4c8`, `TRANSFERCMD_SHARED 0xdc`, `3DREGISTERS 0xd0`,
`HWPBDESC 0x3c`, `HWRENDERCONTEXT 0x44`, `HWRENDERDETAILS 0x1ec`, `HWRTDATA 0x38`,
`HWRTDATASET 0x50`, `HWTRANSFERCONTEXT 0xb4`, `HOST_CTL 0x44`, `COMMAND 0x20`. A host-side
implementation lays these structures out to exactly these sizes.

### 9.4 Init scripts

**Part 1** (before the reset, 2 writes): `EVENT_PDS_ENABLE = 0`, `EVENT_TIMER = 0`
(Evidence: E006).

**Part 2** (after the reset, 38 writes, in order). Address-valued entries are given by what
they name: a heap base or a buffer's device address.

| # | reg | name | value |
|---|---|---|---|
| 1 | `0x0818` | - | `0x000007ff` |
| 2 | `0x0810` | - | `0x00000001` |
| 3 | `0x0814` | - | `0x0000ffff` |
| 4 | `0x0130` | `EVENT_HOST_ENABLE` | `0x00004000` |
| 5 | `0x0110` | `EVENT_HOST_ENABLE2` | `0x00000000` |
| 6 | `0x013c` | `PDS_CACHE_HOST_ENABLE` | `0x00000000` |
| 7 | `0x0a7c` | `USE_G0` | `0x00000000` |
| 8 | `0x0a80` | `USE_G1` | `0x00000000` |
| 9 | `0x0a74` | `DMS_CTRL` | `0x00208200` |
| 10 | `0x04e8` | - | `0x00000100` |
| 11 | `0x0a78` | - | `0x0000002c` |
| 12 | `0x0aac` | `USE_TMPREG` | `0x00000045` |
| 13 | `0x0abc` | - | `0x0000000e` |
| 14 | `0x0800` | - | `0x00000030` |
| 15 | `0x0804` | `CACHE_CTRL` | `0x0000ffff` |
| 16 | `0x0a00` | `USE_CTRL` | `0x0007c000` |
| 17-26 | `0x0a0c-0x0a30` | `USE_CODE_BASE_0..9` | PIXELSHADER heap + n x `0x80000`, DM pixel |
| 27-30 | `0x0a34-0x0a40` | `USE_CODE_BASE_10..13` | VERTEXSHADER heap + n x `0x80000`, DM vertex |
| 31 | `0x0a48` | `USE_CODE_BASE_15` | KERNEL_CODE heap base, DM EDM |
| 32 | `0x0ab8` | `PDS_EXEC_BASE` | PDSPIXEL_CODEDATA heap base |
| 33 | `0x0b30` | - | `0x00000100` |
| 34 | `0x0ac4` | `EVENT_KICKER` | device address of the event-kicker word |
| 35 | `0x0a68` | `EVENT_OTHER_PDS_EXEC` | device address of PDS #10 |
| 36 | `0x0a6c` | `EVENT_OTHER_PDS_DATA` | `0x00000001` (PDS #10's data rows) |
| 37 | `0x0a70` | `EVENT_OTHER_PDS_INFO` | `0x00000006` |
| 38 | `0x0a58` | `EVENT_PDS_ENABLE` | `0x2204b00f` |

(Evidence: E006, E403, E404.) What `0x0810`-`0x0818` control is open (Q001), narrowed by E403 and
E404: none changes a job's time or causes a fault at any load tried, and a reset (one tried) runs
this part again;
`0x0818` with bit 8 set and bit 10 clear makes a triangle draw wrong after another of a
different size, the job reporting ok.

**Deinit** (9 writes): clear `EVENT_PDS_ENABLE`, `EVENT_OTHER_PDS_EXEC`, `_DATA` and `_INFO`,
`USE_CODE_BASE_15`, `EVENT_HOST_ENABLE` and `EVENT_HOST_ENABLE2`, then `CLKGATECTL = 0` and
`CLKGATECTL2 = 0` (Evidence: E006). On the laptop, the registers the driver's snapshot reads
hold the scripts' values after a boot, and the ones the deinit script clears read 0 after the
stop (Evidence: E006, E008).

`USE_CODE_BASE_n` holds `ADDR` [24:0], the code address in 128-byte units, and a data-master
field `DM` [26:25] (`sgx545defs.h:635-638`). With that decode the three groups land on the
pixel-shader heap (DM 1), the vertex-shader heap (DM 0) and, for `USE_CODE_BASE_15`, the base of
the KERNEL_CODE heap (DM 3): the EDM's code base is where the microkernel sits (Evidence: E003;
`doc/specs/fw_format.md` §5).

Reading the order `[infer]`: cache and event configuration, then the shader code bases, the PDS
code base, `0x0b30`, the kicker word's address, the EDM's boot PDS program (PDS #10, with
`_DATA` = 1 and `_INFO` = 6), and last `EVENT_PDS_ENABLE`, which arms event-to-PDS dispatch so
that the first kicked event starts the EDM.

### 9.5 What depends on the kernel's answers

srvinit asks the kernel for the heap table and the page-directory address
(`SGXGetInfoForSrvinitKM`, `sgxinit.c:591`). The heap bases reach `PDS_EXEC_BASE`, the code
bases and `asInitDevData[12..13]` (the PDS and pixel-shader heap bases). The page-directory
address becomes TA3DCtl dword 23 (Evidence: E002); a capture with only that address changed
differs in that dword and nowhere else (Evidence: E011). On the hardware it is
the physical address of the page directory the host builds for the EDM.

srvinit also asks `SGX_GETMISCINFO` once for the driver's revision (`DRIVER_SGXREV`). The DDK
version, build and build options in the answer change nothing: answered with the struct
untouched, all zeros, the DDK's own values or build options that disagree with srvinit's
`0x60218` in every bit, srvinit makes the same 57 bridge calls, succeeds, and leaves a
byte-identical init info and buffers at the `REV1` layout (Evidence: E352). The core revision
and core id words were 0 in every run.

### 9.6 Other EDM values

- **EDM task registers:** `USE0_SERV_EVENT` and `USE1_SERV_EVENT` (`0xb14`, `0xb20`).
- **Clock gating:** `CLKGATECTL = 0xa6aa`, `CLKGATECTL2 = 0xaaaaaa`; idle is polled on
  `CLKGATESTATUS` (`0x8`) with the mask `0xffffffdf`.
- **Cache control:** `0x2`.
- **`asInitDevData[8..13]`:** `2, 0, 0x300, 0x940`, then the PDS and pixel-shader heap bases.

(Evidence: E011.)

*Based on E001, E002, E003, E005, E006, E008, E011, E352; `doc/specs/fw_format.md`; sgx545-ce
`src/services4/srvkm/devices/sgx/sgxinit.c`, `src/services4/srvkm/hwdefs/sgx545defs.h`.*

## 10. The registers the microkernel reaches

The EDM reaches SGX registers with register load and store instructions whose immediate is a
dword register index (offset = index x 4). Our disassembly of the firmware, for
interoperability, finds 191 distinct indices, 72 of them read and 140 written, with 183 read
sites and 421 write sites; `sgx545defs.h` names 21 of them (Evidence: E010).

The microkernel reads `CORE_ID` and `CORE_REVISION`, writes `SOFT_RESET` at 2 sites, writes
`EVENT_HOST_CLEAR` at 34 sites and `EVENT_HOST_CLEAR2` at 4 (it acknowledges its own events),
and writes `BIF_CTRL`, `BIF_BANK0` and `BIF_BANK_SET` but no directory-list base (Evidence:
E010). The per-register list, with read and write counts, is regenerated by
`tools/usse-dis/regtouch.py` from the disassembly.

*Based on E010.*

## 11. The boot path

### 11.1 From the kick to `InitStatus`

The EDM is entered through PDS programs: a PDS program loads the secondary attributes and starts
a USSE task. The boot chain, with byte offsets into the microkernel:

1. The last writes of init script part 2 point `EVENT_OTHER_PDS_EXEC` at PDS #10 and enable
   event-to-PDS dispatch (Evidence: E006). The host then clears `HostCtl.ui32InitStatus`, sets
   `ui32HostClock` and writes `EVENT_KICK2` (§6.3), and the kick runs PDS #10, which starts the
   EDM's boot task `[infer]`.
2. The boot task launches PDS #11 and PDS #12: the loader writes their launch control words and
   addresses into it, at bytes `0xd60`-`0xd70` and `0xdb0`-`0xdc0`, and TA3DCtl's address at
   `0xd78` (Evidence: E003). PDS #11 copies TA3DCtl into the secondary attributes, which the EDM
   reads as base pointers into TA3DCtl, HostCtl and the kernel CCB control (Evidence: E002).
3. The boot installs PDS #13 as the steady-state event program: the loader writes PDS #13's
   address and data size into the instructions at bytes `0xe40` and `0xe50`, which store them to
   `EVENT_OTHER_PDS_EXEC` and `_DATA` (Evidence: E002, E003). After the boot those registers read
   PDS #13's address and 6 (Evidence: E008), `EVENT_TIMER` reads bit 24 set with a count below
   HostCtl dword 6 (Evidence: E009), and `HostCtl.ui32InitStatus` bit 0
   (`PVRSRV_USSE_EDM_INIT_COMPLETE`) is set. `SGXInitialise` polls exactly that bit, so it is
   the signal that the firmware is up (Evidence: E008).

To read the microkernel's boot path itself, with its handlers and register-access sites
labelled, run `harness/ukernel-extract/make_r2.sh` on your own firmware.

### 11.2 PDS programs

The five KERNEL_CODE allocations after the microkernel are PDS programs, each a data segment
followed by 32-bit PDS instructions (`doc/specs/fw_format.md` §3). Their data segments hold the
code words of the USSE entries they start, which the loader relocates with the microkernel
(`CODE_WORD` records; Evidence: E003).

| program | started by | data size |
|---|---|---|
| #10 | init script part 2 (`EVENT_OTHER_PDS_EXEC`) | 1 (`_DATA`; Evidence: E006) |
| #11 | the boot task | |
| #12 | the boot task | |
| #13 | installed by the boot as the event program | 6 (`_DATA` after the boot; Evidence: E008) |

PDS #13 and #14 serve the running firmware and belong with the host protocol.

### 11.3 Placement

The EDM code base (`USE_CODE_BASE_15`) is the KERNEL_CODE heap base. resgx545's driver places
the microkernel at the base itself, and it boots there (Evidence: E008). srvinit, under the
extraction harness, places it `0x1000` bytes in (Evidence: E011) and moves the PDS code words
with it, while it leaves the kick-address table alone (Evidence: E002).

*Based on E002, E003, E006, E008, E009, E011; `doc/specs/fw_format.md`.*

## 12. The boot on the hardware

The laptop boots the firmware from our gma500 (Linux 7.3) with the sequence of
`doc/specs/boot_sequence.md` and the buffers the reference loader builds from the firmware file
(Evidence: E008).

- **It comes up.** In 18 of 20 cycles `HostCtl.ui32InitStatus` bit 0 is seen 165-355 µs after
  the `EVENT_KICK2` write (median 170 µs); the driver's poll sleeps 50-100 µs between reads, so
  these are upper bounds. The first boot of a run took up to 2.4 ms. There is no BIF fault and
  no `AssertFail`, and `CLKGATESTATUS` reads `0x20` (Evidence: E008).
- **The EDM's address space is directory list 15.** After the boot `BIF_BANK0` reads `0xf`, so
  `INDEX_EDM` = 15 and every other requestor uses list 0; `BIF_DIR_LIST_BASE15` holds the page
  directory the host built for the EDM, the one TA3DCtl dword 23 names (§5.5; Evidence: E008).
- **It ticks.** HostCtl dword 12 (the EDM tick count, `ui32TimeWraps` in the DDK) and
  `USE0_SERV_EVENT` advance at 997.46 Hz against an NTP-checked clock. With
  `ui32uKernelTimerClock` = 400000 that puts the SGX clock at 399.0 MHz, 0.25% below the DDK's
  `SYS_SGX_CLOCK_SPEED` (`sysconfig.c:48`); `TIMER`, read as 1/16 of the core clock, gives the
  same (Evidence: E009; Q002).
- **The address layout is the DDK's REV1 table.** With the heaps at `sgxconfig.h:134-171`
  (kernel code `0x30000000`, kernel data `0x32000000`, PDS `0x2e000000`, pixel shaders
  `0x37000000`, vertex shaders `0x3c000000`, textures `0xf0000000`) the firmware boots and
  passes every check above (Evidence: E008), and srvinit computes its boot payload for these
  bases (Evidence: E011). Apart from the microkernel sitting at the EDM code base (§11.3), the
  layout is the loader's choice `[infer]`: the reference loader reproduces srvinit's buffers at
  two layouts (Evidence: E002).
- **It stops and boots again.** The deinit script followed by `SOFT_RESET = 0x3f` stops it, and
  the next boot passes the same checks (Evidence: E008).

### 12.1 Registers after the boot

The debug option's `sgx/regs` lists the registers the microkernel reaches (§10), the ones the
host uses on its own (event enable, `BIF_INT_STAT`, `BIF_FAULT`, `BIF_MEM_REQ_STAT`, the 16
directory lists), then HostCtl, TA3DCtl and the kernel CCB control words. Registers whose write
starts work are never read. After the boot:

`CLKGATECTL` `0xa6aa`, `CLKGATESTATUS` `0x20`, `0x0040` `0x1ff`, `EVENT_HOST_ENABLE` `0x4000`
(the software event only), `CACHE_CTRL` `0xffff`, `DMS_CTRL` `0x208200`, `0x0800` `0x30`,
`0x04e8` `0x100`, `PDS_EXEC_BASE` `0x2e000000`, the other-event PDS program at
`0x30010000` with 6 data rows (PDS #13), `BIF_BANK0` `0xf` and directory list 15 set
(Evidence: E006, E008).

### 12.2 The EDM tick

Left alone, the running firmware changes four values between any two reads: `TIMER`,
`EVENT_TIMER`, `USE0_SERV_EVENT` and HostCtl dword 12. Nothing else moves. `USE0_SERV_EVENT`
has bit 16 always set and counts in bits 15:0, 3 or 4 counts ahead of dword 12 (Evidence:
E009). On the SGX535, Intel's register list names bit 16 of the same register the event
queue's `EMPTY` flag and bits 15:0 its served-event `COUNT`, which fits (emgd-psb_regs,
`psb_regs.h`).

A firmware task of ours in the general slot (E531) sees the tick's event as `pa0` = 2, `pa1` =
0x02000000 and `pa2` = 0x01061a70 (E532: 2 of 2 runs). The byte `pa1` bits 31:24 is a count that
every event carries: 2 after the arm, +1 after each kick of the kernel's command buffer, a host
GETMISCINFO or a client job's own (E746 held out 3 of 3; E747 for 138 job events, read after the
run), so bits 24 and 25 are bits of the count and not event bits; PDS #13 reads only bits 23:0.
The count is the number of commands (kicks) the kernel has sent through the CCB since the firmware
load, mod 256, equal to the CCB write offset: 2 after the arm path's two GETMISCINFO, 1 with one
and 4 with four, 0 after 254 more kicks, +1 per fill or copy command (E768, 15 of 15 jobs); a kick's own event carries the value from before its bump, and whether the hardware
counts the writes to `CR_EVENT_KICK` or reads the kernel's kicker word is not separated (Q290).
`pa2` is the EDM's event timer sampled for the event (bits 31:24 = 0x01, bits 23:0 counting down
from 400000 core clocks), 16 clocks after the reload for a tick served at once (0x01061a70) and any
value for a kick; it is not a constant (E746, E747). A host kick (a GETMISCINFO with no job) is one
event in the general slot with `pa0` = 0 and `pa1` bits 23:0 = 0x100 (E746); the words E538 logged
for it, 0x03000000 with `pa0` = 2, are those of the tick after it. A client job's events arrive one
status bit at a time, in an order the same in every replicate, and the fill's end of render reached
slot 3 with `pa1` bit 4, the reversed order of E155 (E747); bit 19 did not appear in any of them,
nor in 8 jobs of 4096x4096 with 1500 vertices that did and did not raise the TA's threshold (E771,
Q033). While a task of ours holds the EDM the
events are queued and not lost: up to four ticks (three latched on arrival, one when the hold ends,
the rest dropped), a kick once, a job's events once, all served after the hold (E749, E751, E752);
two kicks in one 90-tick hold are two entries, each with the count it had when it arrived (2 and 3,
the ticks after them 4), 3 of 3 jobs (E794).
After a task that wrote `sa`, `r`, `i`, `p` and `pclink` state and ended with `nop.end` instead of
jumping to the closed general task, the tick stopped: dword 12 and `USE0_SERV_EVENT` did not move
over three reads 20 ms apart, and one debugfs reset recovered it (E533, 1 run). A task of ours that
wrote nothing and ended one tick pass with `nop.end`, without calling the closed task, stopped it
in 2 of 2 runs, with `CR_CLKGATESTATUS` 0x000ccfa0, `CR_EVENT_STATUS` 0x20000000, the event timer
counting and `USE0_SERV_EVENT` frozen with its empty bit clear: skipping the closed task is enough
(E793, Q152). A task of ours that wrote `sa`, `r`, `i` and `p` and then called the closed task
left the tick running (E536, 3 of 3 rounds, 911 to 1005 Hz), and a second one that also wrote `sa63`
and `sa65` and called it was not followed by its armed reader within 100 ms (E537, 1 run; HostCtl
dword 12 advanced 6 in that window and then read 0x9db in both dumps taken seconds later, and
`USE0_SERV_EVENT` 0x9e0 in both, against E533's three reads 20 ms apart; Q152). The closed task does
not by itself keep the tick, then, but a task that ends a pass without it does not keep it either.
No single write of `sa63` (a marker, read back after 1200 ms), `sa64` (with the tick bit set or
clear) or `sa65` (its own value, or a marker restored before the call), and no tail call with p0 =
p1 = 1 and r and i written, stopped it (E791, 19 of 19 jobs); after an `sa64` with bit 1 clear the
next entry read `pclink` 6 and p1 as left, after the others 0x98 (E792).

*Based on sgx545-ce `src/services4/system/unified/sysconfig.c`,
`src/services4/srvkm/devices/sgx/sgxconfig.h`; emgd-psb_regs; E002, E006, E008, E009, E011, E531,
E532, E533, E536, E537, E538, E746, E747, E749, E751, E752, E768, E771, E791, E792, E793, E794.*

## 13. Open questions

- **The rest of `asInitDevData`.** Entries outside [8..13] are unexplained.
- **Whether any payload value depends on the core revision or core id** the kernel reports to
  srvinit. The DDK version, build and build options do not (E352); the core words were 0 in
  every run, so a capture with nonzero ones would settle it.
- **What `0x0810`, `0x0814` and `0x0818` control** (Q001): `0x0818` bits 8 and 10 reach the
  render path (E404); the rest is open.
- **The SGX clock**: 399.0 MHz, or a tick and a `TIMER` fed from another reference (Q002).

*Based on E001, E011; `doc/specs/fw_format.md`.*
