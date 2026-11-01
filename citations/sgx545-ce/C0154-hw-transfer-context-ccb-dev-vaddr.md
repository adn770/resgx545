+++
id = "C0154"
source = "sgx545-ce"
locator = "src/services4/include/sgxinfo.h:377"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgxinfo.h#L377"
quote = "IMG_SID\t\t\thCCBMemInfo;"
terms = ["hw_transfer_context.ccb_dev_vaddr"]
+++

Line 377 of `sgxinfo.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares `hCCBMemInfo`.
It backs the glossary field `hw_transfer_context.ccb_dev_vaddr`: transfer client CCB; and the
glossary field `transfer_kick.ccb_kernel_mem_info`: transfer client CCB meminfo.
