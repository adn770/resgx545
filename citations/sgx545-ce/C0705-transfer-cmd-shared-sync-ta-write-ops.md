+++
id = "C0705"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:179"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L179"
quote = "IMG_UINT32\t\tui32TASyncWriteOpsPendingVal;"
terms = ["transfer_cmd_shared.sync_ta_write_ops_pending_val"]
+++

Line 179 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui32TASyncWriteOpsPendingVal`. It backs the glossary field
`transfer_cmd_shared.sync_ta_write_ops_pending_val`: TA sync write pending.
