+++
id = "C0700"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:186"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L186"
quote = "IMG_DEV_VIRTADDR\ts3DSyncWriteOpsCompleteDevVAddr;"
terms = ["transfer_cmd_shared.sync_3d_write_ops_complete_dev_vaddr"]
+++

Line 186 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`s3DSyncWriteOpsCompleteDevVAddr`. It backs the glossary field
`transfer_cmd_shared.sync_3d_write_ops_complete_dev_vaddr`: 3D sync write-complete addr.
