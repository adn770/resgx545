+++
id = "E018"
claim = "Dummy transfers complete on the laptop: eleven in a row each apply their update, write their status word, advance the client CCB's read offset by the command size, leave the context's count at 0 and raise one SW_EVENT; a dummy behind a destination sync one write short stays queued for the 50 ms the kernel waits and, once the host completes the sync and sends PROCESS_QUEUES, then runs and sets the write counter to pending + 1"
unit = "transfer"
method = "the phase-4 kernel's debugfs on the laptop (probes/transfer/dummy.toml): xfer_dummy eleven times, then xfer_sync three times; register snapshots after the boot, after the repeats and after the syncs"
tiers = ["HW", "DDK"]
date = "2026-10-31"
data = ["transfer-dummy"]
terms = ["hw_transfer_context.pd_dev_paddr", "hw_transfer_context.priority", "hw_transfer_context.ccb_dev_vaddr", "hw_transfer_context.ccb_ctl_dev_vaddr", "hw_transfer_context.submitted_commands", "device_sync_object", "CR_BIF_DIR_LIST_BASE1", "CR_BIF_BANK0.INDEX_3D", "CR_EVENT_STATUS.SW_EVENT"]
+++

**The command.** Built by `sgx_xfer_dummy()`: size `0x1c0`, flags `0x20` (dummy), one status
entry `{F, 0x1234 + n}`, one update `{U, 0xcafe0000 + n}`, no source sync; the context names the
EDM's own page directory, priority 0. The kernel writes the write offset, then sends command 1
(TRANSFER) with the context's address in data word 1.

**Eleven in a row.** Each time: the SW_EVENT interrupt arrives (after 130 to 290 µs, once 2717
µs, measured from the kick to the wake-up; the three sync-released ones 97, 87 and 128 µs), and
when the kernel reads after the event, U and F already hold their values, the CCB read offset
has advanced by `0x1c0` (`0x1c0`, `0x380`, ...), the context's count (`+0x14`) is 0 and exactly
one SW_EVENT was counted.

**The sync wait.** With the destination sync's write-complete counter at 5 and its pending
value 6, after 50 ms F is still 0, the read offset has not moved and the context's count is 1.
The host then writes 6 to the counter and sends PROCESS_QUEUES (command 7): the command runs as
above, the write counter reads 7 and the read counter keeps 0. Three times out of three.

**What the BIF shows.** After the eleven dummies, `BIF_DIR_LIST_BASE1` holds the context's page
directory (here the EDM's own, also in list 15) and `BIF_BANK0` reads `0x100f`: the 3D index
(bits 15:12) is 1 and the EDM's is 15. Before any transfer list 1 reads 0 and `BIF_BANK0`
`0xf`. So even a dummy points a directory list at the context's directory.

**[DDK]** sgx545-ce's sync object layout (read pending, read-complete address, write pending,
write-complete address: `src/services4/include/servicesint.h`:163-169) and the PROCESS_QUEUES
command, which the kernel sends to make the EDM look at its queues again (`sgxutils.c`:597).
