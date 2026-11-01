+++
id = "C0418"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:815"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L815"
quote = "#define EUR_CR_BIF_CTRL_MMU_BYPASS_TE_MASK  0x00000400U"
terms = ["CR_BIF_CTRL.MMU_BYPASS_TE"]
+++

Line 815 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_BIF_CTRL_MMU_BYPASS_TE`. It backs the glossary bit field `CR_BIF_CTRL.MMU_BYPASS_TE`: bypass
MMU translation for TE requests.
