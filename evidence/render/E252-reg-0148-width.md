+++
id = "E252"
claim = "CR_REG_0148 takes bit 0 only"
unit = "render"
method = "probes/platform/register-widths.toml on the laptop, linux fork with the debug option on: regwidth.c through /dev/mem writes each register with all ones, its prior value, zero and its prior value, reading after each write, with the firmware live and idle, in ten batches with a debugfs fill and the triangle checked after each; two runs"
tiers = ["HW"]
date = "2026-11-02"
data = ["platform-register-widths"]
terms = ["CR_REG_0148"]
+++

**What runs.** The register census of E246, batch 7.

| register | name | value before | bits that took a write | width | read 1 after zero |
|---|---|---|---|---|---|
| `0x0148` | `CR_REG_0148` | `0x00000000` | 0 | 1 | - |

The register the 3D and transfer paths load per job takes one bit: it is a flag, not an address. It
held 0.

**Not shown.** What the bit selects (Q043).
