+++
id = "C0031"
source = "linux-imagination"
locator = "drivers/gpu/drm/imagination/pvr_rogue_fwif_client.h:340"
link = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/drivers/gpu/drm/imagination/pvr_rogue_fwif_client.h?id=c03c1a14507dfaf8b856c2608f9ac216021fc222#n340"
quote = "u32 event_pixel_pds_code;"
terms = ["transfer_cmd.event_pixel_pds_code"]
+++

Line 340 of `pvr_rogue_fwif_client.h` in Linux's Rogue driver declares `event_pixel_pds_code`. It
backs the glossary field `hw_render_details.event_pixel_pds_code`: end-of-tile pixel PDS program;
and the glossary field `transfer_cmd.event_pixel_pds_code`: end-of-tile PDS program.
