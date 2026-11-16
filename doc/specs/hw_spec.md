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
  4M); address mask `0xFFFFF000`. The 36-bit layout does not apply (§2). **On the SGX545 the
  size field is not taken:** a client PDE with any code 0 to 7 is walked as a table of 4 KiB
  entries, entry va[21:12], the entry's address plus va[11:0]; codes 1 to 5 read and wrote the
  pages the 4 KiB walk names, never the large page (E1117), the PDE's bits 11:4 do not offset the
  table (E1118), and the unnamed codes 6 and 7 neither fault nor stall (E1119; BIF_INT_STAT 0x80000
  and BIF_FAULT 0 after each job). Measured through the transfer's texture reads and pixel writes
  with the fork's debugfs `vm_pde_addr`, `vm_pde_size`, `vm_pde_layout` and `vm_large` (fork
  8bc0877e8603, module 7CE8E38E; r30-pde); the EDM's and the kernel's directories and the render
  requestors were not tried.
- **PTE** (`sgxmmu.h:65-69`): `VALID` `0x1`, `WRITEONLY` `0x2`, `READONLY` `0x4`,
  `CACHECONSISTENT` `0x8`, `EDMPROTECT` `0x10`; address mask `0xFFFFF000`. A write to a
  read-only page faults (E021, E319). The round 8 kernel's debugfs `vm_pte_flags` puts the
  other three on one client mapping (fork r8-kernel 2a650d74, module B60AB0B4) (E945, the
  triangle's rows, frozen; E946, the transfer's, read post hoc; E964 and E965, frozen):
  - `WRITEONLY`: the writes land (the fill's and the triangle's images exact), then the job
    faults at the page of the last pixel written with `SB` 31 (`BIF_INT_STAT` 0x80020; held out
    at a 64 x 16 fill from row 16 and at 64 x 64, never the mapping's first or last page, E964);
    the ZLS store lands whole, then faults at the store window's last page (0x80200, `SB` 0,
    E965); a read faults at the mapping's first page before anything is drawn: the render's VDM
    stream page (0x80008) and, with the copy's own `READONLY`, its texture source (0x80002). So
    no access passes cleanly, but the write is not refused as a read-only one is [infer: the
    last-page fault is a read by the writing unit after its writes].
  - `CACHECONSISTENT`: no change to a copy's texture read or a render's stream read of the host's
    writes made after the map (both images exact), nor to a ZLS depth load (no fault). A depth
    load in the second render of a context reads what the host wrote to the buffer after the
    first render loaded it, with the flag and without it: no stale data (E1046).
  - `EDMPROTECT`: a client write faults at the mapping's first page with `FAULT_TYPE` 2, nothing
    written: the transfer's and the 3D's pixel write (0xa0020) and the ZLS store (0xa0200,
    E965); the render's stream read and a copy's texture read of its `READONLY` source (PTE
    0x14, E964) pass.
  - `WRITEONLY` with `EDMPROTECT` (0x12) on a colour target faults as `EDMPROTECT` alone, at the
    first page before any pixel (E965).
  - Alone on a mapping that is only read (E1071, held out): `WRITEONLY` faults a ZLS depth load
    (0x80200) and a texture read of a probe's scratch (0x80002) at the mapping's first page, `SB`
    0, before anything is read; `EDMPROTECT` lets both through (the load and the texture read
    exact). Together (0x12) on those reads they fault as `WRITEONLY` alone, not with
    `EDMPROTECT`'s type (E1108, held out).
  The rest (the flags on the TA's writes or the EDM's buffers,
  `CACHECONSISTENT` on data cached within one render or by other units) is Q108.
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

On the laptop `CLEAR_FAULT` hides a latched fault and does not clear it: with four bus faults held
(a TA read, a TA write, a texture fetch; E826) setting bit 4 made the kernel's next reads of
`BIF_INT_STAT` and `BIF_FAULT` return the idle 0x80000 (or 0) and 0, and clearing it again
returned both to the fault's values, 4 of 4. The registers stayed latched through a 2.5 s watch
and only the debugfs reset cleared them (E826; the frozen rows were cannot tell, the three
readings agree across rows, post hoc). In that reset the fault words read clear in the same 4.3 µs
row as the halt, 6.8 to 11.3 ms before the event status is host-cleared, so before the kernel
writes `CLEAR_FAULT` [infer, post hoc] (E767).

### 5.5 Faults and directory lists

- `BIF_INT_STAT` (0xC04): `FAULT_REQ` [15:0], one bit per faulting requestor; `FAULT_TYPE`
  [18:16]; `FLUSH_COMPLETE` [19]. Writing the set bits back to it changes nothing on the laptop
  (0x1 and the fault word without bit 19, 4 of 4 held faults, E826); what clears a fault is the
  reset (§5.4).
- `BIF_FAULT` (0xC08): `CID` [3:0], the directory list the faulting access went through; `SB`
  [8:4]; `ADDR` [31:12], the faulting page.
- `BIF_DIR_LIST_BASE0` (0xC84) and `BASE1..15`: the page directory of each list.
- `BIF_BANK0` (0xC78): the list each requestor uses: `INDEX_EDM` [3:0], `INDEX_TA` [7:4],
  `INDEX_HOST` [11:8], `INDEX_3D` [15:12], `INDEX_2D` [19:16].

So `CID` and `BIF_DIR_LIST_BASE<CID>` name the page directory, hence the address space, of a
fault.

The fault words of the records, by the access that made them. Which unit a `FAULT_REQ` bit
belongs to is read from the access each record set up, not from a source [infer]:

| `BIF_INT_STAT` | `FAULT_REQ` bit | access | records |
|---|---|---|---|
| 0x90002 | 1 | texture fetch past the probe's scratch (page 0x3e017) | E765, E826 |
| 0x90004 | 2 | TA write of region headers past the kernel's layout (`SB` 6) | E729, E789, E826 |
| 0x90004 | 2 | TA header write of a macrotile word whose axis bounds are all 0 (page 0x20008 at 384 x 256 and, x or y, at 512 x 512) | E1073, E1074, E1109 |
| 0x90008 | 3 | TA read of an unmapped stream page | E764, E826 |
| 0x80020 | 5 | transfer write to a read-only alias | E766 |
| 0x80020 | 5 | fill or render colour write to a `WRITEONLY` page, after the image was written (`SB` 31, the image's last page) | E945, E946 |
| 0x80002 | 1 | copy's texture read of a `READONLY` + `WRITEONLY` source | E946 |
| 0x80008 | 3 | render's read of its VDM stream page mapped `WRITEONLY` | E945 |
| 0x80020 | 5 | the same at a 64 x 16 fill from row 16 and a 64 x 64 fill (the last pixel's page) | E964 |
| 0xa0020 | 5 | fill or render colour write to an `EDMPROTECT` page (`FAULT_TYPE` 2), also with `WRITEONLY` | E945, E946, E964, E965 |
| 0x80200 | 9 | ZLS store to a `WRITEONLY` page, after the store landed (the window's last page) | E965 |
| 0xa0200 | 9 | ZLS store to an `EDMPROTECT` page (`FAULT_TYPE` 2, nothing stored) | E965 |
| 0x90100 | 8 | 4x render, at page 0x10000 (`SB` 1) | E511, E828, E845, E846, E867 to E869 |
| 0x90100 | 8 | a macrotile word whose first macrotile ends inside the target, at page 0x10000 | E1073, E1074 |
| 0x90200 | 9 | ZLS store reaching a page nothing maps, at that page (a mapped page past its buffer takes it) | E1070 |
| 0x80200 | 9 | ZLS load of a `WRITEONLY` depth buffer, the first page, nothing read | E1071 |
| 0x80002 | 1 | texture read of a `WRITEONLY` scratch, the first page | E1071 |
| 0x80200, 0x80002 | 9, 1 | the same reads with `WRITEONLY` and `EDMPROTECT` together (0x12) | E1108 |
| 0xd0400 | 10 | background program's fetch (`FAULT_TYPE` 5) | E764 |
| 0xd0400 | 10 | ISP word 0 bit 18, at page 0, on the library triangle and a depth-buffered ramp | E1072 |
| 0x91000 | 12 | first job with buffer 0 left out of the client alias | E573, E745, E761 |

A held fault sets no bit of `EVENT_STATUS` of its own; `EVENT_STATUS2` bit 7 (TA side) or bit 6
follows 121 to 124 µs after the fault word (§6.4; E764 to E766, E789).

During the renders of a context on a freshly reset GPU `BIF_BANK0` takes `INDEX_TA` = 1 and
`INDEX_3D` = 1 (12 of 12 runs; `INDEX_EDM` = 1 as well in 5), and a fault of the first job names
`CID` 1, so the render's TA and 3D reach memory through list 1 (E457). In the client directory the
aliases of the EDM's buffers 6, 7, 8, 10 and 11 are not needed for a 64 x 64 render (each left out
alone, 10 of 10 runs exact); TA3DCtl is, writable (Q076). Nor are buffers 1 to 5 and 12 to 14,
one at a time (E573), the pairs among 1 to 5 tried and 1 to 5 together in a two-render job, 6, 7,
8, 10 and 11 together over three renders (E745, held out), and 1 to 4 together in two 1024 x 768
renders that both overflow the parameter buffer (E761); with buffer 0 left out the first job
faults (0x91000 at 0x3000b021 or 0x3000b022; E573, E745, E761). Nor are they needed together:
every buffer but 0 and 9 left out at once (mask 0x7dfe), the 0x32 heap without TA3DCtl and the
pairs and the three of 12 to 14 kept two renders exact, and 0x7dfe three renders and two
overflowing 1024 x 768 renders (E980, held out 8 of 8): of the EDM's buffers the client directory
needs only 0 and 9.

On the laptop the EDM keeps its own directory in `BASE15` and gives each render context's
directory one of lists 0 to 14 at its first kick, in turn after a reset (1, 2, ... 14, then 0),
recording the last in TA/3D control block dword 49; our kernel reads a fault's directory back from
the list `CID` names (E360). A fault raises no bit of `EVENT_STATUS` or `EVENT_STATUS2` of its
own (E357).

A 4x multisampled render of our stack (mode 2, `CR_TE_AA` 0xe0000000, the unpoked macrotile words)
at 320 x 160 and up faulted the job with `BIF_FAULT` reading 0x90004 at the page 0x20006 (320 x 160
to 512 x 256), 0x20008 (512 x 384) and 0x2000a (640 x 480) (6 of 6 jobs, E507); the script's health
check, a plain 64 x 64 triangle, failed after each of the last three in a row and stopped it (five
`SGX recovery failed: -110` kernel lines in the run). The faults are our kernel's layout, not the
hardware's: it held one array of region headers where the TA writes four at `CR_TE_AA` 0xe0000000
(E788); with four the render completes at every size run up to 1024 x 768 (E824). The kernel now
gives four to a context made with `DRM_SGXFIVE_CTX_RENDER_AA_4X` and refuses a 4x job on any other
unless debugfs forced its count (E828). A 4x render at 4096 x 4096 on four arrays faulted at the
parameter buffer's base (0x90100 at 0x10000011, the word of E511's three faults) with 1048576
pixels right, the first wrong at (1024, 0), and the health triangles after it passed, 3 of 3
(E828). It is not a parameter-buffer overflow: the same 4x full triangle faulted with the
same word at 1280 x 1024 and 2048 x 1536, whose scenes need 321 and 769 of the 1024 usable pages
(P - 0x22 at the maximum P 0x422; the need 1 + ceil(2 (W / 16) (H / 16) / 32) fits E824's ten
dumps and two more here), with no pixel right and health ok after each (E845, held out), and at
4096 x 1152 (E846). A 4x scene that does overflow ends in -ENOSPC without a fault, as at 1x: 1024
x 768 at P 0xe2 (need 193, 192 usable) and 288 x 144 at P 0x23, while 0xe3 completed (E846, read
after the run; the stage's control was frozen for another scene). Every four-array 4x job that
completed was at most 1024 x 768 and every one that faulted at least 1280 x 1024 (E845, E846). Round
5 held out H-ENOSPC4: one page short of the need a 4x scene ends in -ENOSPC with no BIF line and at
the need it completes, at 640 x 480 (76 pages) and 512 x 384 (49) as at 1024 x 768 and 288 x 144 (6
of 6 rows decided, E866). The fault depends on the context the job runs on, not on the target alone:
1280 x 1024 completed on contexts made for 1280 x 1040 and 2048 x 2048, and 2048 x 1536 on 4096 x
4096, contexts whose tail-pointer room (the kernel's 4 side^2 bytes before the control, OTPM, state
pages and region headers) is four times the target's own, while 1280 x 1024 on 2048 x 1024, whose
region buffer grows and whose room does not, faulted (E867, H-TPC held 4 of 4; every size rule had
predicted faults). On its own maximum the job faulted at 1184 x 768, 1024 x 800, 1280 x 768, 1024 x
1024, 2048 x 240 and 768 x 2048 and completed at 1024 x 512 and 256 x 1536: no width, height, count,
page or area limit and none of four frozen tail-pointer extents fits (E868). A held 1280 x 1024
fault had written its whole scene (321 pages) and left 1212 of its 12288 region headers off the
doubled-grid rule from `td.rgn` (0x7000) to 0xd804, most with word 0 intact and a zero stream
offset, nothing below `td.rgn` non-zero (E869, the off headers' kinds post hoc); [infer] a zero
offset points the 3D at the request base, page 0x10000, never mapped. Read offline from that dump
against a completed twin, the lost offsets are the tail pointers: with one dword per tile of the
doubled grid (16 x 8 pixels) at TA-data offset 4 x Z(x, y), Z the bit interleave with y on the even
bits and x on the odd bits, the 1023 headers that lost word 1 are exactly those whose word 1 lies
at an in-target tile's entry (H-TPM; with x on the even bits 426). "A 4x job faults iff the end of
its target's entries, 4 x (Z(2tx - 1, 2ty - 1) + 1), passes the `td.rgn` of its context's maximum"
then gives all 26 four-array outcomes on record, the faults of E868 at 2048 x 240 and 768 x 2048
included: a wide target faults early because x 64 sets bit 13 of the index (E870; post hoc, one
dump, the 26 outcomes known when the rule was written, so not held out). The room a 4x context
needs is then 4 x (Z(2tx - 1, 2ty - 1) + 1) bytes, at most 4 x (2 side)^2 [infer]. Not explained:
189 word-0 losses at header-grid entries outside the target, bit 27 set on 914 headers and in no
completed dump, and the 4096-wide right blocks of E828 and E846 (E870). Round 6 held the rule out on
the module that made these contexts (11 of 11 rows decided): 1024 x 1280 (entries end 0x13000,
`td.rgn` 0x13000), 992 x 1280 and 512 x 1536 completed on their own maximum, and 1024 x 1024 and
1024 x 800 on a 1024 x 1280 one, where size rules of E868 said fault; 1024 x 1296, 1040 x 1280, 1024
x 1536 and 1024 x 800 on 2048 x 1024 faulted with the same word; two held faults, 1024 x 800 and
1280 x 768, lost exactly the frozen stream offsets (43, header 0 among them, and 511, as sets), and
of the eight frozen variants only y on the even bits with the limit at `td.rgn` stays (E887). A
module that gives a 4x context four times the room (fork r6-kernel 3f0b3e74) ends the fault: the
eight own-maximum sizes that faulted complete with 0 wrong pixels and no region header off the rule,
and so do 2048 x 2032 and 4096 x 960, while 4096 x 1152 (1153 pages needed) ends in -ENOSPC with no
fault; with the room set by hand 1280 x 1024 completes at 0xb000 (`td.rgn` 0xe000, its entries end
0xd800) and faults one page lower losing exactly the frozen 171 offsets from 0xd000 to 0xd7f8, and
1024 x 768 faults at 0x3000 (E889). So a four-array 4x job needs its target's tail-pointer entries,
4 x (Z(2tx - 1, 2ty - 1) + 1) bytes from the tail-pointer base, to end at or before the region
headers; where they pass them the end of the TA's run zeroes the entries that lie over the headers
[infer], and the in-target headers whose stream offset sits at an in-target entry are the ones lost.
The scene pages of 992 x 1280 and 1184 x 768, 313 and 225, are two above the page need above (E887,
E889). The faulting state's residue (the word-0 losses, bit 27, the 4096-wide blocks) belongs to a
layout the r6-kernel module no longer gives a 4x context and is not pursued.

After a TA write fault (0x90004, `SB` 6) and the reset, the next renders that run the TA fault at
the failed job's page with `SB` 6, once or twice, before one passes: 4 of 4 such health faults
named the job's page, at 0x20006 and at 0x2000a, never the health context's own end; their `CID`
is the list current at that render (1, or 2 after a fill took list 1). A fill between them does
not end it and leaves `CR_CLKGATESTATUS` at 0x78; a 64 x 64 render on a context that maps the page
ends it with no fault, and the status returns to 0x20 after a completed render (E848; the frozen
row of the fill cell failed on the list number alone, read after the run). [infer] The TA's
pending region-header write survives the reset and is issued again at its next run. The boots
after 3 of 4 held resets and 2 of 4 health faults timed out (`SGX recovery failed: -110`), their
register dumps reading `BIF_INT_STAT` 0x000d0004, read as a TA write inside the boot [infer]
(E848; Q003). Held out on the r6 kernel (E891): after a fill the first replay went through list 2
at 640 x 480 and at 288 x 144, so the list is the one current at the next TA run, not the faulted
job's (H-LIST 2 of 2; the whole-word test refuted); a second replay, when there is one, goes
through the next render's own list. A directory-cache invalidate (`INVAL_DC` set and cleared)
written while the fault is held leaves `BIF_INT_STAT` and `BIF_FAULT` latched and does not drop the
write: the replay came as without it, 3 of 3 (E892), and a flushed held reset at 288 x 144 still
ended in a -110 boot. On that boot every -110 followed a 288 x 144 cell (4 of 5 recoveries there,
none of 12 at 640 x 480), the dumps reading `BIF_INT_STAT` 0x000d0004 (E892). Over every kept
kernel log (2956, read after the runs) the boot after a fault timed out only after 0x90004 (54 of
147; 0 of 756 after any other word), and with `SB` 6 by the job's fault page: 10 of 11 at 0x20006,
0 of 15 at 0x2000a; a page rule fitted to that (0x20006 to 0x20008 time out) gave 16 of 17 r6-held
boots, a score on data already read (E901). Each timed-out boot's dump has the TA's clocks on
(`CR_CLKGATESTATUS` 0x000ccff8) and a TA write through list 0, the reset directory at that point
[infer], and the second boot comes up (54 of 54). The kernel's reset reads `BIF_FAULT` 0 and
`BIF_INT_STAT` 0x80000 with every block held in reset, before and after `CLEAR_FAULT`, also before
the boots that time out (10 of 10): reading clear while held does not mean the write is gone
(E901; Q003). Held out, that page rule fails (E919): held resets at 0x20008 came up 3 of 3, one at
0x20006 (256 x 288) came up and one at 0x20009 (128 x 528) timed out; and neither a
`CLEAR_FAULT` toggle nor a 10 s hold while held decides the boot at 288 x 144, which timed out after
5 of 6 held resets with or without them (E920). Over those two stages 14 of 29 boots after a
0x90004 timed out, 11 of 14 at 288 x 144 and 3 of 15 at five other sizes, the same cell going either
way, and no register read at the hold separates them [post hoc]: the -110 is frequent at one size,
not a rule of page or size. Every one had E901's dump and a second boot that came up (14 of 14).
Once, after a toggle of `CLEAR_FAULT` while held, the boot came up and the first triangle drew with
no replay (E920).

### 5.6 Unit names

`BIF` bus interface and MMU; `DPM` parameter memory manager; `TA` tile accelerator; `VDM`
vertex data master; `TE`, `MTE` tiling engine and macro-tiling engine; `PDS` programmable data
sequencer; `USE` the USSE shader core; `ISP` hidden-surface processor; `TSP`, `TSPP` texture
and shading processor and its pre-processor; `PBE` pixel back end (tile write-out).

*Based on sgx545-ce `src/services4/srvkm/hwdefs/sgx545defs.h`,
`src/services4/srvkm/devices/sgx/sgxreset.c`; E357, E360, E457, E507, E511, E573, E729, E745,
E761, E764 to E767, E789, E824, E826, E828, E845, E846, E848, E866 to E870, E887, E889, E891,
E892, E901, E919, E920.*

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
partly known; how long a bit stays set is known for the two below (STATUS2 bit 6, STATUS bit
18) and open for the rest (Q111). Seen on the hardware (E547, E548):
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
At 541 ns a sample with `EVENT_STATUS` read alone (E1115), a plain 64 x 64 triangle reads
0x20000000 outside the job, and `MADD_CACHE_INVALCOMPLETE` whenever set reads as 0x24000000
alone, 88 to 119 us before the render end in a one-render job and fallen before it, in 8 of 14
jobs (4 to 93 us wide). Post hoc (E1116): `CACHE_CTRL` reads 0x0000ffff after a reset and
0x1000ffff from a kick on, its bit 28 set about 35 us before bit 26; sampled beside it, bit 26
shows 5 to 13 us wide. Held out with the right premises (E1120, E1121): `CACHE_CTRL` 0x0000ffff
after a reset and
0x1000ffff from a change ahead of every event of a kicked job until a reset (19 of 19 rows), bit
26 19.5 to 48.3 us after it in 9 of 12 rows and 106.6 us in one; the word while bit 26 is set is
the idle word with bit 26 and any other pending bit (once 0xa4004000); a plain triangle adds 9
to 11 counts to `USE0_SERV_EVENT` beyond the ticks. The change comes before the kick's next
served count (E1122, E1123: none in the 30 us before it, 23 of 23 rows), and a fill's kick makes
it too (E1123, 6 of 6). In the two rows that order it against the kick pass, `BIF_CTRL` reads
0x00000008 for 4 to 8 us before it and is clear again in the change's sample (E1123) [infer: the
firmware's BIF invalidation for cache-control bits 0 and 1, then its own `CACHE_CTRL |
0x10000000` for bit 3, E013; the host's own bit 3 writes are two back-to-back MMIO writes on
paths no job takes], so the hardware does not set bit 28 at the kick. A served GETMISCINFO, whose
command carries no INVAL_DATA, leaves `CACHE_CTRL` at 0x0000ffff (E1126, E1127: 9 of 9 rows, after
the boot's own and the kit's `pre:miscinfo`), so bit 28 needs the command's INVAL_DATA; whether it
is the firmware's write or a hardware response to the firmware's work for it is not measured.
sgx-sim's hardware model
answers `EVENT_STATUS` with its idle word until a kick is served and refuses it after; it
answers `CACHE_CTRL` with the reset word until a kick and after it until the run writes the
register, then the run's write, 0x1000ffff only (crates/sgx-sim/src/hw.rs). With the kept order
replayed after that write (0x20000000, 0x24000000, 0x20000000; explicit per run, moving on only at
a proven spin), the stock kick pass waits on `MADD_CACHE_INVALCOMPLETE` with no count and, after
the read that shows it, writes 0x04000000 to `EVENT_HOST_CLEAR` and emits PDS #14 (E1130 [RE,
infer]): the firmware clears bit 26 itself; whether that write ends the bit is not measured.

`EVENT_STATUS2` (`0x0118`) reads 0x400 (`DCU_INVAL_COMPLETE`) when the core is idle;
OTPM_MEM_CLEARED (bit 12) and DPM_TA_FREE_LOAD (bit 0) pulse in some depth-store, 256-pixel and
partial jobs (E547). Its
`TRIG_TA` (bit 7) and `TRIG_3D` (bit 6) latch on the laptop; neither sets in the renders, fills
and copies of our stack (E357).

- **Bit 7** sets 0.1 to 0.2 ms after the PB load of a TA that hangs or faults (E357), and, read
  post hoc from timelines sampled every 4.3 µs, 121 µs after the fault word of a held TA read
  fault (E764). A vertex program of our own that loops on a relative `br` sets it on the tool's
  triangle: with an 8-instruction body on 3 vertices clear at 1045 iterations and set at 1100 in
  both orders of a held-out ladder (E807; E784 had placed it in (880, 1760]), with a
  16-instruction body in (601, 649], with a 4-instruction body already at 1760, the lowest point
  run, with 12 vertices in (554, 698] and with 48 in (329, 538]. No fixed count of instructions or
  of multiply-adds a vertex, nor a count a job, places these points (HV-INSTR, HV-MA and HV-JOB
  refuted, E807 and its correction of 2026-11-11). Bit 7 showed 184 to 195 µs after the burst
  began in every set job (E807).
- **Bit 6** sets in a fill whose pixel program loops, at a point that depends on the loop body and
  not on a count of iterations: E431's 8-instruction body (six multiply-adds) is clear at 53 and
  set at 56 (55 in 3 of 3 runs, 54 in 2 of 3; E431, and E804 2 of 2 with a relative `br` and with
  `ba`); E357's "128 iterations or more" came from runs of 16 and 128 only. Over six
  bodies run in two orders, with a loop proof, the first set points held out are 25 for a body of
  16 instructions (24 clear), 35 for 12 (34 clear), in (80, 130] for 4, every point from 500 for a
  body with no multiply-add and from 60 for six `or`; a body with a load and a wait stayed clear to
  320 iterations, bursts of 13.4 ms (E805, E769). So neither a count of multiply-adds (H-MA), nor a
  tile time (H-WD), nor the job's burst (H-BURST) places the bit, held out (E805). Read after the
  run [infer, no frozen row]: in the 106 load-free fills of E804 and E805 every set job had a burst
  of at least 535.9 µs and every clear one at most 539.3 µs (E805). In triangles that cover the
  target (E806) it first set at 56 iterations at 32 x 16, 32 x 32 and 128 x 128 (clear at 53), at
  110 at 8 x 8, 16 x 16, 64 x 32 and 256 x 256 and at 220 at 4 x 4; the per-instance, per-tile and
  per-job thresholds frozen for it were refuted at 3, 6 and 6 of the 8 sizes (E806 with its
  correction). It showed 120 to 340 µs after the burst began (E805, 48 of 48 set jobs; E806, 28 of
  32), and, post hoc, 121 to 124 µs after the fault word of a held background-program fetch, a
  texture fetch and a transfer write fault (E764, E765, E766). The quantity the latch watches is
  open (Q082).
- **Readings of 2026-11-11 from the kept timelines** (round 4 planning, none held out; FIT: read
  from the data it is scored on; SEMI: a rule written to a file before the jobs it is scored on
  were opened, after others of the same stage were seen). *Bit 7* [data, SEMI]: in the vertex-loop
  jobs `CLKGATESTATUS` reads 0x000ccff8 while the TA works on the vertices; with L the longest such
  run, every clear job of E807's 74 had L at most 129.1 µs and every set one at least 129.8 µs,
  over four bodies and 3, 12 and 48 vertices, and the bit showed 123 to 134 µs after that run
  began. It is not the TA phase's length alone: ten 1500-vertex jobs of milliseconds of TA ended
  with STATUS2 0x400, and E357's held TA hang set it with a run of 8 µs [data]. *Bit 6 in fills*
  [data; FIT on E804 and E805, SEMI on E431 and E357]: with a tile's time (B - 60.2) / 4 against
  125 µs, an edge band of 118 to 132 µs, 187 of 187 load-free fills fall on the predicted side or
  in the band (159 and 28); a body with a load stays clear far beyond that time (E805's ld8 to 320
  iterations). *Bit 6 in triangles* [data, FIT]: in E806's ladders the time a tile takes at the
  last clear and the first set point brackets 120 to 160 µs at every size. [infer] One timeout of
  about 125 µs without progress, of the TA for bit 7 and of the pixel side for bit 6, would fit
  these and the 121 to 124 µs after a fault word; a load would end a piece of work. These are
  readings to test, not rules.
- **Held out in round 4 (R4-pixel, 2026-11-11).** *Bit 7 in a vertex loop* [HW]: the rule above, set
  iff L >= 129.5 µs with an edge of 122 to 136 µs, held in 14 of 14 decided rows of three ladders
  E807 never ran (13, 2 and 8 instructions an iteration; 3 and 24 vertices), the bit showing 122 to
  130 µs after the run began in 10 of 10 set jobs; the stock program's 1500 vertices at 2048 x 2048
  kept the TA's clocks busy for 11 ms with bit 7 clear (2 of 2), so the rule is one of a vertex loop
  and not of the TA phase's length (E839). sgx-pipe models it as `events::status2_bit7`. *Bit 6 with
  a load* [HW]: a fill's pixel program that waits on one load before the ALU loop that sets the bit
  on its own, or alternates loads with rounds of it, kept bit 6 clear in 11 of 11 jobs, to 220
  iterations after the load and 4.2 ms: a program that waits on a load does not latch (H-LOADOFF),
  and neither a timer restarted by the wait nor a summed busy time fits (E840). *Bit 6 in triangles*
  [HW]: in triangles that cover the target bit 6 first sets in (96, 104] at 8 x 8, (140, 170] at 4 x
  4, (56, 60] at 32 x 16, (60, 66] at 64 x 32 and not up to 72 at 16 x 16; a pass count, E806's
  discrete points and a tile's time without progress are each refuted, and in the long rows the bit
  showed 250 to 360 µs after the burst began, as frozen (E841). What bit 6 follows in a triangle
  stays open (Q082).
- **Clearing.** Without a clear each stays set through later jobs (E357, whose runs wrote none);
  the debugfs reset clears both (E357, E764). A host write to `CR_EVENT_HOST_CLEAR2` (0x0114)
  clears the bits written: 0x8000 left a latched 0x440 as it was, 0x40 cleared it to 0x400, and
  the next loop fill latched it again, 3 of 3 rounds held out (E821: H-W; any non-zero write
  clearing all, H-ALL, and no write clearing, H-NONE, refuted). A firmware task's `str` of the same
  words does the same, 3 of 3 (E822). That CLEAR2 clears bit 7 is not measured.

`CR_EVENT_STATUS` bit 18 (`PIXELBE_END_RENDER`) is a level until acknowledged: with the slot 3
end-of-render pass skipped once it read set in every read of a 50 ms watch started at the slot 3
entry (7 of 7, held out, 1 job) and two seconds later, and never in the fill without the skip (9 of
9; E837); E823's job, read after the run, had it set from 7.3 ms to the end of its watch (8 of 9,
its first read before the render's end). A host write of bit 18 to `CR_EVENT_HOST_CLEAR` (0x0134)
cleared it within 1 ms and kept it clear at 20 ms, a write of bit 15 left it set (E823 post hoc,
E837). Held out the bit is a level in every job with the pass skipped (E855, 9 of 9 watch reads in
3 of 3 jobs; E856, 4 of 4 at two slower ticks) and the host's write clears the bits written and no
others that are set, bit 15 leaving bit 18 and `TIMER`, bit 18 clearing bit 18 alone: 3 of 3 with
the EDM stopped (E855) and 3 of 3 with it running, the writes at the slot 3 entry (E857; H-W, H-ALL
and H-NONE refuted; 8 jobs with E823 and E837). Its 4 to 6 µs pulses in ordinary jobs are then the
firmware's acknowledgement [infer] (E547). How long the other bits stay set, and what a write of
the other bits clears, is open (Q111).

Both STATUS2 latches are host events: written alone into
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
`src/services4/srvkm/hwdefs/sgx545defs.h`; E357, E365, E431, E444, E445, E547, E764 to E766,
E769, E784, E804 to E807, E821 to E823, E837, E839 to E841.*

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
What `0x0a78` controls is open too (Q024): every value 0x00-0x3f draws a triangle exactly
(E045), and none moves a 256x256 triangle's render time by more than 1 percent on two shuffled
passes (E1124, a frozen verdict; E396, E1114 readings), nor the render time of 500 triangles
at 1024x768, each about a quarter of the target (E1129). The same 500 triangles at 64x64 (about
0.73 ms a render) do not time to a percent, at 6 to 40 renders a job (E1125, E1128).

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
0x02000000 and `pa2` = 0x01061a70 (E532: 2 of 2 runs). The paragraphs below are what the records
of the closing pass add, by topic; the contract a task of ours must keep is gathered in the USSE
book's *Tasks and phases* (`doc/specs/usse_isa.md` §3.6).

**The timer and the tick [HW].** The tick is `CR_EVENT_TIMER` (0x0acc): bit 24 set, bits 23:0
counting down 400000 core clocks and reloading by themselves (E746, E751). One tick is 25000
`CR_TIMER` units (E746, E813; the plain gaps of the kept rings are 25000 to within a few units).
`pa2` of an event is the timer sampled for it: 0x01061a70, 16 clocks after the reload, for a tick
served at once, 0x01061a74 for a tick latched while the EDM was not idle (the first ticks after a
hold, E751), and any value for a kick (E746, E747). A task's `str` of the reload word 0x01061a80 to
the timer followed by the closed task kept the tick and moved the next entry to 25114 units, 2 of 2
(E818 T1), and the later gaps were 25000 again, so the grid moved and stayed moved (E818's
correction of 2026-11-11); [infer] the store restarts the countdown where it executes. The timer
reloads with nobody serving it: in 9 stops (E813, E814, E817, E818, E823, E830) bits 23:0 read
below 400000 in 18 of 18 samples taken seconds after the last served pass [data, round 4 reading;
a counter that ran through 24 bits would be below 400000 in 2.4% of samples]. A pass with the tick
bit of `sa64` clear leaves `pclink` 6 and does not advance HostCtl dword 12 (E792, E812 C5: 50
passes, 2 of 2), and a tick pass handed to the slot 2 closed task keeps the tick without advancing
it (E813 X1, X20), so dword 12 counts the passes of the closed tick handler, not ticks [infer].

**The end of a pass [HW].** After a task that wrote `sa`, `r`, `i`, `p` and `pclink` state and
ended with `nop.end` instead of jumping to the closed general task, the tick stopped (E533, 1 run),
and a task that wrote nothing and ended one tick pass that way stopped it in 2 of 2 runs (E793). A
task of ours that wrote `sa`, `r`, `i` and `p` and called the closed task left it running (E536, 3
of 3 rounds), and no single write of `sa63`, `sa64` or `sa65` (without bit 8) and no tail call with
p0 = p1 = 1 stopped it (E791, 19 of 19; E812, 13 of 13). What the EDM needs is the phase end: a
plain tick pass of ours keeps the tick iff it executes `phas #0, #0, pixel, end, parallel` before
its `nop.end`, 13 of 13 jobs with it and 7 of 7 stopped without it, `cfi.global` neither needed nor
enough (E817 held out, H-PHAS; E830 replicated in three blocks, H-REP; E793, E818 T2). The closed
exit reached by a tail call (`cont4`) keeps it, 8 of 8, as does any closed path that reaches that
exit, the general task's or slot 2's (E817, E830, E813: H-EXIT); a kick pass ended with `idf, wdf,
nop.end` stops it too (E813 B3), and a store to the timer does not replace the phase end (E818 T2).
[infer] This is the program-shape rule of client programs (E118, `usse_isa.md` §3.6) in an EDM
task. A kick pass ended with the `phas` keeps the tick too, 2 of 2 held out, its command left
unread (read = write - 1, HostCtl dword 14 0) because the closed reader never ran, and the next
tick comes 24994 units after the one before the kick, as after an acted tick pass (E835: the phase
end is what a pass of either kind needs). Slot 3's end-of-render pass skipped and ended with the
`phas` was followed by 10 ticks on the grid, where without the `phas` nothing followed it (E823),
but the tick stopped later, after exactly 20 slot 0 passes after the fill's kick, with the fill
held (E836, 1 job; the count read offline from its page, E849; held out in 3 of 3, E855): the phase
end ended the pass, and the stop is the EDM's own 3D lockup check, which the skipped closed handler
would have ended. The count is in tick passes, not time: with HostCtl dword 6 at 800000 and 1600000
the stop came after the same 20 passes, about 40 and 80 ms after the kick (E856, 4 of 4; a stop at
a fixed 19.3 ms refuted). Host clears of `CR_EVENT_STATUS` bits 15 and 18 at the slot 3 entry and a
GETMISCINFO served after them, with the EDM still running, did not prevent it (E857, 3 of 3: the
same 20 passes and marks). A stop reads
`CR_CLKGATESTATUS` 0x000ccfa0, `USE0_SERV_EVENT` bit 16 clear and its count frozen, the event timer
counting and `CR_EVENT_STATUS` 0x20000000; it answers no host command (0 of 8 tries) and one
debugfs reset recovers it (13 of 13 stops in the records, E533 to E830); a task still running inside
a 90.5 ms hold reads the same, so the signature cannot tell a stop from a long task (E811, E816). A
phantom kick bit (`sa65` bit 8 with read = write) makes the closed reader take an empty command and
stop with HostCtl dword 14 0xad002600, read = write + 1 (E814 D2, E537); E537's word without bit 8
stops it with no mark (E814 D1). The signature has two kinds (E849, read offline after the
hypothesis, post hoc): the stop after the skipped slot 3 pass left HostCtl dword 3
(`host_ctl.ukernel_detected_lockups`) = 1, dword 8 (`host_ctl.interrupt_flags`) = 1, one
`SW_EVENT` and TA3DCtl dword 58 (`+0xe8`) written, all 0 at the arm, after 20 passes = 2 x
dword 5 (`host_ctl.hw_recovery_sample_rate`, 10): the lockup path of E353, seen once; the 22
other kept dumps with this signature (stops of a pass without the phase end, phantom kicks,
reads inside a long task) read dwords 3 and 8 and TA3DCtl dwords 56 to 58 as 0. Held out, the
marked kind came in 10 of 10 jobs that skipped the pass (E855 to E857: dword 3 + 1, dword 8 = 1,
one `SW_EVENT`, dword 57 0, dword 58 0xaac267c2 in every one, `CR_EVENT_STATUS` bit 6 clear) and
each was recovered by one reset. [RE] (our reading R-6 of the firmware, the reading frozen
before the run; E855, E857) After a 3D kick, while sa9 bit 0 ("3D running") is set, the tick
routine counts its passes in dword 57 against dword 5, stores a signature of the USE pixel service
counters and four other registers in dword 58 at the 10th and compares at the 20th; equal, it
counts the lockup, sets dword 8 bit 0, writes `SW_EVENT`, then (R-6's reading) takes a lock,
stores 2 to `CR_DPM_TASK_STATE` and polls `CR_EVENT_STATUS` bit 6 (`DPM_STATE_CLEAR`) with no
exit, so that the EDM stays busy until the host's reset. The 3D kicks set sa9 bit 0 and only the
end-of-render path (and the recovery) clears it; on the hardware that state survives a host clear
of bit 18 and a command (E857). The store is not seen [HW]: a host read of `CR_DPM_TASK_STATE`
(0x0694) gave 0 at the arm, at the stop, after the clears and after the recovery, 2 of 2 held out,
the marks replicated (E890; the rgn4 kernel never read it, E855). Whether the EDM waits before the
store, the store goes elsewhere or the register does not read back what is written is open, so
the EDM's wait after the lockup is not shown to be the bit 6 poll (bit 6 reads clear). The
register does not read back what the TA kick writes either: in six held first kicks, whose Clear
writes `(index << 3) | 2` there [RE], a host read gave 0 before the job, during the hold and after
the reset, 18 of 18 (E902), so a read of 0x0694 cannot show whether the lockup's store was made.

**The kick [HW].** A kick is the command at the CCB write offset, the kicker word bumped (mod 256)
and a write to `CR_EVENT_KICK`. It is one event in the general slot, `pa0` = 0, `pa1` = (K << 24) |
0x100 with K the count before the bump, and the ticks after it carry K + 1 (E746, E768, E816 G0).
The byte `pa1` bits 31:24 is a count every event carries: the kicks served since the firmware
load, mod 256 (H-CNT, E834), which for the kernel's kicks is the number of commands it has sent
through the CCB and the CCB write offset (2 after the arm path's two GETMISCINFO, 0 after 254 more
kicks, +1 per fill or copy command; E768, 15 of 15 jobs; E747 for 138 job events, read after the
run), so bits 24 and 25 are bits of the count and not event bits; PDS #13 reads only bits 23:0. It
is not the kicker word: written alone (0x42) the word raises no event and leaves the count at 2
(E819 Q1, 3 of 3: H-KW refuted), and set to 0x42 before a kick that the kernel bumps to 0x43 the
ticks after the served kick carry 3 (E834, 3 of 3: H-LATCH refuted). It is not a count of
`CR_EVENT_KICK` writes: a write without the bump leaves it unchanged (E834, 5 of 5: H-HWC
refuted). A kick pass of ours that left its command unread was followed by ticks with K 3 (E835),
so the count follows the kick events delivered rather than the commands read [infer, post hoc;
Q290]. A kick written without the bump is not consumed and raises no event: the read offset stays,
no answer comes in 504 ms, no kick entry reaches slot 0 and a later served kick does not deliver it
(one entry, one command read, CCB 4 and 3), and the tick goes on (E819 Q3, E834: 8 of 8). Read after
the run (E834, 5 of 5 jobs), it is not inert: from the write on every tick carries 0x01061a74 and
`CR_CLKGATESTATUS` reads 0x000ccfa0 while the EDM serves ticks and kicks with its queue empty
(`USE0_SERV_EVENT` bit 16 set), for at least 500 ms and through a served kick, until a debugfs reset
(what it starts is Q290). The words E538
logged for a kick, 0x03000000 with `pa0` = 2, are those of the tick after it. A client job's events
arrive one status bit at a time, in an order the same in every replicate, and the fill's end of
render reached slot 3 with `pa1` bit 4, the reversed order of E155 (E747); bit 19 did not appear in
any of them, nor in 8 jobs of 4096x4096 with 1500 vertices (E771, Q033). While a task of ours holds
the EDM the events are queued and not lost: up to four ticks (three latched on arrival, one when
the hold ends, the rest dropped), a kick once, a job's events once, all served after the hold
(E749, E750, E751, E752); two kicks in one 90-tick hold are two entries, each with the count it had
when it arrived (2 and 3, the ticks after them 4), 3 of 3 jobs (E794). Skipping the slot 3
end-of-render pass once stopped the tick and held the fill (E823).

**State between passes [HW].** At the next entry after a task of ours `pclink` reads 0x98, p0 1
and p1, p2 and p3 what the task left (E809, 12 of 12; after an `sa64` with the tick bit clear
`pclink` reads 6, E792); after a client fill, a firmware reload or a reset p0 p1 read 1 1, p2 0 and
p3 as left (E810). `i0`, `i1` and `r21` survive a reload and a reset, `r20` and `sa63` do not
(E810). `pa0` to `pa4` read `sa64` to `sa68`; a `mov` to `pa3` writes `sa67` for this pass and the
next, to `pa2` writes `sa66` for the pass only, to `pa4` is lost (E748, E820). Q158 holds the start
state after other perturbations and a cold boot.

**The event registers a task or the host writes** (named in the glossary; the effects are the
records'):

| register | offset | what the records show |
|---|---|---|
| `CR_EVENT_TIMER` | 0x0acc | periodic by itself; a `str` of 0x01061a80 moves the grid (E818) |
| `CR_EVENT_KICK` | 0x0ac8 | an event a kick with the word bumped, else none (E746, E819, E834) |
| `CR_EVENT_HOST_CLEAR2` | 0x0114 | clears the STATUS2 bits written, host or task (E821, E822) |
| `CR_EVENT_HOST_CLEAR` | 0x0134 | bit 18 clears STATUS bit 18, bit 15 does not (E823, E837) |

*Based on sgx545-ce `src/services4/system/unified/sysconfig.c`,
`src/services4/srvkm/devices/sgx/sgxconfig.h`; emgd-psb_regs; E002, E006, E008, E009, E011, E531,
E532, E533, E536, E537, E538, E746, E747, E749 to E752, E768, E771, E791 to E794, E809 to E814,
E816 to E823, E830, E834 to E837.*

## 13. Open questions

- **The rest of `asInitDevData`.** Entries outside [8..13] are unexplained.
- **Whether any payload value depends on the core revision or core id** the kernel reports to
  srvinit. The DDK version, build and build options do not (E352); the core words were 0 in
  every run, so a capture with nonzero ones would settle it.
- **What `0x0810`, `0x0814` and `0x0818` control** (Q001): `0x0818` bits 8 and 10 reach the
  render path (E404); the rest is open.
- **The SGX clock**: 399.0 MHz, or a tick and a `TIMER` fed from another reference (Q002).

*Based on E001, E011; `doc/specs/fw_format.md`.*
