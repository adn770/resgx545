+++
id = "E442"
claim = "A background object whose pixel shader fetches the render target itself at the pixel's position (the target as a strided ARGB8888 texture, the position from a douti of source 0 with two components) gives all of the triangle's pixels, 4422528 of 4422528 as a count, of the 4096x4096 job that overflows a 0x100-page parameter buffer, in three of three runs, where the library's background gives 987008 of them (three of three); at 1024x768 in 0x23 pages the image is exact with either background (207456 triangle pixels, three runs each); where nothing was stored the reload shows the target's 0xdeadbeef pre-fill (578976 and 12354688 pixels), also in jobs that do not overflow"
unit = "dpm"
method = "probes/dpm/partial-reload.toml (partial-reload.sh) on the laptop (direct cable), linux fork f1fad0ed9d0e with the debug option on: probe --tri pixel (green) at 1024x768 with 0x422 and 0x23 pages and at 4096x4096 with 0x422 and 0x100 pages (render_pb_pages), each without bgpixel and bgpds slots (the library's background, 0xff203040) and with them (bg_reload_1024.s or bg_reload_4096.s and pds_bg_pos.s: the background primary's douti 0x20400000 puts x + 0.5 and y + 0.5 in pa0 and pa1, the shader scales them by 1/width and 1/height and fetches with smp2dreplace from a strided texture at the target's address, T0 and T1 the copy's words for the size, its texel the pixel); three runs of each of the 8 cases (24 jobs, 12 with the reload), the target the sentinel 0xdeadbeef before the job, the colours counted (every pixel read at 1024x768)"
tiers = ["HW", "infer"]
date = "2026-11-07"
data = ["dpm-partial-reload", "dpm-partial-reload-pos"]
terms = ["Parameter Buffer (PB)", "Dynamic Parameter Management (DPM)", "DOUTI0.ATTR_SOURCE", "CR_ISP_CTL.PROCESS_EMPTY_TILES"]
+++

**What runs.** E437's source 0 gives the pixel's place to the background's primary program (a
background object has no vertices of its own to carry a coordinate set). The tool patches the
target's address into the background shader (`SGXFIVE_TRI_PROBE_TARGET_IMM`) and, after an
overflow, reads the target (probe --tri prints its colours after the failure). The final render
therefore paints each pixel it draws the background of with the texel the target holds at that
pixel when the shader runs.

**Results** (triangle G, library background B, sentinel S, other O: 0 everywhere; identical in the
three runs of each case):

| target | pages | background | job | G | B | S |
|---|---|---|---|---|---|---|
| 1024x768 | 0x422 | library | completes | 207456 | 578976 | 0 |
| 1024x768 | 0x422 | reload | completes | 207456 | 0 | 578976 |
| 1024x768 | 0x23 | library | overflows | 207456 | 578976 | 0 |
| 1024x768 | 0x23 | reload | overflows | 207456 | 0 | 578976 |
| 4096x4096 | 0x422 | library | completes | 4422528 | 12354688 | 0 |
| 4096x4096 | 0x422 | reload | completes | 4422528 | 0 | 12354688 |
| 4096x4096 | 0x100 | library | overflows | 987008 | 15790208 | 0 |
| 4096x4096 | 0x100 | reload | overflows | 4422528 | 0 | 12354688 |

**What it shows.** The overflowing 4096x4096 job loses 3435520 triangle pixels (78 percent) to the
library background, which paints regions that held geometry at a partial render (E311); the reload
background keeps what the partial renders stored and the triangle's pixel count is the whole
triangle, the count of the job that does not overflow. So the remedy the question names fills the
triangle's pixels on this hardware [infer]: a background object that reads the target back gives
the full pixel count of an overflowing scene's triangle, and the background's fetch of the target
works in a render that does not overflow too. The
1024x768 job in 0x23 pages is exact anyway (E310: its last abort comes before any region holds
geometry), so it does not tell the two backgrounds apart.

**What it does not show.** The depth half of the question (a depth buffer stored by ZLS across
partial renders, the 3D kick's RT status bit 1), the per-pixel identity of the 4096x4096 images
(only the colours were counted there), or a real driver's reload.
