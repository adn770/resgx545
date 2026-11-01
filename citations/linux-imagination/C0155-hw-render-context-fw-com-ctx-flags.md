+++
id = "C0155"
source = "linux-imagination"
locator = "drivers/gpu/drm/imagination/pvr_rogue_fwif.h:679"
link = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/drivers/gpu/drm/imagination/pvr_rogue_fwif.h?id=c03c1a14507dfaf8b856c2608f9ac216021fc222#n679"
quote = "u32 fw_com_ctx_flags;"
terms = ["hw_transfer_context.fw_com_ctx_flags"]
+++

Line 679 of `pvr_rogue_fwif.h` in Linux's Rogue driver declares `fw_com_ctx_flags`. It backs the
glossary field `hw_render_context.fw_com_ctx_flags`: context flags (new context, per-context PB);
and the glossary field `hw_transfer_context.fw_com_ctx_flags`: context flags.
