+++
id = "E122"
claim = "Of the three registers the init script sets once, 0x0810 implements bit 0 only, 0x0814 bits 16:0 and 0x0818 bits 10:0; a fill with any of them written to 0, to any single bit or with any one of bits 0 to 15 of its init value flipped completes exactly as with the init values"
unit = "platform"
method = "probes/platform/init-registers.toml: each register written with all ones and with zero through the debug group's kreg and read back, then restored; probes/platform/init-register-jobs.toml: a sweep of 49 values a register around a 64x32 fill; on the laptop, linux fork with the debug option on"
tiers = ["HW"]
date = "2026-11-01"
data = ["platform-init-registers", "platform-init-register-jobs"]
terms = []
+++

**What runs.** The script loads and boots the firmware, reads the three registers, then for
each writes all ones, zero and its init value back, reading after each write. The sweep writes
each register, around a fill, with 0, with each single bit 0 to 31 and with its init value with
one of bits 0 to 15 flipped: 49 cases a register, 147 in all, against a baseline fill with the
init values.

**Readback.** At boot the registers hold the init values (`0x1`, `0xffff`, `0x7ff`, E006).
Written with all ones, `0x0810` reads `0x1`, `0x0814` reads `0x1ffff` and `0x0818` reads
`0x7ff`; written with zero, each reads 0; written with its init value, each reads it back. So
`0x0810` holds one bit, `0x0814` seventeen, one more than the init script sets, and `0x0818`
eleven, all of which the init script sets.

**Fills.** All 147 cases complete with the baseline's target (hash `0xb60c6095080bd325`):
none faults, hangs or changes a pixel. The flips the register keeps are exactly its
implemented bits: of bits 0 to 15, `0x0810` keeps bit 0 only, `0x0814` all sixteen and
`0x0818` bits 0 to 10. No job changes a register's value, and the ISP visibility counters stay
at zero throughout.

This shows which bits exist and that a single fill does not depend on them. It does not show
what they control: copies, triangles and loads large enough to reach a limit were not run with
the registers narrowed (Q001).
