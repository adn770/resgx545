+++
id = "C0592"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:485"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L485"
quote = "#define EUR_CR_EVENT_HOST_ENABLE_OTPM_FLUSHED_MASK 0x00080000U"
terms = ["CR_EVENT_HOST_ENABLE.OTPM_FLUSHED"]
+++

Line 485 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_HOST_ENABLE_OTPM_FLUSHED`. It backs the glossary bit field
`CR_EVENT_HOST_ENABLE.OTPM_FLUSHED`: send to host: OTPM flushed.
