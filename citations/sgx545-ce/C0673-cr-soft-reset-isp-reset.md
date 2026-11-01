+++
id = "C0673"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:222"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L222"
quote = "#define EUR_CR_SOFT_RESET_ISP_RESET_MASK    0x00000010U"
terms = ["CR_SOFT_RESET.ISP_RESET"]
+++

Line 222 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_SOFT_RESET_ISP_RESET`. It backs the glossary bit field `CR_SOFT_RESET.ISP_RESET`: hold the
ISP in reset.
