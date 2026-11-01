+++
id = "C0241"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:439"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L439"
quote = "#define EUR_CR_EVENT_STATUS_DPM_STATE_STORE_MASK 0x00000010U"
terms = ["CR_EVENT_STATUS.DPM_STATE_STORE"]
+++

Line 439 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_STATUS_DPM_STATE_STORE`. It backs the glossary bit field
`CR_EVENT_STATUS.DPM_STATE_STORE`: status: DPM state store done.
