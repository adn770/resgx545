+++
id = "C0582"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:530"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L530"
quote = "#define EUR_CR_EVENT_HOST_ENABLE_DPM_REACHED_MEM_THRESH_MASK 0x00000008U"
terms = ["CR_EVENT_HOST_ENABLE.DPM_REACHED_MEM_THRESH"]
+++

Line 530 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_HOST_ENABLE_DPM_REACHED_MEM_THRESH`. It backs the glossary bit field
`CR_EVENT_HOST_ENABLE.DPM_REACHED_MEM_THRESH`: send to host: DPM page use reached the threshold.
