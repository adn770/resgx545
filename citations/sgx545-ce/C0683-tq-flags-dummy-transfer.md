+++
id = "C0683"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:166"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L166"
quote = "#define SGXMKIF_TQFLAGS_DUMMYTRANSFER\t\t\t0x00000020"
terms = ["TQ_FLAGS.DUMMY_TRANSFER"]
+++

Line 166 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`SGXMKIF_TQFLAGS_DUMMYTRANSFER`. It backs the glossary flag `TQ_FLAGS.DUMMY_TRANSFER`: no render,
sync/status only (0x20).
