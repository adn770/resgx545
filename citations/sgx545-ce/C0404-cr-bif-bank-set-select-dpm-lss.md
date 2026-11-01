+++
id = "C0404"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:1029"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L1029"
quote = "#define EUR_CR_BIF_BANK_SET_SELECT_DPM_LSS_MASK 0x00000200U"
terms = ["CR_BIF_BANK_SET.SELECT_DPM_LSS"]
+++

Line 1029 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_BIF_BANK_SET_SELECT_DPM_LSS`. It backs the glossary bit field
`CR_BIF_BANK_SET.SELECT_DPM_LSS`: bank register used by DPM load/store requests.
