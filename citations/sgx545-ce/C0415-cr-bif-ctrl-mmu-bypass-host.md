+++
id = "C0415"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:830"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L830"
quote = "#define EUR_CR_BIF_CTRL_MMU_BYPASS_HOST_MASK 0x00008000U"
terms = ["CR_BIF_CTRL.MMU_BYPASS_HOST"]
+++

Line 830 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_BIF_CTRL_MMU_BYPASS_HOST`. It backs the glossary bit field `CR_BIF_CTRL.MMU_BYPASS_HOST`:
bypass MMU translation for host requests.
