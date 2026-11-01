+++
id = "C0599"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:458"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L458"
quote = "#define EUR_CR_EVENT_HOST_ENABLE_TIMER_MASK 0x20000000U"
terms = ["CR_EVENT_HOST_ENABLE.TIMER"]
+++

Line 458 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_HOST_ENABLE_TIMER`. It backs the glossary bit field `CR_EVENT_HOST_ENABLE.TIMER`: send
to host: event timer expired (CR_EVENT_TIMER).
