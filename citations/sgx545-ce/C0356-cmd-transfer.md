+++
id = "C0356"
source = "sgx545-ce"
locator = "src/services4/include/sgxinfo.h:53"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgxinfo.h#L53"
quote = "SGXMKIF_CMD_TRANSFER\t\t= 1,"
terms = ["CMD.TRANSFER"]
+++

Line 53 of `sgxinfo.h` in Intel's GPL DDK 1.7 kernel module for Cedarview names
`SGXMKIF_CMD_TRANSFER`. It backs the glossary enum value `CMD.TRANSFER`: kernel CCB command 1: kick
a transfer from a transfer context.
