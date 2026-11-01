+++
id = "E006"
claim = "The init scripts srvinit hands the kernel write 2 registers before the reset and 38 after it, in a fixed order ending with EVENT_PDS_ENABLE = 0x2204b00f, and the deinit script clears 9; on the laptop the registers they leave read back as written"
unit = "platform"
method = "srvinit run to completion under the extraction harness at the DDK's REV1 heap bases, its 2068-byte boot payload decoded with initinfo.py; the registers the phase-3 kernel's sgx/regs reads, before a load, after a boot, after a stop and after a second boot"
tiers = ["CAP", "HW", "infer"]
date = "2026-10-30"
data = ["firmware-init-payload", "platform-boot-registers"]
terms = ["CR_EVENT_PDS_ENABLE", "CR_EVENT_TIMER", "CR_EVENT_HOST_ENABLE", "CR_EVENT_HOST_ENABLE2", "CR_PDS_CACHE_HOST_ENABLE", "CR_USE_G0", "CR_USE_G1", "CR_DMS_CTRL", "CR_USE_TMPREG", "CR_CACHE_CTRL", "CR_USE_CTRL", "CR_USE_CODE_BASE_0", "CR_USE_CODE_BASE_10", "CR_USE_CODE_BASE_15", "CR_PDS_EXEC_BASE", "CR_EVENT_KICKER", "CR_EVENT_OTHER_PDS_EXEC", "CR_EVENT_OTHER_PDS_DATA", "CR_EVENT_OTHER_PDS_INFO"]
+++

**The scripts (CAP).** In the REV1 run of firmware-init-payload (heap bases: kernel code
`0x30000000`, kernel data `0x32000000`, pixel shaders `0x37000000`, vertex shaders
`0x3c000000`, PDS `0x2e000000`), part 1 is `0x0a58 = 0`, `0x0acc = 0` (`EVENT_PDS_ENABLE`,
`EVENT_TIMER`). Part 2 is, in order (PDS #10 is the allocation at `0x3000e000` in this run):

| # | reg | value |
|---|---|---|
| 1-3 | `0x0818`, `0x0810`, `0x0814` | `0x7ff`, `0x1`, `0xffff` |
| 4-5 | `0x0130` `EVENT_HOST_ENABLE`, `0x0110` `EVENT_HOST_ENABLE2` | `0x4000`, `0` |
| 6-8 | `0x013c`, `0x0a7c`, `0x0a80` | `0`, `0`, `0` |
| 9-12 | `0x0a74` `DMS_CTRL`, `0x04e8`, `0x0a78`, `0x0aac` | `0x208200`, `0x100`, `0x2c`, `0x45` |
| 13-16 | `0x0abc`, `0x0800`, `0x0804`, `0x0a00` | `0xe`, `0x30`, `0xffff`, `0x7c000` |
| 17-26 | `0x0a0c`-`0x0a30` `USE_CODE_BASE_0..9` | `0x026e0000 + n x 0x1000` |
| 27-30 | `0x0a34`-`0x0a40` `USE_CODE_BASE_10..13` | `0x00780000 + m x 0x1000` |
| 31 | `0x0a48` `USE_CODE_BASE_15` | `0x06600000` |
| 32 | `0x0ab8` `PDS_EXEC_BASE` | `0x2e000000` |
| 33 | `0x0b30` | `0x100` |
| 34 | `0x0ac4` `EVENT_KICKER` | `0x32004000`, the event-kicker word |
| 35-37 | `0x0a68`-`0x0a70` (`EVENT_OTHER_PDS_EXEC`, `_DATA`, `_INFO`) | PDS #10, 1, 6 |
| 38 | `0x0a58` `EVENT_PDS_ENABLE` | `0x2204b00f` |

The deinit script clears `EVENT_PDS_ENABLE`, `EVENT_OTHER_PDS_EXEC`, `_DATA` and `_INFO`,
`USE_CODE_BASE_15`, `EVENT_HOST_ENABLE` and `EVENT_HOST_ENABLE2`, then writes `CLKGATECTL = 0`
and `CLKGATECTL2 = 0`. Decoded as `ADDR` [24:0] in 128-byte units and `DM` [26:25], the code
bases land on the pixel-shader heap plus n x `0x80000` (DM 1), the vertex-shader heap plus m x
`0x80000` (DM 0) and the kernel-code heap base (DM 3): an independent check of the decode and
of the layout (E003 has the same expressions for the cut firmware).

**On the laptop (HW).** `sgx/regs` reads only part of these registers (the ones the firmware
reaches, and the host's own). Of those, after a boot in platform-boot-registers:
`EVENT_HOST_ENABLE` `0x4000`, `DMS_CTRL` `0x208200`, `0x04e8` `0x100`, `0x0800` `0x30`,
`0x0804` `0xffff` and `PDS_EXEC_BASE` `0x2e000000`, as written. Before the first load, gma500
alone had left all of them 0 except `PDS_EXEC_BASE` (`0x20000000`). After the stop,
`EVENT_HOST_ENABLE` is 0 again and the four not in the deinit script keep their values.
`EVENT_OTHER_PDS_EXEC` and `_DATA` read `0x30010000` and 6 after the boot, not the script's
values: the firmware rewrites them (E008).

**Reading the order [infer].** Cache and event configuration first, then the shader code
bases, the PDS code base, `0x0b30`, the kicker word's address, the EDM's boot PDS program, and
last `EVENT_PDS_ENABLE`, which arms event-to-PDS dispatch so that the first kicked event starts
the EDM.

This does not read back the registers `sgx/regs` leaves out (among them `EVENT_HOST_ENABLE2`,
`EVENT_KICKER`, `EVENT_OTHER_PDS_INFO` and `EVENT_PDS_ENABLE`), nor say what `0x0810`-`0x0818`,
`0x04e8`, `0x0a78`, `0x0abc`, `0x0800` and `0x0b30` do.
