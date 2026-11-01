+++
id = "C0145"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:65"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L65"
quote = "IMG_UINT32\t\t\t\tui32WriteOffset;"
terms = ["ccb_ctl.write_offset"]
+++

Line 65 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui32WriteOffset`. It backs the glossary field `ccb_ctl.write_offset`: write offset (host advances).
