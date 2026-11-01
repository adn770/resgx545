+++
id = "E247"
claim = "Of the tiling-engine, VDM and TA registers, CR_TE_MTILE1 takes bits 31, 29:22, 19:12 and 7:0, CR_TE_MTILE2 bits 30:22, 20:12 and 8:0, CR_TE_SCREEN bits 20:12 and 7:0, CR_TE_MACROTILE_STRIDE bits 17:0, CR_TE_PSG bits 26:18 and 6:0, the region and tail-pointer cache bases bits 31:6, CR_VDM_CTRL_STREAM_BASE bits 31:2 and CR_PPP_SCREEN bits 28:16 and 12:0; CR_TE_CONTEXT_STATE and 0x02b4 take no write; the other TA store registers take the bits E054 found"
unit = "ta"
method = "probes/platform/register-widths.toml on the laptop, linux fork with the debug option on: regwidth.c through /dev/mem writes each register with all ones, its prior value, zero and its prior value, reading after each write, with the firmware live and idle, in ten batches with a debugfs fill and the triangle checked after each; two runs"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["platform-register-widths"]
terms = [
    "CR_TE_AA", "CR_TE_MTILE1", "CR_TE_MTILE2", "CR_TE_SCREEN", "CR_TE_MACROTILE_STRIDE",
    "CR_TE_PSG", "CR_TE_PSGREGION_ADDR", "CR_TE_TPC_ADDR", "CR_VDM_CTRL_STREAM_BASE",
    "CR_PPP_SCREEN", "CR_TE_CONTEXT_STATE", "CR_TE_REG_02A8", "CR_TA_REG_02B0", "CR_TA_REG_02B4",
    "CR_TA_REG_02D0", "CR_TA_REG_02D4", "CR_REG_0324", "CR_REG_0364", "CR_REG_0368", "CR_REG_0370",
    "CR_REG_0374",
]
+++

**What runs.** The register census of E246, batches 1, 2 and 7.

| register | name | value before | bits that took a write | width | read 1 after zero |
|---|---|---|---|---|---|
| `0x0204` | `CR_TE_AA` | `0x20000000` | 31:29 | 3 | - |
| `0x0208` | `CR_TE_MTILE1` | `0x01004004` | 31, 29:22, 19:12, 7:0 | 25 | - |
| `0x020c` | `CR_TE_MTILE2` | `0x01004004` | 30:22, 20:12, 8:0 | 27 | - |
| `0x0210` | `CR_TE_SCREEN` | `0x00003001` | 20:12, 7:0 | 17 | - |
| `0x0214` | `CR_TE_MACROTILE_STRIDE` | `0x00000010` | 17:0 | 18 | - |
| `0x0218` | `CR_TE_PSG` | `0x01400000` | 26:18, 6:0 | 16 | - |
| `0x021c` | `CR_TE_PSGREGION_ADDR` | `0x20004000` | 31:6 | 26 | - |
| `0x0220` | `CR_TE_TPC_ADDR` | `0x20000000` | 31:6 | 26 | - |
| `0x0238` | `CR_VDM_CTRL_STREAM_BASE` | `0x3e000000` | 31:2 | 30 | - |
| `0x0248` | `CR_PPP_SCREEN` | `0x003f003f` | 28:16, 12:0 | 26 | - |
| `0x0274` | `CR_TE_CONTEXT_STATE` | `0x00010000` | 0x00000000 | 0 | 16 |
| `0x02a8` | `CR_TE_REG_02A8` | `0x00000000` | 19:12 | 8 | - |
| `0x02b0` | `CR_TA_REG_02B0` | `0x00000000` | 31:24 | 8 | - |
| `0x02b4` | `CR_TA_REG_02B4` | `0x000000ff` | 0x00000000 | 0 | 7:0 |
| `0x02d0` | `CR_TA_REG_02D0` | `0x00000000` | 31:2 | 30 | - |
| `0x02d4` | `CR_TA_REG_02D4` | `0x00000000` | 25:0 | 26 | - |
| `0x0324` | `CR_REG_0324` | `0x00000000` | 31:4 | 28 | - |
| `0x0364` | `CR_REG_0364` | `0x00000000` | 31:0 | 32 | - |
| `0x0368` | `CR_REG_0368` | `0x00000000` | 14:0 | 15 | - |
| `0x0370` | `CR_REG_0370` | `0x00000000` | 31:0 | 32 | - |
| `0x0374` | `CR_REG_0374` | `0x00000000` | 31:0 | 32 | - |

**Reading.** The macrotile words have three fields each, with one gap bit or more between them: in
`CR_TE_MTILE1` 29:22, 19:12 and 7:0 under bit 31, in `CR_TE_MTILE2` 30:22, 20:12 and 8:0, one bit
wider each; we read the extra bit as room for a target that is taller in 16-pixel tile rows than
wide in 32-pixel columns [infer].
`CR_TE_SCREEN` holds the last tile row in 20:12 (9 bits) and the last column in 7:0 (8 bits): at
most 8192 pixels each way, which `CR_PPP_SCREEN`'s two 13-bit fields (width and height less one)
also allow. The two tiling-engine addresses are 64-byte aligned, the control stream base 4-byte
aligned. Sizes and values at eight targets are E257.

`CR_TE_CONTEXT_STATE` reads 0x00010000 after every write, as before: bit 16 is set and nothing takes
a write from the host. 0x02b4 reads 0xff after every write. The other TA store registers take
exactly the bits the TA command loaded into them (E054).

**Not shown.** What the gap bits would hold if they existed, and the meaning of `CR_TE_PSG`'s two
fields beyond bits 22 and 25 (E184).
