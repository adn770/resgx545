+++
id = "E269"
claim = "SIDEBAND bits 8:6 pick the channel a one-byte pack mode stores: in mode 8, 0 stores alpha, 1 red, 2 green, and 3 to 7 the byte that is blue in both colours run (0x40, so blue is not told apart from another source of 0x40); at each of 0 to 7 they change no pixel under CR_ISP_MSAA modes 1 and 2, on a 128x128 target, or in pack modes 4, 5, 9 and 26; sideband bit 10 dithers (one run): in pack modes 3, 4 and 5 it changes 650 to 1484 of the 4096 dwords, 650 to 2196 pixels, each one step of one or two channels off the plain value, the new value set by the plain value and the pixel's place in a 4x4 cell of x and y, and changes nothing in pack mode 0; bit 11 faults the job and bit 12 stores other values at every pixel"
unit = "pbe"
method = "probes/pbe/sideband-fields.toml and sideband-dither.toml on the laptop, linux fork with the debug option on, and the follow-up run of sideband-fields (sideband-dither ran once): the 64x64 triangle (128x128 for the multi-tile cases) with the end-of-tile program eot_plain.s and the probe's sideband, the shader writing 0x80ff8040 (three colours in sideband-dither) over the background 0xff203040; for MSAA the render command's words 10 and 16 at 0xeaa26e26 and word 13 at 0x80000001 or 0x80000002 as in E210; every pixel read back; in the 16-bit modes each dword holds two pixels, the first in bits 15:0, 32 dwords a row of 64 pixels"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["pbe-sideband-fields", "pbe-sideband-dither", "pbe-sideband-fields-followup"]
terms = ["SIDEBAND.BITS8_6", "SIDEBAND.PACKMODE", "SIDEBAND.DITHER", "CR_ISP_MSAA", "PACKMODE"]
+++

**What runs.** E030 found that bits 8:6 change no pixel of an ARGB8888 or RGB565 triangle. Here
each setting runs with the field at 0 (the control, sideband 0x200 plus the pack mode) and at 1
to 7, and the images are compared with the control's.

**Results**, pixels that differ from the field at 0:

| setting | control image | bits 8:6 = 1 to 7 |
|---|---|---|
| MSAA mode 1 | 868 triangle pixels, 3228 background | 0 each |
| MSAA mode 2 | 896 and 3200 | 0 each |
| 128x128, pack mode 0 | 4284 and 12100 | 0 each |
| pack mode 4 (ARGB1555) | 0xfe08 and 0x90c8 pairs, 2048 unwritten | 0 each |
| pack mode 5 (ARGB4444) | 0x8f84 and 0xf234 pairs | 0 each |
| pack mode 9 (whole colours, a quarter) | 120 and 904 dwords, 3072 unwritten | 0 each |
| pack mode 26 | 0x421f and 0x40c4 pairs | 0 each |
| pack mode 8 (one byte) | bytes 0x80 and 0xff: the alphas | 796 to 1024 each |

In pack mode 8 the stored bytes are, for the triangle (0x80ff8040) and the background
(0xff203040): field 0, 0x80 and 0xff (alpha); 1, 0xff and 0x20 (red); 2, 0x80 and 0x30 (green);
3, 4, 5, 6 and 7, 0x40 and 0x40. Both colours have blue 0x40, so these five values store blue,
or any other source that gives 0x40 for both colours: this run does not tell them apart. The
bytes land at the same places, four to a dword, and 3072 dwords stay unwritten in every case.

Sideband bits 10 to 12, pack mode 0: bit 10 (0x600) the control image; bit 11 (0xa00) faults the
job and the context is lost; bit 12 (0x1200) writes every pixel, none with the control's value:
0x00660000 (1459), 0x00660066 (1376), 0x00000066 (730), 0x00000000 (291) and others.
The follow-up run of sideband-fields gave every image again, but bit 12's, which differs from the
first run's in 464 pixels.

With bit 10 in pack modes 3, 4 and 5 (sideband-dither, one run; colours 0x80ff8040, 0x80818283
and 0xff7f7f7f) 650 to 1484 of the 4096 dwords differ from the image without it, for every
colour, the background too. Each dword holds two pixels (the triangle's 0xfc08 halves land on
E031's 1062 triangle pixels), so 650 to 2196 pixels change. Read by pixel (x, y), each changed
pixel is one step of one or two channels off the plain value, and in each of the nine images
every pixel of one plain value at one place (x mod 4, y mod 4) changes alike. In RGB565 the
background 0x2188 becomes 0x2187 (blue one down) at (1, 0) and (3, 2) of each 4x4 cell only, 2
pixels in 16; the triangle's 0xfc08 becomes 0xfc07 (blue one down) at the same two places and
0xfbe8 (green one down) at (0, 1), (2, 1), (0, 3) and (2, 3); 0x8410 (from 0x80818283) becomes
0x7c10 (red one down) at (1, 1), (3, 1), (1, 3) and (3, 3); 0x7bef (from 0xff7f7f7f) changes at
every pixel, to 0x7c10 (green and blue one up) and 0x83ef (red one up) in a checkerboard.
ARGB1555 and ARGB4444 show the same kind of change, alpha included (0x90c8 to 0x90c7 and
0x90a8, 0xf234 to 0xf233, 0xf224 and 0xf134, 0x8888 to 0x7788, 0x8887 and others).

**What it shows.** Bits 8:6 select the source channel of a mode that stores a single channel,
in the order alpha, red, green and, at 3, blue **[infer]**; 4 to 7 give the bytes 3 gives, and
whether that is blue or another source is open (Q046); in the modes
that store every channel, or several, they do nothing seen here, also under multisampling and on
several tiles. Bit 10 is a dither enable, as Rogue's name for it has it: an ordered pattern
over a 4x4 cell of pixels that moves each pixel to a neighbouring value of the reduced format
**[infer]**; its thresholds are not fitted here. What bit 12 stores is not decoded.
