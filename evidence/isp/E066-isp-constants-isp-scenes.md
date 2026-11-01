+++
id = "E066"
claim = "Under four depth scenes of the 64x64 triangle (less written, translucent, punch-through, bit-exact equal) the only words of seven render words that change the image are cmd:11 bit 25 (and ~0) and cmd:13 bits 0 and 1 (and ~0, a hang); every flip, 0 and ~0 of cmd:17, cmd:21, cmd:22, rd:19 and rd:21 leaves it as it is, and the equal scene draws the triangle when vp4 and the background depth are both 0.3, which fits vp4 being the triangle's depth (no case varies vp4 under a depth test)"
unit = "isp"
method = "four sweeps of probes/isp/constant-registers.toml (tri-depth, tri-translucent, tri-punch, tri-equal): every bit and the values 0 and ~0 of seven words, 239 jobs each including the baseline, with the ISP registers sampled; plus the vp4 flips of the sweep in probes/vdm/stream-words.toml; on the laptop with the linux fork and the debug option on, one run"
tiers = ["HW", "infer"]
date = "2026-11-01"
data = ["isp-constant-registers", "vdm-stream-words"]
terms = [
    "CR_REG_0400", "CR_ISP_MSAA", "CR_REG_0800", "CR_ISP_LINE_SAMPLE_POS", "CR_ISP_REG_04E8",
    "CR_ISP_SAMPLE_POS", "CR_ISP_REG_04DC", "VIEWPORT.Z_OFFSET", "VIEWPORT.Z_SCALE",
    "CR_ISP_BGOBJDEPTH",
]
+++

**What runs.** Each sweep poked the 32 bits of the command words cmd:11, cmd:13, cmd:17, cmd:21 and
cmd:22 and of the render-details words rd:19 and rd:21 (the latter through the kernel's poke), plus
0 and ~0 of each: 34 jobs a word, 238 plus the baseline. The scenes set ISP0 (`blk:1`) to depth test
less with depth written (0x00400200), to the same in a translucent pass (0x02400200), to the same in
a punch-through pass (0x08400200), and to depth equal (0x00800200) with `blk:10` (vp4) and the
background object's depth `cmd:14` both at 0x3e99999a (0.3).

**Results.** All four sweeps agree case by case: 233 jobs give the baseline image, 4 change it and 1
hangs.

- cmd:11 bit 25 and the value ~0: all 4096 pixels become non-triangle, non-background (the byte 3
  inversion of E029), in every scene. No other bit of cmd:11 changes anything.
- cmd:13 bit 0: 844 triangle pixels, 693 pixels differ from the baseline; bit 1: 876 triangle
  pixels, 750 differ; ~0 hangs the job. Other bits of cmd:13 leave the image as it is.
- cmd:17, cmd:21, cmd:22, rd:19 and rd:21: no flip, no 0 and no ~0 changes the image in any of the
  four scenes (170 jobs a scene, all with the baseline image).

The equal scene draws the triangle (1062 pixels, the baseline hash) with vp4 and the background
depth both at 0.3. The depth compare is exact to the bit (E072), and the triangle's stored depth is
0.5 with vp4 at its default (E071), so a triangle drawn under equal had exactly the background's
depth, 0.3: consistent with the triangle's depth being vp4 when the vertices' z is 0. The vp4 flips
of the state-block sweep (E061), under the job's own ISP0, leave the image alone in 33 of 34 cases,
as that reading expects; only ~0 removes the triangle.

The visibility counters stayed at 0 in all 956 jobs. Under the punch-through scene they did not
count (E065).

**What it does not show.** No case varies vp4 under a depth test, so "vp4 is the viewport's z
offset" is a reading of one equality, not a measured dependence; vp5 as the z scale is not tested.
What the five words do needs more than one object, a loaded depth buffer or multisampling (E067
for transfers, E074 for multisampling). Each scene ran once.
