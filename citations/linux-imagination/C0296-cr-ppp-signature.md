+++
id = "C0296"
source = "linux-imagination"
locator = "drivers/gpu/drm/imagination/pvr_rogue_cr_defs.h:4313"
link = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/drivers/gpu/drm/imagination/pvr_rogue_cr_defs.h?id=c03c1a14507dfaf8b856c2608f9ac216021fc222#n4313"
quote = "#define ROGUE_CR_PPP_SIGNATURE 0x5020U"
terms = ["CR_PPP_SIGNATURE"]
+++

Line 4313 of `pvr_rogue_cr_defs.h` in Linux's Rogue driver defines `ROGUE_CR_PPP_SIGNATURE`. It
backs the glossary register `CR_PPP_SIGNATURE`: running signature of the primitive pipeline's
output; the EDM waits for it to stop changing (Rogue analogue).
