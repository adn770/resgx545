+++
id = "C0487"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx535defs.h:81"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx535defs.h#L81"
quote = "#define EUR_CR_CORE_REVISION_MAJOR_MASK     0x00FF0000U"
terms = ["CR_CORE_REVISION.MAJOR"]
+++

Line 81 of `sgx535defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_CORE_REVISION_MAJOR`. It backs the glossary bit field `CR_CORE_REVISION.MAJOR`: major
revision.
