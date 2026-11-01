+++
id = "C0419"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:821"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L821"
quote = "#define EUR_CR_BIF_CTRL_MMU_BYPASS_TSPP_MASK 0x00001000U"
terms = ["CR_BIF_CTRL.MMU_BYPASS_TSPP"]
+++

Line 821 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_BIF_CTRL_MMU_BYPASS_TSPP`. It backs the glossary bit field `CR_BIF_CTRL.MMU_BYPASS_TSPP`:
bypass MMU translation for TSP parameter fetch requests.
