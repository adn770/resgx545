+++
id = "C0694"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:176"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L176"
quote = "IMG_UINT32\t\t\tui32NumDstSyncs;"
terms = ["transfer_cmd_shared.num_dst_syncs"]
+++

Line 176 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui32NumDstSyncs`. It backs the glossary field `transfer_cmd_shared.num_dst_syncs`: destination sync
count.
