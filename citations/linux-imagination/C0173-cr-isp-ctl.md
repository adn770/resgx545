+++
id = "C0173"
source = "linux-imagination"
locator = "drivers/gpu/drm/imagination/pvr_rogue_cr_defs.h:2265"
link = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/drivers/gpu/drm/imagination/pvr_rogue_cr_defs.h?id=c03c1a14507dfaf8b856c2608f9ac216021fc222#n2265"
quote = "#define ROGUE_CR_ISP_CTL 0x0F38U"
terms = ["CR_ISP_CTL"]
+++

Line 2265 of `pvr_rogue_cr_defs.h` in Linux's Rogue driver defines `ROGUE_CR_ISP_CTL`. It backs the
glossary register `CR_ISP_CTL`: ISP control word of a render; the EDM sets bit 8 (process empty
tiles) for partial renders (Rogue analogue).
