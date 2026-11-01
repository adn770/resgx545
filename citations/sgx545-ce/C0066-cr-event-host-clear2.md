+++
id = "C0066"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:274"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L274"
quote = "#define EUR_CR_EVENT_HOST_CLEAR2            0x0114"
terms = ["CR_EVENT_HOST_CLEAR2"]
+++

Line 274 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_HOST_CLEAR2`. It backs the glossary register `CR_EVENT_HOST_CLEAR2`: write-1-to-clear
events, bank 2.
