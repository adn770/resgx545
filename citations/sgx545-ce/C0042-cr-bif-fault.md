+++
id = "C0042"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:843"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L843"
quote = "#define EUR_CR_BIF_FAULT                    0x0C08"
terms = ["CR_BIF_FAULT"]
+++

Line 843 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_BIF_FAULT`. It backs the glossary register `CR_BIF_FAULT`: MMU faulting address and context.
