+++
id = "C0354"
source = "sgx545-ce"
locator = "src/services4/include/sgxinfo.h:55"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgxinfo.h#L55"
quote = "SGXMKIF_CMD_POWER\t\t\t= 3,"
terms = ["CMD.POWER"]
+++

Line 55 of `sgxinfo.h` in Intel's GPL DDK 1.7 kernel module for Cedarview names `SGXMKIF_CMD_POWER`.
It backs the glossary enum value `CMD.POWER`: kernel CCB command 3: power request (POWER.*).
