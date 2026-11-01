+++
id = "C0563"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:293"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L293"
quote = "#define EUR_CR_EVENT_HOST_CLEAR2_GSG_FLUSHED_MASK 0x00000200U"
terms = ["CR_EVENT_HOST_CLEAR2.GSG_FLUSHED"]
+++

Line 293 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_HOST_CLEAR2_GSG_FLUSHED`. It backs the glossary bit field
`CR_EVENT_HOST_CLEAR2.GSG_FLUSHED`: clear: GSG state flushed.
