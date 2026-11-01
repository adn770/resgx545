+++
id = "C0390"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:125"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L125"
quote = "IMG_UINT32\t\t\tui32TATQSyncReadOpsPendingVal;"
terms = ["cmd_ta_shared.tq_sync_ta_read_ops_pending_val"]
+++

Line 125 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui32TATQSyncReadOpsPendingVal`. It backs the glossary field
`cmd_ta_shared.tq_sync_ta_read_ops_pending_val`: TA-side TQ sync: read pending value.
