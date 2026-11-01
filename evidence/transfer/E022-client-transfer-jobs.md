+++
id = "E022"
claim = "Transfer jobs submitted from userspace through the render node complete exactly on the laptop: a chain of eight dummies, fills of a whole 64x32 surface, an inset rectangle, a 300x70 rectangle across tiles and one pixel, and copies of three rectangles, three times each, with every pixel as the CPU computes it and no dword of the buffer outside the rectangle changed; on a fresh boot the first job starts the firmware"
unit = "transfer"
method = "sgxfive-test on the laptop with the debug option on, on a fresh boot (probes/render/client-jobs.toml): query, dummy -n 8, four fills and three copies three times each, the kernel log after each group"
tiers = ["HW"]
date = "2026-11-01"
data = ["render-client-jobs"]
terms = ["transfer_cmd", "hw_transfer_context"]
+++

**What runs.** sgxfive-test opens the render node, creates a VM and a transfer context, places
its assembled fill and copy programs (`programs asm`; format §9, §10) in its own heaps, and
submits each job through the transfer ioctl. The eight dummies are chained by a syncobj and
the tool waits for the last one. The script writes a mark to the kernel log when it starts,
and each log section shows only lines after the mark.

**Results.** The query, run first, reports `fw_state 0` and a firmware identity of zeros
(`ddk 0.0.0 build 0 options 0x0`): the firmware is not loaded yet. The dummy chain ends
with `dummy: 8 jobs ok`, and the log after it shows the firmware loaded and booted for
those jobs: the EDM answers the boot kick within 644 µs (an upper bound, E017).

All 21 fills and copies are exact. Each target matches the CPU's image pixel for pixel
(2048, 21000 or 1 pixels a fill, 2048 or 21000 a copy), and no dword of the buffer outside
the rectangle, the guard page included, changes. Each round gives the same target hashes, as
with the kernel's own debugfs fills and copies (E019, E020). The log adds no line after the
boot during the fills and copies.
