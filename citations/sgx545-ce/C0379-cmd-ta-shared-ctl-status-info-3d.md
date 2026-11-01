+++
id = "C0379"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:153"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L153"
quote = "CTL_STATUS\t\t\tsCtl3DStatusInfo[SGX_MAX_3D_STATUS_VALS];"
terms = ["cmd_ta_shared.ctl_status_info_3d"]
+++

Line 153 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`sCtl3DStatusInfo`. It backs the glossary field `cmd_ta_shared.ctl_status_info_3d`: status updates
at render end [4].
