+++
id = "C0619"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:433"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L433"
quote = "#define EUR_CR_EVENT_STATUS_DPM_STATE_CLEAR_MASK 0x00000040U"
terms = ["CR_EVENT_STATUS.DPM_STATE_CLEAR"]
+++

Line 433 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_STATUS_DPM_STATE_CLEAR`. It backs the glossary bit field
`CR_EVENT_STATUS.DPM_STATE_CLEAR`: status: DPM state clear done.
