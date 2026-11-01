+++
id = "E017"
claim = "Through the kernel CCB the EDM on the laptop answers GETMISCINFO with the core and DDK identity and the thirteen structure sizes srvinit's payload records, idles and powers off on the POWER command within about 0.2 ms with its clocks gated, and boots again after a power-off"
unit = "edm"
method = "the phase-4 kernel's debugfs on the laptop (probes/edm/ccb.toml): miscinfo three times, idle three times, stop (POWER with POWEROFF, then the deinit script and the reset), a second boot with miscinfo, a reload and boot with miscinfo; the kernel's log and a register snapshot around each step"
tiers = ["HW", "DDK"]
date = "2026-10-31"
data = ["edm-ccb"]
terms = ["misc_info", "misc_info.flags", "MISC_INFO_FLAGS.GET_STRUCT_SIZES", "MISC_INFO_FLAGS.READY", "misc_info_features", "misc_info.struct_sizes", "host_ctl.power_status", "ccb_ctl.read_offset", "ccb_ctl.write_offset"]
+++

**GETMISCINFO.** The kernel writes the request flag `GET_STRUCT_SIZES` (`0x2`) in the misc
buffer's first dword and sends command 6 with the buffer's address in data word 1. The EDM sets
the ready bit (`0x1`) (the kernel's poll saw it after 2, 642 and 2127 µs in the first three reads,
175 µs after the second boot and 173 µs after the reload) and fills in: core revision
  `0x0001000d` and core id `0x01150000` (equal to the registers), DDK version `0x00010711` (1.7,
  branch 17), build `0x000d2aaa` (862890), core id `0x221` (545), the revision it was built for
  `0x0001000d`, build options `0x60218`, then the thirteen structure sizes `0x2b0`, `0x1e0`,
  `0x4c8`, `0xdc`, `0xd0`, `0x3c`, `0x44`, `0x1ec`, `0x38`, `0x50`, `0xb4`, `0x44`, `0x20`, each
  equal to the size the boot payload records (E001). All five reads in the run agree. After the
  command the CCB control block reads write offset 1 and read offset 1: the EDM consumed the one
  command.

**POWER.** Idle (request 2 in data word 1): the kernel sees HostCtl's power status (dword 1) get
bit 2 and then the clock-gating status register clear under the init info's mask, 1031, 172 and
167 µs after the command, three times out of three. Power-off (request 1, from `stop`): bit 3,
168, 172 and 177 µs; the deinit script and the reset follow. A boot after a power-off, with the
same buffers, and a boot after a reload both reach init complete in about 0.2 ms and answer
GETMISCINFO again.

**[DDK]** The request values and the status bits are sgx545-ce's: `PVRSRV_POWERCMD_POWEROFF`
1 and `_IDLE` 2, `PVRSRV_USSE_EDM_POWMAN_IDLE_COMPLETE` bit 2 and `_POWEROFF_COMPLETE` bit 3
(`src/services4/include/sgx_mkif_km.h`:224-225, 255-256; used in `sgxpower.c`:242-250).

The times are the kernel's own, measured from the kick to the poll that sees the change, with
50-100 µs sleeps between polls: upper bounds.
