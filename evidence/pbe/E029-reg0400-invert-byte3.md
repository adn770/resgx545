+++
id = "E029"
claim = "Bit 25 of the word that loads 0x0400 changes every pixel a fill, a copy or a triangle writes, the first pixel of each reading with bits 31:24 inverted (0xff336699 to 0x00336699, 0xa5000000 to 0x5a000000, 0xff203040 to 0x00203040); no other bit of the word changes a pixel, and over the every-value source exactly the 128 values of bits 31:24 with bit 25 set change the image"
unit = "pbe"
method = "sweeps on the laptop, linux fork with the debug option on: probes/transfer/command-words.toml (xfer-fill, xfer-copy, copy-every-xfer, values-xfer14-byte3; word 14 of the transfer command, 64x32) and probes/render/command-words.toml (render-command-words, word 11 of the render command, 64x64 triangle)"
tiers = ["HW"]
date = "2026-11-01"
data = ["transfer-command-words", "render-command-words", "render-command-words-followup"]
terms = ["CR_REG_0400", "CR_REG_0400.INVERT_BYTE3", "transfer_cmd.reg_0400", "hw_render_details.reg_0400"]
+++

**What runs.** The transfer command's word 14 and the render command's word 11 are the words
that load the register 0x0400 (E028 lists the transfer tables; the render table flips every
bit of every word of the triangle's render command). Each case flips one bit of the word, or
sets 0 or 0xffffffff, and compares every pixel of the target with the unflipped job's.

**Results.**

- Fill: flipping bit 25 (0x02000000) of word 14 changes all 2048 pixels; the first reads
  0x00336699 where 0xff336699 was written. Target hash 0x333a1220c0b2a325 against the
  baseline's 0xb60c6095080bd325. Setting 0xffffffff gives the same hash.
- Copy: the same, 2048 pixels, 0xa5000000 becomes 0x5a000000, hash 0x813b8ce308e98425
  against 0x9b1c0be484ac0d25, in the plain source; the every-value source gives the baseline
  0x88c655df5891e325 against 0x680d053209803325.
- Triangle: flipping bit 25 of word 11 of the render command changes all 4096 pixels of the
  64x64 target, background and triangle alike, the first from 0xff203040 to 0x00203040; hash
  0x25e3b1ba58ea2cc5 against the baseline's 0x99385a04ee01c585. 0xffffffff gives the same hash.
- No other bit of either word changes a pixel in any of the jobs: every other flip, and the
  value 0, leaves the image identical.
- Every-value copy, bits 31:24 of word 14 set to each of 255 values: the 128 values with bit
  25 set give one hash and the 127 others the baseline hash. Bits 24 and 26 to 31 do nothing
  whatever the pixel's value.
- Each transfer job ran once per case; the render table ran twice (the second is the follow-up
  run) with the same triangle hash for the bit 25 flip and for 0xffffffff. The visibility counters
  counted in none of these cases.

The first pixel shows the effect on bits 31:24 only: its other three bytes are the written
ones in every case above.

**Not shown.** Which unit of the chip performs the inversion; the data sees only the target.
That the effect holds for pack modes other than ARGB8888 (E031 covers the modes, with the
register at its default).
