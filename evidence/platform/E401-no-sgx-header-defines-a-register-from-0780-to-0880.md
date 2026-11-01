+++
id = "E401"
claim = "None of the 161 sgx*defs.h headers of the openpvrsgx archive defines a register from 0x0780 to 0x0880 (the nearest defined are EUR_CR_TIMER at 0x0144 and EUR_CR_USE_CODE_BASE_0 at 0x0a0c), so no public SGX header names 0x0810, 0x0814 or 0x0818; Linux's Rogue driver defines ROGUE_CR_MIPS_WRAPPER_CONFIG at 0x0810 and ROGUE_CR_MIPS_ADDR_REMAP1_CONFIG1 at 0x0818, each with a 64-bit mask (0x000001030F01FFFF and 0x00000000FFFFF001) on an 8-byte stride, where E122 found 0x0810, 0x0814 and 0x0818 to implement bit 0, bits 16:0 and bits 10:0 as separate 4-byte registers"
unit = "platform"
method = "offline search of github.com/openpvrsgx-devgroup/linux_openpvrsgx at commit 2342ce92fdde66ac5a7ed7548b47a3a0836c9e77 (the pin of cites/openpvrsgx-1.9.toml, cloned and checked out, drivers/gpu/drm/pvrsgx only): every sgx*defs.h under it, 161 files in 17 directories (DDK 1.5 to 1.17 and generic: sgx520defs.h, sgx530defs.h, sgx531defs.h, sgx535defs.h, sgx540defs.h, sgx543defs.h, sgx543_v1.164defs.h, sgx544defs.h, sgx545defs.h, sgxdefs.h, sgxfeaturedefs.h and sgxmpdefs.h), for every #define whose value is a hexadecimal number from 0x0780 to 0x0880, for every register offset (a #define of an EUR_CR_ or PSB_CR_ name with no _MASK, _SHIFT, _SIGNED, _SIZE, _ENABLE, _DISABLE or _ALIGN ending, 174 names) and for the numbers 0x0810, 0x0814 and 0x0818 as bare tokens; then Linux at commit c03c1a14507dfaf8b856c2608f9ac216021fc222, drivers/gpu/drm/imagination/pvr_rogue_cr_defs.h lines 1252 to 1277"
tiers = ["DDK"]
date = "2026-11-07"
data = []
terms = ["CR_REG_0810", "CR_REG_0814", "CR_REG_0818", "Rogue MIPS wrapper registers"]
+++
**Results.** The only defines with a value from 0x0780 to 0x0880 in the 161 headers are field
masks (0x7ff and 0x800: EUR_CR_BIF_CTRL_MMU_BYPASS_PBE_MASK, EUR_CR_EVENT_STATUS_TPC_CLEAR_MASK
and the like). Of the 174 register offsets none lies there; the nearest below is EUR_CR_TIMER
(0x0144) and the nearest above EUR_CR_USE_CODE_BASE_0 (0x0a0c). The numbers 0x0810, 0x0814 and
0x0818 appear in no sgx*defs.h.

In Linux's Rogue driver 0x0810 is ROGUE_CR_MIPS_WRAPPER_CONFIG (line 1252; mask
0x000001030F01FFFF: bits 40, 33:32, 27:24 and 16:0) and 0x0818 is ROGUE_CR_MIPS_ADDR_REMAP1_CONFIG1
(line 1276; mask 0x00000000FFFFF001: bits 31:12 and 0); the next register,
ROGUE_CR_MIPS_ADDR_REMAP1_CONFIG2, is at 0x0820. Each is 64 bits wide, so 0x0814 would lie inside
the first. E122 found 0x0810, 0x0814 and 0x0818 to implement bit 0, bits 16:0 and bits 10:0, each
read as its own 4-byte register.

**Not shown.** What the SGX545 registers do. This record says only that the searched open sources
have no SGX register at these offsets and that Rogue's two registers there differ in width and
fields. No other source was searched.
