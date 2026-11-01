+++
id = "C0135"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:953"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L953"
quote = "#define EUR_CR_BIF_DIR_LIST_BASE1           0x0C38"
terms = ["CR_BIF_DIR_LIST_BASE1"]
+++

Line 953 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_BIF_DIR_LIST_BASE1`. It backs the glossary register `CR_BIF_DIR_LIST_BASE1`: page-directory
base, list 1: the first kick of a VM after a reset writes the render context's page directory there
(the HW context's PD word, 3 of 3 jobs); the TA and 3D requestors translate through it during a
render.
