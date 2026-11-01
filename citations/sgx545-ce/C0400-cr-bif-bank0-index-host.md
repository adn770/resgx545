+++
id = "C0400"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:1039"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L1039"
quote = "#define EUR_CR_BIF_BANK0_INDEX_HOST_MASK    0x00000F00U"
terms = ["CR_BIF_BANK0.INDEX_HOST"]
+++

Line 1039 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_BIF_BANK0_INDEX_HOST`. It backs the glossary bit field `CR_BIF_BANK0.INDEX_HOST`:
directory-list index for host requests.
