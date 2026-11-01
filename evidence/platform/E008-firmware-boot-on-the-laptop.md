+++
id = "E008"
claim = "The phase-3 kernel boots the firmware on the laptop at the DDK's REV1 heap bases in 20 of 20 load, boot and stop cycles: InitStatus bit 0 within about 0.2 ms in most cycles, no BIF fault, no AssertFail, the EDM translating through directory list 15, and a clean stop"
unit = "platform"
method = "the phase-3 kernel's debugfs (sgx/load, layout, boot, status, stop, regs) on the laptop: 20 load, boot and stop cycles with the kernel's boot log and status after each step, and register snapshots before a load, after a boot, after a stop and after a second boot"
tiers = ["HW", "DDK", "infer"]
date = "2026-10-30"
data = ["platform-boot", "platform-boot-registers"]
terms = ["CR_BIF_BANK0", "CR_BIF_DIR_LIST_BASE0", "CR_BIF_DIR_LIST_BASE15", "CR_BIF_CTRL", "CR_BIF_INT_STAT", "CR_BIF_FAULT", "CR_CLKGATECTL", "CR_CLKGATESTATUS", "CR_SOFT_RESET", "CR_EVENT_STATUS", "CR_EVENT_TIMER", "CR_EVENT_OTHER_PDS_EXEC", "CR_EVENT_OTHER_PDS_DATA", "ta3d_ctl"]
+++

**Twenty cycles (platform-boot).** Every cycle's layout is the same: the microkernel at
`0x30000000` (the kernel-code heap base), PDS #10-#14 at `0x3000d000`-`0x30011000`, the control
blocks from `0x32000000`, heap bases kernel code `0x30000000`, kernel data `0x32000000`, pixel
shaders `0x37000000`, vertex shaders `0x3c000000`, PDS `0x2e000000` and textures `0xf0000000`
(the REV1 bases of sgx545-ce `sgxconfig.h`). After every boot: `live 1`, no software event, no
BIF fault, `CLKGATECTL` `0xa6aa`, `CLKGATESTATUS` `0x20`, `SOFT_RESET` 0, `BIF_INT_STAT`
`0x00080000` (no fault requestor), `BIF_FAULT` 0, the CCB control words both 0, HostCtl as E005
gives it. After every stop: `live 0`, `CLKGATECTL` and `CLKGATESTATUS` 0, `SOFT_RESET` `0x3f`.

**How long it takes.** The kernel logs the time from its `EVENT_KICK2` write to the poll that
sees `InitStatus` bit 0. The poll sleeps 50-100 µs between reads, so each figure is an upper
bound. 18 of the 20 cycles took 165-355 µs (median 170 µs); one took 711 µs; the first cycle of
the run took 2364 µs, and the first boot after the cold boot (platform-boot-registers) 637 µs.

**What the boot leaves (platform-boot-registers).** After a boot `BIF_BANK0` reads `0xf`:
`INDEX_EDM` (bits 3:0) is 15 and every other requestor's index is 0. `BIF_DIR_LIST_BASE15`
holds the EDM's page directory (`0x05c40000` in this run), equal to TA3DCtl dword 23 read in
the same snapshot (E002: the dword the EDM reads as `sa23`); lists 1-14 and `BIF_CTRL` read 0.
`BIF_DIR_LIST_BASE0` holds gma500's page directory, as before the load: this kernel writes it
back after the reset (the DDK's `FIX_HW_BRN_28011` variant), so the run says nothing about the
DDK's own BIF-reset directory. `EVENT_OTHER_PDS_EXEC` reads `0x30010000`, the address of PDS #13,
and `EVENT_OTHER_PDS_DATA` 6, where the init script had written PDS #10's address and 1 (E006);
E002 and E003 place the writes of PDS #13's address and data size in the boot task.
`EVENT_TIMER` reads bit 24 set and a count below `0x61a80`; `EVENT_STATUS` reads `0x20000000`,
the `TIMER` bit only, with no `SW_EVENT`; the gma500 interrupt count is unchanged by the boot.
After the stop the other-event PDS registers and `EVENT_TIMER` read 0 again; the second boot
leaves the same values as the first.

**[infer]** The boot needs the microkernel at the EDM code base: this kernel places it there,
and it boots. The run does not try another placement.

This does not show the EDM code that does each write, nor any command after the boot.
