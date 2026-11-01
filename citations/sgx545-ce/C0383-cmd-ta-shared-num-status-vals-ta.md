+++
id = "C0383"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:119"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L119"
quote = "IMG_UINT32\t\t\tui32NumTAStatusVals;"
terms = ["cmd_ta_shared.num_status_vals_ta"]
+++

Line 119 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui32NumTAStatusVals`. It backs the glossary field `cmd_ta_shared.num_status_vals_ta`: count of
sCtlTAStatusInfo.
