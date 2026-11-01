+++
id = "C0237"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:424"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L424"
quote = "#define EUR_CR_EVENT_STATUS_DPM_CONTROL_CLEAR_MASK 0x00000200U"
terms = ["CR_EVENT_STATUS.DPM_CONTROL_CLEAR"]
+++

Line 424 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_STATUS_DPM_CONTROL_CLEAR`. It backs the glossary bit field
`CR_EVENT_STATUS.DPM_CONTROL_CLEAR`: status: DPM control clear done.
