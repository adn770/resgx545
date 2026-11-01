+++
id = "C0652"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:327"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L327"
quote = "#define EUR_CR_EVENT_STATUS2_VDM_TASK_KICKED_MASK 0x00002000U"
terms = ["CR_EVENT_STATUS2.VDM_TASK_KICKED"]
+++

Line 327 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_STATUS2_VDM_TASK_KICKED`. It backs the glossary bit field
`CR_EVENT_STATUS2.VDM_TASK_KICKED`: status: VDM task kicked.
