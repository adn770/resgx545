+++
id = "C0167"
source = "linux-imagination"
locator = "drivers/gpu/drm/imagination/pvr_rogue_fwif.h:815"
link = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/drivers/gpu/drm/imagination/pvr_rogue_fwif.h?id=c03c1a14507dfaf8b856c2608f9ac216021fc222#n815"
quote = "u32 cmd_size;"
terms = ["transfer_cmd.cmd_size"]
+++

Line 815 of `pvr_rogue_fwif.h` in Linux's Rogue driver declares `cmd_size`. It backs the glossary
field `cmd_ta.cmd_size`: command size in the CCB, 64-byte units; and the glossary field
`transfer_cmd.cmd_size`: command size, 64-byte multiple.
