+++
id = "C0410"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:800"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L800"
quote = "#define EUR_CR_BIF_CTRL_FLUSH_MASK          0x00000004U"
terms = ["CR_BIF_CTRL.FLUSH"]
+++

Line 800 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_BIF_CTRL_FLUSH`. It backs the glossary bit field `CR_BIF_CTRL.FLUSH`: flush the MMU caches.
