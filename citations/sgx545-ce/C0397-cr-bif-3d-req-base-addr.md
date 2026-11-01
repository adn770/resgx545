+++
id = "C0397"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:1077"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L1077"
quote = "#define EUR_CR_BIF_3D_REQ_BASE_ADDR_MASK    0xFFF00000U"
terms = ["CR_BIF_3D_REQ_BASE.ADDR"]
+++

Line 1077 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_BIF_3D_REQ_BASE_ADDR`. It backs the glossary bit field `CR_BIF_3D_REQ_BASE.ADDR`: heap base
for these requests (top 12 bits).
