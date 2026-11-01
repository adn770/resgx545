+++
id = "C0177"
source = "linux-imagination"
locator = "drivers/gpu/drm/imagination/pvr_rogue_cr_defs_client.h:31"
link = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/drivers/gpu/drm/imagination/pvr_rogue_cr_defs_client.h?id=c03c1a14507dfaf8b856c2608f9ac216021fc222#n31"
quote = "#define ROGUE_CR_TE_AA 0x0C00U"
terms = ["CR_TE_AA"]
+++

Line 31 of `pvr_rogue_cr_defs_client.h` in Linux's Rogue driver defines `ROGUE_CR_TE_AA`. It backs
the glossary register `CR_TE_AA`: tiling-engine anti-aliasing word: 0x20000000 in every
single-sample capture, bits 31 and 30 more (0xe0000000) with 4x multisampling [infer].
