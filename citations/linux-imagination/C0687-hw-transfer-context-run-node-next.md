+++
id = "C0687"
source = "linux-imagination"
locator = "drivers/gpu/drm/imagination/pvr_rogue_fwif.h:716"
link = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/drivers/gpu/drm/imagination/pvr_rogue_fwif.h?id=c03c1a14507dfaf8b856c2608f9ac216021fc222#n716"
quote = "struct rogue_fwif_dllist_node run_node __aligned(8);"
terms = ["hw_transfer_context.run_node_next", "hw_transfer_context.run_node_prev"]
+++

Line 716 of `pvr_rogue_fwif.h` in Linux's Rogue driver declares `run_node`. It backs the glossary
field `hw_transfer_context.run_node_next`: next context in EDM list; and the glossary field
`hw_transfer_context.run_node_prev`: previous context in EDM list.
