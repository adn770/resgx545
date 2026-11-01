+++
id = "C0644"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:330"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L330"
quote = "#define EUR_CR_EVENT_STATUS2_OTPM_MEM_CLEARED_MASK 0x00001000U"
terms = ["CR_EVENT_STATUS2.OTPM_MEM_CLEARED"]
+++

Line 330 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_STATUS2_OTPM_MEM_CLEARED`. It backs the glossary bit field
`CR_EVENT_STATUS2.OTPM_MEM_CLEARED`: status: OTPM memory cleared.
