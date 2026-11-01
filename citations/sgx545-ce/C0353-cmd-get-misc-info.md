+++
id = "C0353"
source = "sgx545-ce"
locator = "src/services4/include/sgxinfo.h:58"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgxinfo.h#L58"
quote = "SGXMKIF_CMD_GETMISCINFO\t\t= 6,"
terms = ["CMD.GET_MISC_INFO"]
+++

Line 58 of `sgxinfo.h` in Intel's GPL DDK 1.7 kernel module for Cedarview names
`SGXMKIF_CMD_GETMISCINFO`. It backs the glossary enum value `CMD.GET_MISC_INFO`: kernel CCB command
6: fill the misc-info buffer.
