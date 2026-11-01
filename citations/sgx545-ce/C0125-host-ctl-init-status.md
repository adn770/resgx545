+++
id = "C0125"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:77"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L77"
quote = "volatile IMG_UINT32\t\tui32InitStatus;"
terms = ["host_ctl.init_status"]
+++

Line 77 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui32InitStatus`. It backs the glossary field `host_ctl.init_status`: EDM init status;
INIT_STATUS.COMPLETE.
