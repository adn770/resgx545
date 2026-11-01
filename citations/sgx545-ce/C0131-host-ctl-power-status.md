+++
id = "C0131"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:78"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L78"
quote = "volatile IMG_UINT32\t\tui32PowerStatus;"
terms = ["host_ctl.power_status"]
+++

Line 78 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui32PowerStatus`. It backs the glossary field `host_ctl.power_status`: POWER_STATUS.* bits.
