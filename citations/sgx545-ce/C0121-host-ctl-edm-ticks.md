+++
id = "C0121"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:96"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L96"
quote = "IMG_UINT32\t\t\t\tui32TimeWraps;"
terms = ["host_ctl.edm_ticks"]
+++

Line 96 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui32TimeWraps`. It backs the glossary field `host_ctl.edm_ticks`: EDM timer tick count; the host never writes
it.
