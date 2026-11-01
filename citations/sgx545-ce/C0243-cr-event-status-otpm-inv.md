+++
id = "C0243"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:394"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L394"
quote = "#define EUR_CR_EVENT_STATUS_OTPM_INV_MASK   0x00100000U"
terms = ["CR_EVENT_STATUS.OTPM_INV"]
+++

Line 394 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_STATUS_OTPM_INV`. It backs the glossary bit field `CR_EVENT_STATUS.OTPM_INV`: status:
OTPM invalidated.
