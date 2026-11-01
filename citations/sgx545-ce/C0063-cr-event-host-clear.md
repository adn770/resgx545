+++
id = "C0063"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:542"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L542"
quote = "#define EUR_CR_EVENT_HOST_CLEAR             0x0134"
terms = ["CR_EVENT_HOST_CLEAR"]
+++

Line 542 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_HOST_CLEAR`. It backs the glossary register `CR_EVENT_HOST_CLEAR`: write-1-to-clear
events, bank 1.
