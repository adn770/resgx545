+++
id = "C0765"
source = "linux-imagination"
locator = "drivers/gpu/drm/imagination/pvr_rogue_cr_defs.h:1252"
link = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/drivers/gpu/drm/imagination/pvr_rogue_cr_defs.h?id=c03c1a14507dfaf8b856c2608f9ac216021fc222#n1252"
quote = "#define ROGUE_CR_MIPS_WRAPPER_CONFIG 0x0810U"
terms = ["Rogue MIPS wrapper registers"]
+++

Line 1252 of `pvr_rogue_cr_defs.h` in Linux's Rogue driver defines `ROGUE_CR_MIPS_WRAPPER_CONFIG`.
It backs the glossary concept `Rogue MIPS wrapper registers`: Rogue's MIPS firmware wrapper
configuration register, at offset 0x0810 and 64 bits wide: an analogy at the offset of SGX545's
CR_REG_0810 that does not explain it, since SGX545 implements bit 0 of the dword there (E401).
