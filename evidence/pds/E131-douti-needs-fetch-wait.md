+++
id = "E131"
claim = "In the triangle host's primary pixel program, a douti started with no wait and no texture fetch delivers nothing to pa0 for any of the 64 sources (pa0 keeps 16 stale values), while with the fetch wait (DOUTU1 0x02000004) and the fetch's doutt it delivers source 0 (the pixel's x + 0.5), source 1 (the coordinate set's x), sources 32 and 33 (0xff000000) and 0 for sources 2 to 31, 34 and 35, and sources 36 to 63 leave the texel"
unit = "pds"
method = "probes pds-iteration-sources-iter-sources and -iter-coords of probes/pds/iteration-sources.toml (pds_iter.s: DOUTU1 4, one douti with DOUTI0 0x40000000 | source << 11, no doutt) and texture-fetch-tex-sources and -tex-fetch of probes/texture/fetch.toml (pds_tex.s: DOUTU1 0x02000004, the same douti with bit 0 set, then a doutt) on the laptop, linux fork with the debug option on: 64x64 triangle job whose pixel shader writes pa0 out as the colour (1062 triangle pixels), one run of each case, fresh context each"
tiers = ["HW"]
date = "2026-11-01"
data = ["pds-iteration-sources", "pds-iteration-sources-followup", "texture-fetch"]
terms = ["DOUTI0.ATTR_SOURCE", "DOUTI0.LAST_FETCH", "DOUTU1.WAIT_FETCH"]
+++

**What runs.** The triangle job's primary pixel PDS program starts the pixel shader, issues one
`douti` whose first word is `0x40000000 | source << 11` (second word 0) and ends. In the
iteration-sources probes the shader's DOUTU1 is 4 and nothing else follows; the `iter-coords` probe
adds a coordinate set (the vertex's clip x and y) to the vertices and `iter-sources` does not. In
the texture probes the shader's DOUTU1 is 0x02000004 (waits for the fetch), the `douti` has bit 0
set (the fetch takes coordinate set 1) and the program issues a `doutt` with the texture words for a
16x16 RGBA texture whose dword i is 0xd0000000 | i. The shader writes `pa0` out; 64 sources each,
1062 triangle pixels and 3034 background pixels.

**Results.**

- No wait, no fetch (128 cases, 64 sources in each of the two probes): `pa0` holds none of the
  iterations' values. At no pixel of any case is it the pixel's x + 0.5 or the clip x. Over the
  67968 triangle pixels of each probe it holds 16 different values (17 with the coordinate
  set, the extra one 0x20000), the same ones in both probes: 0x3e800000 (19866 pixels), 0 (12483),
  2 (12085), 0x3e400000, 0x99aabbcc, 0x3e000000, 0x55667788, 6, 0xbf3e0000, 0xbebe0000,
  0x11223344, 0x2000, 0x3f408000, 0xbf400000, 0x40000, 0xdf43. Per case, over both probes,
  0x3e800000 is 297 to 324 pixels, 0 is 181 to 200 and 2 is 179 to 203.
- With the fetch wait and the `doutt`, per source, over the 1062 pixels:

  | source | `pa0` |
  |---|---|
  | 0 | the pixel's window x + 0.5, at all 1062 pixels (within 1e-6) |
  | 1 | the coordinate set's x, (px + 0.5) / 32 - 1, at all 1062 (within 1e-6) |
  | 2 to 31, 34, 35 | 0 at all 1062; all 32 of these cases give one image |
  | 32, 33 | 0xff000000 at all 1062 |
  | 36 to 63 | the texel: one image in all 28 cases, the same as the `tex-fetch` case (233 values) |

**Second run.** The follow-up run of the two no-wait probes again shows no source-specific value in
`pa0`, but its stale values differ from the first run's: 54 different values (50 with the
coordinate set) over the 67968 pixels, 0 on 41067 of them. In each of the 128 cases 60 to 115
pixels hold the pixel's own clip x (5940 and 6004 pixels in all; none the window x + 0.5), where
the first run had none. It is the same for all 64 sources, so it is not a delivery by the
source. The texture probes have no follow-up.

**Not shown.** Which of the two, the wait or the `doutt`, makes the difference is not told by
these two probes, since each changes both. E048 has the wait cases: a wait on the iteration
(DOUTU1 bit 24) with the iteration's completion bit delivers the iterated value without a
fetch, and a fetch wait without a `doutt` hangs. The 36 to 63 sources are read as "the texel
overwrote `pa0`", not as a source that does nothing, since their image equals the fetch case. What
the stale values are, and where they come from, is not examined. One run of each case in the
first run, and of the two no-wait probes in the follow-up run.
