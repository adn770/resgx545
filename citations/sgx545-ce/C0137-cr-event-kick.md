+++
id = "C0137"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:754"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L754"
quote = "#define EUR_CR_EVENT_KICK                   0x0AC8"
terms = ["CR_EVENT_KICK"]
+++

Line 754 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_KICK`. It backs the glossary register `CR_EVENT_KICK`: host doorbell: start the EDM
event task.
