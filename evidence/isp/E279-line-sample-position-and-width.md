+++
id = "E279"
claim = "CR_ISP_LINE_SAMPLE_POS bit 0 moves the sample of a line's span test: a column x is covered when x + 1/2 (1) or x + 1 (0) lies in the line's span [start, end), and at both values its rows are those whose centre r + 1/2 lies within half the line's width of the line's y at x + 1/2, ties to the upper row; this fits all 32 cases of both runs, 6 of the 8 cases moved in x and y and all nine widths with no pixel missed [infer: one x-major line]; triangles never read the register; ISP1.LINE_WIDTH is the width in sixteenths of a pixel (0x10 one pixel, 48 pixels for the 48-column line, 0x08 24, 0x20 96; one run)"
unit = "isp"
method = "probes/isp/line-sample.toml on the laptop, linux fork with the debug option on: the line from vertex 0 to vertex 1 of the triangle job, (8, 8) to (56, 20) on a 64x64 target (index list type 1, two indices, VDM word 2 0x84c00002; ISP word 0 0x01d08200, object type 1), moved by the viewport's x offset (state-block word 6) in sixteenths and by x and y together in quarters, with render-details word 26 (it loads 0x0418, a kernel poke) at 1 and 0; the triangle at four sub-pixel offsets at both values; ISP word 1 bits 15:8 at nine values; every pixel read back and scored by isp_words.py lines against the line model; the sixteenths twice, the rest once"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["isp-line-sample"]
terms = ["CR_ISP_LINE_SAMPLE_POS", "hw_render_details.isp_line_sample_pos", "ISP0.OBJ_TYPE", "ISP1.LINE_WIDTH"]
+++

**What runs.** The probes `isp-line-sample-x` (and `-x-r2`) draw the line with the viewport's x
offset at 32 + k/16 for k = 0 to 15, with 0x0418 at 1 (the job's value) and at 0: 32 cases each.
`-xy` moves x and y together by 0, 1/4, 1/2 and 3/4 at both values; `-tri` draws the triangle
moved by 0, 5/16, 1/2 and 15/16 in x and y at both values; `-width` sets ISP word 1 bits 15:8 to
0, 4, 8, 0x10 (the job's), 0x18, 0x20, 0x40, 0x80 and 0xff with 0x0418 at 1. These three ran
once.

`isp_words.py lines` scores each line case against the line model (`line_cover`): a column x is
covered when its span sample, x + 1/2 at 1 and x + 1 at 0, lies in [start, end); in it, the rows
r whose centre r + 1/2 lies in [y - w/2, y + w/2), y the line's y at x + 1/2 and w the width
over 16, so that a centre exactly half a pixel from the line takes the upper row.

**Results.** The line covers 48 pixels in every case of `-x`, one per column, four columns a row
from row 8 to row 19. Only the columns at its ends move, alike in both runs:

| x offset | 0x0418 = 1 | 0x0418 = 0 |
|---|---|---|
| 0 | columns 8-55 | columns 7-54, column 7 in row 7 |
| 1/16-7/16 | columns 8-55 | columns 8-55 |
| 8/16 | columns 8-55, column 8 in row 7 | columns 8-55, column 8 in row 7 |
| 9/16-15/16 | columns 9-56 | columns 8-55, column 8 in row 7 |

The line model misses no pixel of the 32 cases of either run. The far-corner reading (the row
whose r + 1 lies within half a pixel of the line's y at x + 1) misses 576 pixels in each run, in
all 16 cases at 0: at x + 1/16, column 8 sits in row 8, while the line's y at x = 9 is 8.23,
which puts it in row 7.

Moving x and y together by quarters gives, at both values, one image for 1/4 and 1/2 and others,
one pixel apart at the ends, for 0 and 3/4. The line model fits six of the eight cases; at 3/4
it misses 2 pixels at each value, column 8 drawn and 56 not at 1, the other way round at 0, as
the far-corner reading does too. The triangle gives the same image at 0 and 1 at each
of its four offsets (1062, 1074, 1062 and 1062 pixels). `-width`:

| LINE_WIDTH | 0 | 0x04 | 0x08 | 0x10 | 0x18 | 0x20 | 0x40 | 0x80 | 0xff |
|---|---|---|---|---|---|---|---|---|---|
| pixels | 0 | 12 | 24 | 48 | 72 | 96 | 192 | 384 | 768 |

The line model predicts all nine images pixel for pixel.

**What it shows.** With 0x0418 at 1 a column x is covered when x + 1/2, the pixel's centre, lies
in [start, end): the first column steps from 8 to 9 once the start passes 8 + 8/16, and the last
from 55 to 56 once the end passes 56 + 8/16. At 0 the span's sample is x + 1: the start at 8
takes column 7, and from 8 + 1/16 on column 8. The rows do not follow it: at both values the row
is the one whose centre r + 1/2 lies within half a pixel of the line's y at the column's centre,
the upper one on a tie, so at 8 + 8/16 the line's y at column 8's centre is 8 exactly and the
column takes row 7, and with the start at 8 and bit 0 clear column 7's centre gives y = 7.875
and row 7. So bit 0 of 0x0418 moves the sample of the line's span test by half a pixel, or
shifts the span by half a pixel, and nothing shows a sample at y + 1 [infer: one x-major line];
triangles do not read it. This reproduces the notebook's line-sample record and its
cross-reference, and narrows its reading of 0.

The pixel counts are 48 x LINE_WIDTH / 16 up to 0x80 (and 768 = 48 x 16 at 0xff): the field is
the line's width in sixteenths of a pixel, measured across the line's minor axis, rows taken
by their centres as above; 0 draws nothing [infer: one x-major line, one run]. Points are not
drawn by these probes.
