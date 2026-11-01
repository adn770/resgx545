+++
id = "C0403"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:1017"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L1017"
quote = "#define EUR_CR_BIF_BANK_SET_SELECT_3D_MASK  0x0000000CU"
terms = ["CR_BIF_BANK_SET.SELECT_3D"]
+++

Line 1017 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_BIF_BANK_SET_SELECT_3D`. It backs the glossary bit field `CR_BIF_BANK_SET.SELECT_3D`: bank
register used by 3D requests.
