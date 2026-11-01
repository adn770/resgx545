+++
id = "C0120"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:79"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L79"
quote = "volatile IMG_UINT32\t\tui32CleanupStatus;"
terms = ["host_ctl.cleanup_status"]
+++

Line 79 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui32CleanupStatus`. It backs the glossary field `host_ctl.cleanup_status`: CLEANUP_STATUS.* bits.
