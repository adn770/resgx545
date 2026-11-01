+++
id = "E460"
claim = "With coordinate registers that deliver (E459), DOUTU1 bit 24 set or clear under the fetch wait gives the same image and registers in 33 of 33 completed jobs with both bits against 36 of 36 with bit 25 alone (12 probes of three shapes, three runs each), and 3 of 36 jobs with both bits hung, one in each probe that reads the last iterated register; 0 of 60 further jobs with both bits hung; bit 24 alone or neither bit differ from the stable image in 36 of 36 jobs each"
unit = "pds"
method = "probes/pds/iter-coords-bit24.toml on the laptop (direct cable): textured primaries that iterate a 2-component set alone (s), the vertex colour then a 2-component set (t) and then a 3-component set (u) before the fetch, on vertices that carry the dwords (E459), the shader's U1 at 0x03000004, 0x02000004, 0x01000004 and 0x00000004, three runs each, pa0 to pa3 (pa0 to pa4 for u) read in separate probes (15 probes: 13 of 12 cases and two of 30 jobs with U1 0x03000004), every pixel hashed and compared"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["pds-iter-coords-bit24"]
terms = ["DOUTU1.WAIT_ITER", "DOUTU1.WAIT_FETCH", "DOUTI0.LAST_ITER", "DOUTI0.ATTR_SOURCE"]
+++

**What runs.** E454 compared bit 24 on the colour shapes; its coordinate registers read 0, so the
coordinate shapes were open. With vertices that carry the set's dwords (E459) the textured primary
`pds_tex_col.s` or `pds_tex_col2.s` iterates a coordinate set before the fetch; the shader writes
one primary attribute out as the colour. Shapes: s, a 2-component set alone (source 1,
`vtx_coords.s`, pa0 and pa1 the set, pa2 the texel; pa3 nothing writes); t, the vertex colour
(douti `0x07c10000`) then a 2-component set (`vtx_color2.s`, 6 coordinate dwords, word 13 =
0xa3800; pa0 the colour, pa1 and pa2 the set, pa3 the texel); u, the colour then a 3-component set
(`vtx_color3.s`, word 13 = 0xb3800; pa1 to pa3 the set, pa4 the texel). DOUTU1 = 0x03000004 (bits
24 and 25), 0x02000004 (bit 25 alone), 0x01000004 (bit 24 alone) or 0x00000004, three runs of each:
12 cases a probe, 12 probes that read a register the program writes (3 + 4 + 5) and the 13th (s,
pa3), a register nothing writes. The douti of the set has the completion bit. Then two probes of 30
jobs with both bits on the colour then 2-component set: on E454's vertices (colour only,
`pds-iter-coords-bit24-hang-e454`) and on the sized ones (`-hang-t`), reading pa0. 216 jobs in all.

**Results** (12 probes, 36 jobs a setting; pixel hashes of every pixel compared with the probe's
own stable image, the one bit 25 alone gives in all three runs):

| DOUTU1 | completed | same as the stable image | hung |
|---|---|---|---|
| bits 24 and 25 | 33 | 33 | 3 |
| bit 25 only | 36 | 36 (the stable image) | 0 |
| bit 24 only | 36 | 0 (11 of 12 probes differ among the three runs; u pa3, a constant 0.25, reads the same in all three but not as the stable image) | 0 |
| neither | 36 | 0 (12 of 12 probes differ among the three runs) | 0 |

The coordinate registers hold varying non-zero values in the stable images (for example 0xbeb80000
on 44 pixels, 0xbec80000 on 43), the colour the vertex values (0xff020240 and so on) and the texel
(0xd0000000 | i) in the register after the set. The 3 hung jobs are the first run of s pa1, the
second of t pa2 and the second of u pa3 (the jobs 312, 386 and 456 of kernel.log, "hung,
recovering"; no recovery failed): in each shape the register read is the last that the program
iterates (the set's second component, its second component, its third component). Reading the last
iterated register under both bits is 9 jobs, 3 of them hung; the other 27 jobs with both bits (the
colour and the other set registers) and all 108 jobs of the other settings completed. s pa3, the
register nothing writes: 12 jobs, none hung, bit 25 alone gave three different images. The 60
further jobs with both bits (30 on E454's vertices, 30 on the sized ones, reading pa0, the colour)
all completed with one image (60 of 60). E454's own hang read pa0 of a colour then 2-component
shape, which is not the last iterated register.

**What it shows.**

- Under the fetch wait the registers and the image are the same with bit 24 set and clear in every
  job that completed (33 of 33 against the 36 of 36 with bit 25 alone), now with coordinates that
  vary [HW]. Without bit 25 they change from run to run, as in E436 and E454 [HW].
- A job with both bits hung in 3 of 36 (8 percent), and in none of 36 with bit 25 alone or of 60
  more with both bits on the colour register. The three hangs were all in the probe that reads the
  last register the program iterates [HW]; that reading it right after the iteration's completion
  is what hangs is a reading of 3 of 9 jobs [infer]. With E454's 1 of 30 hung (a different
  register) the hang is rare and not tied to one register, and it was seen only with both bits in
  these runs [HW]; that bit 24 with bit 25 can hang a job is a reading of 4 jobs [infer]; its
  cause is not shown.

**What it does not show.** The cause of the hang, other shapes (18 of E364's 21 programs were not
run themselves), a primary with no fetch, why the closed driver sets both bits.

**Provenance.** linux fork commit 6ee9501832af with the debug option on, module srcversion
14D099861204842EA496D85 (read by the campaign with modinfo from the installed module file and named
in each env.toml; the run script compared it with the loaded module's /sys/module value before the
run, outside the data, and neither is printed in the dataset), sgxfive-test sha256
2c2949e4e6bf9b6120a63014770f0bdc1dabb4e9249046c792dd08fb88fe1b8d (built from this phase's overlay
source as it stood at the run, named in each env.toml), the laptop over the direct cable. Three
builds of the tool ran in this phase (this one predates the rename of --depth-clear to --depth-base
and the registers at the words snapshots; the probe subcommand is the same in all three); the
sha256 of each dataset's build is in its env.toml.
