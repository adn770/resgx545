+++
id = "C0556"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:597"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L597"
quote = "#define EUR_CR_EVENT_HOST_CLEAR_TPC_FLUSH_MASK 0x00000400U"
terms = ["CR_EVENT_HOST_CLEAR.TPC_FLUSH"]
+++

Line 597 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_HOST_CLEAR_TPC_FLUSH`. It backs the glossary bit field
`CR_EVENT_HOST_CLEAR.TPC_FLUSH`: clear: tail-pointer cache flush done.
