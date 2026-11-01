+++
id = "C0391"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:124"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L124"
quote = "IMG_DEV_VIRTADDR\tsTATQSyncWriteOpsCompleteDevVAddr;"
terms = ["cmd_ta_shared.tq_sync_ta_write_ops_complete_dev_vaddr"]
+++

Line 124 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`sTATQSyncWriteOpsCompleteDevVAddr`. It backs the glossary field
`cmd_ta_shared.tq_sync_ta_write_ops_complete_dev_vaddr`: TA-side TQ sync: write-complete address.
