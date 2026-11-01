+++
id = "C0570"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:299"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L299"
quote = "#define EUR_CR_EVENT_HOST_CLEAR2_TRIG_TA_MASK 0x00000080U"
terms = ["CR_EVENT_HOST_CLEAR2.TRIG_TA"]
+++

Line 299 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_HOST_CLEAR2_TRIG_TA`. It backs the glossary bit field `CR_EVENT_HOST_CLEAR2.TRIG_TA`:
clear: TA trigger.
