+++
id = "C0569"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:305"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L305"
quote = "#define EUR_CR_EVENT_HOST_CLEAR2_TRIG_DL_MASK 0x00000020U"
terms = ["CR_EVENT_HOST_CLEAR2.TRIG_DL"]
+++

Line 305 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_HOST_CLEAR2_TRIG_DL`. It backs the glossary bit field `CR_EVENT_HOST_CLEAR2.TRIG_DL`:
clear: DL trigger.
