+++
id = "C0070"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:228"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L228"
quote = "#define EUR_CR_EVENT_HOST_ENABLE2           0x0110"
terms = ["CR_EVENT_HOST_ENABLE2"]
+++

Line 228 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_EVENT_HOST_ENABLE2`. It backs the glossary register `CR_EVENT_HOST_ENABLE2`: host interrupt
enable, bank 2.
