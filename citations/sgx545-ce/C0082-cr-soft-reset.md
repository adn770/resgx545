+++
id = "C0082"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:209"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L209"
quote = "#define EUR_CR_SOFT_RESET                   0x0080"
terms = ["CR_SOFT_RESET"]
+++

Line 209 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_SOFT_RESET`. It backs the glossary register `CR_SOFT_RESET`: per-unit soft reset bits.
