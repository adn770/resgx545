+++
id = "E019"
claim = "Solid fills built from the firmware file's templates render exactly on the laptop: a whole 64x32 surface, a 32x16 rectangle on a 320-byte stride, a 33x16 rectangle across tiles and one pixel, each with every other dword of three pages untouched, the command equal to the file's 12 TQ_CMD words, no BIF fault, interleaved with dummies"
unit = "transfer"
method = "the phase-4 kernel's debugfs on the laptop (probes/transfer/fill.toml): xfer_fill (four rectangles) three times, then twice a dummy and a fill, then a dummy; the kernel checks every dword of the two destination pages and a guard page"
tiers = ["HW"]
date = "2026-10-31"
data = ["transfer-fill"]
terms = ["transfer_cmd.isp_render", "transfer_cmd.pds_exec_base"]
+++

**What runs.** For each rectangle the kernel builds the seven fill programs from the firmware
file's templates (format §9, E004) at the PDS heap base and the pixel-shader code base, a
background object with no texture layer (PDS state and three vertices), and the command: its
12 words named in the file's TQ_CMD list match the file's values every time; the render box
words follow the rectangle in 32 x 16 tiles; the fence count and the status value n + 1.

**Results.** 20 fills out of 20 are exact: every dword inside the rectangle holds the colour
(`0xff336699`, `0xff00ff00`, `0x80112233`, `0x12345678`), every dword outside it in the three
pages keeps the sentinel, so the writes stop at the rectangle on a padded stride and across a
tile edge, and nothing reaches the guard page. Each fill raises one SW_EVENT (79 to 145 µs
after the kick), the status word holds n + 1 when the kernel reads after the
event, the read offset advances by `0x1c0`, the context's count returns to 0 and no BIF
fault is counted. Dummies before, between and after fills complete as in E018.

**[infer]** A transfer needs no parameter buffer, render target or DPM state: the kernel
supplies none.
