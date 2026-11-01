+++
id = "C0550"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:591"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L591"
quote = "#define EUR_CR_EVENT_HOST_CLEAR_TA_TERMINATE_MASK 0x00001000U"
terms = ["CR_EVENT_HOST_CLEAR.TA_TERMINATE"]
+++

Line 591 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_HOST_CLEAR_TA_TERMINATE`. It backs the glossary bit field
`CR_EVENT_HOST_CLEAR.TA_TERMINATE`: clear: TA terminate done.
