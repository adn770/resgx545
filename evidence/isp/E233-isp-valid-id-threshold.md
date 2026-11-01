+++
id = "E233"
claim = "CR_ISP_CTL bits 5:0 act as a threshold that the opaque triangle's ISP word 1 bits 31:26 are compared with: over the 49 pairs of the thresholds 0, 1, 2, 3, 5, 32, 63 against the values 0, 1, 2, 3, 5, 32, 63 (46 run as pairs, the other 3 by the free-bit probes of ISP1 bits 26, 27 and 31) the triangle is drawn exactly when the ISP1 value is at least the threshold; and with the threshold at 1, setting any one of ISP1 bits 26 to 31 draws it again, while none of the other free bits of the presence word, ISP word 0 or ISP word 1 tried does (the presence word's bit 27 hangs the job)"
unit = "isp"
method = "the probes isp-valid-id-vid-* of probes/isp/valid-id.toml, the plain 64x64 triangle (pix_op.s, green, ISP0 0x01d00200, ISP1 0x000010f0): vid-c<C>-i<I> with render command word 12 = 0x000f0100 | C and ISP word 1 bits 31:26 = I (46 pairs), and vid-presence-*, vid-isp0-* and vid-isp1-* with command word 12 = 0x000f0101 and one free bit of the state block flipped; one probe a case, fenced, on the laptop with the linux fork and the debug option on, one run (no follow-up run)"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["isp-valid-id"]
terms = ["CR_ISP_CTL", "CR_ISP_CTL.VALID_ID", "ISP1", "ISP1.VALID_ID", "ISP0"]
+++

**What runs.** The control `vid-ctl0` (command word 12 = 0x000f0100, threshold 0) draws the
triangle and `vid-ctl1` (0x000f0101, threshold 1) removes it (E232). The pairs: the thresholds
C = 0, 2, 3, 5, 32 and 63 against I = 0, 1, 2, 3, 5, 32 and 63, and C = 1 against 0, 3, 5 and 63
(46 of the 49 pairs of the seven values). The free-bit probes flip, with the threshold at 1:
presence word (state word 0, 0x0000df43) bits 16 to 31; ISP word 0 bits 10, 12, 13, 14, 19 and
28 to 31; ISP word 1 bits 13 to 31.

**Results.** One run; every baseline before and after a probe was clean.

- All 46 pairs agree with "drawn exactly when I >= C": a case draws the 1062 pixels or none, and
  the cases that draw are those with I >= C. Rows C = 0 draw at every I; C = 1 at I = 3, 5 and
  63 of the pairs run; C = 63 only at I = 63. The 3 pairs not run as such, C = 1 with I = 1, 2 and
  32, are the free-bit probes vid-isp1-b26, -b27 and -b31 (ISP1 0x040010f0, 0x080010f0 and
  0x800010f0 with command word 12 = 0x000f0101 on the same triangle): all three draw the 1062
  pixels, so all 49 pairs fit I >= C.

| C \ I | 0 | 1 | 2 | 3 | 5 | 32 | 63 |
|-------|---|---|---|---|---|----|----|
| 0 | D | D | D | D | D | D | D |
| 1 | . | D* | D* | D | D | D* | D |
| 2 | . | . | D | D | D | D | D |
| 3 | . | . | . | D | D | D | D |
| 5 | . | . | . | . | D | D | D |
| 32 | . | . | . | . | . | D | D |
| 63 | . | . | . | . | . | . | D |

  D drew all 1062 pixels, . none; D* is a free-bit probe below.
- With the threshold at 1, each of ISP word 1 bits 26, 27, 28, 29, 30 and 31 set alone draws the
  triangle again. Not drawn: the presence word's bits 16 to 26 and 28 to 31, ISP word 0's bits
  10, 12, 13, 14, 19 and 28 to 31, and ISP word 1's bits 13 to 25. The presence word's bit 27
  hung the job (job hung, context lost); the baseline afterwards was clean.

**What it shows.** Bits 5:0 of CR_ISP_CTL are a validation threshold and ISP word 1 bits 31:26
the object's own value, compared unsigned, for the seven values run. Calling the pair a
validation value is our reading **[infer]**. A value below the threshold makes the ISP drop
the object. E235 is about the pass types the check applies to.

**Not shown.** Every value outside the seven: a rule over all 6-bit values is an extrapolation.
Combinations of free bits. What the check does for objects of other pass types is E235's. The data
come from one run.
