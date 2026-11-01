+++
id = "C0585"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:527"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L527"
quote = "#define EUR_CR_EVENT_HOST_ENABLE_DPM_STATE_STORE_MASK 0x00000010U"
terms = ["CR_EVENT_HOST_ENABLE.DPM_STATE_STORE"]
+++

Line 527 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_HOST_ENABLE_DPM_STATE_STORE`. It backs the glossary bit field
`CR_EVENT_HOST_ENABLE.DPM_STATE_STORE`: send to host: DPM state store done.
