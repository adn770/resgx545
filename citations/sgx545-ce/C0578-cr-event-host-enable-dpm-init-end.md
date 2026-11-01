+++
id = "C0578"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:476"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L476"
quote = "#define EUR_CR_EVENT_HOST_ENABLE_DPM_INITEND_MASK 0x00400000U"
terms = ["CR_EVENT_HOST_ENABLE.DPM_INIT_END"]
+++

Line 476 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_HOST_ENABLE_DPM_INITEND`. It backs the glossary bit field
`CR_EVENT_HOST_ENABLE.DPM_INIT_END`: send to host: DPM initialisation finished.
