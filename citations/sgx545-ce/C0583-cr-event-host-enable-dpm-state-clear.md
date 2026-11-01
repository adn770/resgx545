+++
id = "C0583"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:521"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L521"
quote = "#define EUR_CR_EVENT_HOST_ENABLE_DPM_STATE_CLEAR_MASK 0x00000040U"
terms = ["CR_EVENT_HOST_ENABLE.DPM_STATE_CLEAR"]
+++

Line 521 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_HOST_ENABLE_DPM_STATE_CLEAR`. It backs the glossary bit field
`CR_EVENT_HOST_ENABLE.DPM_STATE_CLEAR`: send to host: DPM state clear done.
