+++
id = "C0424"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:1065"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L1065"
quote = "#define EUR_CR_BIF_DIR_LIST_BASE0_ADDR_MASK 0xFFFFFF00U"
terms = ["CR_BIF_DIR_LIST_BASE0.ADDR"]
+++

Line 1065 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_BIF_DIR_LIST_BASE0_ADDR`. It backs the glossary bit field `CR_BIF_DIR_LIST_BASE0.ADDR`:
page-directory address.
