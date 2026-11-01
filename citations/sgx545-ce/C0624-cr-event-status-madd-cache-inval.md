+++
id = "C0624"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:376"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L376"
quote = "#define EUR_CR_EVENT_STATUS_MADD_CACHE_INVALCOMPLETE_MASK 0x04000000U"
terms = ["CR_EVENT_STATUS.MADD_CACHE_INVAL_COMPLETE"]
+++

Line 376 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_STATUS_MADD_CACHE_INVALCOMPLETE`. It backs the glossary bit field
`CR_EVENT_STATUS.MADD_CACHE_INVAL_COMPLETE`: status: MADD cache invalidate complete.
