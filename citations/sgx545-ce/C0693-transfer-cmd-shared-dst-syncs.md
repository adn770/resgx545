+++
id = "C0693"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:177"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L177"
quote = "PVRSRV_DEVICE_SYNC_OBJECT\tasDstSyncs[SGX_MAX_DST_SYNCS];"
terms = ["transfer_cmd_shared.dst_syncs"]
+++

Line 177 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`asDstSyncs`. It backs the glossary field `transfer_cmd_shared.dst_syncs`: destination sync [1].
