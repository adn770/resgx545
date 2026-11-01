+++
id = "E151"
claim = "With a transfer context naming a client page directory that alone maps the fill's destination and an update target, the fill lands exactly and the update word holds its value, whether the EDM's own buffers are aliased in that directory read-write, read-only, or (for the fill alone) not at all; a fill aimed at a read-only alias of a kernel buffer writes nothing and leaves CR_BIF_FAULT naming that page and list 1"
unit = "bif"
method = "the phase-4 kernel's debugfs on the laptop, probes/transfer/isolation.toml, linux fork with the debug option on: xfer_iso twice with read-write aliases (a 32x16 solid fill at (8,4), stride 320, plus an update word, each into addresses only the client directory maps), once with read-only aliases (alias_ro), once with no aliases and no update (no_alias), then xfer_ro (a 64x32 fill aimed at the destination's kernel address, mapped read-only in the client directory); one run of each, status and registers read after each; the same run as E021"
tiers = ["HW"]
date = "2026-11-01"
data = ["transfer-isolation"]
terms = ["hw_transfer_context.pd_dev_paddr", "CR_BIF_BANK0", "CR_BIF_FAULT", "CR_BIF_INT_STAT", "CR_BIF_DIR_LIST_BASE1", "transfer_cmd.patches"]
+++

**What runs.** The kernel builds a second page directory that maps a destination area at
`0x20000000` and an update target at `0x20010000`, neither mapped in the EDM's own directory,
plus the fill's programs and background object and, unless `no_alias`, every EDM buffer at its
kernel address (read-write, or read-only with `alias_ro`). The transfer context names this
directory (E021 has the same run). The fill's pixel writes, the programs' fetches and the
update (the transfer command's patch list) all have to reach their addresses to complete.

**Results.**

- Read-write aliases, two jobs: both 32x16 fills are exact (no wrong dword), SW_EVENT after
  145 us and 119 us, the update words read `0xc0ffee00` and `0xc0ffee01` as written, the BIF
  fault count stays 0, and `CR_BIF_DIR_LIST_BASE1` then holds the client directory
  (`0x0550a000`).
- Read-only aliases, one job: the fill is exact, the update word reads `0xc0ffee02`, no BIF
  fault.
- No aliases, no update, one job: the fill is exact, no BIF fault.
- The 64x32 fill aimed at the read-only alias: no SW_EVENT in 500 ms, the status word stays 0,
  the context's count stays 1, all 2048 destination dwords keep their sentinel (nothing written),
  `CR_BIF_INT_STAT` reads `0x80020` and `CR_BIF_FAULT` `0x32200001`, the page of the destination
  and list 1, the list that holds the client directory. `CR_BIF_BANK0` reads `0x100f` after the
  runs. No fault was counted by the kernel's handler.

So in this run the pixel-side writes (the fill and the programs it runs) translated through the
client directory, an update into an address only that directory maps was written, read-only
aliases of the EDM's buffers were enough for those jobs, and the same read-only mapping stopped
a write aimed at it.

**Not shown.** That the EDM needs its own buffers mapped in the client directory: the one job
with no aliases carried no update, so it does not show what an update does there (E021 says the
same), and no run left the EDM without aliases while it applied a patch. Which requestor of the
pixel side (PDS, USE, ISP, TSP, PBE) wrote or tried to write is not shown, only the fill as a
whole. One run of each case; the read-write job is the only one repeated.
