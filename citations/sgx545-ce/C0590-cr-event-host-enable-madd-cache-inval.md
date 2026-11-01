+++
id = "C0590"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:464"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L464"
quote = "#define EUR_CR_EVENT_HOST_ENABLE_MADD_CACHE_INVALCOMPLETE_MASK 0x04000000U"
terms = ["CR_EVENT_HOST_ENABLE.MADD_CACHE_INVAL_COMPLETE"]
+++

Line 464 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_HOST_ENABLE_MADD_CACHE_INVALCOMPLETE`. It backs the glossary bit field
`CR_EVENT_HOST_ENABLE.MADD_CACHE_INVAL_COMPLETE`: send to host: MADD cache invalidate complete.
