+++
id = "C0704"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:180"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L180"
quote = "IMG_DEV_VIRTADDR\tsTASyncWriteOpsCompleteDevVAddr;"
terms = ["transfer_cmd_shared.sync_ta_write_ops_complete_dev_vaddr"]
+++

Line 180 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`sTASyncWriteOpsCompleteDevVAddr`. It backs the glossary field
`transfer_cmd_shared.sync_ta_write_ops_complete_dev_vaddr`: TA sync write-complete addr.
