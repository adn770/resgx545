+++
id = "C0339"
source = "sgx545-ce"
locator = "src/services4/srvkm/devices/sgx/sgxinfokm.h:315"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/devices/sgx/sgxinfokm.h#L315"
quote = "PVRSRV_KERNEL_MEM_INFO  *psHWBlockKernelMemInfo;"
terms = ["pb_block"]
+++

Line 315 of `sgxinfokm.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`psHWBlockKernelMemInfo`. It backs the glossary structure `pb_block`: GPL name of the HW PB block
allocation.
