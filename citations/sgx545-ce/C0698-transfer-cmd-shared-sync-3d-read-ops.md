+++
id = "C0698"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:188"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L188"
quote = "IMG_DEV_VIRTADDR\ts3DSyncReadOpsCompleteDevVAddr;"
terms = ["transfer_cmd_shared.sync_3d_read_ops_complete_dev_vaddr"]
+++

Line 188 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`s3DSyncReadOpsCompleteDevVAddr`. It backs the glossary field
`transfer_cmd_shared.sync_3d_read_ops_complete_dev_vaddr`: 3D sync read-complete addr.
