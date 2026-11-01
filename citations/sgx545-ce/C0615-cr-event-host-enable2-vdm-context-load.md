+++
id = "C0615"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:232"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L232"
quote = "#define EUR_CR_EVENT_HOST_ENABLE2_VDM_CONTEXT_LOAD_MASK 0x00004000U"
terms = ["CR_EVENT_HOST_ENABLE2.VDM_CONTEXT_LOAD"]
+++

Line 232 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_HOST_ENABLE2_VDM_CONTEXT_LOAD`. It backs the glossary bit field
`CR_EVENT_HOST_ENABLE2.VDM_CONTEXT_LOAD`: send to host: VDM context load done.
