+++
id = "C0236"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:847"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L847"
quote = "#define EUR_CR_BIF_FAULT_SB_MASK            0x000001F0U"
terms = ["CR_BIF_FAULT.SB"]
+++

Line 847 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_BIF_FAULT_SB`. It backs the glossary bit field `CR_BIF_FAULT.SB`: SB bits of the fault
(meaning open).
