+++
id = "C0505"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:600"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L600"
quote = "#define EUR_CR_EVENT_HOST_CLEAR_DPM_CONTROL_CLEAR_MASK 0x00000200U"
terms = ["CR_EVENT_HOST_CLEAR.DPM_CONTROL_CLEAR"]
+++

Line 600 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_HOST_CLEAR_DPM_CONTROL_CLEAR`. It backs the glossary bit field
`CR_EVENT_HOST_CLEAR.DPM_CONTROL_CLEAR`: clear: DPM control clear done.
