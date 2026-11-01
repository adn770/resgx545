+++
id = "C0610"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:241"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L241"
quote = "#define EUR_CR_EVENT_HOST_ENABLE2_OTPM_FLUSHED_INV_MASK 0x00000800U"
terms = ["CR_EVENT_HOST_ENABLE2.OTPM_FLUSHED_INV"]
+++

Line 241 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_HOST_ENABLE2_OTPM_FLUSHED_INV`. It backs the glossary bit field
`CR_EVENT_HOST_ENABLE2.OTPM_FLUSHED_INV`: send to host: OTPM flush and invalidate done.
