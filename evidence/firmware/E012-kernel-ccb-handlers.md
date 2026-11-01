+++
id = "E012"
claim = "The boot payload's kick-address table names an EDM handler for eight of the eleven kernel CCB commands (TA, TRANSFER, POWER, CONTEXTSUSPEND, CLEANUP, GETMISCINFO, PROCESS_QUEUES, SETHWPERFSTATUS) and none for 2D, DATABREAKPOINT and FLUSHPDCACHE; the same at both captured layouts"
unit = "firmware"
method = "srvinit run under the harness without a GPU (captures/firmware/init-payload.toml), its boot payload decoded by harness/ukernel-extract/initinfo.py at the DDK's REV1 layout and with only the page directory moved"
tiers = ["CAP", "DDK"]
date = "2026-10-31"
data = ["firmware-init-payload"]
terms = ["kernel_ccb", "command.service_address", "command.cache_control", "command.data", "CR_EVENT_KICK"]
+++

**The table.** The boot payload carries one kick address per kernel CCB command, in the order of
the DDK's command enumeration (sgx545-ce `src/services4/include/sgxinfo.h`:50-67,
`SGXMKIF_CMD_TA` = 0 to `SGXMKIF_CMD_FLUSHPDCACHE` = 10): the address the host writes as a
command's first dword, an instruction index of the microkernel (byte offset / 8). At the REV1
layout:

| index | command | handler | byte offset |
|---|---|---|---|
| 0 | TA | `0x011d` | `0x008e8` |
| 1 | TRANSFER | `0x0103` | `0x00818` |
| 2 | 2D | none | |
| 3 | POWER | `0x00d4` | `0x006a0` |
| 4 | CONTEXTSUSPEND | `0x00eb` | `0x00758` |
| 5 | CLEANUP | `0x013a` | `0x009d0` |
| 6 | GETMISCINFO | `0x0173` | `0x00b98` |
| 7 | PROCESS_QUEUES | `0x0156` | `0x00ab0` |
| 8 | DATABREAKPOINT | none | |
| 9 | SETHWPERFSTATUS | `0x0157` | `0x00ab8` |
| 10 | FLUSHPDCACHE | none | |

The run with only the page directory moved gives the same eleven entries: the handlers are
instruction indices from the EDM code base, independent of where the data heaps sit.

**What it shows.** The table names a handler for exactly these eight commands; for the other
three it holds no kick address, so this build has no handler for them. The firmware file
records the table (`sgx_fw` meta words `SGX_FW_META_KICK`, fw_format.md), so a driver takes
the handler from the file rather than from a constant.

**[DDK]** sgx545-ce's `SGXScheduleCCBCommandKM` writes the command type's kick address as the
command's first dword (`src/services4/srvkm/devices/sgx/sgxutils.c`:374), whose layout is
`{ui32ServiceAddress, ui32CacheControl, ui32Data[6]}` (`src/services4/include/sgx_mkif_km.h`:49-54).

This does not show what each handler does; the dataflow (E013) and the runs on the laptop
(E017, E018) do.
