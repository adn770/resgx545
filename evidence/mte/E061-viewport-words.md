+++
id = "E061"
claim = "The state block's words vp0-vp3 are IEEE singles that scale and place the 64x64 triangle: each pair acts alike on the two axes, the offset words (vp0, vp2) leave 348 triangle pixels at 0 and the scale words (vp1, vp3) leave none, and vp3 at -32.0 gives the triangle's mirror image; which pair is x and which is y rests on that one mirror, and vp4, vp5 change nothing in the flat triangle except that a NaN removes it"
unit = "mte"
method = "sweep of every word of the 64x64 triangle's state block (probes/vdm/stream-words.toml, sweep vdm-stream-words): a flip of each bit, 0 and ~0 of each word, 1055 cases, on the laptop with the linux fork and the debug option on; the sweep ran twice, the second time as the follow-up run"
tiers = ["HW"]
date = "2026-11-01"
data = ["vdm-stream-words", "vdm-stream-words-followup"]
terms = ["VIEWPORT.X_OFFSET", "VIEWPORT.X_SCALE", "VIEWPORT.Y_OFFSET", "VIEWPORT.Y_SCALE"]
+++

**What runs.** The triangle job writes a state block of 18 words; the sweep poked each bit of each
word (`blk:N^=1<<b`) and the values 0 and 0xffffffff, one job per case, a fresh context each, and
classified the image against the unpoked job (1062 triangle pixels of 4096). In the job the words
`blk:6` to `blk:9` (vp0 to vp3) hold 32.0 (0x42000000) and `blk:10` (vp4) holds 0.5 (0x3f000000).
The first run and the follow-up run of the whole sweep gave the same class and the same image hash
for `blk:6` to `blk:11`.

**Results.** Read as IEEE singles, the flips of the four words move and scale the triangle in the
way a viewport does. The tables give the triangle pixels left in the target and the pixels that
differ from the unpoked image (936 when the triangle is gone):

| flip of vp0 (`blk:6`) | value | triangle pixels | pixels differing |
|---|---|---|---|
| bit 21 | 40.0 | 1062 | 532 |
| bit 22 | 48.0 | 1026 | 1059 |
| bit 23 | 64.0 | 714 | 1465 |
| bit 24 | 128.0 | 0 | 936 |
| bit 25 | 2.0 | 409 | 1116 |
| bit 30, and the value 0 | about 0 | 348 | 1113 |
| bit 31, and ~0 | negative, NaN | 0 | 936 |

The triangle keeps its 1062 pixels while it moves inside the target, loses them as it leaves, and 0
does not remove it: 348 pixels stay. Flips of bits 0 to 8 leave the image unchanged; bits 9 to 18
change edge pixels only (0 pixels beyond the tolerance of the image check, 1098 down to 1062
triangle pixels), and bits 19 to 21 move 45, 199 and 532 pixels.

vp2 (`blk:8`) gives the same triangle-pixel and differing-pixel counts as vp0 for every flip from
bit 19 up. The image differs (a different hash) whenever a triangle pixel is left; the 6 flips that
remove the triangle (bits 24, 26, 27, 28, 29 and 31) give the same empty image in both words. vp1
and vp3 (`blk:7`, `blk:9`) pair the same way from bit 22 up, bar the sign bit (bit 21 gives 208 and
210 differing pixels):

| flip of vp1 (`blk:7`) | value | triangle pixels | pixels differing |
|---|---|---|---|
| bit 21 | 40.0 | 1344 | 208 |
| bit 22 | 48.0 | 1594 | 481 |
| bit 23 | 64.0 | 1840 | 771 |
| bit 24 | 128.0 | 1920 | 929 |
| bit 25 | 2.0 | 60 | 895 |
| bit 30, the value 0, ~0 | about 0, NaN | 0 | 936 |
| bit 31 | -32.0 | 1098 | 608 |

The triangle widens as the scale grows (1062 to 1344, 1594, 1840) and shrinks below it; at 0 nothing
is drawn. vp3 at -32.0 gives 1062 triangle pixels and 612 differing pixels, which is the figure for
the triangle flipped upside down in the unpoked job's own check ("612 if flipped"), and the same
image hash as the second sweep of E062, where vp3 is poked to -32.0 on purpose. vp1 at -32.0 gives
1098 pixels and 608 differing: a mirror in the other axis, of a triangle that is not symmetric.

The four words differ in what their low mantissa bits do, not in kind: vp0 and vp2 have 9 unchanged
flips, vp1 and vp3 have 10. vp4 and vp5 (`blk:10`, `blk:11`): 33 of 34 cases leave the image as it
is; only ~0 (NaN) removes the triangle.

**What this does not show.** Triangle pixel counts cannot tell x from y: vp0 and vp2 give equal
counts and, where a triangle pixel is left, different images, as an x offset and a y offset of a
triangle of this shape would, and so for the scales. The only case that fixes an axis is vp3 at
-32.0 giving the upside-down triangle. That the offset words add and the scale words multiply is
read from 0 (the offsets leave a triangle, the scales do not) and from the growth; no case sets an
offset and a scale together. The flat triangle's depth does not show vp4 and vp5 either (E066).