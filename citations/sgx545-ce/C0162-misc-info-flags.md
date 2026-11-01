+++
id = "C0162"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:307"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L307"
quote = "IMG_UINT32\t\t\t\t\t\tui32MiscInfoFlags;"
terms = ["misc_info.flags"]
+++

Line 307 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui32MiscInfoFlags`. It backs the glossary field `misc_info.flags`: MISC_INFO_FLAGS.* request/ready
bits.
