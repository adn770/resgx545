+++
id = "C0388"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:129"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L129"
quote = "IMG_UINT32\t\t\tui323DTQSyncWriteOpsPendingVal;"
terms = ["cmd_ta_shared.tq_sync_3d_write_ops_pending_val"]
+++

Line 129 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui323DTQSyncWriteOpsPendingVal`. It backs the glossary field
`cmd_ta_shared.tq_sync_3d_write_ops_pending_val`: 3D-side TQ sync: write pending value.
