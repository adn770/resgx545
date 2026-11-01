+++
id = "C0573"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:494"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L494"
quote = "#define EUR_CR_EVENT_HOST_ENABLE_BREAKPOINT_MASK 0x00008000U"
terms = ["CR_EVENT_HOST_ENABLE.BREAKPOINT"]
+++

Line 494 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_HOST_ENABLE_BREAKPOINT`. It backs the glossary bit field
`CR_EVENT_HOST_ENABLE.BREAKPOINT`: send to host: breakpoint hit.
