+++
id = "C0142"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:67"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L67"
quote = "} PVRSRV_SGX_CCB_CTL;"
terms = ["ccb_ctl", "hw_transfer_context.ccb_ctl_dev_vaddr"]
+++

Line 67 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`PVRSRV_SGX_CCB_CTL`. It backs the glossary structure `ccb_ctl`: CCB control: write and read offsets
(kernel and client CCBs); the glossary field `hw_render_context.ccb_ctl_dev_vaddr`: TA client CCB
control; and the glossary field `hw_transfer_context.ccb_ctl_dev_vaddr`: transfer CCB control.
