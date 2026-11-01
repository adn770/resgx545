+++
id = "C0382"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:120"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L120"
quote = "IMG_UINT32\t\t\tui32Num3DStatusVals;"
terms = ["cmd_ta_shared.num_status_vals_3d"]
+++

Line 120 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui32Num3DStatusVals`. It backs the glossary field `cmd_ta_shared.num_status_vals_3d`: count of
sCtl3DStatusInfo.
