+++
id = "C0689"
source = "linux-imagination"
locator = "drivers/gpu/drm/imagination/pvr_rogue_fwif_client.h:331"
link = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/drivers/gpu/drm/imagination/pvr_rogue_fwif_client.h?id=c03c1a14507dfaf8b856c2608f9ac216021fc222#n331"
quote = "u32 isp_render_origin;"
terms = ["transfer_cmd.isp_render_origin"]
+++

Line 331 of `pvr_rogue_fwif_client.h` in Linux's Rogue driver declares `isp_render_origin`. It backs
the glossary field `transfer_cmd.isp_render_origin`: top-left tile of the render: y0 / 16 | (x0 /
32) << 16, 32 x 16 tiles; the EDM copies it into register 0x040c.
