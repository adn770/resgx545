+++
id = "E038"
claim = "In a UYVY copy through colour-space set 0, bit 0 of the transfer word that loads 0x0848 drops the luma offset and bit 2 reads U and V as signed bytes, the value 0xffffffff doing both; its other bits change nothing, and neither the words that load 0x0860 to 0x0868 nor any bit of colour-space set 1 changes a copy here; each model gives the target's hash"
unit = "texture"
method = "sweeps of probes/texture/tpu-csc.toml (copy-uyvy-csc1: xfer:23 to xfer:28, 205 cases; copy-tpu-group and copy-uyvy-tpu-group: xfer:29 to xfer:31, 103 cases each) on the laptop, linux fork with the debug option on: the UYVY copy of E037 over the every-value source, set 0 loaded as the BT.601 words, one run"
tiers = ["HW"]
date = "2026-11-01"
data = ["texture-tpu-csc"]
terms = ["CR_TPU_YUV_CSC_INPUT", "CR_TPU_YUV_CSC_INPUT.Y_NO_OFFSET", "CR_TPU_YUV_CSC_INPUT.UV_SIGNED", "CR_TPU_LUMA_KEY_RG", "CR_TPU_LUMA_KEY_B_OFFSET", "CR_TPU_LUMA_KEY_ALPHA", "T1.TEXTYPE"]
+++

**What runs.** The UYVY copy of E037 (baseline hash 0xb6067a95fa98de2d). Each case flips a bit
of one transfer word, or sets it to 0 or 0xffffffff, with the word's own load flag raised:
xfer:23 to xfer:27 are colour-space set 1, xfer:28 loads 0x0848, and xfer:29 to xfer:31 load
0x0860, 0x0864 and 0x0868 (the three words of E039), the last three also over the plain
every-value copy.

**Results.**

- Set 1 (xfer:23 to xfer:27, 34 cases each): every case leaves the target identical to the
  baseline.
- xfer:29 to xfer:31: all 102 cases of each table (the plain copy and the UYVY copy) leave
  the target identical to the baseline.
- xfer:28: flipping bit 0 changes all 2048 pixels (hash 0xac992291af12e7fd), bit 2 changes all
  2048 (0x5c401bf0949f20b5), and 0xffffffff changes all 2048 (0x9d328c00dee55005); every other
  single bit and the value 0 give the baseline's hash.
- Models of E037, computed on the plain source's bytes with the same coefficients and the
  FNV-1a hash the tool prints: without the luma offset (Y in place of Y - 16) the hash is
  0xac992291af12e7fd, which is bit 0's; with U and V read as signed bytes (U - 256 for U of
  128 or more, in place of U - 128) and the offset kept it is 0x5c401bf0949f20b5, which is
  bit 2's; both together it is 0x9d328c00dee55005, which is 0xffffffff's. So the three hashes
  are exactly the three models' images.

**Not shown.** What a signed reading does to the matrix other than at these coefficients; the
other bits of the word are inert in this job only. The words of 0x0860 to 0x0868 act under
T0 bit 31 (E039).
