+++
id = "C0484"
source = "sgx545-ce"
locator = "src/services4/srvkm/hwdefs/sgx535defs.h:77"
link = "https://github.com/The1TrueJoe/sgx545-ce/blob/1c3ecae090ad7b5801a351cf1341bbcd56e03440/src/services4/srvkm/hwdefs/sgx535defs.h#L77"
quote = "#define EUR_CR_CORE_REVISION_MAINTENANCE_MASK 0x000000FFU"
terms = ["CR_CORE_REVISION.MAINTENANCE"]
+++

Line 77 of `sgx535defs.h` in Intel's GPL DDK 1.7 kernel module for Cedarview defines
`EUR_CR_CORE_REVISION_MAINTENANCE`. It backs the glossary bit field `CR_CORE_REVISION.MAINTENANCE`:
maintenance revision.
