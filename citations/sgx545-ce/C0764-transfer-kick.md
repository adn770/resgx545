+++
id = "C0764"
source = "sgx545-ce"
locator = "src/services4/include/sgxinfo.h:414"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgxinfo.h#L414"
quote = "} PVRSRV_TRANSFER_SGX_KICK, *PPVRSRV_TRANSFER_SGX_KICK;"
terms = ["transfer_kick"]
+++

Line 414 of `sgxinfo.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`PVRSRV_TRANSFER_SGX_KICK`. It backs the glossary structure `transfer_kick`: bridge payload of
SGX_SUBMITTRANSFER.
