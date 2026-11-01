+++
id = "C0477"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:185"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L185"
quote = "#define EUR_CR_CORE_ID_ID_MASK              0xFFFF0000U"
terms = ["CR_CORE_ID.ID"]
+++

Line 185 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_CORE_ID_ID`. It backs the glossary bit field `CR_CORE_ID.ID`: core identifier.
