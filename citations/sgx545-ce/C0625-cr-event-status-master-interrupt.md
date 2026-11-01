+++
id = "C0625"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:367"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L367"
quote = "#define EUR_CR_EVENT_STATUS_MASTER_INTERRUPT_MASK 0x80000000U"
terms = ["CR_EVENT_STATUS.MASTER_INTERRUPT"]
+++

Line 367 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_STATUS_MASTER_INTERRUPT`. It backs the glossary bit field
`CR_EVENT_STATUS.MASTER_INTERRUPT`: status: summary: some enabled event is pending.
