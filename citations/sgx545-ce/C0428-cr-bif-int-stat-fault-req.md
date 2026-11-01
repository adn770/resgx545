+++
id = "C0428"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:834"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L834"
quote = "#define EUR_CR_BIF_INT_STAT_FAULT_REQ_MASK  0x0000FFFFU"
terms = ["CR_BIF_INT_STAT.FAULT_REQ"]
+++

Line 834 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_BIF_INT_STAT_FAULT_REQ`. It backs the glossary bit field `CR_BIF_INT_STAT.FAULT_REQ`:
requestors that faulted.
