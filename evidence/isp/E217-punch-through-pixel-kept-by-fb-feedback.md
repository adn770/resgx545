+++
id = "E217"
claim = "In the five-copy punch-through pass a pixel is kept only when the pt phase ends in atst8 with fb, a passing alpha test and 0xe001 in src1 (~0 keeps it too, with the depth always winning): nfb, nop.end and ten other src1 words keep none, and a failing test shows the copy behind; the depth result (1062 pixels of the nearest copy, 36 of the next) is the same without pcoeff, without the source-34 iteration and without both, and moves between runs only when pcoeff runs with that iteration missing, or with a source register unset"
unit = "isp"
method = "probes isp-punch-through-pt2-punch, -pt2-punch-src1, -pt2-punch-srcs, -pt2-punch-discard, -pt2-punch-pcoeff-only, -pt2-punch-src34-only, -pt2-punch-neither and -pt2-punch-iter1 of probes/isp/punch-through.toml on the laptop, linux fork with the debug option on: five copies of the 64x64 triangle at depths 0 to 4/16 in the punch-through pass (render block word 1 = 0x08400200), every pixel read back, each probe fenced by a baseline render before and after; two runs (the second is the follow-up run)"
tiers = ["HW"]
date = "2026-11-01"
data = ["isp-punch-through", "isp-punch-through-followup"]
terms = ["FEEDBACK_CTL.ENABLE", "FEEDBACK_CTL.KEEP", "FEEDBACK_CTL.DEPTH_ALWAYS", "ISP0.PASS_TYPE", "DOUTI0.LAST_ITER", "DOUTU1.WAIT_ITER"]
+++

**What runs.** The scene of E083. The pixel program has a pt phase and a colour phase; the colour
phase writes the copy's depth as the colour, so a pixel's value names the copy that drew it
(background 0xff203040, depth 0 = 0x00000000, 1/16 = 0x3d800000, 1/8 = 0x3e000000, 1/4 =
0x3e800000). The pt phase ends in one instruction: atst8 with fb or nfb, or nop.end. Its src1 is
0xe001 and src2 0xee00 unless a probe varies them; the pds program iterates source 1 (the copy's
depth) and, in the full shader, source 34 (three components) with pcoeff handing them to the ISP.
Ablations drop pcoeff, drop the source-34 iteration, drop both, or replace the iteration by one
without a fetch.

**Results.** Full shader, atst8 with fb: 1062 pixels of depth 0 and 36 of 1/16 (2998 background);
with nfb or with nop.end: none. Both runs.

- src1 varied (src2 0xee00; this probe and the next two use the variant without pcoeff and
  without the source-34 iteration, which gives the same image as the full shader, see the last
  bullet): 0xe001 gives the image above; ~0 gives 1074 pixels of 1/4 and 24 of 1/8 (the last
  copy, as if the depth test were always); 0, 1, 2, 3, 0xf, 0xe000, 0xe002, 0x100, 0x10001 and
  0x80000001 give none. The same in both runs.
- src1 and src2 set to the same register: 0xee00 in both gives none, 0xe001 in both gives the
  image above; with the register never written the first run gives 247 pixels of depth 0, 18 of
  1/16 and 13 of 1/4 (3815 background), and the follow-up run none.
- Failing alpha tests (the compare function in src2 bits 15:13): one that copy 0 fails gives the
  1/16 copy on 1098 pixels; "less than 0x3e", which copies 2 to 4 fail, gives the image above;
  "never" gives none. The same in both runs.
- Ablations of the full shader, fb: no pcoeff but the source-34 iteration, no pcoeff and no
  source-34 iteration, and no pcoeff with a fetchless iteration all give 1062 and 36, in both runs.
  With pcoeff and no source-34 iteration the first run gives 1054 pixels of depth 0, 36 of 1/16 and
  8 of 1/8, and the follow-up run 1046, 36 and 8 of 1/4.

**Not shown.** That the depth decision is reproducible only with pcoeff and the iteration it
reads is not what the data show: three variants without pcoeff, one of them without the iteration
too, repeat the full shader's image in both runs. The two variations are one where pcoeff reads
values the pds program did not iterate, and one where a source register of the test was never
written; that those read stale state is a reading, not tested. Which src1 bits keep a pixel is
E218's. The alpha function's byte is not varied beyond three cases. Two runs, each probe once.
