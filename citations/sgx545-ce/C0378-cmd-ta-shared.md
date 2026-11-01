+++
id = "C0378"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:155"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L155"
quote = "} SGXMKIF_CMDTA_SHARED;"
terms = ["cmd_ta_shared"]
+++

Line 155 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`SGXMKIF_CMDTA_SHARED`. It backs the glossary structure `cmd_ta_shared`: kernel-written sync/status
block of the TA command.
