+++
id = "C0065"
source = "linux-imagination"
locator = "drivers/gpu/drm/imagination/pvr_rogue_cr_defs.h:831"
link = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/drivers/gpu/drm/imagination/pvr_rogue_cr_defs.h?id=c03c1a14507dfaf8b856c2608f9ac216021fc222#n831"
quote = "#define ROGUE_CR_EVENT_CLEAR 0x0138U"
terms = ["CR_EVENT_HOST_CLEAR"]
+++

Line 831 of `pvr_rogue_cr_defs.h` in Linux's Rogue driver defines `ROGUE_CR_EVENT_CLEAR`. It backs
the glossary register `CR_EVENT_HOST_CLEAR`: write-1-to-clear events, bank 1 (Rogue analogue).
