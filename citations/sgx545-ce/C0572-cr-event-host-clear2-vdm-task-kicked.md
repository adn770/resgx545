+++
id = "C0572"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:281"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L281"
quote = "#define EUR_CR_EVENT_HOST_CLEAR2_VDM_TASK_KICKED_MASK 0x00002000U"
terms = ["CR_EVENT_HOST_CLEAR2.VDM_TASK_KICKED"]
+++

Line 281 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_HOST_CLEAR2_VDM_TASK_KICKED`. It backs the glossary bit field
`CR_EVENT_HOST_CLEAR2.VDM_TASK_KICKED`: clear: VDM task kicked.
