+++
id = "E045"
claim = "Writing every value 0 to 63 into register 0x0a78 before a triangle job changes nothing, and the same into 0x0abc hangs the job exactly for the values whose bits 4:1 are all zero (0, 1, 0x20, 0x21); every other value of 0x0abc gives the baseline image, and every value read back as written"
unit = "pds"
method = "sweep table probes/platform/untouched-registers.toml (kreg-values: 64 values of each of the two registers, written through the kernel fork's debugfs kreg) on the laptop, linux fork with the debug option on: 64x64 triangle job, one run of each case, fresh context each"
tiers = ["HW"]
date = "2026-11-01"
data = ["platform-untouched-registers"]
terms = ["CR_PDS_REG_0A78", "CR_PDS_REG_0ABC", "CR_PDS_REG_0ABC.BITS4_1"]
+++

**What runs.** Before each triangle job the script writes one value (0 to 0x3f, the six bits the
registers implement) into register 0x0a78 or register 0x0abc through debugfs, reads the register
back, and runs the job. The registers held 0x2c (0x0a78) and 0xe (0x0abc) before the writes. The
baseline is the unpoked job (1062 triangle pixels, 3034 background, hash 0x99385a04ee01c585). 128
cases and the baseline.

**Results.**

- Every one of the 128 writes reads back as written, so the six bits are implemented in both.
- 0x0a78: all 64 values complete with the baseline image.
- 0x0abc: 60 values complete with the baseline image; 0, 1, 0x20 and 0x21 hang the job (the
  tool times out, the context is lost and the target keeps the sentinel). These are the values
  whose bits 4:1 are all zero; bit 0 and bit 5 do not matter, and the unwritten value 0xe holds
  bits 4:1 = 7.
- The visibility counters stayed at 0 in all 129 runs.

**Not shown.** Only the triangle job, only the six bits, and a single run of each value. The
job's time was not measured here. The same two registers swept bit by bit around a fill, a copy
and a triangle are in E026.
