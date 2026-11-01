+++
id = "C0141"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:238"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L238"
quote = "#define PVRSRV_USSE_MISCINFO_READY\t\t0x1UL"
terms = ["MISC_INFO_FLAGS.READY"]
+++

Line 238 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`PVRSRV_USSE_MISCINFO_READY`. It backs the glossary flag `MISC_INFO_FLAGS.READY`: reply ready (0x1).
