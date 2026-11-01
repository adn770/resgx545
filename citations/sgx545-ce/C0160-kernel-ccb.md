+++
id = "C0160"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:60"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L60"
quote = "} PVRSRV_SGX_KERNEL_CCB;"
terms = ["kernel_ccb"]
+++

Line 60 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`PVRSRV_SGX_KERNEL_CCB`. It backs the glossary structure `kernel_ccb`: kernel CCB: 256 commands.
