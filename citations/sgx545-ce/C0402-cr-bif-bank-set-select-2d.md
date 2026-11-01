+++
id = "C0402"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:1014"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L1014"
quote = "#define EUR_CR_BIF_BANK_SET_SELECT_2D_MASK  0x00000001U"
terms = ["CR_BIF_BANK_SET.SELECT_2D"]
+++

Line 1014 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_BIF_BANK_SET_SELECT_2D`. It backs the glossary bit field `CR_BIF_BANK_SET.SELECT_2D`: bank
register used by 2D core requests.
