+++
id = "C0406"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:1020"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L1020"
quote = "#define EUR_CR_BIF_BANK_SET_SELECT_HOST_MASK 0x00000010U"
terms = ["CR_BIF_BANK_SET.SELECT_HOST"]
+++

Line 1020 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_BIF_BANK_SET_SELECT_HOST`. It backs the glossary bit field `CR_BIF_BANK_SET.SELECT_HOST`:
bank register used by host requests.
