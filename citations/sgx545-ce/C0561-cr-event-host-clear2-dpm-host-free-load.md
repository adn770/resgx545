+++
id = "C0561"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:311"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L311"
quote = "#define EUR_CR_EVENT_HOST_CLEAR2_DPM_HOST_FREE_LOAD_MASK 0x00000004U"
terms = ["CR_EVENT_HOST_CLEAR2.DPM_HOST_FREE_LOAD"]
+++

Line 311 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_HOST_CLEAR2_DPM_HOST_FREE_LOAD`. It backs the glossary bit field
`CR_EVENT_HOST_CLEAR2.DPM_HOST_FREE_LOAD`: clear: DPM host free-list load done.
