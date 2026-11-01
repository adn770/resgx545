+++
id = "C0036"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:793"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L793"
quote = "#define EUR_CR_BIF_CTRL                     0x0C00"
terms = ["CR_BIF_CTRL"]
+++

Line 793 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_BIF_CTRL`. It backs the glossary register `CR_BIF_CTRL`: MMU control: pause, invalidate,
clear fault.
