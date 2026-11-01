+++
id = "C0538"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:573"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L573"
quote = "#define EUR_CR_EVENT_HOST_CLEAR_OTPM_FLUSHED_MASK 0x00080000U"
terms = ["CR_EVENT_HOST_CLEAR.OTPM_FLUSHED"]
+++

Line 573 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_HOST_CLEAR_OTPM_FLUSHED`. It backs the glossary bit field
`CR_EVENT_HOST_CLEAR.OTPM_FLUSHED`: clear: OTPM flushed.
