+++
id = "C0013"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:638"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L638"
quote = "#define EUR_CR_USE_CODE_BASE_DM_00_MASK     0x06000000U"
terms = ["CR_USE_CODE_BASE_0.DM"]
+++

Line 638 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_USE_CODE_BASE_DM_00`. It backs the glossary bit field `CR_USE_CODE_BASE_0.DM`: data master
that owns a USE code base.
