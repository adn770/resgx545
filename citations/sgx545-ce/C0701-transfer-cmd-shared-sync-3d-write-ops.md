+++
id = "C0701"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:185"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L185"
quote = "IMG_UINT32\t\tui323DSyncWriteOpsPendingVal;"
terms = ["transfer_cmd_shared.sync_3d_write_ops_pending_val"]
+++

Line 185 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui323DSyncWriteOpsPendingVal`. It backs the glossary field
`transfer_cmd_shared.sync_3d_write_ops_pending_val`: 3D sync write pending.
