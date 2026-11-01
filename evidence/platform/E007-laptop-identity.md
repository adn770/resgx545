+++
id = "E007"
claim = "The laptop's GPU is PCI 8086:0be1 rev 09 with its registers in a 1 MB BAR0 at 0x80000000 and no BAR2; the host bridge is 8086:0bf1 rev 03; the core reads CORE_ID 0x01150000 and CORE_REVISION 0x0001000d"
unit = "platform"
method = "lspci, the PCI sysfs, /proc/iomem and /proc/interrupts on the laptop, and the phase-3 kernel's sgx/status and sgx/regs read right after a cold boot, before any firmware load"
tiers = ["HW", "DDK", "infer"]
date = "2026-10-30"
data = ["platform-identity", "platform-boot-registers"]
terms = ["CR_CORE_ID", "CR_CORE_REVISION", "CR_CLKGATECTL", "CR_SOFT_RESET", "CR_BIF_DIR_LIST_BASE0", "CR_BIF_BANK0"]
+++

**PCI (platform-identity).** `00:02.0` is `8086:0be1` revision 09, subsystem `8086:1999`, bound to
gma500 (Linux 7.3.0-resgx545). Its resources: BAR0 memory `0x80000000`-`0x800fffff` (1 MB,
32-bit, non-prefetchable), BAR1 I/O ports `0x7100`-`0x7107`, the expansion ROM at `0xc0000`;
resources 2 and 3 are empty. Its interrupt is MSI, IRQ 25. The host bridge `00:00.0` is
`8086:0bf1` revision 03, subsystem `8086:1999`.

**The core before any load.** `sgx/status` reads `loaded 0`; `CORE_ID` (`0x1c`) is `0x01150000`
and `CORE_REVISION` (`0x20`) `0x0001000d`, which the DDK's fields (`sgx545defs.h`: `ID`
[31:16]; designer, major, minor, maintenance bytes) read as ID `0x0115` and revision 1.0.13.
`CLKGATECTL`, `CLKGATESTATUS` and `SOFT_RESET` read 0.

**What gma500 leaves (platform-boot-registers, "before load").** `BIF_BANK0` is 0,
`BIF_DIR_LIST_BASE0` holds a page directory (`0x028b7000` in this boot), directory list 2
(`0xc3c`) another (`0x028b9000`), `PDS_EXEC_BASE` `0x20000000`, `BIF_CTRL` 0, `BIF_INT_STAT`
`0x00080000` (no fault requestor; bit 19 set), and `EVENT_HOST_ENABLE` 0. The gma500 interrupt
had fired once.

Read with Linux v7.3's `gtt.c` (`psb_gtt_init`, `PSB_GATT_RESOURCE` = 2), an empty resource 2
means gma500 takes its fallback aperture, `gatt_start` = `0x40000000` and 128 MB [infer: from
the source, not read back].

This does not show the stolen-memory or GTT sizes, which the run does not read.
