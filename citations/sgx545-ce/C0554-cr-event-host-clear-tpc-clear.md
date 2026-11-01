+++
id = "C0554"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:594"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L594"
quote = "#define EUR_CR_EVENT_HOST_CLEAR_TPC_CLEAR_MASK 0x00000800U"
terms = ["CR_EVENT_HOST_CLEAR.TPC_CLEAR"]
+++

Line 594 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_HOST_CLEAR_TPC_CLEAR`. It backs the glossary bit field
`CR_EVENT_HOST_CLEAR.TPC_CLEAR`: clear: tail-pointer cache clear done.
