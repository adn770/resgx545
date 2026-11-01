+++
id = "C0346"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:145"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L145"
quote = "IMG_UINT32\t\t\tui32NumSrcSyncs;"
terms = ["hw_render_details.num_src_syncs"]
+++

Line 145 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui32NumSrcSyncs`. It backs the glossary field `hw_render_details.num_src_syncs`: source sync count.
