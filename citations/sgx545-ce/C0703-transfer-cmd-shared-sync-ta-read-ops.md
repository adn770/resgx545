+++
id = "C0703"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:181"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L181"
quote = "IMG_UINT32\t\tui32TASyncReadOpsPendingVal;"
terms = ["transfer_cmd_shared.sync_ta_read_ops_pending_val"]
+++

Line 181 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui32TASyncReadOpsPendingVal`. It backs the glossary field
`transfer_cmd_shared.sync_ta_read_ops_pending_val`: TA sync read pending.
