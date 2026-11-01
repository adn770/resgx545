+++
id = "C0519"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:618"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L618"
quote = "#define EUR_CR_EVENT_HOST_CLEAR_DPM_REACHED_MEM_THRESH_MASK 0x00000008U"
terms = ["CR_EVENT_HOST_CLEAR.DPM_REACHED_MEM_THRESH"]
+++

Line 618 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_HOST_CLEAR_DPM_REACHED_MEM_THRESH`. It backs the glossary bit field
`CR_EVENT_HOST_CLEAR.DPM_REACHED_MEM_THRESH`: clear: DPM page use reached the threshold.
