+++
id = "C0384"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:150"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L150"
quote = "PVRSRV_DEVICE_SYNC_OBJECT\tsTA3DDependency;"
terms = ["cmd_ta_shared.ta3d_dependency"]
+++

Line 150 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`sTA3DDependency`. It backs the glossary field `cmd_ta_shared.ta3d_dependency`: TA->3D dependency
sync.
