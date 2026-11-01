+++
id = "C0527"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:558"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L558"
quote = "#define EUR_CR_EVENT_HOST_CLEAR_DPM_TA_MEM_FREE_MASK 0x01000000U"
terms = ["CR_EVENT_HOST_CLEAR.DPM_TA_MEM_FREE"]
+++

Line 558 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_HOST_CLEAR_DPM_TA_MEM_FREE`. It backs the glossary bit field
`CR_EVENT_HOST_CLEAR.DPM_TA_MEM_FREE`: clear: DPM finished freeing TA pages.
