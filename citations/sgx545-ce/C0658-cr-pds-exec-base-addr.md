+++
id = "C0658"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:747"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L747"
quote = "#define EUR_CR_PDS_EXEC_BASE_ADDR_MASK      0xFFF00000U"
terms = ["CR_PDS_EXEC_BASE.ADDR"]
+++

Line 747 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_PDS_EXEC_BASE_ADDR`. It backs the glossary bit field `CR_PDS_EXEC_BASE.ADDR`: PDS program
base, top 12 bits (1 MB aligned).
