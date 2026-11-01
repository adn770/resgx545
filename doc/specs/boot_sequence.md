# SGX545 host boot sequence

This is the host side of the first firmware boot on Cedarview (Atom N2600), from "SGX island
powered" to "`HostCtl.ui32InitStatus` bit 0 = 1". It lists every register access and every
control-block write in order, with each `#if` of the DDK resolved for this build. It is the
spec for the boot code of the kernel driver, which lives on the linux fork's `resgx545`
branch under `drivers/gpu/drm/gma500/sgxfive/`: `sgxfive_boot()` in `sgxfive.c`, with the
phase C register sequence in `sgx_seq.c`. The firmware side of the same boot is described in
`doc/specs/hw_spec.md`; the content srvinit hands the kernel (code images, init scripts,
control-block images) is the firmware file of `doc/specs/fw_format.md`.

Conventions:

- **Sources.** The DDK is Intel's GPL DDK 1.7 kernel module for Cedarview, cited as
  sgx545-ce with paths from its repository root. In tables and running text, `sgxreset.c`,
  `sgxinit.c`, `sgxpower.c`, `sgxutils.c`, `mmu.c` and `sgxconfig.h` are the files under
  `src/services4/srvkm/devices/sgx/`; `sysconfig.c`, `sysconfig.h` and `sysinfo.h` are under
  `src/services4/system/unified/`; the `hwdefs/` headers are under `src/services4/srvkm/`.
  `gma500` is linux-gma500, Linux v7.3 `drivers/gpu/drm/gma500/`.
- **Ops.** `W` register write, `R` register read, `P` poll, `M` write to shared memory,
  `D` delay. Register offsets are from the SGX base, BAR0 + `0x80000` (sgx545-ce
  `src/services4/system/unified/sysconfig.h:43`, applied in `sysconfig.c:202`). On the
  laptop BAR0 is `0x80000000`, so the registers sit at `0x80080000` (E007).
- Inferences are marked **[infer]**. Everything else is read from the DDK or the mainline
  kernel source, or measured, as each section's last line says.

## 0. Configuration, resolved

The DDK's module build defines `SGX545`, `SUPPORT_SGX545` and `SGX_CORE_REV`, together with
`SYS_USING_INTERRUPTS`, `SUPPORT_HW_RECOVERY`, `PVR_SECURE_HANDLES`, `SUPPORT_SGX_HWPERF`,
`SUPPORT_PERCONTEXT_PB`, `DISABLE_PM` and `SUPPORT_SGX_NEW_STATUS_VALS`. It defines no
`PDUMP`, `EMULATOR`, `NO_HARDWARE`, `SUPPORT_ACTIVE_POWER_MANAGEMENT` or
`SGX_DYNAMIC_TIMING_INFO`. The firmware's own build reports client build options `0x60218`
(`src/include4/sgx_options.h`: bits 3, 4, 9, 17 and 18 set; bit 15, active power
management, clear) (E011).

The core revision of the firmware's build is 10131 **[infer]**: srvinit reports a HostCtl of
`0x44` bytes (E001), which is the 17-dword layout of `sgx_mkif_km.h`, and the only errata set
`sgxerrata.h` gives a 10131 core is `FIX_HW_BRN_SAMPLE_CACHE` alone (`sgxerrata.h:634`). The
sgx545-ce module itself builds 1013 by default, which adds `FIX_HW_BRN_31939`; nothing in the
boot sequence below depends on that erratum.

Device features and errata (`hwdefs/sgxfeaturedefs.h`, `hwdefs/sgxerrata.h`,
`hwdefs/sgx545defs.h`, `hwdefs/sgxmmu.h`, `src/services4/include/sgx_mkif_km.h`):

| item | value for this build |
|------|----------------------|
| errata (rev 10131) | only `FIX_HW_BRN_SAMPLE_CACHE` |
| `SGX_FEATURE_MULTIPLE_MEM_CONTEXTS` | on, with 16 directory lists |
| `SGX_BIF_DIR_LIST_INDEX_EDM` | **15** (`SGX_FEATURE_BIF_NUM_DIRLISTS - 1`) |
| `SGX_FEATURE_MULTI_EVENT_KICK` | on |
| `_MP`, `_36BIT_MMU`, `_SYSTEM_CACHE` | off |
| `_2D_HARDWARE`, `_DATA_BREAKPOINTS` | off |
| `EUR_CR_POWER` | **not defined** on 545 |
| `EUR_CR_BIF_CTRL_INVAL`, `EUR_CR_BIF_MEM_ARB_CONFIG` | not defined |
| `SOFT_RESET` bits | BIF 0, DPM 1, TA 2, USE 3, ISP 4, TSP 5, nothing else |
| BRN 23944, 23410, 28011, 28889, 31939, 23281 | off |
| `SGX_MMU_PDE_ADDR_ALIGNSHIFT` | 0: the PD address is written as-is |

System constants (`sysinfo.h:30-31`, `sysconfig.c:48-50` and `sysconfig.c:364-373`):

| item | value |
|------|-------|
| `MAX_HW_TIME_US`, `WAIT_TRY_COUNT` | 500000, 10000, so polls are 500 ms in 50 µs steps |
| `SYS_SGX_CLOCK_SPEED` | 400000000 (a constant) |
| `SYS_SGX_PDS_TIMER_FREQ` (ukernel tick) | 1000 Hz |
| `SYS_SGX_HWRECOVERY_TIMEOUT_FREQ` | 100 Hz |
| `bEnableActivePM` | false (`SysInitialise`) |

`SGXResetSleep` is `SGXWaitClocks(100)` (`sgxreset.c:SGXResetSleep`). That is
`OSWaitus(1 + 100 * 1000000 / 400000000)`, which is **1 µs** in integer arithmetic
(`sgxutils.c:SGXWaitClocks`). It is written `D` below.

*Based on sgx545-ce `Kbuild:58-112`, `src/include4/sgx_options.h`,
`src/services4/srvkm/hwdefs/sgxerrata.h:634`, `src/services4/system/unified/sysinfo.h:30-31`,
`src/services4/system/unified/sysconfig.c:48-50,364-373`; E001, E011.*

## 1. Ordered register-level sequence

### 1.1 How the DDK gets there

1. `DevInitSGXPart1` creates the kernel memory context (`BM_CreateContext`), whose page
   directory address becomes `sKernelPDDevPAddr`. It then calls `MMU_BIFResetPDAlloc`
   (`mmu.c`), which takes 3 contiguous pages: the **BIF-reset PD** (zeroed), the BIF-reset
   PT (zeroed) and a dummy page filled with `0xDB`.
2. `SGXGetInfoForSrvinitKM` hands `sKernelPDDevPAddr` to srvinit, which stores it in TA3DCtl
   dword 23, the value the EDM reads as `sa23` (E002). CPU and device physical addresses
   are identical on this platform (`sysconfig.c:SysCpuPAddrToDevPAddr`).
3. srvinit loads the ukernel, PDS programs and control blocks, then calls
   `DevInitSGXPart2KM`. HostCtl comes back from srvinit all zero (E005).
4. `DevInitSGXPart2KM` (`sgxinit.c`) sets `HostCtl.ui32PowerStatus |= 0x20` (`POWMAN_NO_WORK`)
   and zeroes the kernel CCB (`0x2000` bytes), the CCB control (8 bytes) and the event-kicker
   word (4 bytes). It registers the SGX power device with default state **OFF**.
5. So `PVRSRVFinaliseSystem` (state `DEFAULT` = OFF) changes nothing. The first CCB command
   powers the device on: it goes through `sgxutils.c:SGXScheduleCCBCommandKM`, which calls
   `PVRSRVSetDevicePowerStateKM(ON)`. That runs `SysDevicePostPowerState` (a no-op for SGX:
   the system layer never powers the SGX off), then `sgxpower.c:SGXPostPowerState`, which
   is phase B below. The host protocol spec, which arrives with the host protocol unit,
   covers that first command.

### 1.2 Phase B: `SGXPostPowerState(ON, from OFF)`

Source: `sgxpower.c:SGXPostPowerState`, which calls `SGXUpdateTimingInfo` (B2-B5),
`SGXInitialise` (B6) and `SGXStartTimer` (B7).

| # | op | target | value |
|---|----|--------|-------|
| B1 | M | HostCtl `+0x04` `ui32PowerStatus` | `0` |
| B2 | - | host timer `SGXOSTimer`, created disabled | period `1000*50/1000` = **50 ms** |
| B3 | M | HostCtl `+0x14` `ui32HWRecoverySampleRate` | `1000/100` = **10** |
| B4 | M | HostCtl `+0x18` `ui32uKernelTimerClock` | `400000000/1000` = **400000** (`0x61a80`) |
| B5 | M | HostCtl `+0x1c` `ui32ActivePowManSampleRate` | **0** (APM off) |
| B6 | - | `SGXInitialise(psDevInfo, bHardwareRecovery = FALSE)` | phase C |
| B7 | - | enable the 50 ms timer | - |

On the laptop, HostCtl holds these values once the boot completes (E005).

### 1.3 Phase C: `SGXInitialise`, registers and memory in order

Source: `sgxinit.c:SGXInitialise`; C1-C2 are `sgxreset.c:SGXInitClocks`, C3-C4 are
`sgxinit.c:SGXRunScript` on init script part 1 (`fw_format.md` §5, list 0).

| # | op | reg | name | value |
|---|----|-----|------|-------|
| C1 | W | `0x000` | `CLKGATECTL` | `0x0000a6aa` (init info `ui32ClkGateCtl`) |
| C2 | W | `0x004` | `CLKGATECTL2` | `0x00aaaaaa` (init info `ui32ClkGateCtl2`) |
| C3 | W | `0xa58` | `EVENT_PDS_ENABLE` | `0` |
| C4 | W | `0xacc` | `EVENT_TIMER` | `0` |
| C5 | - | | `ui32NumResets++` | then `SGXReset(bHWR = bFirstTime \|\| FALSE)` |

The clock-gating values come from the init info (E011); script part 1 is exactly the two
writes C3-C4 (E006).

`bFirstTime` is a function-static that starts true (`sgxinit.c:292`), is passed to
`SGXReset` (`sgxinit.c:316`) and is cleared after the first boot (`sgxinit.c:450`). So
**the first boot takes the hardware-recovery branch of `SGXReset`** (rows R8-R15). Later
power-ons skip it.

`SGXReset`, non-MP variant. Source: `sgxreset.c`; R1 and R10 are `SGXResetSoftReset`,
R3-R7 `SGXResetInitBIFContexts`, R12-R14 and R18-R20 `SGXResetInvalDC`, R16-R17
`SGXResetSetupBIFContexts`, the delays `SGXResetSleep`.

| # | op | reg | name | value |
|---|----|-----|------|-------|
| R1 | W | `0x080` | `SOFT_RESET` | `0x3f` (all six blocks, BIF included) |
| R2 | D | | | 1 µs |
| R3 | W | `0xc00` | `BIF_CTRL` | `0` |
| R4 | W | `0xc74` | `BIF_BANK_SET` | `0` |
| R5 | W | `0xc78` | `BIF_BANK0` | `0` |
| R6 | W | `0xc84` | `BIF_DIR_LIST_BASE0` | `0` |
| R7 | W | `0xc38`...`0xc70` | `BIF_DIR_LIST_BASE1`...`15` | `0`, 15 writes, ascending |
| R8 | W | `0xc84` | `BIF_DIR_LIST_BASE0` | BIF-reset PD physical address |
| R9 | D | | | 1 µs |
| R10 | W | `0x080` | `SOFT_RESET` | `0x3e` (release BIF only) |
| R11 | D | | | 1 µs |
| R12 | W | `0xc00` | `BIF_CTRL` | `0x8` (`INVALDC`) |
| R13 | W | `0xc00` | `BIF_CTRL` | `0` |
| R14 | D | | | 1 µs; no `BIF_MEM_REQ_STAT` poll with multiple contexts |
| R15 | R | `0xc04` | `BIF_INT_STAT` | `& 0xffff` (`FAULT_REQ`): 0 -> R16, else loop F |
| R16 | W | `0xc78` | `BIF_BANK0` | **`0xf`** (`INDEX_EDM` = 15; TA, host, 3D, 2D = 0) |
| R17 | W | `0xc70` | `BIF_DIR_LIST_BASE15` | **kernel PD physical address** (`>> 0`) |
| R18 | W | `0xc00` | `BIF_CTRL` | `0x8` |
| R19 | W | `0xc00` | `BIF_CTRL` | `0` |
| R20 | D | | | 1 µs |
| R21 | W | `0x080` | `SOFT_RESET` | `0` |
| R22 | D | | | 1 µs |

After a boot on the laptop, `BIF_BANK0` reads `0xf` and `BIF_DIR_LIST_BASE15` holds the
kernel PD (E008).

On a power-on that is not the first (and not HWR), R8-R15 become: `W SOFT_RESET = 0x3e`,
`D 1 µs`. No `BIF_DIR_LIST_BASE0` write happens then, so it stays 0 from R6. The laptop's
runs do not show this branch: resgx545's driver takes the first-boot path on every boot and
writes gma500's directory back to `BIF_DIR_LIST_BASE0` (§5 item 2; E008).

Fault loop F, run only while R15 sees a fault. Each pass maps the faulting page to the dummy
page, resets, invalidates, and unmaps it again:

| # | op | target | value |
|---|----|--------|-------|
| F1 | R | `0xc08` `BIF_FAULT` | `addr`; `pd = addr >> 22`, `pt = (addr & 0x3ff000) >> 12` |
| F2 | W | `0x080` `SOFT_RESET` | `0x3f` |
| F3 | M | reset PD `[pd]`; reset PT `[pt]` | `PT_phys \| 1` (4 KB, valid); `dummy_phys \| 1` |
| F4 | R, W | `0x12c` `EVENT_STATUS` -> `0x134` `EVENT_HOST_CLEAR` | the value read |
| F5 | R, W | `0x118` `EVENT_STATUS2` -> `0x114` `EVENT_HOST_CLEAR2` | the value read |
| F6 | D | | 1 µs |
| F7 | W, D | `0x080` `SOFT_RESET` | `0x3e`, then 1 µs |
| F8 | W, W, D | `0xc00` `BIF_CTRL` | `0x8`, `0`, then 1 µs |
| F9 | M | reset PD `[pd]`; reset PT `[pt]` | `0`, `0`; back to R15 |

With every buffer mapped, the first boot on the laptop sees `BIF_INT_STAT` = 0 at R15 and
never enters the loop (E008).

After `SGXReset` returns, `SGXInitialise` continues (`sgxinit.c:373-413`):

| # | op | target | value |
|---|----|--------|-------|
| C6 | - | `EUR_CR_POWER` | **no write**: the register does not exist on 545 |
| C7 | M | event-kicker word | `0` |
| C8 | W×38 | init script part 2 | `fw_format.md` §5 list 1, in order, relocated by the loader |
| C9 | M | HostCtl `+0x34` `ui32HostClock` | `OSClockus()` = `jiffies * (1000000 / HZ)`, u32 |
| C10 | M | HostCtl `+0x00` `ui32InitStatus` | `0` |
| C11 | - | `OSWriteMemoryBarrier()` | `wmb` |
| C12 | W | `0xae8` `EVENT_KICK2` | **`0x1`** (`NOW`); the kicker word is **not** bumped |
| C13 | - | `OSMemoryBarrier()` | `mb` |
| C14 | P | HostCtl `+0x00` | `(v & 1) == 1`; timeout **500 ms**, busy-wait every 50 µs |
| C15 | - | CCB control | assert `ReadOffset == WriteOffset` (both 0) |

C12 is the `SGX_FEATURE_MULTI_EVENT_KICK` branch; C14 is `PollForValueKM`. Script part 2
holds 38 writes (E006). On the laptop the poll succeeds well inside its timeout, in most
boots within about 0.2 ms, and the CCB offsets are equal afterwards (E008).

On timeout `SGXInitialise` calls `SGXDumpDebugInfo(psDevInfo, IMG_FALSE)` and returns
`PVRSRV_ERROR_RETRY` (`FIX_HW_BRN_23281` is off, so the dump happens and there is no retry
loop). With `bDumpSGXRegs = FALSE` the dump only covers memory:
`HostCtl.ui32AssertFail` (logged, then cleared to 0), all 17 HostCtl dwords and all TA3DCtl
dwords. The register half of the dump (enabled by HWR) reads `CORE_ID`, `CORE_REVISION`,
`EVENT_STATUS`, `EVENT_STATUS2`, `BIF_CTRL`, `BIF_BANK0`, `BIF_INT_STAT`, `BIF_FAULT`,
`BIF_MEM_REQ_STAT` and `CLKGATECTL`. A boot-timeout path in a new driver should read both
halves.

### 1.4 What the sequence leaves behind

- `BIF_BANK0 = 0xf`: the EDM requestor uses directory list **15**, the others use list 0.
- `BIF_DIR_LIST_BASE15` = kernel PD, which must be the same PD as TA3DCtl dword 23 (`sa23`,
  E002).
- `BIF_DIR_LIST_BASE0` = the BIF-reset PD (all zero) after the first boot, 0 after a later
  power-on. Lists 1-14 are 0.
- `BIF_CTRL = 0`: no MMU bypass, no pause.
- The DCU, USE code-base, PDS and event registers are as script part 2 left them, and the
  event-to-PDS dispatch is armed (`EVENT_PDS_ENABLE = 0x2204b00f`).

On the laptop, after a boot, `BIF_BANK0`, lists 1-15 and `BIF_CTRL` read these values and
`BIF_DIR_LIST_BASE15` equals TA3DCtl dword 23 (E008). `BIF_DIR_LIST_BASE0` holds gma500's
directory there, which the driver restores (§5 item 2), and the driver's snapshot does not read
`EVENT_PDS_ENABLE`.

Per-context PDs are set up later, not during boot **[infer]**: the ukernel has no statically
resolvable `DIR_LIST_BASE` write, but it does write `BIF_BANK0` and `BIF_BANK_SET` (E010).
A register-access listing of the
reader's own ukernel comes from running `harness/ukernel-extract/make_r2.sh`.

### 1.5 Teardown, for reference

`sgxpower.c:SGXPrePowerState`, new state OFF: disable the timer; submit `SGXMKIF_CMD_POWER`
with `ui32Data[1] = 1` (POWEROFF); poll `HostCtl.ui32PowerStatus` for bit 3
(`POWEROFF_COMPLETE`), 500 ms. Poll `CLKGATESTATUS` (`0x008`) `& 0xffffffdf == 0`, 500 ms.
Then run the deinit script (`fw_format.md` §5 list 2, 9 writes; E006). IDLE is the same
with command 2 and status bit 2, without the deinit script. The command half belongs to the
host protocol spec, which arrives with the host protocol unit. Without it, the deinit script
followed by `SOFT_RESET = 0x3f` stops an idle core: on the laptop, clock gating and the
other-event PDS registers read 0 afterwards and the next boot succeeds (E008).

*Based on sgx545-ce `src/services4/srvkm/devices/sgx/sgxinit.c`, `sgxreset.c`, `sgxpower.c`,
`sgxutils.c`, `mmu.c`; E002, E005, E006, E008, E010, E011; `doc/specs/fw_format.md`.*

## 2. HostCtl and the other control blocks

`SGXMKIF_HOST_CTL` (`src/services4/include/sgx_mkif_km.h`) is 17 dwords, `0x44` bytes, the
size srvinit reports (E001). srvinit allocates it zeroed. The last column lists every host
write in the DDK; all other writes are the EDM's.

| dw | off | field | host writes |
|----|-----|-------|-------------|
| 0 | `0x00` | `ui32InitStatus` | `0` just before the kick (C10); polled for bit 0 |
| 1 | `0x04` | `ui32PowerStatus` | `\|= 0x20` in Part2KM; `0` at power-on (B1) |
| 2 | `0x08` | `ui32CleanupStatus` | `&= ~1` after each cleanup command |
| 3 | `0x0c` | `ui32uKernelDetectedLockups` | never (read by misc info) |
| 4 | `0x10` | `ui32HostDetectedLockups` | `++` on a lockup seen by `SGXOSTimer` |
| 5 | `0x14` | `ui32HWRecoverySampleRate` | **10** (B3) |
| 6 | `0x18` | `ui32uKernelTimerClock` | **400000** (B4) |
| 7 | `0x1c` | `ui32ActivePowManSampleRate` | **0** (B5) |
| 8 | `0x20` | `ui32InterruptFlags` | never; the EDM sets `HWR` = 1, `ACTIVE_POWER` = 2 |
| 9 | `0x24` | `ui32InterruptClearFlags` | `\|= 1` in HWR; `\|= 2` / `&= ~2` for active power |
| 10 | `0x28` | `ui32BPSetClearSignal` | `0` (breakpoint misc-info path only) |
| 11 | `0x2c` | `ui32NumActivePowerEvents` | `++` after an active power-down |
| 12 | `0x30` | `ui32TimeWraps`, the EDM tick count | never |
| 13 | `0x34` | `ui32HostClock` | `OSClockus()` before the kick of every boot (C9) |
| 14 | `0x38` | `ui32AssertFail` | `0` after logging it in the debug dump |
| 15 | `0x3c` | `ui32PerfGroup` | set by the `SET_HWPERF_STATUS` misc-info request |
| 16 | `0x40` | `ui32OpenCLDelayCount` | decremented or zeroed by `SGXOSTimer` |

Sources: `sgxinit.c`, `sgxpower.c`, `sgxutils.c` (`SGXCleanupRequest`,
`SGXTestActivePowerEvent`). Dword 12 is never written by the host, yet on the laptop it
advances once per EDM tick (E005, E009); the glossary names it `host_ctl.edm_ticks`. After the
boot `EVENT_TIMER` reads bit 24 set and a count below dword 6's 400000, which fits a
down-counter the EDM reloads from dword 6 each tick **[infer]** (E009).

Before the first kick the host has written exactly: `PowerStatus` (`0x20`, then 0),
`HWRecoverySampleRate` = 10, `uKernelTimerClock` = 400000, `ActivePowManSampleRate` = 0,
`HostClock` and `InitStatus` = 0. All other dwords are 0 (E005).

The other control blocks at the kick:

| block | state at the kick |
|-------|-------------------|
| kernel CCB (`0x2000`) | all zero (Part2KM) |
| CCB control (8 B) | write offset 0 (host), read offset 0 (EDM) |
| event kicker (4 B) | 0 (zeroed in Part2KM and at C7); `EVENT_KICKER` holds its address |
| TA3DCtl (`0xec`) | srvinit's content; `sa23` = the kernel PD (= `DIR_LIST_BASE15`) |
| Misc, HWPerf CB, TA/3D signature | srvinit's content (zero) |

The block sizes and their order come from the init payload (E011), their contents from the
layout captures (E002). The kicker's address is the value script part 2 writes to
`EVENT_KICKER` (E006).

### 2.1 Where the clock comes from

Nothing reads the SGX clock from the hardware. `SysInitialise` stores the constant
`SYS_SGX_CLOCK_SPEED = 400000000` in `gsSGXDeviceMap.sTimingInfo` (`sysconfig.c:364`).
`SGXUpdateTimingInfo` reads it from there, because `SGX_DYNAMIC_TIMING_INFO` is off
(`sgxpower.c:61-70`). The value sets only two things: `ui32uKernelTimerClock`, the EDM tick
in core clocks (1 ms at 400 MHz), and the `SGXWaitClocks` delays (1 µs). On the laptop the
EDM tick runs at 997.46 Hz, which puts the clock at 399.0 MHz if a tick is dword 6 core clocks
(E009, Q002). A clock off 400 MHz changes only the tick period and those delays **[infer]**.

The first command after boot carries `ui32CacheControl = 0x2` (`INVAL_BIF_PD`): it comes from
the init info's `ui32CacheControl` (`sgxinit.c:InitDevInfo`), and `SGXScheduleCCBCommand`
copies it into the next command and clears it (E011). The host
protocol spec, which arrives with the host protocol unit, covers that command.

*Based on sgx545-ce `src/services4/include/sgx_mkif_km.h`,
`src/services4/srvkm/devices/sgx/sgxinit.c`, `sgxpower.c:61-70`, `sgxutils.c`,
`src/services4/system/unified/sysconfig.c:364`; E001, E002, E005, E006, E009, E011.*

## 3. Interrupt protocol

**Line.** The SGX `MASTER_INTERRUPT` reaches the CPU as bit 18 (`_PSB_IRQ_SGX_FLAG`) of the
display block's `PSB_INT_IDENTITY_R` (`0x20a4`). It is enabled in `PSB_INT_ENABLE_R` and
unmasked in `PSB_INT_MASK_R` (Linux v7.3 `drivers/gpu/drm/gma500/psb_irq.c`). In the DDK the
system layer's `SYSPVRServiceSGXInterrupt` (`sysconfig.c:1022`) calls `SGX_ISRHandler` and
schedules the MISR if that returns true. Which SGX events assert the line is set by
`EVENT_HOST_ENABLE`. Script part 2 sets it to `0x4000`, so only **`SW_EVENT`** (bit 14)
interrupts the host, and sets `EVENT_HOST_ENABLE2` = 0 (E006). On the laptop
`EVENT_HOST_ENABLE` reads `0x4000` after the boot (E006), and the boot itself raises no
`SW_EVENT`: `EVENT_STATUS` then holds the `TIMER` bit alone and the interrupt count does not
change (E008).

**LISR: `sgxinit.c:SGX_ISRHandler`.**

1. `R 0x12c EVENT_STATUS`, `R 0x130 EVENT_HOST_ENABLE`; `status &= enable`.
2. If `status & 0x4000` (`SW_EVENT`): `W 0x134 EVENT_HOST_CLEAR = 0x80004000`
   (`SW_EVENT | MASTER_INTERRUPT`), then `W 0x114 EVENT_HOST_CLEAR2 = 0`. Return handled.
3. Otherwise write nothing and return not handled. `EVENT_STATUS2` is not read
   (`SGX_FEATURE_DATA_BREAKPOINTS` is off).

The host never clears any other event bit. The EDM acknowledges its own events: it writes
`EVENT_HOST_CLEAR` at 34 sites and `EVENT_HOST_CLEAR2` at 4 (E010).
Running `harness/ukernel-extract/make_r2.sh` on the reader's own firmware lists the sites.

**MISR: `SGX_MISRHandler`, then `common/pvrsrv.c:PVRSRVMISR`.**

1. If `InterruptFlags & 1` (HWR) and not `InterruptClearFlags & 1`: `HWRecoveryResetSGX`.
   It sets `InterruptClearFlags |= 1`, dumps the debug info (registers included), runs
   `SGXInitialise(TRUE)` (the full phase C again, with the HWR reset branch), then
   `SGXScheduleProcessQueuesKM` and `PVRSRVProcessQueues`.
2. If `bReProcessDeviceCommandComplete` (a command was deferred from LISR context):
   `SGXScheduleProcessQueuesKM`. It sends `PROCESS_QUEUES` unless `PowerStatus` has
   `NO_WORK`.
3. `SGXTestActivePowerEvent`: if `InterruptFlags & 2` and not `InterruptClearFlags & 2`, it
   sets `InterruptClearFlags |= 2` and powers the device OFF. On `RETRY` it clears the bit
   again. This cannot fire here: with `ActivePowManSampleRate = 0` the EDM never requests it
   **[infer]**.
4. `PVRSRVProcessQueues`, then signal the global event object (waiters re-check their sync
   objects).

The host only ever sets bits in `InterruptClearFlags`. No host code clears
`InterruptFlags` or `InterruptClearFlags`: the EDM does. Its `POWER` handler clears bit 1 of
both, and the routine that tests `InterruptClearFlags` bit 0 clears bit 0 of both on a path that
also zeroes the TA/3D control words and sets the kernel CCB's read offset to its write offset;
the same routine sets `InterruptFlags` bit 0 on a lockup it
counts and bit 1 when its active-power countdown runs out, each with a `SW_EVENT` (E353, from
the firmware's code; not yet seen on the hardware).

**Host watchdog: `SGXOSTimer`, every 50 ms while powered.** It reads `USE0_SERV_EVENT`
(`0xb14`) XOR `USE1_SERV_EVENT` (`0xb20`), the EDM task registers named by the init info
(E011). Three equal readings in a row, with no reset in between,
count as a lockup: `HostDetectedLockups++`, then `HWRecoveryResetSGX`. A live EDM must change
these counters at least every 150 ms; on the laptop the EDM tick advances `USE0_SERV_EVENT`
about once a millisecond (E009). This also makes a cheap liveness check right after boot.

**On the hardware, faults and hangs.** A bus-interface fault asserts no host interrupt: held without
recovery (our kernel's debug switch), a render's fault leaves the interrupt and `SW_EVENT` counts
where they were while `BIF_INT_STAT` and `BIF_FAULT` keep the fault (E317, E319, one run each), so a
host learns of it only by polling. The EDM stops with it: it answers no kernel command and
`USE0_SERV_EVENT` stands still, which the DDK's watchdog above would take for a lockup [infer]
(E317, one run; the count read twice, for the fault only). `EVENT_STATUS2`, which the DDK's handler
never reads, reads `0x480` after the stream-read fault and the VDM hang, `0x440` for the pixel-task
hang and `0x400`, as when idle, for the control-block write fault (E317 to E319, one run each). Its
bits 7 and 6 latch when a TA stops at its start and when a pixel program runs long, until the next
reset (E357). After a boot in place the EDM answers GETMISCINFO within 169 to 175 µs (E321, one
run).

**Mainline gma500 (`psb_irq.c`).** `gma_irq_handler` reads `EVENT_STATUS` and
`EVENT_STATUS2` **unmasked** whenever bit 18 is set, and `gma_sgx_interrupt` then:

- reads `0xe04` if `EVENT_STATUS` bit 27 is set (SGX535 `2D_BLIT_STATUS`; bit 27 and `0xe04`
  are undefined on 545);
- if `EVENT_STATUS2` bit 4 is set (535 `BIF_REQUESTER_FAULT`, undefined on 545), reads
  `BIF_INT_STAT`/`BIF_FAULT` and logs them, decoded with 535 field names;
- **writes `EVENT_HOST_CLEAR = EVENT_STATUS` and `EVENT_HOST_CLEAR2 = EVENT_STATUS2`**, so
  every pending event bit is cleared, then reads `EVENT_HOST_CLEAR2` back.

The last step races the EDM **[infer]**: it can clear TA, 3D, DPM, timer or
cache-invalidate events the EDM has not consumed yet. `gma_irq_preinstall` writes
`EVENT_HOST_ENABLE = 0`. `gma_irq_postinstall` writes `EVENT_HOST_ENABLE2 = 0x10` and
`EVENT_HOST_ENABLE = 0x08000000`, both undefined bits on 545. Script part 2 overwrites all
three. §5 lists the required changes.

*Based on sgx545-ce `src/services4/srvkm/devices/sgx/sgxinit.c`,
`src/services4/system/unified/sysconfig.c:1022`; Linux v7.3
`drivers/gpu/drm/gma500/psb_irq.c`; E006, E008, E009, E010, E011, E317, E318, E319, E321,
E353.*

## 4. `FIX_HW_BRN_SAMPLE_CACHE` and the heap layout

`sysconfig.c:PCIInitDev` sets `need_sample_cache_workaround` when the `00:00.0` host bridge
revision is below 4 (`sysconfig.c:98`). The laptop's host bridge is revision 3, so it
applies (E007). The compile-time define only adds
`SGX_TEXTURE_HEAP_ID = 14` (`src/include4/sgxapi_km.h`), and `SGX_MAX_HEAP_ID` stays 15.
**The runtime flag changes the device heap layout and nothing else**: no register, script or
HostCtl value depends on it. `sgxinit.c:SGXRegisterDevice`:

- reports 14 heaps instead of 15 when the flag is false;
- uses the `*_REV1` bases from `sgxconfig.h` (SGX545 block, from line 134) for every heap;
- adds a **Texture** heap (ID 14) at `0xf0000000`, size `0x0ffff000`, per-context, WC.

| heap | 545 default | 545 `REV1` (host bridge rev < 4) |
|------|-------------|----------------------------------|
| General | `0x10000000` | `0x3e000000` (to `0xefffefff`) |
| 3D parameters (per-context) | `0xd2000000` | `0x10000000` |
| TA data | `0xe2000000` | `0x20000000` |
| Sync info | `0xef000000` | `0x2d000000` |
| PDS pixel code/data | `0xf0000000` | `0x2e000000` |
| **Kernel code** | `0xf2000000` | **`0x30000000`** |
| PDS vertex code/data | `0xf2400000` | `0x30400000` |
| **Kernel data** | `0xf4000000` | **`0x32000000`** |
| Pixel shader | `0xf9000000` | `0x37000000` |
| Vertex shader | `0xfe000000` | `0x3c000000` |
| Texture | - | `0xf0000000` |

On this silicon the workaround moves everything except textures below `0x3e000000` and gives
textures a 256 MB region of their own. That suggests the erratum is about textures sharing
address bits with other data in the sample cache **[infer]**.

Consequences:

- **The boot itself is indifferent.** It touches only the kernel code/data, PDS and shader
  heaps, at whatever addresses the firmware loader is given: the reference loader reproduces
  the captures at two different layouts (`fw_format.md` §6, E002).
- **Recommendation: use the `REV1` layout** for the device address map. It is the layout the
  DDK selects on revision-3 host bridges. Its boot heaps (`0x2e000000`-`0x3dffffff`) also
  stay clear of gma500's default-PD mappings (§5). A boot on the laptop at the `REV1` bases
  completes (E008), and its boot heaps lie below `0x40000000`, where gma500's aperture starts
  on the laptop (E007).

*Based on sgx545-ce `src/services4/system/unified/sysconfig.c:98`,
`src/include4/sgxapi_km.h`, `src/services4/srvkm/devices/sgx/sgxinit.c`,
`src/services4/srvkm/devices/sgx/sgxconfig.h:134`; E002, E007, E008;
`doc/specs/fw_format.md`.*

## 5. gma500 v7.3 interplay and required changes

What gma500 does to the SGX, and when. All writes marked "probe" happen before the driver's
boot trigger, so `SGXReset` and script part 2 redo or override them. On the laptop, before
the first load, `BIF_DIR_LIST_BASE0` and list 2 hold gma500's directories, `BIF_BANK0` is 0
and `PDS_EXEC_BASE` is `0x20000000`, as the table says (E007).

| when | gma500 action | effect on 545 | conflict |
|------|---------------|---------------|----------|
| probe | `cdv_init_pm`: APM `GFX` = ON, wait for D0 | powers the island | needed |
| probe | `psb_mmu_driver_init`: `BIF_CTRL` `CLEAR_FAULT` pulse | redone by reset | no |
| probe | `psb_do_init`: `BANK0 = BANK1 = 0`; `BIF_CTRL &= ~0x1ff00` | redone by reset | no |
| probe | `psb_spank`: `SOFT_RESET = 0x7f`, 1 ms, `0` | bits 0-5 + a spare bit | no |
| probe | `psb_spank`, `psb_do_init`: `W 0xc88 = gatt_start` | 535 `TWOD_REQ_BASE`, unused | no |
| probe | `psb_mmu_set_pd_context(default, 0)`: `DIR_LIST_BASE0` | zeroed by R6 | item 2 |
| probe | `psb_mmu_set_pd_context(pf_pd, 1)`: `W 0xc3c` | `DIR_LIST_BASE2`, zeroed by R7 | no |
| probe | `PDS_EXEC_BASE = 0x20000000`, `BIF_3D_REQ_BASE = 0x30000000` | overwritten | no |
| probe, resume | `gma_irq_pre/postinstall`: `HOST_ENABLE`, `ENABLE2` | clobbers part 2 | **yes** |
| SGX IRQ | `gma_sgx_interrupt`: clears all `EVENT_STATUS`/`STATUS2` bits | eats events | **yes** |
| GEM pin/unpin | `psb_mmu_flush`: read-modify-write of `BIF_CTRL` | races the EDM | **yes** |
| sleep | `gma_power_suspend`: `cdv_power_down` (island D3), PCI D3hot | state lost | **yes** |
| unload | `psb_mmu_free_pagedir`, `psb_mmu_driver_takedown` | PD freed | **yes** |

Files: `cdv_device.c`, `mmu.c`, `psb_drv.c`, `psb_irq.c`, `power.c`. The `BIF_CTRL` race is
**[infer]**: the EDM writes `BIF_CTRL` at 4 sites (E010), and
gma500's flush is not atomic with them. `psb_mmu_free_pagedir` writes `0` to
`0xc84 + 4 * hw_context`, that is `0xc84` and `0xc88`.

Runtime PM is not a risk. `gma_power_init` does `pm_runtime_get()` and nothing puts it back
until unload, so the device never runtime-suspends. Runtime PM is also forbidden by default
for PCI. Only system sleep and unload power the island down. The DDK never power-gates the
SGX island either (`sysconfig.c:938-982`, `SysDevicePrePowerState`).

gma500's SGX MMU mappings do not sit at `0xe0000000`. `mmu_gatt_start = 0xe0000000` only feeds
`gatt_free_offset`. Stolen memory and pinned GEM objects are mapped into the default PD at
**`gatt_start` + offset** (`psb_drv.c:psb_driver_load`, `gem.c:psb_gem_pin`), where `gatt_start`
is BAR2. When CDV does not report BAR2, `gtt.c:psb_gtt_init` falls back to `0x40000000` + 128
MB. The laptop reports no BAR2, so it gets the fallback (E007). The driver's heaps must stay out
of that range if they share the default PD.

Required changes, in the order the first boot needs them. A driver built this way boots the
firmware on the laptop and leaves the registers of §1.4 (E008).

1. **SGX interrupt (before the kick).** Give `gma_sgx_interrupt` the `SGX_ISRHandler`
   semantics while the firmware is up: if `status & enable & 0x4000`, write
   `EVENT_HOST_CLEAR = 0x80004000` and `EVENT_HOST_CLEAR2 = 0`, then queue the MISR work.
   Never write the raw status back. Report BIF faults by reading `BIF_INT_STAT` (`0xc04`,
   `FAULT_REQ` = bits 15:0, `FAULT_TYPE` = 18:16) and `BIF_FAULT`, without clearing.
   For the very first boot, masking bit 18 in `PSB_INT_MASK_R` is an acceptable stopgap,
   since the boot handshake is polled.
2. **BIF directory lists.** The EDM translates through **`DIR_LIST_BASE15`**, selected by
   `BANK0 = 0xf`, not `DIR_LIST_BASE0`. A PD kept only in `DIR_LIST_BASE0`, as gma500 sets
   it up, is not what the EDM uses. Write the EDM's PD to `0xc70` (R17), and put the same
   address in TA3DCtl dword 23 (`sa23`). For `DIR_LIST_BASE0` (R8), either implement the
   3-page BIF-reset PD as the DDK does, or restore gma500's default PD after the reset.
   Writing the kernel PD to `DIR_LIST_BASE0` is the DDK's own `FIX_HW_BRN_28011` variant, so
   the second choice is a configuration the DDK supports.
3. **Which PD.** Prefer a private kernel PD (as `DevInitSGXPart1` does) over gma500's
   default PD. Unload then cannot free it under the EDM, and gma500's GEM mappings are not
   visible to the firmware **[infer]**. If the default PD is used, the heap layout must avoid
   `[gatt_start, gatt_start + aperture)`. PDE format is `PT_phys | 1` and PTE format is
   `page_phys | flags` with `1` valid, `2` write-only, `4` read-only, `8` cache-consistent,
   `0x10` EDM-protect (`hwdefs/sgxmmu.h`); gma500's PTE bits are the same.
4. **No IRQ reinstall while live.** `gma_irq_preinstall`/`_postinstall` must not run while
   the firmware is up. They only run at probe and resume, and after resume the firmware must
   be booted again anyway.
5. **Suspend and unload.** In `gma_power_suspend` and before `psb_mmu_driver_takedown`, stop
   the firmware: the POWEROFF sequence of §1.5, or at least the deinit script and
   `SOFT_RESET = 0x3f`. Mark it not booted; the boot trigger boots it again.
6. **`BIF_CTRL` ownership.** The DDK writes `BIF_CTRL` only inside `SGXReset`. Later MMU
   invalidations go through the next command's `ui32CacheControl` (`mmu.c` sets
   `INVAL_BIF_PD`/`PT`/`SL` in `psDevInfo->ui32CacheControl`). Until gma500's SGX-MMU flushes
   are routed the same way, avoid gma500 GEM pins while the firmware runs: no modesets, no
   cursor or framebuffer changes.
7. **Cache attributes of the shared buffers.** The DDK maps kernel heaps write-combined
   (`PVRSRV_HAP_WRITECOMBINE`) and relies on `wmb()` before the kick (C11). Do the same
   (`set_pages_array_wc`, as `psb_gem_pin` does), or set PTE bit 3 if the pages stay cached.
   Either way, the C14 poll must use `READ_ONCE` on a mapping the SGX writes are visible
   through.
8. **Addresses below 4 GB.** No 36-bit MMU, so every PD, PT and data page must be below
   4 GB. That holds on this 2 GB i686 machine; `GFP_DMA32` is harmless.

*Based on linux-gma500 (`cdv_device.c`, `mmu.c`, `psb_drv.c`,
`psb_irq.c`, `power.c`, `gem.c`, `gtt.c`); sgx545-ce
`src/services4/system/unified/sysconfig.c:938-982`, `src/services4/srvkm/devices/sgx/mmu.c`,
`src/services4/srvkm/hwdefs/sgxmmu.h`; E007, E008, E010.*

## 6. Open questions

1. **Does a private PD versus gma500's default PD change anything** beyond the teardown
   coupling? The `BIF_CTRL` race of §5 item 6 exists either way (Q095).
2. **Does the ukernel itself do anything for the sample-cache erratum?** No such code is
   known; heap placement is the only visible part of the workaround (Q096).
3. **The SGX clock.** The laptop's EDM tick puts it at 399.0 MHz, not the DDK's 400 MHz, if a
   tick is dword 6 core clocks (§2.1; Q002).

The runs on the laptop answer four earlier questions: the boot raises no `SW_EVENT` (§3), the
`REV1` layout boots (§4), gma500 takes its fallback aperture there (§5), and the first boot
sees no BIF fault (§1.3). The firmware's code answers a fifth: the EDM clears `InterruptFlags`
and `InterruptClearFlags` itself (§3, E353).

*Based on §1-§5; E007, E008, E009, E353; Q095, Q096.*
