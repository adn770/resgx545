+++
id = "E426"
claim = "With a source row whose weighted sum S sits at cut x 1024 + k for every even k from -16 to 16 (102 cases, twice), the band of the luma key starts at least 16 below the low cut for the cuts 119, 120 and 122 (all of the 8 sums below the cut inside the band, 2 of 2 runs, three cuts), and at the high cut five pixels with S 1000 to 1016 above cut x 1024 are outside the band where others up to 1016 are inside, so the comparison is not on S alone"
unit = "texture"
method = "probes/texture/luma-ramp.toml (luma-ramp.sh) on the laptop (direct cable), linux fork f1fad0ed9d0e with the debug option on: sgxfive-test copy --width 64 --height 1 --ramp b=B --ramp-base 0xffRRGG00 with T0 bit 31 and the three luma-key words loaded (E275's weights 262, 514, 100 and offset 33), the red and green of each case chosen so that pixel 0 has S = cut x 1024 + k, low cuts 119, 120 and 122 (low byte = the cut, threshold 128) and high cuts (low byte 0, threshold = the cut), k = -16 to 16 in steps of 2; 204 copies, each 64 pixels read back; analysed against tools/usse-asm/tex_words.py's band"
tiers = ["HW", "infer"]
date = "2026-11-07"
data = ["texture-luma-ramp"]
terms = ["CR_TPU_LUMA_KEY_ALPHA", "CR_TPU_LUMA_KEY_RG", "CR_TPU_LUMA_KEY_B_OFFSET"]
+++

**What ran.** S = 262 R + 514 G + 100 B + 512 x 33 (E275) is even for every colour, so odd
distances from a cut cannot be made; the pixels after the first of a row have S larger by 100 a
pixel. Every pixel's RGB is the source's. The band model of E275 (alpha_below where low <= (S + r)
>> 10 and S >> 10 <= threshold) was checked on all 13056 pixels.

- Low cut. For the cuts 119, 120 and 122 the pixels with S = cut x 1024 + k, k = -16, -14, ..., -2,
  are inside the band (alpha_below) in 2 of 2 runs: 8 pixels a cut in a run, 16 a cut and 48 in all
  counting both runs, where the model with r = 0 puts them outside. With r from 16 to 35 (E275
  fitted 12 to 35) no low-cut pixel misfits; the pixels at k = 0 to 16 are inside as the model says,
  including S = cut x 1024 + 4, which E275 found outside at the cuts 119 and 122. - High cut (low
  byte 0, threshold = the cut). Of 6528 pixels, 10 (5 pixels, 2 runs) with S 1000 to 1016 above cut
  x 1024 are outside the band, where the model puts them inside: T = 119: S - cut x 1024 = 1006 (R,
  G, B = 22, 193, 10), 1014 (75, 166, 10) and 1016 (24, 192, 10); T = 120: 1010 (22, 195, 10); T =
  122: 1000 (224, 96, 10). Pixels with S 1004 (73, 167, 10) and 1008 (228, 88, 10) at T = 119, and
  1016 (126, 142, 10) at T = 120, are inside: so two pixels with S on either side of one that is
  outside are inside, and the result is not a function of S.

**What it shows.** The low end of the band counts sums at least 16 below low x 1024 as inside, in
every repetition and for three cuts; E275's two misfitting pixels at the low cut do not recur at
the same S with other colours. The high end does not follow the weighted sum alone: five
particular colours near it fall outside. A per-channel rounding is a reading [infer]; its form is
not found.

**What it does not show.** The roles of bits 31:16 of the alpha word and of the offset's
precision, and the high cut at other cuts. Q008 stays open.
