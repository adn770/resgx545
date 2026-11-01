+++
id = "C0552"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:546"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L546"
quote = "#define EUR_CR_EVENT_HOST_CLEAR_TIMER_MASK  0x20000000U"
terms = ["CR_EVENT_HOST_CLEAR.TIMER"]
+++

Line 546 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_HOST_CLEAR_TIMER`. It backs the glossary bit field `CR_EVENT_HOST_CLEAR.TIMER`: clear:
event timer expired (CR_EVENT_TIMER).
