+++
id = "C0691"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:192"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L192"
quote = "} SGXMKIF_TRANSFERCMD_SHARED, *PSGXMKIF_TRANSFERCMD_SHARED;"
terms = ["transfer_cmd_shared"]
+++

Line 192 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`SGXMKIF_TRANSFERCMD_SHARED`. It backs the glossary structure `transfer_cmd_shared`: kernel-written
sync/status block of the transfer command.
