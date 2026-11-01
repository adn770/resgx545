+++
id = "C0387"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:130"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L130"
quote = "IMG_DEV_VIRTADDR\ts3DTQSyncWriteOpsCompleteDevVAddr;"
terms = ["cmd_ta_shared.tq_sync_3d_write_ops_complete_dev_vaddr"]
+++

Line 130 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`s3DTQSyncWriteOpsCompleteDevVAddr`. It backs the glossary field
`cmd_ta_shared.tq_sync_3d_write_ops_complete_dev_vaddr`: 3D-side TQ sync: write-complete address.
