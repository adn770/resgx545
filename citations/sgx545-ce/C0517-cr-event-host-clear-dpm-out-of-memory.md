+++
id = "C0517"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:555"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L555"
quote = "#define EUR_CR_EVENT_HOST_CLEAR_DPM_OUT_OF_MEMORY_ZLS_MASK 0x02000000U"
terms = ["CR_EVENT_HOST_CLEAR.DPM_OUT_OF_MEMORY_ZLS"]
+++

Line 555 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_HOST_CLEAR_DPM_OUT_OF_MEMORY_ZLS`. It backs the glossary bit field
`CR_EVENT_HOST_CLEAR.DPM_OUT_OF_MEMORY_ZLS`: clear: DPM out of memory (ZLS).
