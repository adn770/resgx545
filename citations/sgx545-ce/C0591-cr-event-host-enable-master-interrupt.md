+++
id = "C0591"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:455"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L455"
quote = "#define EUR_CR_EVENT_HOST_ENABLE_MASTER_INTERRUPT_MASK 0x80000000U"
terms = ["CR_EVENT_HOST_ENABLE.MASTER_INTERRUPT"]
+++

Line 455 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_HOST_ENABLE_MASTER_INTERRUPT`. It backs the glossary bit field
`CR_EVENT_HOST_ENABLE.MASTER_INTERRUPT`: send to host: summary: some enabled event is pending.
