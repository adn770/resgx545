+++
id = "C0546"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:549"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L549"
quote = "#define EUR_CR_EVENT_HOST_CLEAR_TA_DPM_FAULT_MASK 0x10000000U"
terms = ["CR_EVENT_HOST_CLEAR.TA_DPM_FAULT"]
+++

Line 549 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_HOST_CLEAR_TA_DPM_FAULT`. It backs the glossary bit field
`CR_EVENT_HOST_CLEAR.TA_DPM_FAULT`: clear: TA hit a DPM fault.
