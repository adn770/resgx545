+++
id = "C0515"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:624"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L624"
quote = "#define EUR_CR_EVENT_HOST_CLEAR_DPM_OUT_OF_MEMORY_MT_MASK 0x00000002U"
terms = ["CR_EVENT_HOST_CLEAR.DPM_OUT_OF_MEMORY_MT"]
+++

Line 624 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_HOST_CLEAR_DPM_OUT_OF_MEMORY_MT`. It backs the glossary bit field
`CR_EVENT_HOST_CLEAR.DPM_OUT_OF_MEMORY_MT`: clear: DPM out of memory (macrotile).
