+++
id = "C0168"
source = "linux-imagination"
locator = "drivers/gpu/drm/imagination/pvr_rogue_fwif_client.h:251"
link = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/drivers/gpu/drm/imagination/pvr_rogue_fwif_client.h?id=c03c1a14507dfaf8b856c2608f9ac216021fc222#n251"
quote = "u32 flags;"
terms = ["cmd_ta.frag_flags", "hw_render_details.frag_flags", "transfer_cmd.flags"]
+++

Line 251 of `pvr_rogue_fwif_client.h` in Linux's Rogue driver declares `flags`. It backs the
glossary field `cmd_ta.frag_flags`: fragment (3D) flags: depth/stencil buffer present, visibility
results (FRAG_FLAGS.*); the glossary field `hw_render_details.frag_flags`: fragment (3D) flags:
depth/stencil buffer present, visibility results (FRAG_FLAGS.*); and the glossary field
`transfer_cmd.flags`: TQ_FLAGS.* of the transfer.
