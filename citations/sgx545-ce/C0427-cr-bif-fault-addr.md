+++
id = "C0427"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:850"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L850"
quote = "#define EUR_CR_BIF_FAULT_ADDR_MASK          0xFFFFF000U"
terms = ["CR_BIF_FAULT.ADDR"]
+++

Line 850 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_BIF_FAULT_ADDR`. It backs the glossary bit field `CR_BIF_FAULT.ADDR`: faulting page address.
