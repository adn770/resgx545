+++
id = "C0153"
source = "linux-imagination"
locator = "drivers/gpu/drm/imagination/pvr_rogue_fwif.h:671"
link = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/drivers/gpu/drm/imagination/pvr_rogue_fwif.h?id=c03c1a14507dfaf8b856c2608f9ac216021fc222#n671"
quote = "u32 ccb_fw_addr; /* CCB base */"
terms = ["hw_transfer_context.ccb_dev_vaddr"]
+++

Line 671 of `pvr_rogue_fwif.h` in Linux's Rogue driver declares `ccb_fw_addr`. It backs the glossary
field `hw_render_context.ccb_dev_vaddr`: TA client CCB; and the glossary field
`hw_transfer_context.ccb_dev_vaddr`: transfer client CCB.
