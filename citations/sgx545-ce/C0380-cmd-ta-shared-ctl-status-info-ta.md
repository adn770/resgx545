+++
id = "C0380"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:152"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L152"
quote = "CTL_STATUS\t\t\tsCtlTAStatusInfo[SGX_MAX_TA_STATUS_VALS];"
terms = ["cmd_ta_shared.ctl_status_info_ta"]
+++

Line 152 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`sCtlTAStatusInfo`. It backs the glossary field `cmd_ta_shared.ctl_status_info_ta`: status updates
at TA end [32].
