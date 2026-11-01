+++
id = "C0053"
source = "linux-imagination"
locator = "drivers/gpu/drm/imagination/pvr_rogue_cr_defs.h:222"
link = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/drivers/gpu/drm/imagination/pvr_rogue_cr_defs.h?id=c03c1a14507dfaf8b856c2608f9ac216021fc222#n222"
quote = "#define ROGUE_CR_CLK_STATUS 0x0008U"
terms = ["CR_CLKGATESTATUS"]
+++

Line 222 of `pvr_rogue_cr_defs.h` in Linux's Rogue driver defines `ROGUE_CR_CLK_STATUS`. It backs
the glossary register `CR_CLKGATESTATUS`: per-unit clock-gating state (Rogue analogue).
