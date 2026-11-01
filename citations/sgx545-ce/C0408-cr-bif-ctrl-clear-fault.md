+++
id = "C0408"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:806"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L806"
quote = "#define EUR_CR_BIF_CTRL_CLEAR_FAULT_MASK    0x00000010U"
terms = ["CR_BIF_CTRL.CLEAR_FAULT"]
+++

Line 806 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_BIF_CTRL_CLEAR_FAULT`. It backs the glossary bit field `CR_BIF_CTRL.CLEAR_FAULT`: clear the
latched MMU fault.
