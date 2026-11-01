+++
id = "C0323"
source = "linux-imagination"
locator = "drivers/gpu/drm/imagination/pvr_rogue_fwif_client.h:227"
link = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/drivers/gpu/drm/imagination/pvr_rogue_fwif_client.h?id=c03c1a14507dfaf8b856c2608f9ac216021fc222#n227"
quote = "u64 pds_bgnd[3U];"
terms = ["cmd_ta.pds_bgnd", "hw_render_details.pds_bgnd"]
+++

Line 227 of `pvr_rogue_fwif_client.h` in Linux's Rogue driver declares `pds_bgnd`. It backs the
glossary field `cmd_ta.pds_bgnd`: background object words [3]: dwords 0-2 of the background object,
the first a pixel PDS reference; copied to the render details' pds_bgnd at the TA kick; and the
glossary field `hw_render_details.pds_bgnd`: background object words [3], copied from the TA
command's pds_bgnd at the TA kick; the 3D kick writes words 0 and 1 into the background object.
