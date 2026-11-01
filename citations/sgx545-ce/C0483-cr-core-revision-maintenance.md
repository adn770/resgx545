+++
id = "C0483"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:189"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L189"
quote = "#define EUR_CR_CORE_REVISION_MAINTENANCE_MASK 0x000000FFU"
terms = ["CR_CORE_REVISION.MAINTENANCE"]
+++

Line 189 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_CORE_REVISION_MAINTENANCE`. It backs the glossary bit field `CR_CORE_REVISION.MAINTENANCE`:
maintenance revision.
