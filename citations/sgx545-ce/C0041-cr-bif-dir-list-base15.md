+++
id = "C0041"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:1009"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L1009"
quote = "#define EUR_CR_BIF_DIR_LIST_BASE15          0x0C70"
terms = ["CR_BIF_DIR_LIST_BASE15"]
+++

Line 1009 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_BIF_DIR_LIST_BASE15`. It backs the glossary register `CR_BIF_DIR_LIST_BASE15`:
page-directory base, list 15: the EDM's own directory (0x28b0c000 in 30 of 30 runs, the debugfs
layout's pd_phys), not a list a kick gives a render context's directory.
