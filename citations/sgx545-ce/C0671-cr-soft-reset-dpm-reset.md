+++
id = "C0671"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:213"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L213"
quote = "#define EUR_CR_SOFT_RESET_DPM_RESET_MASK    0x00000002U"
terms = ["CR_SOFT_RESET.DPM_RESET"]
+++

Line 213 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_SOFT_RESET_DPM_RESET`. It backs the glossary bit field `CR_SOFT_RESET.DPM_RESET`: hold the
DPM in reset.
