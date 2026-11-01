+++
id = "E251"
claim = "CR_REG_0400 takes bit 25 and bits 11:0"
unit = "pbe"
method = "probes/platform/register-widths.toml on the laptop, linux fork with the debug option on: regwidth.c through /dev/mem writes each register with all ones, its prior value, zero and its prior value, reading after each write, with the firmware live and idle, in ten batches with a debugfs fill and the triangle checked after each; two runs"
tiers = ["HW"]
date = "2026-11-02"
data = ["platform-register-widths"]
terms = ["CR_REG_0400"]
+++

**What runs.** The register census of E246, batch 5.

| register | name | value before | bits that took a write | width | read 1 after zero |
|---|---|---|---|---|---|
| `0x0400` | `CR_REG_0400` | `0x00000080` | 25, 11:0 | 13 | - |

Besides bit 25 (byte 3 inverted, E028), the register takes 12 bits, 11:0; it held 0x80, bit 7. So 12
bits are unexplained, not 31.

**Not shown.** What bits 11:0 control (Q044).
