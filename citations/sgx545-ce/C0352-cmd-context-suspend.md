+++
id = "C0352"
source = "sgx545-ce"
locator = "src/services4/include/sgxinfo.h:56"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgxinfo.h#L56"
quote = "SGXMKIF_CMD_CONTEXTSUSPEND\t= 4,"
terms = ["CMD.CONTEXT_SUSPEND"]
+++

Line 56 of `sgxinfo.h` in Intel's GPL DDK 1.7 kernel module for Cedarview names
`SGXMKIF_CMD_CONTEXTSUSPEND`. It backs the glossary enum value `CMD.CONTEXT_SUSPEND`: kernel CCB
command 4: suspend or resume a context (CONTEXT_SUSPEND.*).
