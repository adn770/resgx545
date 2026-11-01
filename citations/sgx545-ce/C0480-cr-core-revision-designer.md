+++
id = "C0480"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:198"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L198"
quote = "#define EUR_CR_CORE_REVISION_DESIGNER_MASK  0xFF000000U"
terms = ["CR_CORE_REVISION.DESIGNER"]
+++

Line 198 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_CORE_REVISION_DESIGNER`. It backs the glossary bit field `CR_CORE_REVISION.DESIGNER`:
designer revision.
