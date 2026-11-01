+++
id = "C0140"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:239"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L239"
quote = "#define PVRSRV_USSE_MISCINFO_GET_STRUCT_SIZES\t0x2UL"
terms = ["MISC_INFO_FLAGS.GET_STRUCT_SIZES"]
+++

Line 239 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`PVRSRV_USSE_MISCINFO_GET_STRUCT_SIZES`. It backs the glossary flag
`MISC_INFO_FLAGS.GET_STRUCT_SIZES`: request struct sizes (0x2).
