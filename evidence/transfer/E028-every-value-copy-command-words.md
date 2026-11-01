+++
id = "E028"
claim = "Over a source holding every value of every channel, a copy answers every flip of the transfer command's words in the same class as over the plain pattern (1429 of 1429 cases), and of the 256 values of bits 31:24 of word 14 exactly the 128 with bit 25 set change the image; the data does not show, for the few words whose changed pixel counts differ between the two sources (word 0 bits 24 to 30, word 7 bit 1), that they apply no function of the value"
unit = "transfer"
method = "sweeps of probes/transfer/command-words.toml on the laptop, linux fork with the debug option on, 64x32 copy: xfer-copy (plain source), copy-every-xfer (sgxfive-test copy --every-value, 1429 cases) and values-xfer14-byte3 (256 cases)"
tiers = ["HW"]
date = "2026-11-01"
data = ["transfer-command-words"]
terms = ["transfer_cmd", "CR_REG_0400.INVERT_BYTE3"]
+++

**What runs.** The copy host builds a 64x32 source and copies it to the same place in a second
buffer. With `--every-value` the source holds every value of every channel instead of the
usual pattern. Each case flips one bit of one dword of the transfer command (or sets the
dword to 0 or to 0xffffffff), 1429 cases a table, and compares the target to what an
unflipped copy writes (baseline hash 0x88c655df5891e325 over the every-value source,
0x9b1c0be484ac0d25 over the plain one). The third table sets the high byte of word 14 to each
of its 255 other values and runs them with the baseline.

**Results.**

- The two 1429-case tables agree case for case in class: for every case the job is rejected,
  faults, hangs, is unchanged or is changed alike (unchanged 1176, changed 22, fault 65, hang
  6, rejected 159 in both).
- In 13 of the 22 changed cases the pixel count is the same in both sources. In the other nine
  it differs a little: word 0 with bits 24 to 30 flipped or set to 0 (eight cases) changes 2047
  pixels over the plain source and 2040 over the every-value one, and word 7 bit 1 changes 2047
  and 2044. In these the first pixel written differs from the expected one in both sources, and
  no fixed relation to the source value is visible in the first pixel alone.
- Word 14 (the word that loads 0x0400, E029): over the every-value source the 128 values of
  bits 31:24 that have bit 25 set all give one target hash, 0x680d053209803325, and the other
  127 values and the baseline give the baseline's hash 0x88c655df5891e325. No other flip of
  word 14 changes the image.
- Counters: 0 of 1429 cases counted in every table.

**Not shown.** The sweeps flip bits one at a time and set 0 and 0xffffffff, so they do not
cover a word whose effect needs two bits together. The two groups with differing counts are
words that change where or how the copy reads or writes, not shown to apply a function of the
pixel's value; the data does not exclude one either, and no run reads the target's pixels
against the every-value source to check.
