+++
id = "E016"
claim = "In 67 transfers of the closed stack under the harness every command is 0x1c0 bytes with flags 0x8, no update and one status entry whose value is the command's fence word plus one, the fence word counting the context's commands from 0; the commands lie back to back from offset 0 of a 0x104c8-byte client CCB in KERNEL_DATA, and the context is a 0xb4-byte KERNEL_DATA object"
unit = "transfer"
method = "the firmware-transfer capture (14 runs of the closed OpenVG stack under the harness, fills and copies) read with tools/fwcutter/tqcapture.py's commands report: the bridge log's allocations and kick requests, and every command read from the client CCB of the run's last snapshot"
tiers = ["CAP", "DDK"]
date = "2026-10-31"
data = ["firmware-transfer"]
terms = ["transfer_cmd", "transfer_cmd.cmd_size", "transfer_cmd.flags", "hw_transfer_context", "ccb_ctl"]
+++

**What the kick names.** In all 14 runs the kick's CCB is one allocation of `0x104c8` bytes
(`0x10000` + `0x4c8`, one command's worth past 64 KiB) in the KERNEL_DATA heap, and its
context one of `0xb4` bytes, also in KERNEL_DATA. The allocation made right after the CCB has
8 bytes and the same heap and attributes; the kick does not name it, so it is the control
block by position only. An earlier pair of the same kind (`0x10420` and 8 bytes) is never
named by a transfer kick.

**The commands.** The first command of every run starts at offset 0, and each later one
`0x1c0` bytes further on: the 67 commands are contiguous and the CCB never wraps within a
run (the furthest end is `0xc40`). In all 67:

- the size word (`+0xa4`) is `0x1c0` and the flags word (`+0xa8`) is `0x8`; the dummy flag
  `0x20` is never set;
- the update count (`+0x19c`) is 0;
- the shared block has one status entry (`+0x164` = 1); its value (`+0x16c`) is the fence word
  (`+0x198`) plus one, and the fence word is the command's index in its run (0, 1, 2, ...);
- the register block's fixed words are those fw_format.md §9.5 lists, and the words that vary
  are the background-object tag, the request base, the pixel-event program, the PDS execution
  base and the two render-box words (E004).

**What it does not show.** The snapshots keep only the CCB, the background objects and the
programs, so the context's own words and the CCB control block are not in the capture. The
shared block's sync counts read 0 because the harness does not do the kernel's part of the
kick (sgx545-ce `sgxtransfer.c` fills them, **[DDK]**); the closed stack's own sync use is not
seen.

**[DDK]** The kernel writes the shared block in the client CCB at the kick's shared offset
(sgx545-ce `src/services4/srvkm/devices/sgx/sgxtransfer.c`:87-254).
