+++
id = "C0684"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:160"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L160"
quote = "#define SGXMKIF_TQFLAGS_KEEPPENDING\t\t\t\t0x00000002"
terms = ["TQ_FLAGS.KEEP_PENDING"]
+++

Line 160 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`SGXMKIF_TQFLAGS_KEEPPENDING`. It backs the glossary flag `TQ_FLAGS.KEEP_PENDING`: kernel does not
bump pending counts (0x2).
