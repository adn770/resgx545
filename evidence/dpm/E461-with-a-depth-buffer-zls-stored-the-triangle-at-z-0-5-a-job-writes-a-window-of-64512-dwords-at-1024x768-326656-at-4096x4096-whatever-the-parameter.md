+++
id = "E461"
claim = "With a depth buffer (ZLS stored, the triangle at z 0.5) a job writes a window of 64512 dwords at 1024x768 (326656 at 4096x4096) whatever the parameter buffer; when the job overflows, the window's first 15104 dwords (80640) read 0.0 and, at 0x28 pages and below at 1024x768, the rest hold the depth with its sign bit set (-1.0, -0.5), in 2 of 2 runs of every 1024x768 case, and the job draws fewer triangle pixels than without the depth buffer (0, 27408, 31629 and 31629 against 51408, 162544, 205061 and 207456 at 0x30, 0x28, 0x24 and 0x23 pages)"
unit = "dpm"
method = "probes/dpm/depth-partial.toml (depth-partial.sh) and probes/dpm/depth-load.toml (depth-load.sh) on the laptop (direct cable): sgxfive-test tri --keep-overflow --depth (a depth buffer of the target's size with the ZLS flag, base, control and load and store bases armed by kernel pokes) on the 1024x768 and 4096x4096 triangle at z 0.5 with depth test less, render_pb_pages 0x422, 0x30, 0x28, 0x24, 0x23 (0x100 and 0x40 at 4096x4096), fills 0xdeadbeef, 1.0f and 0.25f, controls 0x0017100c, 0x0017100e and 0x0011700a, the buffer reduced to its distinct values on the laptop, two runs of each 1024x768 case"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["dpm-depth-partial", "dpm-depth-load"]
terms = ["CR_ISP_ZLSCTL", "CR_ISP_ZLOAD_BASE", "CR_ISP_ZSTORE_BASE", "FRAG_FLAGS.DEPTH_BUFFER", "Parameter Buffer (PB)"]
+++

**What runs.** The library's triangle at z 0.5 with depth test less (`--poke blk:1=0x00400200`) on
a render context for the target, 1024x768 (207456 triangle pixels, 578976 background) or 4096x4096
(4422528 and 12354688). `tri --depth` (new in this phase) maps a depth buffer of the target's width
x height dwords and sixteen pages over (784 pages at 1024x768, 16400 at 4096x4096), fills it before
the render, and arms the kernel pokes `ta:7^=0x80` (render flag DEPTH_BUFFER), `rd:1` = 0x3e000000
(the ZLS base, the general heap's), `rd:11` the ZLS control and `rd:12`, `rd:13` (the load and
store bases) at the buffer. The control is the clearing store frame `0x0017100c` unless stated;
`--keep-overflow` counts an overflowed job and reads on. The buffer is read back after the job: the
dwords that left the fill, the distinct values and the four most frequent, and (depth-partial) the
whole dump reduced to every value with its first and last dword. The parameter buffer is set by
debugfs `render_pb_pages`; the GPU was reset before each case. Two tables: `dpm/depth-partial` (24
cases: 1024x768 with 0x422, 0x30, 0x28, 0x24 and 0x23 pages and the sentinel 0xdeadbeef as fill,
0x422, 0x28 and 0x23 with 1.0f as fill, each twice; 4096x4096 with 0x422, 0x100, 0x40 and 0x23
once; and `-n 2` with the load-only control `0x0011700a` for the second render at 0x422 and 0x28,
twice) and `dpm/depth-load` (24 cases, two runs each of: no depth buffer at 0x422, 0x30, 0x28, 0x24
and 0x23; fill 0.25f with the control `0x0017100e` (the store control with bit 1) at 0x422, 0x30,
0x28 and 0x23; fill 0.25f with the load-only control `0x0011700a` at 0x422, 0x28 and 0x23). The two
runs of every 1024x768 case gave identical lines (all 10 pairs of depth-partial and all 12 of
depth-load; the one difference in a pair is the health lines after the last case); the 4 cases at
4096x4096 ran once.

**Results**, 1024x768, control `0x0017100c`, fill 1.0f or the sentinel (the sentinel shows what the
store touched; with 1.0f the same counts, only the background reads 1.0f):

| pages | job | window changed (dwords) | window content | triangle pixels with / without the depth buffer |
|---|---|---|---|---|
| 0x422 | ok | 64512 of 802816 | 62122 x 1.0, 2390 x 0.5 (dwords 25664 to 33056) | 207456 / 207456 |
| 0x30 | overflowed | 64512 | 15104 x 0.0 (dwords 0 to 15103), 47018 x 1.0, 2390 x 0.5 (same dwords) | 0 / 51408 |
| 0x28 | overflowed | 64512 | 15104 x 0.0, 22000 x -1.0, 27408 x -0.5 | 27408 / 162544 |
| 0x24 | overflowed | 64512 | 15104 x 0.0, 17779 x -1.0, 31629 x -0.5 | 31629 / 205061 |
| 0x23 | overflowed | 64512 | 15104 x 0.0, 17779 x -1.0, 31629 x -0.5 | 31629 / 207456 |

At 4096x4096 (one run each, sentinel fill): 0x422, ok: window 326656 of 16793600 dwords, 293408 x
1.0 and 33248 x 0.5 (dwords 122880 to 161448), 4422528 triangle pixels; 0x100, overflowed: 80640 x
0.0 (dwords 0 to 80639), 210848 x 1.0, 35168 x 0.5, 1920 triangle pixels; 0x40 and 0x23,
overflowed: 80640 x 0.0, 78645 x -1.0 and 167371 x -0.5 in both, 29779 and 12491 triangle pixels.
Dwords beyond the window kept the fill in the cases with the sentinel and 0.25f fills (738304 of
802816 at 1024x768, 16466944 at 4096x4096). The jobs without a depth buffer (depth-load, a
separate run 11 minutes later) drew 51408, 162544, 205061 and 207456 triangle pixels at 0x30,
0x28, 0x24 and 0x23, and 207456 at 0x422. No job faulted or
hung; the overflowed ones returned -ENOSPC with their context kept (19 jobs of depth-partial;
kernel.log has no hung, fault or recovery-failed line).

Loads (depth-load, fill 0.25f, 1024x768): the control `0x0017100e` stored as `0x0017100c` at 0x422
(62122 x 1.0 and 2390 x 0.5 in the window, 207456 triangle pixels: the buffer was not loaded); at
0x30 only 15104 dwords left the fill (set to 0.0) and no 1.0 or 0.5 was stored, at 0x28 and 0x23
the window held 15104 x 0.0 and 49408 x -0.25 (0xbe800000), the loaded fill negated, with 0
triangle pixels in all three. The load-only control `0x0011700a` stored nothing at 0x422 (0
changed) and drew 0 triangle pixels (the loaded 0.25f is in front of z 0.5, E058), and at 0x28 and
0x23 stored 64512 x -0.25 over the whole window, with 0 triangle pixels. With `-n 2` and the
load-only control for the second render at 0x422, the second render drew 183867 triangle pixels
(the tool counted 23421 pixels that differ from its reference); at 0x28 both renders overflowed,
the second left 15104 x -0.0 (0x80000000), 17779 x -1.0 and 31629 x -0.5 in the window and drew no
triangle pixel.

**What it shows.**

- The ZLS store of this setup writes a window of the buffer, not the target: 64512 dwords at
  1024x768 and 326656 at 4096x4096 whatever the parameter buffer, for a job with the whole scene
  too (E058 stored 4096 for 64x64). The window holds 2390 of the 207456 triangle depths at
  1024x768, so it is not one dword per pixel of the target; its layout is not shown [HW] (Q107).
- A job that overflows the buffer leaves the window changed: its first 15104 dwords (80640 at
  4096x4096) read 0.0 and, at 0x28 pages and below, the rest hold the stored depth with its sign
  bit set, in two runs of every case [HW]. The magnitudes survive (the triangle's 0.5 and the
  background's 1.0), so the depth the partial renders stored is what the window holds at the end of
  the job, with a sign flip that the whole-buffer job does not have [infer]. That the final render
  reads the partial renders' stored depth back is supported by the load-only job storing the
  negated fill (-0.25) where the whole-buffer job stores nothing, but the data do not separate "the
  final render loads the partial render's depth" from "the partial render stores and the final
  render stores the same window negated" [infer].
- With the depth buffer the overflowing job draws fewer triangle pixels than without it at every
  size that overflows (27408 against 162544 at 0x28; 31629 against 207456 at 0x23, where the job
  without a depth buffer is exact): the depth flag changes the partial-render outcome [HW].
- The ZLS control with bit 1 alone (0x0017100e) did not load the buffer at 0x422 [HW]; the
  load-only control removed the triangle in the 0.25f-fill cases (0 triangle pixels at 0x422, 0x28
  and 0x23) and stored the negated fill [HW]; that it loaded the buffer is a reading of these
  [infer].

**What it does not show.** The layout of the window, the meaning of the 15104 and 80640 zero dwords
and the sign flip, a depth reload in the background object (E442 reloads colour only), a depth test
with overlapping triangles whose order the depth decides, and the colour-reload remedy with a depth
buffer.

**Provenance.** linux fork commit 6ee9501832af with the debug option on, module srcversion
14D099861204842EA496D85 (the installed module file and the loaded module, read from /sys/module,
were equal; the run prints both and stops if they differ), sgxfive-test sha256
7d9e63c7c6407df9ee7444420b6796c99bddd2a7f824f494e0e550f28ce55203 (built from this phase's overlay
source as it stood at the run, named in each env.toml), the laptop over the direct cable.
kernel.log is authoritative for the logged lines.
