+++
id = "C0146"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:52"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L52"
quote = "IMG_UINT32\t\t\t\tui32CacheControl;"
terms = ["command.cache_control"]
+++

Line 52 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`ui32CacheControl`. It backs the glossary field `command.cache_control`: CACHE_CONTROL.*
invalidations done before the command.
