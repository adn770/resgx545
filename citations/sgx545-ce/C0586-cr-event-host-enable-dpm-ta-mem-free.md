+++
id = "C0586"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:470"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L470"
quote = "#define EUR_CR_EVENT_HOST_ENABLE_DPM_TA_MEM_FREE_MASK 0x01000000U"
terms = ["CR_EVENT_HOST_ENABLE.DPM_TA_MEM_FREE"]
+++

Line 470 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_HOST_ENABLE_DPM_TA_MEM_FREE`. It backs the glossary bit field
`CR_EVENT_HOST_ENABLE.DPM_TA_MEM_FREE`: send to host: DPM finished freeing TA pages.
