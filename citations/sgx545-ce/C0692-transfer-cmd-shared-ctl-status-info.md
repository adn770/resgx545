+++
id = "C0692"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:191"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L191"
quote = "CTL_STATUS  \tsCtlStatusInfo[SGXTQ_MAX_STATUS];"
terms = ["transfer_cmd_shared.ctl_status_info"]
+++

Line 191 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`sCtlStatusInfo`. It backs the glossary field `transfer_cmd_shared.ctl_status_info`: status updates
[4] incl. the fence.
