+++
id = "C0007"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:1169"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L1169"
quote = "#define EUR_CR_USE_CODE_BASE(X)     (0x0A0C + (4 * (X)))"
terms = ["CR_USE_CODE_BASE_0"]
+++

Line 1169 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_USE_CODE_BASE(X)`. It backs the glossary register `CR_USE_CODE_BASE_0`: USSE code base 0:
address and data master.
