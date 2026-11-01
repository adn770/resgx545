+++
id = "E253"
claim = "Of the DPM registers, the page-table, state and control bases take bits 31:4, the two free lists and the two page-count words all 32 bits, the TA, ZLS and PDS thresholds bits 15:0, CR_DPM_TA_GLOBAL_LIST bits 16:0, CR_DPM_STATE_CONTEXT_ID and CR_DPM_CONTEXT_PB_BASE bits 2:0, CR_DPM_3D_RT_INDEX and CR_DPM_REG_074C bits 8:0 and CR_DPM_SPM_SWITCH bit 0"
unit = "dpm"
method = "probes/platform/register-widths.toml on the laptop, linux fork with the debug option on: regwidth.c through /dev/mem writes each register with all ones, its prior value, zero and its prior value, reading after each write, with the firmware live and idle, in ten batches with a debugfs fill and the triangle checked after each; two runs"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["platform-register-widths"]
terms = [
    "CR_DPM_3D_PAGE_TABLE_BASE", "CR_DPM_3D_FREE_LIST", "CR_DPM_TA_ALLOC_PAGE_TABLE_BASE",
    "CR_DPM_TA_ALLOC_FREE_LIST", "CR_DPM_TA_PAGE_THRESHOLD", "CR_DPM_ZLS_PAGE_THRESHOLD",
    "CR_DPM_TA_GLOBAL_LIST", "CR_DPM_STATE_BASE0", "CR_DPM_STATE_CONTEXT_ID", "CR_DPM_CONTROL_BASE",
    "CR_DPM_TA_PAGE_COUNTS", "CR_DPM_SPM_SWITCH", "CR_DPM_3D_PAGE_COUNTS", "CR_DPM_CONTEXT_PB_BASE",
    "CR_DPM_PDS_THRESHOLD", "CR_DPM_STATE_BASE1", "CR_DPM_3D_RT_INDEX", "CR_DPM_REG_074C",
]
+++

**What runs.** The register census of E246, batch 8. The DPM's status registers and the registers
the kernel's register file skips (task registers, the TA and 3D allocation state, the partial-render
flag) were only read (E256 for their values across jobs).

| register | name | value before | bits that took a write | width | read 1 after zero |
|---|---|---|---|---|---|
| `0x0600` | `CR_DPM_3D_PAGE_TABLE_BASE` | `0x10423000` | 31:4 | 28 | - |
| `0x0604` | `CR_DPM_3D_FREE_LIST` | `0x04220003` | 31:0 | 32 | - |
| `0x0618` | `CR_DPM_TA_ALLOC_PAGE_TABLE_BASE` | `0x10423000` | 31:4 | 28 | - |
| `0x061c` | `CR_DPM_TA_ALLOC_FREE_LIST` | `0x04220001` | 31:0 | 32 | - |
| `0x0620` | `CR_DPM_TA_PAGE_THRESHOLD` | `0x00000432` | 15:0 | 16 | - |
| `0x0624` | `CR_DPM_ZLS_PAGE_THRESHOLD` | `0x00000400` | 15:0 | 16 | - |
| `0x0628` | `CR_DPM_TA_GLOBAL_LIST` | `0x00010400` | 16:0 | 17 | - |
| `0x062c` | `CR_DPM_STATE_BASE0` | `0x20003000` | 31:4 | 28 | - |
| `0x0630` | `CR_DPM_STATE_CONTEXT_ID` | `0x00000000` | 2:0 | 3 | - |
| `0x0634` | `CR_DPM_CONTROL_BASE` | `0x20001000` | 31:4 | 28 | - |
| `0x0638` | `CR_DPM_TA_PAGE_COUNTS` | `0x00000000` | 31:0 | 32 | - |
| `0x065c` | `CR_DPM_SPM_SWITCH` | `0x00000000` | 0 | 1 | - |
| `0x0660` | `CR_DPM_3D_PAGE_COUNTS` | `0x00000002` | 31:0 | 32 | - |
| `0x0664` | `CR_DPM_CONTEXT_PB_BASE` | `0x00000005` | 2:0 | 3 | - |
| `0x0668` | `CR_DPM_PDS_THRESHOLD` | `0x00000300` | 15:0 | 16 | - |
| `0x0674` | `CR_DPM_STATE_BASE1` | `0x20006000` | 31:4 | 28 | - |
| `0x073c` | `CR_DPM_3D_RT_INDEX` | `0x00000000` | 8:0 | 9 | - |
| `0x074c` | `CR_DPM_REG_074C` | `0x00000000` | 8:0 | 9 | - |

**Reading.** `CR_DPM_CONTEXT_PB_BASE` takes three bits and held 5, too few for an address; we read
it as an index or a small count [infer]. `CR_DPM_STATE_CONTEXT_ID` also takes three bits, which we
read as eight context slots [infer]. `CR_DPM_3D_RT_INDEX` and `CR_DPM_REG_074C` take nine bits each;
bit 8 of the second is the enable E203 and E206 read. The thresholds take 16 bits each, which we
read as page counts [infer].

**Not shown.** The fields of the 32-bit free-list and page-count words beyond their halves.
