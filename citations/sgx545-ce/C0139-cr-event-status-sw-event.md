+++
id = "C0139"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:409"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L409"
quote = "#define EUR_CR_EVENT_STATUS_SW_EVENT_MASK   0x00004000U"
terms = ["CR_EVENT_STATUS.SW_EVENT"]
+++

Line 409 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_STATUS_SW_EVENT`. It backs the glossary bit field `CR_EVENT_STATUS.SW_EVENT`: status:
software event.
