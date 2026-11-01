+++
id = "C0152"
source = "linux-imagination"
locator = "drivers/gpu/drm/imagination/pvr_rogue_fwif.h:670"
link = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/drivers/gpu/drm/imagination/pvr_rogue_fwif.h?id=c03c1a14507dfaf8b856c2608f9ac216021fc222#n670"
quote = "u32 ccbctl_fw_addr; /* CCB control */"
terms = ["hw_transfer_context.ccb_ctl_dev_vaddr"]
+++

Line 670 of `pvr_rogue_fwif.h` in Linux's Rogue driver declares `ccbctl_fw_addr`. It backs the
glossary field `hw_render_context.ccb_ctl_dev_vaddr`: TA client CCB control; and the glossary field
`hw_transfer_context.ccb_ctl_dev_vaddr`: transfer CCB control.
