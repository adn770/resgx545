+++
id = "E021"
claim = "A transfer renders and applies its updates through the page directory its context names: a fill and an update into addresses only a client directory maps land, with the EDM's buffers aliased read-write or read-only in that directory, and the fill alone without them; a fill aimed at a read-only alias of a kernel buffer writes nothing, faults at that page, never completes, and leaves the EDM unable to power off until a reload and boot"
unit = "transfer"
method = "the phase-4 kernel's debugfs on the laptop (probes/transfer/isolation.toml): xfer_iso twice with read-write aliases, once with alias_ro, once with no_alias, then xfer_ro; status, registers and the kernel's log; stop, reload, boot, a dummy and a fill"
tiers = ["HW"]
date = "2026-10-31"
data = ["transfer-isolation"]
terms = ["hw_transfer_context.pd_dev_paddr", "CR_BIF_FAULT", "CR_BIF_INT_STAT", "CR_BIF_DIR_LIST_BASE1"]
+++

**Client directory.** The kernel builds a second page directory that maps a destination at
`0x20000000` and an update target at `0x20010000`, neither mapped in the EDM's own directory,
plus the fill's programs and background object and (unless `no_alias`) every EDM buffer at its
kernel address. The context names the client directory. With read-write aliases (twice) and
read-only aliases (once) the 32x16 fill is exact and the update word holds its value
(`0xc0ffee00` + n); with no aliases and no update the fill is exact. No BIF fault. Afterwards
`BIF_DIR_LIST_BASE1` holds the client directory (`0x0550a000` in this run) and `BIF_BANK0` `0x100f`.

**Read-only alias.** With read-only aliases, a 64x32 fill aimed at the destination area's kernel
address (mapped read-only in the client directory): no SW_EVENT within 500 ms, the status word
stays 0, the context's count stays 1, every dword of the three pages keeps the sentinel (nothing
written), `BIF_INT_STAT` reads `0x80020` and `BIF_FAULT` `0x32200001` (page `0x32200000`, the
destination's; `CID` 1, the list holding the client directory, hw_spec.md). No SGX interrupt
reached the kernel's handler (the host enable mask is `0x4000`, SW_EVENT only), so it counted no
BIF fault. The next `stop` gets no answer to POWEROFF (time-out after 500 ms) and halts the
core; after a reload and a boot a dummy and a fill complete as before.

**[infer]** The EDM reaches the update targets through the context's directory, so a client
directory without the EDM's buffers cannot carry updates; the run with no aliases sends none,
so it does not show what an update would do there.

This does not show which requestor wrote (or tried to write) through which list beyond the two
registers above, nor how to recover in place (phase 9).
