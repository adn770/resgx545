+++
id = "C0059"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx535defs.h:76"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx535defs.h#L76"
quote = "#define EUR_CR_CORE_REVISION                0x0014"
terms = ["CR_CORE_REVISION"]
+++

Line 76 of `sgx535defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_CORE_REVISION`. It backs the glossary register `CR_CORE_REVISION`: silicon revision
(designer/major/minor/maint).
