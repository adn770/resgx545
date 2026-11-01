+++
id = "C0008"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:634"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L634"
quote = "#define EUR_CR_USE_CODE_BASE_0              0x0A0C"
terms = ["CR_USE_CODE_BASE_0"]
+++

Line 634 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_USE_CODE_BASE_0`. It backs the glossary register `CR_USE_CODE_BASE_0`: USSE code base 0:
address and data master.
