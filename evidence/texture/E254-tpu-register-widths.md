+++
id = "E254"
claim = "Each colour-space and luma-key coefficient word takes two 10-bit fields, 25:16 and 9:0, except words 4 of each set (9:0 only), the luma-key B and offset word (23:16 and 9:0) and the luma-key alpha word (31:0); CR_TPU_YUV_CSC_INPUT takes bits 3:0"
unit = "texture"
method = "probes/platform/register-widths.toml on the laptop, linux fork with the debug option on: regwidth.c through /dev/mem writes each register with all ones, its prior value, zero and its prior value, reading after each write, with the firmware live and idle, in ten batches with a debugfs fill and the triangle checked after each; two runs"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["platform-register-widths"]
terms = [
    "CR_TPU_YUV_CSC0_0", "CR_TPU_YUV_CSC0_4", "CR_TPU_YUV_CSC1_0", "CR_TPU_YUV_CSC1_4",
    "CR_TPU_YUV_CSC_INPUT", "CR_TPU_LUMA_KEY_RG", "CR_TPU_LUMA_KEY_B_OFFSET",
    "CR_TPU_LUMA_KEY_ALPHA",
]
+++

**What runs.** The register census of E246, batch 3.

| register | name | value before | bits that took a write | width | read 1 after zero |
|---|---|---|---|---|---|
| `0x0820` | `CR_TPU_YUV_CSC0_0` | `0x00000000` | 25:16, 9:0 | 20 | - |
| `0x0824` | `CR_TPU_YUV_CSC0_1` | `0x00000000` | 25:16, 9:0 | 20 | - |
| `0x0828` | `CR_TPU_YUV_CSC0_2` | `0x00000000` | 25:16, 9:0 | 20 | - |
| `0x082c` | `CR_TPU_YUV_CSC0_3` | `0x00000000` | 25:16, 9:0 | 20 | - |
| `0x0830` | `CR_TPU_YUV_CSC0_4` | `0x00000000` | 9:0 | 10 | - |
| `0x0834` | `CR_TPU_YUV_CSC1_0` | `0x00000000` | 25:16, 9:0 | 20 | - |
| `0x0838` | `CR_TPU_YUV_CSC1_1` | `0x00000000` | 25:16, 9:0 | 20 | - |
| `0x083c` | `CR_TPU_YUV_CSC1_2` | `0x00000000` | 25:16, 9:0 | 20 | - |
| `0x0840` | `CR_TPU_YUV_CSC1_3` | `0x00000000` | 25:16, 9:0 | 20 | - |
| `0x0844` | `CR_TPU_YUV_CSC1_4` | `0x00000000` | 9:0 | 10 | - |
| `0x0848` | `CR_TPU_YUV_CSC_INPUT` | `0x00000000` | 3:0 | 4 | - |
| `0x0860` | `CR_TPU_LUMA_KEY_RG` | `0x00000000` | 25:16, 9:0 | 20 | - |
| `0x0864` | `CR_TPU_LUMA_KEY_B_OFFSET` | `0x00000000` | 23:16, 9:0 | 18 | - |
| `0x0868` | `CR_TPU_LUMA_KEY_ALPHA` | `0x00000000` | 31:0 | 32 | - |

The coefficient words hold two 10-bit coefficients each, the fifth word of a set one: nine per set,
which we read as a 3x3 matrix [infer]. `CR_TPU_YUV_CSC_INPUT` takes four bits. The luma-key B and
offset word has an 8-bit field in 23:16 above the 10-bit weight; the alpha word takes all 32 bits.

**Not shown.** What bits 31:16 of the alpha word and bits 3:2 of the input word select.
