+++
id = "C0422"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:794"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L794"
quote = "#define EUR_CR_BIF_CTRL_NOREORDER_MASK      0x00000001U"
terms = ["CR_BIF_CTRL.NO_REORDER"]
+++

Line 794 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_BIF_CTRL_NOREORDER`. It backs the glossary bit field `CR_BIF_CTRL.NO_REORDER`: disable
memory request reordering.
