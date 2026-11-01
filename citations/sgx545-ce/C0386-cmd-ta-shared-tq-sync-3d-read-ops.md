+++
id = "C0386"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:131"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L131"
quote = "IMG_UINT32\t\t\tui323DTQSyncReadOpsPendingVal;"
terms = ["cmd_ta_shared.tq_sync_3d_read_ops_pending_val"]
+++

Line 131 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui323DTQSyncReadOpsPendingVal`. It backs the glossary field
`cmd_ta_shared.tq_sync_3d_read_ops_pending_val`: 3D-side TQ sync: read pending value.
