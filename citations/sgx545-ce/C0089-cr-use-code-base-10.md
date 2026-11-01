+++
id = "C0089"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx545defs.h:704"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx545defs.h#L704"
quote = "#define EUR_CR_USE_CODE_BASE_10             0x0A34"
terms = ["CR_USE_CODE_BASE_10"]
+++

Line 704 of `sgx545defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_USE_CODE_BASE_10`. It backs the glossary register `CR_USE_CODE_BASE_10`: USSE code base 10:
address and data master.
