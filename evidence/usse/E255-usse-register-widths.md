+++
id = "E255"
claim = "The USSE filter coefficient sets 0 and 1 take all 32 bits of their two tap words and bits 19:0 of their shift and bias words, set 2 only bits 31:24 and 7:0 of its first tap word, 15:8 of its second and 19:0 of its bias word; CR_USE_COEFFS_MODE takes bits 1:0"
unit = "usse"
method = "probes/platform/register-widths.toml on the laptop, linux fork with the debug option on: regwidth.c through /dev/mem writes each register with all ones, its prior value, zero and its prior value, reading after each write, with the firmware live and idle, in ten batches with a debugfs fill and the triangle checked after each; two runs"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["platform-register-widths"]
terms = [
    "CR_USE_REG_0A04", "CR_USE_COEFFS0_A", "CR_USE_COEFFS0_B", "CR_USE_COEFFS0_BIAS",
    "CR_USE_COEFFS1_A", "CR_USE_COEFFS1_B", "CR_USE_COEFFS1_BIAS", "CR_USE_COEFFS_MODE",
    "CR_USE_REG_0AA0", "CR_USE_COEFFS2_A", "CR_USE_COEFFS2_B", "CR_USE_COEFFS2_BIAS",
]
+++

**What runs.** The register census of E246, batches 2 and 4.

| register | name | value before | bits that took a write | width | read 1 after zero |
|---|---|---|---|---|---|
| `0x0a04` | `CR_USE_REG_0A04` | `0x00000000` | 31:4 | 28 | - |
| `0x0a84` | `CR_USE_COEFFS0_A` | `0x00000000` | 31:0 | 32 | - |
| `0x0a88` | `CR_USE_COEFFS0_B` | `0x00000000` | 31:0 | 32 | - |
| `0x0a8c` | `CR_USE_COEFFS0_BIAS` | `0x00000000` | 19:0 | 20 | - |
| `0x0a90` | `CR_USE_COEFFS1_A` | `0x00000000` | 31:0 | 32 | - |
| `0x0a94` | `CR_USE_COEFFS1_B` | `0x00000000` | 31:0 | 32 | - |
| `0x0a98` | `CR_USE_COEFFS1_BIAS` | `0x00000000` | 19:0 | 20 | - |
| `0x0a9c` | `CR_USE_COEFFS_MODE` | `0x00000000` | 1:0 | 2 | - |
| `0x0aa0` | `CR_USE_REG_0AA0` | `0x00000000` | 31:0 | 32 | - |
| `0x0b24` | `CR_USE_COEFFS2_A` | `0x00000000` | 31:24, 7:0 | 16 | - |
| `0x0b28` | `CR_USE_COEFFS2_B` | `0x00000000` | 15:8 | 8 | - |
| `0x0b2c` | `CR_USE_COEFFS2_BIAS` | `0x00000000` | 19:0 | 20 | - |

**Reading.** Sets 0 and 1 take all 32 bits of their two tap words, which we read as eight signed
byte taps each [infer]. Set 2 keeps three bytes: bytes 3 and 0
of its first tap word and byte 1 of its second; its other bytes read 0 after all ones.
`CR_USE_COEFFS_MODE` takes exactly the bits its field names.

**Not shown.** Whether a filter through set 2 uses only those three taps.
