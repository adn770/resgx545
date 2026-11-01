+++
id = "C0034"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:1013"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L1013"
quote = "#define EUR_CR_BIF_BANK_SET                 0x0C74"
terms = ["CR_BIF_BANK_SET"]
+++

Line 1013 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_BIF_BANK_SET`. It backs the glossary register `CR_BIF_BANK_SET`: selects which bank register
each requestor uses.
