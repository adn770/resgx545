+++
id = "C0389"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:126"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L126"
quote = "IMG_DEV_VIRTADDR\tsTATQSyncReadOpsCompleteDevVAddr;"
terms = ["cmd_ta_shared.tq_sync_ta_read_ops_complete_dev_vaddr"]
+++

Line 126 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`sTATQSyncReadOpsCompleteDevVAddr`. It backs the glossary field
`cmd_ta_shared.tq_sync_ta_read_ops_complete_dev_vaddr`: TA-side TQ sync: read-complete address.
