+++
id = "C0248"
source = "sgx545-ce"
locator = "src/services4/include/sgxinfo.h:61"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/include/sgxinfo.h#L61"
quote = "SGXMKIF_CMD_SETHWPERFSTATUS\t= 9,"
terms = ["CMD.SET_HWPERF_STATUS"]
+++

Line 61 of `sgxinfo.h` in Intel's GPL DDK 1.7 kernel module for Cedarview names
`SGXMKIF_CMD_SETHWPERFSTATUS`. It backs the glossary enum value `CMD.SET_HWPERF_STATUS`: kernel CCB
command 9: set the HWPerf status.
