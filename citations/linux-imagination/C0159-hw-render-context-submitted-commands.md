+++
id = "C0159"
source = "linux-imagination"
locator = "drivers/gpu/drm/imagination/pvr_rogue_fwif_shared.h:55"
link = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/drivers/gpu/drm/imagination/pvr_rogue_fwif_shared.h?id=c03c1a14507dfaf8b856c2608f9ac216021fc222#n55"
quote = "u32 submitted_commands;"
terms = ["hw_transfer_context.submitted_commands"]
+++

Line 55 of `pvr_rogue_fwif_shared.h` in Linux's Rogue driver declares `submitted_commands`. It backs
the glossary field `hw_render_context.submitted_commands`: TA commands queued in the context's CCB:
the CCB handler increments it, the TA end decrements it; and the glossary field
`hw_transfer_context.submitted_commands`: commands queued.
