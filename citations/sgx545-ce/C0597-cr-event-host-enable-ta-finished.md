+++
id = "C0597"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:500"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L500"
quote = "#define EUR_CR_EVENT_HOST_ENABLE_TA_FINISHED_MASK 0x00002000U"
terms = ["CR_EVENT_HOST_ENABLE.TA_FINISHED"]
+++

Line 500 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_HOST_ENABLE_TA_FINISHED`. It backs the glossary bit field
`CR_EVENT_HOST_ENABLE.TA_FINISHED`: send to host: TA pass finished.
