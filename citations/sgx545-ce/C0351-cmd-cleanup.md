+++
id = "C0351"
source = "sgx545-ce"
locator = "src/services4/include/sgxinfo.h:57"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgxinfo.h#L57"
quote = "SGXMKIF_CMD_CLEANUP\t\t\t= 5,"
terms = ["CMD.CLEANUP"]
+++

Line 57 of `sgxinfo.h` in Intel's GPL DDK 1.7 kernel module for Cedarview names
`SGXMKIF_CMD_CLEANUP`. It backs the glossary enum value `CMD.CLEANUP`: kernel CCB command 5: release
a firmware object (CLEANUP.*).
