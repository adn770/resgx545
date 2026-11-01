+++
id = "E198"
claim = "OUTSEL bits 7:0 enable user clip planes: with bit 0 and a 5-dword vertex the triangle is drawn when the fifth dword (o4) is +1.0 and removed when it is -1.0, with bits 1:0 and a 6-dword vertex only when o4 and o5 are both positive, a plane crossing the triangle removes it whole instead of cutting it, and fdpc's value serves as the distance like fdp's; with a 4-dword vertex any of bits 7:0 set removes the triangle or faults the job"
unit = "mte"
method = "the 19 probes of probes/mte/user-clip-planes.toml (vtx_fdpc.s and vtx_fdpc10.s: the vertex program writing o4 and o5 with mov, fdp or fdpc), blk:13 (OUTSEL) set to 0x43001, 0x43002, 0x43020, 0x430ff, 0x53000, 0x53001, 0x53002, 0x63002 and 0x63003, blk:15 at five MTECTL values, 64x64 target, on the laptop with the linux fork and the debug option on, one run; and the blk:13 bit flips of the vdm-stream-words sweep, which ran twice"
tiers = ["HW", "infer"]
date = "2026-11-01"
data = ["mte-user-clip-planes", "vdm-stream-words", "vdm-stream-words-followup"]
terms = ["OUTSEL", "OUTSEL.VTX_SIZE", "OUTSEL.PLANES"]
+++

**What runs.** The triangle's OUTSEL is 0x43000 (vertex size 4 dwords in bits 19:16; bits 12 and 13
set). The probes set bits 7:0 and, with `vtx_coords` 1 or 2, a vertex of 5 or 6 dwords. The vertex
programs write the dwords after the position (o4, o5) with `mov` to +1.0 or -1.0, or compute them
with `fdp` of the position against a plane held in r4-r7 (x + 0.5, x - 0.5 or y + 0.5), or run
`fdpc` against such a plane. The triangle is 1062 pixels when drawn and nothing (background only)
when removed.

**Results.**

- 4-dword vertex (0x43001, 0x43002, 0x43020, 0x430ff): the triangle is removed in every case with
  bit 1, bit 5 or all eight bits set, with no `fdpc` and with every vertex inside. With bit 0 alone
  four of the five jobs faulted (the context was lost and recovered each time) and one removed the
  triangle. The sweep's blk:13 flips of bits 2 to 7 remove the triangle in both runs; bit 0
  (`^=0x1`) changed 936 pixels in one run and faulted in the other, and bit 1 (`^=0x2`) the other
  way round.
- 5-dword vertex, bit 0 set (0x53001): o4 = +1.0 draws, o4 = -1.0 removes the triangle. With `fdpc
  cp0` of +w (inside) it draws, of -w (outside) it removes the triangle, and so it does with `fdp`
  or `fdpc` of x when the plane crosses the triangle (half outside). With bit 0 clear (0x53000) all
  six o4 cases draw.
- A plane crossing the triangle removes it whole: `fdp x + 0.5` (one vertex out), `x - 0.5` (one
  vertex in) and `y + 0.5` all give background only. Five MTECTL values (0x01555600, 0x01555624,
  0x01555628, 0x01555630, 0x0155563c) leave that unchanged.
- 6-dword vertex, bits 1:0 (0x63003): o4 = +1 and o5 = +1 draws; either one at -1 removes the
  triangle (two cases). `fdpc cp0` or `fdpc cp1` outside with both distances +1 removes it.
- Bit 1 alone: with a 5-dword vertex (0x53002) the triangle is removed for o4 = -1.0 and +1.0; with
  a 6-dword vertex (0x63002) for o4 = -1, o5 = +1 and for o4 = +1, o5 = -1.
- `fdpc cp0` outside with o4 = +1 removes the triangle with 0x53001, `fdpc cp1` outside draws it
  (plane 1 is off), and `fdpc cp0` inside with o4 = -1 draws it, so the fdpc value replaces the
  vertex's distance dword; this is E096's finding, seen again here.

**Reading [infer].** OUTSEL bits 7:0 are the user plane enables. An enabled plane takes its distance
from a dword after the position (plane 0 from o4; plane 1 together with plane 0 from o5), the vertex
size must hold it, and the MTE rejects a triangle with a negative distance at any vertex. In these
cases it does not cut at the plane, so a user plane acts as a cull distance.

**Not shown.** Which dword plane 1 reads when it is enabled alone: with 0x53002 and 0x63002 the
triangle is removed in all four cases, so neither o4 nor o5 on its own decides it (each case has one
of them positive), and the case with both positive was not run for it. What `cpN` adds beyond E096,
and whether the clipper cuts under some other state, is not tested. What OUTSEL bits 12 and 13 do is
open. One run of the probes.
