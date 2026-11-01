+++
id = "C0529"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:567"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L567"
quote = "#define EUR_CR_EVENT_HOST_CLEAR_ISP2_ZLS_CSW_FINISHED_MASK 0x00200000U"
terms = ["CR_EVENT_HOST_CLEAR.ISP2_ZLS_CSW_FINISHED"]
+++

Line 567 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_HOST_CLEAR_ISP2_ZLS_CSW_FINISHED`. It backs the glossary bit field
`CR_EVENT_HOST_CLEAR.ISP2_ZLS_CSW_FINISHED`: clear: second ISP finished a ZLS context switch.
