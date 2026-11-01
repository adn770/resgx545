+++
id = "E250"
claim = "CR_ISP_ZLSCTL takes bits 26:0, the depth load and store bases bits 30:4 and the stencil load and store bases bits 31:4"
unit = "zls"
method = "probes/platform/register-widths.toml on the laptop, linux fork with the debug option on: regwidth.c through /dev/mem writes each register with all ones, its prior value, zero and its prior value, reading after each write, with the firmware live and idle, in ten batches with a debugfs fill and the triangle checked after each; two runs"
tiers = ["HW"]
date = "2026-11-02"
data = ["platform-register-widths"]
terms = [
    "CR_ISP_ZLSCTL", "CR_ISP_ZLOAD_BASE", "CR_ISP_ZSTORE_BASE", "CR_ISP_STENCIL_LOAD_BASE",
    "CR_ISP_STENCIL_STORE_BASE",
]
+++

**What runs.** The register census of E246, batch 6.

| register | name | value before | bits that took a write | width | read 1 after zero |
|---|---|---|---|---|---|
| `0x0480` | `CR_ISP_ZLSCTL` | `0x00000000` | 26:0 | 27 | - |
| `0x0484` | `CR_ISP_ZLOAD_BASE` | `0x00000000` | 30:4 | 27 | - |
| `0x0488` | `CR_ISP_ZSTORE_BASE` | `0x00000000` | 30:4 | 27 | - |
| `0x048c` | `CR_ISP_STENCIL_LOAD_BASE` | `0x80000000` | 31:4 | 28 | - |
| `0x0490` | `CR_ISP_STENCIL_STORE_BASE` | `0x80000000` | 31:4 | 28 | - |

The depth bases are 16-byte aligned offsets of 31 bits; the stencil bases have bit 31 as well, the
enable their glossary rows name. `CR_ISP_ZLSCTL` takes 27 bits.

**Not shown.** The fields of `CR_ISP_ZLSCTL`.
