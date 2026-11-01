+++
id = "C0075"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:366"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L366"
quote = "#define EUR_CR_EVENT_STATUS                 0x012C"
terms = ["CR_EVENT_STATUS"]
+++

Line 366 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_STATUS`. It backs the glossary register `CR_EVENT_STATUS`: event (interrupt) status,
bank 1.
