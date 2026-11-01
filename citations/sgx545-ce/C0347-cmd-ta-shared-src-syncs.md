+++
id = "C0347"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:146"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L146"
quote = "PVRSRV_DEVICE_SYNC_OBJECT\tasSrcSyncs[SGX_MAX_SRC_SYNCS];"
terms = ["cmd_ta_shared.src_syncs", "hw_render_details.src_syncs"]
+++

Line 146 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`asSrcSyncs`. It backs the glossary field `cmd_ta_shared.src_syncs`: source syncs [8]; and the
glossary field `hw_render_details.src_syncs`: source syncs [8].
