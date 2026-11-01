+++
id = "C0290"
source = "linux-imagination"
locator = "drivers/gpu/drm/imagination/pvr_rogue_cr_defs.h:2328"
link = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/drivers/gpu/drm/imagination/pvr_rogue_cr_defs.h?id=c03c1a14507dfaf8b856c2608f9ac216021fc222#n2328"
quote = "#define ROGUE_CR_ISP_CTL_VALID_ID_SHIFT 4U"
terms = ["CR_ISP_CTL.VALID_ID"]
+++

Line 2328 of `pvr_rogue_cr_defs.h` in Linux's Rogue driver defines `ROGUE_CR_ISP_CTL_VALID_ID`. It
backs the glossary bit field `CR_ISP_CTL.VALID_ID`: validation threshold: opaque and translucent
objects whose ISP1.VALID_ID is below it are not drawn (Rogue analogue).
