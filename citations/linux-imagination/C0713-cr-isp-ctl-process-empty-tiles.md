+++
id = "C0713"
source = "linux-imagination"
locator = "drivers/gpu/drm/imagination/pvr_rogue_cr_defs.h:2304"
link = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/drivers/gpu/drm/imagination/pvr_rogue_cr_defs.h?id=c03c1a14507dfaf8b856c2608f9ac216021fc222#n2304"
quote = "#define ROGUE_CR_ISP_CTL_PROCESS_EMPTY_TILES_SHIFT 17U"
terms = ["CR_ISP_CTL.PROCESS_EMPTY_TILES"]
+++

Line 2304 of `pvr_rogue_cr_defs.h` in Linux's Rogue driver defines
`ROGUE_CR_ISP_CTL_PROCESS_EMPTY_TILES`. It backs the glossary bit field
`CR_ISP_CTL.PROCESS_EMPTY_TILES`: process empty tiles too, so a partial render visits every tile
(Rogue analogue).
