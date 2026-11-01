+++
id = "C0235"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:844"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L844"
quote = "#define EUR_CR_BIF_FAULT_CID_MASK           0x0000000FU"
terms = ["CR_BIF_FAULT.CID"]
+++

Line 844 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_BIF_FAULT_CID`. It backs the glossary bit field `CR_BIF_FAULT.CID`: directory-list index
(context) of the fault.
