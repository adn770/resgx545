+++
id = "C0163"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:309"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L309"
quote = "SGX_MISCINFO_STRUCT_SIZES\t\tsSGXStructSizes;"
terms = ["misc_info.struct_sizes"]
+++

Line 309 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview declares
`sSGXStructSizes`. It backs the glossary field `misc_info.struct_sizes`: structure sizes block.
