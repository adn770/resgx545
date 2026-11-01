+++
id = "E068"
claim = "Among five scenes of five overlapping copies of the triangle (depth always, less, translucent less, translucent always, punch-through less) only 0x04dc bit 1 acts: with it set (values 2 and 7 tried) the punch-through scene hangs and the other four are unchanged; every other implemented bit of 0x0418, 0x04dc, 0x04e8, 0x0520 and 0x0800, and 0 and ~0 of each, gives its scene's baseline image in all five scenes (348 of 350 cases); why the punch-through scene hangs is not shown"
unit = "isp"
method = "the hand script render-only-registers.sh of probes/isp/render-only-registers.toml (function depth_scenes) with the probe programs staged: each of five scenes of the isp/depth-test probes taken twice unpoked, then 70 kernel pokes of render-details words (rd:26, rd:21, rd:51, rd:19, rd:22), and the scenes' own pixels from probes/isp/depth-test.toml, on the laptop with the linux fork and the debug option on; one run"
tiers = ["HW"]
date = "2026-11-01"
data = ["isp-render-only-registers", "isp-depth-test"]
terms = [
    "CR_ISP_LINE_SAMPLE_POS", "CR_ISP_REG_04DC", "CR_ISP_REG_04E8", "CR_ISP_SAMPLE_POS",
    "CR_REG_0800", "ISP0.PASS_TYPE",
]
+++

**What runs.** Five copies of the triangle, at clip z 0 and 1/16 to 4/16, each 1/16 pixel
further, are drawn in that order; each pixel is coloured with the z of the copy that won it. The
five scenes differ in ISP0: depth always without depth write (0x01d00200), less with write
(0x00400200), the same in a translucent pass (0x02400200), translucent always without write
(0x03d00200) and less with write in a punch-through pass (0x08400200). Each scene ran twice
unpoked (the two hashes agree in every scene, and the five scenes differ from each other), then
with one kernel poke per job: a xor of bit 0 of 0x0418; bits 0, 1 and 2 of 0x04dc; bits 0 and 8
of 0x04e8; each of the 32 bits of 0x0520; the 22 implemented bits of 0x0800 (0 to 5 and 8 to 23);
and 0 and ~0 of each of the five. That is 70 pokes a scene and 350 in all. The script prints a
refusal of a poke and a case only when its image differs from the baseline.

**Results.** The loop printed no refusal of any poke. Only two cases differ, both in the last scene,
the punch-through one: `rd:21^=0x2` and `rd:21=0xffffffff`, each of which hangs the job (the context
is lost). Both set bit 1 of 0x04dc. The same two pokes leave the other four scenes at their
baseline, and the other 68 pokes leave the punch-through scene at its.

The scenes alone (from the depth-test probes, same programs): with depth always, no write, the
last copy wins every pixel (1074 pixels at z 0.25, 24 at 0.125); with depth less and write, the
nearest copy wins (1062 pixels at z 0 and 36 at 1/16); the translucent pass with less gives the
same as the opaque one and the translucent pass with always gives the same as always; the
punch-through pass with less gives the always result, the last copy wins (1074 and 24).

**What it does not show.** Of the values of 0x04dc, only 0, 1, 2, 4 and 7 were tried (single-bit
flips of its default 0 give 1, 2 and 4, and ~0 is 7 in its three implemented bits); that every value
with bit 1 set hangs is not tested here. The hang says nothing on its own about what bit 1 waits
for. The scenes have no shader with a punch-through phase. The script's error output holds five
"Invalid argument" lines from the kernel's poke file, printed after the last section; the data do
not say which section's pokes they come from, so "no refusal" rests on the depth-scene loop's own
printout, which reports a refused poke and printed none. One run.