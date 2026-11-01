+++
id = "C0355"
source = "sgx545-ce"
locator = "src/services4/include/sgxinfo.h:52"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgxinfo.h#L52"
quote = "SGXMKIF_CMD_TA\t\t\t\t= 0,"
terms = ["CMD.TA"]
+++

Line 52 of `sgxinfo.h` in Intel's GPL DDK 1.7 kernel module for Cedarview names `SGXMKIF_CMD_TA`. It
backs the glossary enum value `CMD.TA`: kernel CCB command 0: kick a TA (and its 3D) from a render
context.
