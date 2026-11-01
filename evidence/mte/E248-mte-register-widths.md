+++
id = "E248"
claim = "CR_MTE_MULTISAMPLECTL, CR_MTE_RHW_MIN and CR_MTE_RHW_CLAMP take all 32 bits, CR_MTE_OTPM_BASE bits 31:4 and CR_MTE_CTRL bits 14:0"
unit = "mte"
method = "probes/platform/register-widths.toml on the laptop, linux fork with the debug option on: regwidth.c through /dev/mem writes each register with all ones, its prior value, zero and its prior value, reading after each write, with the firmware live and idle, in ten batches with a debugfs fill and the triangle checked after each; two runs"
tiers = ["HW"]
date = "2026-11-02"
data = ["platform-register-widths"]
terms = [
    "CR_MTE_MULTISAMPLECTL", "CR_MTE_OTPM_BASE", "CR_MTE_CTRL", "CR_MTE_RHW_MIN",
    "CR_MTE_RHW_CLAMP",
]
+++

**What runs.** The register census of E246, batch 7.

| register | name | value before | bits that took a write | width | read 1 after zero |
|---|---|---|---|---|---|
| `0x0230` | `CR_MTE_MULTISAMPLECTL` | `0x00000088` | 31:0 | 32 | - |
| `0x0234` | `CR_MTE_OTPM_BASE` | `0x20002000` | 31:4 | 28 | - |
| `0x023c` | `CR_MTE_CTRL` | `0x000000a2` | 14:0 | 15 | - |
| `0x0240` | `CR_MTE_RHW_MIN` | `0x358637bd` | 31:0 | 32 | - |
| `0x0244` | `CR_MTE_RHW_CLAMP` | `0x358637bd` | 31:0 | 32 | - |

`CR_MTE_MULTISAMPLECTL` takes all 32 bits, a byte for each of four sample positions as
`CR_ISP_MULTISAMPLECTL` (E249). The two 1/w words take any IEEE single. The OTPM base is a 16-byte
aligned address. `CR_MTE_CTRL` holds 0xa2 and takes 15 bits.

**Not shown.** What bits 14:8 of `CR_MTE_CTRL` control; no job has set them.
