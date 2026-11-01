+++
id = "C0732"
source = "sgx545-ce"
locator = "src/services4/include/sgx_mkif_km.h:114"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgx_mkif_km.h#L114"
quote = "#define\tSGXMKIF_CMDTA_CTRLFLAGS_READY\t\t\t0x00000001"
terms = ["CMD_TA_CTRL_FLAGS.READY"]
+++

Line 114 of `sgx_mkif_km.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`SGXMKIF_CMDTA_CTRLFLAGS_READY`. It backs the glossary flag `CMD_TA_CTRL_FLAGS.READY`: shared block
complete; set last (0x1).
