+++
id = "E058"
claim = "With the render flags' depth-buffer bit set, the depth store (4096 floats, 4 pages) lands where 0x0488 points and never where 0x0484 points, the depth load reads from 0x0484 whatever 0x0488 holds, and the stencil store (one page of bytes) lands where 0x0490 points only when its bit 31 is set and the stencil flag is on, never where 0x048c points; all repeated cases agree"
unit = "zls"
method = "hand-run script probes/zls/templates/load-store.sh on the laptop, linux fork with the debug option on: sgxfive-test tri --scratch 16 with kernel pokes of the render flags and the ZLS base words, three groups of cases, two of them run twice"
tiers = ["HW"]
date = "2026-11-01"
data = ["zls-load-store"]
terms = [
    "CR_ISP_ZLOAD_BASE", "CR_ISP_ZSTORE_BASE", "CR_ISP_STENCIL_LOAD_BASE",
    "CR_ISP_STENCIL_STORE_BASE", "hw_render_details.zload_base", "hw_render_details.zstore_base",
    "hw_render_details.stencil_load_base", "hw_render_details.stencil_store_base",
    "hw_render_details.bif_zls_req_base", "CR_ISP_ZLSCTL", "FRAG_FLAGS.DEPTH_BUFFER",
    "FRAG_FLAGS.STENCIL_BUFFER", "Z Load Store (ZLS)",
]
+++

**What runs.** The 64x64 triangle job with a 16-page scratch buffer of the job, every dword
0.25f (0x3e800000) before the render; the tool reports the dwords the render changed page by
page. A kernel poke sets the render flags' depth-buffer bit (`ta:7` bit 7), the ZLS base
(`rd:1` = 0x3e000000), the ZLS control word (`rd:11`) and the four base words (`rd:12` is
0x0484, `rd:13` 0x0488, `rd:14` 0x048c, `rd:15` 0x0490), pointing them at pages of the scratch
buffer or at the target. The triangle writes depth (`blk:1` = 0x00400200, test less). The
control words are 0x17100c (a frame that stores) and 0x11700a (a frame that keeps the previous
depth and stores nothing). The script has three groups: load against the triangle (8 cases, two
runs), the stencil bases (6 cases, one run) and the store and load bases against the
scratch pages (8 cases, two runs).

**Results.**

- Flag only, no bases: nothing in the scratch buffer changes and the image is the baseline
  (1062 triangle pixels, 3034 background).
- Store, control 0x17100c: with 0x0488 on scratch page 8 and 0x0484 on page 0, pages 8-11 change
  (4096 dwords, the first one 1.0); with the two swapped, pages 0-3 change. The base 0x0484 is
  never written to. The image is the baseline in both. Both runs agree.
- Load, control 0x11700a: nothing is stored (0 dwords change) and the image depends on 0x0484
  only. With 0x0484 on the scratch buffer (all 0.25f) and the triangle at z 0.5 under test less,
  the triangle is removed (0 triangle pixels, 4096 background, 936 pixels differ from the
  baseline) whatever 0x0488 holds; at z 0.1 under less it is kept (1062 pixels). With 0x0484 on
  the target (0xdeadbeef before the render) and 0x0488 on the scratch buffer, the triangle at z
  0.5 under less is kept (1062 pixels). Two readings stay open: the target was not read as depth
  there, or nothing was loaded (0xdeadbeef read as a float is negative, which no load of it
  would pass under less). Under test
  greater at z 0.1 the triangle is removed in all four cases, with no load as well. All of it
  repeats in the second run.
- Stencil, with control 0x17100c, 0x0484 at 0x11000, 0x0488 at 0xd000 (depth store into pages
  12-15) and both flag bits 7 and 8: with bit 31 set on both 0x048c and 0x0490 and the two on
  different pages, the 64x64 bytes of stencil (1024 dwords, a page, first dword 0) land on the
  page 0x0490 names (page 4, or page 0 with the two swapped), 5120 dwords changed in all. With
  bit 31 clear on 0x0490, or set on 0x048c only, or with flag bit 8 cleared, no stencil page changes
  (4096 dwords, the depth store only).
- One BIF fault line of the kernel log, `BIF fault 0x91000 at 0x37001003`, is the last line of
  the script's log tail; which case produced it is not recorded.

**Not shown.** The stencil base 0x048c was only ever pointed at a page and never seen to be
read, so the stencil load is untested here (the triangle has no stencil test). The layout of the
stored depth inside its four pages is not read by this script, and the guard-page overrun is
not tried.
